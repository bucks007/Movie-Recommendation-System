from enum import Enum
import re


class Intent(Enum):
    RECOMMEND = "recommend"
    SIMILAR = "similar"
    PERSONALIZED = "personalized"
    GENRE = "genre"
    TRENDING = "trending"
    TOP_RATED = "top_rated"
    LATEST = "latest"
    ACTOR = "actor"
    DIRECTOR_MOVIES = "director_movies"
    YEAR = "year"

    MOVIE_INFO = "movie_info"
    SEARCH = "search"
    GREETING = "greeting"
    HELP = "help"
    UNKNOWN = "unknown"

def detect_intent(message):
    message = message.lower().strip()

    # Greeting

    if re.search(
        r"\b(hi|hello|hey|good morning|good evening)\b",
        message
    ):
        return Intent.GREETING

    # Help

    if re.search(
        r"\b(help|what can you do)\b",
        message
    ):
        return Intent.HELP

    # Personalized

    if re.search(
        r"\b(for me|recommend me|my recommendations|personalized)\b",
        message
    ):
        return Intent.PERSONALIZED

    # TRENDING

    if re.search(
        r"\b(trending|popular|viral)\b",
        message
    ):
        return Intent.TRENDING
    
    # Top Rated

    if re.search(
        r"\b(top rated|highest rated|best imdb|top imdb)\b",
        message
    ):
        return Intent.TOP_RATED
    
    # Latest

    if re.search(
        r"\b(latest|new|recent)\b",
        message
    ):
        return Intent.LATEST
    
    # Actor

    if re.search(
        r"\b(starring|actor|actors|with)\b",
        message
    ):
        return Intent.ACTOR
    
    # Director Movies

    if re.search(
        r"\b(directed by|movies by)\b",
        message
    ):
        return Intent.DIRECTOR_MOVIES
    
    # Year

    if re.search(
        r"\b(19\d{2}|20\d{2})\b",
        message
    ):
        return Intent.YEAR

    # Similar movie

    if re.search(
        r"\b(similar|like)\b",
        message
    ):
        return Intent.SIMILAR

    # Recommendation

    if re.search(
        r"\b(recommend|recommendation|suggest|best|top|must watch|good movies|worth watching)\b",
        message
    ):
        return Intent.RECOMMEND
    
    # GENRE

    if re.search(
        r"\b(action|comedy|romance|drama|thriller|crime|horror|animation|family|adventure|fantasy|sci-fi|science fiction)\b",
        message
    ):
        return Intent.GENRE

    # Movie information

    if re.search(
        r"\b(plot|story|director|directed|actor|actors|cast|runtime|release|released|rating|imdb)\b",
        message
    ):
        return Intent.MOVIE_INFO
    
    # Search

    if re.search(
        r"\b(find|search|show)\b",
        message
    ):
        return Intent.SEARCH

    return Intent.UNKNOWN
