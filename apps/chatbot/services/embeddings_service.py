import os

from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings

load_dotenv()


def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-mpnet-base-v2"
    )