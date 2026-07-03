from .intent_service import detect_intent
from .tool_service import execute_tool

def process_message(user,message):
    intent = detect_intent(message)
    response = execute_tool(
        intent=intent,
        user=user,
        message=message,
    )

    return response