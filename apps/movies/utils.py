import re

def clean_movie_title(title):

    # Remove year
    title = re.sub(
        r"\(\d{4}\)",
        "",
        title
    ).strip()

    if title.endswith(", The"):
        title = "The " + title[:-5]

    elif title.endswith(", A"):
        title = "A " + title[:-3]

    elif title.endswith(", An"):
        title = "An " + title[:-4]

    return title.strip()