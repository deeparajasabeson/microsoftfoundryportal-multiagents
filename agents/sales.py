from .base import BaseFoundryAgent
from .tools import PROMOTIONS_TOOL

class FoundrySalesAgent(BaseFoundryAgent):
    """
    FoundrySalesAgent that can provide information about promotions.
    """

    def __init__(self, name: str = "SalesAgent"):
        instructions = """
        You are a sales specialist focused on promotions and discounts.
        Help customers find the best deals and understand our current offers.
        Use the available tools to provide accurate promotion information.
        Be enthusistic and helpful while staing accurate about what's available.        
        """
        super().__init__(name, instructions, [PROMOTIONS_TOOL])
