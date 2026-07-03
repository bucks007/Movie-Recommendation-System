from django.core.management.base import BaseCommand

from apps.chatbot.services.embeddings_service import get_embeddings


class Command(BaseCommand):

    help = "Test Google Embeddings"

    def handle(self, *args, **kwargs):

        embeddings = get_embeddings()

        vector = embeddings.embed_query(
            "Interstellar is a science fiction movie."
        )

        self.stdout.write(
            f"Embedding dimension: {len(vector)}"
        )

        self.stdout.write(
            str(vector[:10])
        )