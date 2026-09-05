from .base import BaseFoundryAgent
from .tools import FAQ_TOOL, ORDER_STATUS_TOOL

class FoundrySupportAgent(BaseFoundryAgent):
    """
    SupportAgent that can answer FAQs and check order status.
    """

    def __init__(self, name: str = "SupportAgent"):
        instructions = """
        You are a customer support specialist. 
        Your role is to help customers with:
        1. General FAQ questions (warranty, returns, shipping)
        2. Order status inquiries

        Use the available tools to provide accurate information.  
        Be helpful, professional, and empathetic.
        If you can not help with something, politely explain your limitations and suggest contacting general support.
        """
        super().__init__(
            name=name,
            instructions=instructions,
            tools=[FAQ_TOOL, ORDER_STATUS_TOOL]
        )
