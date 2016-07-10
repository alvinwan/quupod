"""Custom errors."""


class ApplicationException(Exception):
    """An application error.

    This prompts a more user-friendly error page.
    """

    def __init__(self, message: str):
        self.message = message
