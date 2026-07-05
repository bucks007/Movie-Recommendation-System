import os

BASE_DIR = os.path.dirname(__file__)

PROMPT_DIR = os.path.join(
    BASE_DIR,
    "..",
    "prompts",
)

PROMPT_DIR = os.path.abspath(PROMPT_DIR)


def load_prompt(filename):

    path = os.path.join(
        PROMPT_DIR,
        filename,
    )

    with open(path, encoding="utf-8") as f:
        return f.read()