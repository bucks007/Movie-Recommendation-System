from django.core.management.base import BaseCommand

from apps.chatbot.services.chroma_service import (
    similarity_search,
)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        docs = similarity_search(
            "space movies with black holes"
        )

        for i, doc in enumerate(docs, start=1):

            print("=" * 50)

            print(i)

            print(doc.metadata)

            print(doc.page_content[:300])