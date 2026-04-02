class APIDataError(Exception):
    """Для ошибок, найденных в теле ответа API (ключи code/error)."""


class APIHttpError(Exception):
    """Выбрасывается при получении ответа с кодом состояния 4xx."""
