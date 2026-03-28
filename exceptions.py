from requests.exceptions import RequestException



class APIServerError(Exception):
    """Выбрасывается при получении ответа с кодом состояния 5xx."""

    pass


class APIRequestError(RequestException):
    """Выкидывается при получении ответа с кодом состояния 4xx."""

    pass


class BadRequestError(APIRequestError):
    """Выкидывается при получении ответа с кодом состояния 4xx."""

    pass


class UnauthorizedError(APIRequestError):
    """Выкидывается при получении ответа с кодом состояния 4xx."""

    pass


class ForbiddenError(APIRequestError):
    """Выкидывается при получении ответа с кодом состояния 4xx."""

    pass
