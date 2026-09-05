from azure.ai.projects.models import FunctionTool

## Tools to use in specific agent.

FAQ_TOOL = FunctionTool(
    name="lookup_faq_tool",
    description="Tool to look up frequently asked questions about warranty, returns, and shipping.",
    parameters={
        "type": "object",
        "properties": {
            "topic": {
                "type": "string",
                "enum": ["warranty", "returns", "shipping"],
                "description": "The FAQ topic to look up.",
            }
        },
        "required": ["topic"],
        "additionalProperties": False   # required when strict=True
    },
    strict=True
)


ORDER_STATUS_TOOL = FunctionTool(
    name="check_order_status_tool",
    description="Tool to check the status of a customer order.",
    parameters={
        "type": "object",
        "properties": {
            "order_id": {
                "type": "string",
                "description": "The order ID to check.",
            }
        },
        "required": ["order_id"],
        "additionalProperties": False   # required when strict=True
    },
    strict=True
)


PROMOTIONS_TOOL= FunctionTool(
    name="get_current_promotions_tool",
    description="Get information about current sales and promotions.",
    parameters={
        "type": "object",
        "properties": {
            "category": {
                "type": "string",
                "description": "Product category to check for promotions (optional).",
                "enum": ["electronics", "clothing", "home", "beauty", "sports", "all"],
            }
        },
    },
    # string not set -- category is optiona, strict mode requires all params in "required"
)
