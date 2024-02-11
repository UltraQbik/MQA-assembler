class Token:
    def __init__(self, token: str, code_line: int):
        """
        Token class for the proper traceback.
        Acts mostly as just a string
        :param token: just a string
        :param code_line: line at which the token was defined
        """

        self._token: str = token
        self._code_line: int = code_line

    @property
    def token(self) -> str:
        return self._token

    @property
    def traceback(self) -> int:
        return self._code_line

    def __contains__(self, item):
        return item in self._token

    def __eq__(self, other):
        return self._token == other

    def __repr__(self):
        return self._token.__repr__()

    def __str__(self):
        return self._token
