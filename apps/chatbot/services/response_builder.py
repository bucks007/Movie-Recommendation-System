def build_response(

    response_type,

    message="",

    movies=None,

    metadata=None,

):

    return {

        "success": True,

        "type": response_type,

        "message": message,

        "movies": movies or [],

        "metadata": metadata or {},

    }