from django.core.management.base import BaseCommand

from apps.chatbot.services.chroma_service import (
    similarity_search,
)

from apps.chatbot.services.llm_service import (
    ask_llm,
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        docs = similarity_search(
            "Who directed Interstellar?"
        )

        context = ""

        for i, doc in enumerate(docs, start=1):
            context += f"""

        Movie {i}
        {doc.page_content}
        ----------------------------------------
        """
        answer = ask_llm(
            "Who directed Interstellar?",
            context,
        )

        print(answer)