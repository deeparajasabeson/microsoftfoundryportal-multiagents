from typing import Optional
from .client import foundry_client

class BaseFoundryAgent:
    """
    Base class for Foundry agents.
    """

    def __init__(self, 
                 name: str,
                 instructions: str = None,
                 tools: list = None,):
        self.name = name
        self.agent_id = None
        self.agent_name = None
        self.instructions = instructions
        self.tools = tools or []

    async def initialize(self):
        """
        Initialize the agent with Azure AI Foundry.
        """
        agent_info = await foundry_client.create_agent(
            name=self.name,
            instructions=self.instructions,
            tools=self.tools
        )
        self.agent_id = agent_info['agent_id']
        self.agent_name = agent_info['agent_name']
        print(f" -> {self.name} initialized with ID: {self.agent_id}")

    async def handle_query(self, question:str) -> Optional [str]:
        """ 
        Handle queries using Azure AI Foundry Agent 
        """
        if not self.agent_name:
            await self.initialize()

        try:
            thread_info = await foundry_client.create_thread()
            response = await foundry_client.run_agent(
                agent_name = self.agent_name,
                conversation_id = thread_info['id'],
                message = question
            )
            return response if response and response.strip() else None
        except Exception as ex:
            print(f"{self.name} error: {ex}")
            return None
