from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST

import json
from .services.memory_service import get_memory
from .services.chat_service import process_message


def chatbot_view(request):
    return render(
        request,
        "chatbot/chatbot.html"
    )


@require_POST
def chat_message(request):
    data = json.loads(request.body)

    message = data.get(
        "message",
        ""
    )

    result = process_message(
        request.user,
        message
    )

    return JsonResponse(result)

def new_chat(request):
    memory = get_memory(request.user)
    memory.clear()

    return JsonResponse({

        "status":
        "success"

    })