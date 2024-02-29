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

    def __len__(self):
        return len(self._token)

    def __repr__(self):
        return self._token.__repr__()

    def __str__(self):
        return self._token


class Label(Token):
    """
    Acts exactly the same way the token does,
    Just a little bit special
    """


class Macro:
    """
    Macro token, used in precompilation
    """
    def __init__(self, name: str, args: list[str | Token], body: list):
        self.name = name
        self.args = [x for x in args if x != ","]
        self.argn = len(self.args)
        self.body = body

    def __repr__(self):
        return f"{{{self.name}({self.args})}}"


class InstructionSet:
    instruction_set: dict[str, int] = {}

    # load the instructions set
    with open("mqis", "r") as file:
        # go through each line and yes
        for idx, line in enumerate(file):
            if line != "\n":
                instruction_set[line[:-1]] = idx
