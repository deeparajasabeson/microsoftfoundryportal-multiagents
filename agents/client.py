import os
import json
from typing import List, Dict
from dotenv import load_dotenv
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from azure.ai.projects.models import PromptAgentDefinition
from openai.types.responses.response_input_param import FunctionCallOutput

load_dotenv()


class FoundryAgentClient:
    """
    Client for interacting with Azure AI Foundry Agents.
    """
    def __init__(self, project_endpoint: str = None):
        
        self.project_endpoint = project_endpoint or os.getenv("FOUNDRY_PROJECT_ENDPOINT")        
        if not self.project_endpoint :
            raise ValueError("FOUNDRY_PROJECT_ENDPOINT is not set in the environment variables.")

        self.model_deployment = os.getenv("AZURE_AI_MODEL_DEPLOYMENT_NAME")
        if not self.model_deployment:
            raise ValueError("AZURE_AI_MODEL_DEPLOYMENT_NAME is not set in the environment variables.")

        self.client = None
        self.agents_client = None
        self.openai_client = None
        self.created_agents = []

        self._initialize_client()


    def _initialize_client(self):
        """
        Initialize the Azure AI client with DefaultAzureCredential.
        """
        try:
            credential = DefaultAzureCredential()
            self.client = AIProjectClient(
                endpoint=self.project_endpoint, 
                credential=credential
            )
            self.agents_client = self.client.agents

            # v2.x: get an authenticated OpenAI client - used for all conversations/responses
            self.openai_client = self.client.get_openai_client()

            print("Azure AI Foundry Agents SDK (v2.x) initialized successfully.")

        except ImportError as ex:
            raise ImportError(
                f"Azure AI Foundry SDK not installed: {ex}\n"
                "Run: pip install azure-ai-projects"
            )

        except Exception as ex:
            raise Exception(
                f"Azure AI Foundry initialization failed: {ex}\n"
                "Make sure you're logged in with 'az login'"
            )

             
    async def create_agent(
            self,
            name: str,
            instructions: str = None,
            tools: List = None
    ) -> Dict:
        """
        Create a new agent using  Azure AI Foundry Agents SDK v2.x.
        v1.x: agents_client.create_agent(config_dict)
        v2.x: agents_client.create_version(agent_name, definition=PromptAgentDefinition(...))
        """

        try:
            print(f"DEBUG: Creating agent '{name}' with instructions={instructions is not None}, tools count={len(tools or [])}")

            agent = self.agents_client.create_version(
                agent_name=name,
                definition=PromptAgentDefinition(
                    model=self.model_deployment,
                    instructions=instructions,
                    tools=tools or []
                )
            )

            print(f"DEBUG: Agent created. agent.name={agent.name}, agent.version={agent.version}")
            self.created_agents.append({
                "agent_name": agent.name, 
                "agent_version": agent.version
            })

            result = {
                "agent_id": agent.name, 
                "agent_name": name, 
                "agent_version": agent.version
            }
            print(f"DEBUG: Returning: {result}")
            return result
               
        except Exception as ex:
            print(f"ERROR in create_agent: {str(ex)}")
            raise Exception(f"Agent creation failed: {str(ex)}")

    async def create_thread(self) -> Dict:
        """
        Create a conversation (replaces thread concept in v2.x).
        v1.x: agents_client.threads.create()
        v2.x: openai_client.conversations.create(items=[])
        :return: Dictionary containing the created thread's details.
        """
        try:
            conversation = self.openai_client.conversations.create(items=[])
            return {"id": conversation.id}
        except Exception as ex:
            raise Exception(f"Conversation creation failed: {str(ex)}")


    async def run_agent(
            self,
            agent_name: str,
            conversation_id: str,
            message: str
    ) -> str:
        """
        Run agent with message in conversation - v2.x.
        v1.x required: messages.create() -> runs.create() -> polling loop  -> messages.list()
        v2.x: add message -> responses.create() -> inspect response.output for function calls
        """
        try:
            self.openai_client.conversations.items.create(
                conversation_id=conversation_id,
                items=[{
                    "type": "message", 
                    "role":"user", 
                    "content":message
                }]
            )

            response = self.openai_client.responses.create(
                conversation=conversation_id,
                extra_body={"agent_reference": {
                    "name": agent_name,
                    "type": "agent_reference"
                }}
            )

            for _ in range(5):
                function_outputs = []
                for item in response.output:
                    if item.type == "function_call":
                        result = await self._execute_function_call(
                            item.name,
                            json.loads(item.arguments)
                        )
                        function_outputs.append(
                            FunctionCallOutput(
                                type = "function_call_output",
                                call_id = item.call_id,
                                output = result,
                            )
                        )
                if not function_outputs:
                    return response.output_text or "No response generated."

                #v2.x: responses.create(input=outputs, previous_response_id=response.id)
                response = self.openai_client.responses.create(
                    input = function_outputs,
                    previous_response_id = response.id,
                    extra_body = {
                        "agent_reference": {
                            "name": agent_name,
                            "type": "agent_reference"
                        }
                    }
                )

            return response.output_text or "No response generated."
        except Exception as ex:
            raise Exception(f"Agent run failed: {str(ex)}")



    async def _execute_function_call(
            self,
            function_name: str,
            arguments: Dict)  -> str:
        """
        Execute a function call and return the result.
        """
        try:
            if function_name == "lookup_faq":
                topic = arguments.get("topic", "")
                faq_db = {
                    "warranty": "Our products come with a 1-year warranty covering manufacturing defects.",
                    "return": "You can return any item within 30 days with a receipt.",
                    "shipping": "Standard shipping takes 3-5 business days.  Express is 1-2 days."
                }
                return faq_db.get(topic, f"No information found for topic: {topic}")

            elif function_name == "check_order_status":
                order_id = arguments.get("order_id", "")
                order_db = {
                    "12345": "Shipped, expected delivery in 2 days.",
                    "67890": "Processing, estimated ship date tomorrow ",
                    "54321": "Delivered, left at front door."
                }
                return order_db.get(order_id, f"Order {order_id} not found in our system.")

            elif function_name == "get_current_promotions":
                category = arguments.get("category", "all")
                promotions = {
                    "all": "Current promotions: 10% off electronics, Buy 2 get 1 free clothing, 15% off home items.",
                    "electronics": "10% off all electronics until end of month.",
                    "clothing": "Buy 2 get 1 free on all clothing items.",
                    "home": "15% off home decor and furniture."
                }
                return promotions.get(category, promotions["all"])

            else:
                return f"Unknown function: {function_name}"
        except Exception as ex:
            return f"Error executing function {function_name}: {str(ex)}"


    # To delete everything in Microsoft Foundry
    async def cleanup_agents(self):
        """
        Delete all created agents.
        v1.x: agents_client.delete_agent(agent_id)
        v2.x: agents_client.delete_version(agent_name=..., agent_version=...)
        """
        if not self.created_agents:
            print("No agents to clean up.")
            return

        print(f"Cleaning up {len(self.created_agents)} created agents...")
        cleanup_count = 0
        for agent_info in self.created_agents:
            try:
                self.agents_client.delete_version(
                    agent_name=agent_info["agent_name"],
                    agent_version=agent_info["agent_version"]
                )
                cleanup_count += 1
                print(f"Deleted agent: {agent_info['agent_name']} version {agent_info['agent_version']}")
            except Exception as ex:
                print(f"Failed to delete agent: {agent_info['agent_name']} version {agent_info['agent_version']}. Error: {str(ex)}")

        print(f"Cleanup completed.  {cleanup_count}/ {len(self.created_agents)} agents deleted.")
        self.created_agents.clear()

        
foundry_client = FoundryAgentClient()            