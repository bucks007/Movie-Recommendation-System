from django.core.management.base import BaseCommand

from apps.chatbot.services.llm_service import get_llm


class Command(BaseCommand):

    help = "Test Gemini through LangChain"

    def handle(self, *args, **kwargs):

        llm = get_llm()

        response = llm.invoke(
            "Who directed Interstellar?"
        )

        self.stdout.write(response.content) 