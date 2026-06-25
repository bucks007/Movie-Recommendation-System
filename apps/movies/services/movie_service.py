import re

def format_movie_title(title):

    patterns = [
        (r", The \((\d{4})\)$", r" (\\1)"),
        (r", A \((\d{4})\)$", r" (\\1)"),
        (r", An \((\d{4})\)$", r" (\\1)")
    ]

    if ", The (" in title:
        title = re.sub(
            r"^(.*), The \((\d{4})\)$",
            r"The \1 (\2)",
            title
        )

    elif ", A (" in title:
        title = re.sub(
            r"^(.*), A \((\d{4})\)$",
            r"A \1 (\2)",
            title
        )

    elif ", An (" in title:
        title = re.sub(
            r"^(.*), An \((\d{4})\)$",
            r"An \1 (\2)",
            title
        )

    return title