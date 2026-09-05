from typing import List, Any
from .client import foundry_client
from .support import FoundrySupportAgent
from .sales import FoundrySalesAgent

class FoundryCoordinatorAgent:
    """
    A coordinator agent that manages multiple Foundry Agents
    """

    def __init__(self, agents:List[Any]):
        self.agents = {}

        for agent in agents:
            if isinstance(agent, FoundrySupportAgent):
                self.agents["support"] = agent
            elif isinstance(agent, FoundrySalesAgent):
                self.agents["sales"] = agent

            self.agent_id = None
            self.agent_name = None
            # self.client = FoundryAgentClient()

            self.instructions = """
You are an intelligent customer service coordinator. Your primary role is to:
1. ANALYZE each customer query to understand their intent
2. DECIDE which specialist should handle the query
3. RESPOND with ONLY the routing decision

Available specialists:
- "support" - Handles FAQ questions (warranty, returns, shipping) and order status inquiries.
- "sales" - Handles questions about promotions, discounts, deals, and special offers.
- "general" - For any other questions that don't fit the above categories.

IMPORTANT: You must respond with EXACTLY ONE WORK - either "support", "sales", or "general".
Do not include any other text, explanation, or punctuation.  Just the single word."""

    async def initialize(self):
        """
        Initialize the coordinator agent with Azure AI Foundry services.
        """
        #agent_info = await self.client.create_agent(
        agent_info = await foundry_client.create_agent(
            name = "CoordinatorAgent",
            instructions = self.instructions
        )
        self.agent_id = agent_info["agent_id"]
        self.agent_name = agent_info["agent_name"]
        print(f"  -> Coordinator Agent initialized (ID: {self.agent_id})")


    async def _get_routing_decision(self, question:str) -> str:
        """ 
        Use AI to determine which agent should handle the query
        """
        if not self.agent_name:
            await self.initialize()

        thread_info = await foundry_client.create_thread()
        routing_prompt = f"""Analyze this customer query and decide which specialist should handle it.

        Customer query: "{question}"
        Respond with ONLY one word:  "support", "sales", or "general".
        """

        try:
            result = await foundry_client.run_agent(
                agent_name = self.agent_name,
                conversation_id = thread_info["id"],
                message=routing_prompt
            )

            # Extract text from ResponseReasoningItem
            if hasattr(result, 'content'):
                decision = result.content  # Try accessing .content attribute
            elif isinstance(result, str):
                decision = result
            else:
                decision = str(result)  # Fallback to string conversion
            
            decision = decision.strip().lower()

            if "support" in decision:
                return "support"
            elif "sales" in decision:
                return "sales"
            else:
                return "general"
        except Exception as ex:
            print(f"Error getting routing decision: {ex}")
            return "general"


    async def _handle_general_query(self, question:str) -> str:
        """
        Handle general queries that don't fit specialist agents
        """
        general_prompt = (
            f"You are a helpful general customer service assistant."
            f"A customer asked: \"{question}\"\n\n"
            f"Provide a helpful, accurate response.  If you don't have specific information, "
            f"suggest alternatives like contacting customer support or visiting the website."
        )
        try:
            response = foundry_client.openai_client.responses.create(
                model = foundry_client.model_deployment,
                input = general_prompt
            )
            return response.output_text or "I apologize, but I'm unable to assist with that question."
        except Exception as ex:
            print(f"General query error: {ex}")
            return "I apologize, but I'm currently unable to process your request."


    async def route_query(self, question:str) -> str:
        """
        Main routing method -- uses AI to decide routing, then forwards to appropriate agent.
        """

        print(f"  [Coordinator] Analyzing query...")
        routing_decision = await self._get_routing_decision(question)
        print(f"  [Coordinator] Routing decision: {routing_decision.upper()}")

        if routing_decision == "support":
            support_agent = self.agents.get("support")
            if support_agent:
                print(f"   [Coordinator] Forwarding to Support Agent...")
                response = await support_agent.handle_query(question)
                if response:
                    return f"[Routed via Coordinator -> Support Agent]\n{response}"
                print(f"  [Coordinator] Support Agent failed, falling back to general...")

        elif routing_decision == "sales":
            sales_agent = self.agents.get("sales")
            if sales_agent:
                print(f"   [Coordinator] Forwarding to Sales Agent...")
                response = await sales_agent.handle_query(question)
                if response:
                    return f"[Routed via Coordinator -> Sales Agent]\n{response}"
                print(f"  [Coordinator] Sales Agent failed, falling back to general...")

        print(f"  [Coordinator] Handling as general query...")
        response = await self._handle_general_query(question)
        return f"[Routed via Coordinator -> General Assistant]\n{response}"