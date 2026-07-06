from pathlib import Path


PROMPT_DIR = (
    Path(__file__)
    .parent.parent
    / "prompt"
)


def load_prompt(filename):

    with open(
        PROMPT_DIR / filename,
        encoding="utf-8",
    ) as f:

        return f.read()


SYSTEM_PROMPT = load_prompt(
    "system_prompt.txt"
)

MOVIE_PROMPT = load_prompt(
    "movie_prompt.txt"
)


def build_prompt(
    question,
    context,
):

    return f"""
{SYSTEM_PROMPT}

{MOVIE_PROMPT}

========================

Context

{context}

========================

Question

{question}

Answer:
"""