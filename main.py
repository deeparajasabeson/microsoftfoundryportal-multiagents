from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from agents import FoundryCoordinatorAgent, FoundrySalesAgent, FoundrySupportAgent, foundry_client

class AgentQueryRequest(BaseModel):
    query: str = Field(
        ..., 
        min_length=1, 
        description="Customer query to route through the coordinator"
    )

class AgentQueryResponse(BaseModel):
    response:str

class DeploymentInfoResponse(BaseModel):
    foundry_project_endpoint: str
    model_deployment: str

class CleanupResponse(BaseModel):
    status: str
    detail: str

async def _create_coordinator() -> FoundryCoordinatorAgent:
    sales_agent = FoundrySalesAgent("SalesAgent")
    support_agent = FoundrySupportAgent("SupportAgent")
    coordinator = FoundryCoordinatorAgent(
        agents = [sales_agent, support_agent],
    )

    await support_agent.initialize()
    await sales_agent.initialize()
    await coordinator.initialize()
    return coordinator

@asynccontextmanager
async def lifespan(_: FastAPI):
    app.state.coordinator = await _create_coordinator()
    yield


app = FastAPI(
    title="Azure AI Foundry Multi-Agent API",
    description = "FastAPI service for coordinator-based agent routing in Azure AI Foundry.",
    version="1.0.0",
    docs_url="/swagger",
     lifespan=lifespan
)


# To test whether everything works fine

@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


# This is to set up the agents

@app.get("/agent/deployment", response_model=DeploymentInfoResponse)
async def get_deployment_info() -> DeploymentInfoResponse:
    return DeploymentInfoResponse(
        foundry_project_endpoint=foundry_client.project_endpoint,
        model_deployment=foundry_client.model_deployment
    )


# This is to handle the query 

@app.post("/agent/query", response_model=AgentQueryResponse)
async def route_agent_query(request: AgentQueryRequest) -> AgentQueryResponse:
    coordinator = getattr(app.state, "coordinator", None)
    if coordinator is None:
        try:
            coordinator = await _create_coordinator()
            app.state.coordinator = coordinator
        except Exception as ex:
            raise HTTPException(status_code=500, detail=f"Agent initialization failed: {str(ex)}") from ex

    try:
        response = await coordinator.route_query(request.query)        
    except Exception as ex:
        raise HTTPException(status_code=500, detail=f"Agent query failed: {ex}") from ex

    return AgentQueryResponse(response=response)


# This is to clean up the agents

@app.post("/agent/cleanup", response_model=CleanupResponse)
async def cleanup_agents() -> CleanupResponse:
    try:
        print("Agents before cleanup:", app.state.coordinator)  # Debug
        await foundry_client.cleanup_agents()
        app.state.coordinator = None
    except KeyError as ke:
        print(f"KeyError during cleanup: {ke}")  # See which key is missing
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {ke}") from ke
    except Exception as ex:
        print(f"Exception during cleanup: {ex}")  # Catch all other errors
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {ex}") from ex
    
    return CleanupResponse(
        status="success", 
        detail="Agents cleaned up successfully."
    )