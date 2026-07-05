from .intent_service import detect_intent
from .orchestrator import orchestrate


def process_message(user, message):

    intent = detect_intent(message)

    return orchestrate(
        user=user,
        intent=intent,
        message=message,
    )