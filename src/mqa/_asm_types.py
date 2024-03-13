from enum import Enum
from typing import Any
from copy import deepcopy


class AsmTypes(Enum):
    """
    Argument (class) types
    """

    INTEGER = 1
    POINTER = 2
    NAMED = 3


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

    def __repr__(self):
        return f"${self.token}"


class LabelPointer:
    """
    Points to index of a label.
    """

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f"{self.value}"


class Macro:
    def __init__(self, name: str, args: list[Token], body: list):
        """
        Macro token, used in precompilation
        :param name: name of the macro
        :param args: arguments of the macro
        :param body: instructions composing the macro
        """

        self.name: str = name
        self.args: list[Token] = [x for x in args if x != ","]
        self.argn: int = len(self.args)
        self.body: list[list[Token] | Label | Macro] = body

    def put_args(self, *args: Token):
        """
        Puts the arguments in the corresponding places
        :param args: arguments to the macro
        :raises TypeError: when the amount of arguments does not match
        """

        if len(args) != self.argn:
            raise TypeError()

        for instruction in self.body:
            if isinstance(instruction, (Label, Macro)):
                continue
            for token_idx, tok in enumerate(instruction):
                # the first token must be an instruction word
                if token_idx == 0:
                    continue
                for arg_idx, arg in enumerate(self.args):
                    if tok == arg:
                        instruction[token_idx] = args[arg_idx]
        self.args = args

    def __copy__(self):
        return Macro(self.name, deepcopy(self.args), deepcopy(self.body))

    def __repr__(self):
        return f"{{{self.name}({self.args})}}"


class ForLoop:
    def __init__(self, var: str, range_: str, body: list[list[Token] | Label | Macro]):
        """
        A for loop class
        :param var: variable of a for loop
        :param range_: range of a for loop
        :param body: body of the for loop
        :raises SyntaxError: when the syntax is incorrect
        """

        self.var: str = var
        self.body: list[list[Token] | Label | Macro] = body

        # string range
        if range_[0] == range_[-1] in "\"\'":
            self.range = [ord(x) for x in range_[1:-1]]

        # integer range
        elif range_.find("..") > -1:
            split_range = range_.split("..")
            try:
                range_start = int(split_range[0], base=0)
                range_end = int(split_range[1], base=0)
                if range_end > range_start:
                    self.range = range(range_start, range_end)
                else:
                    # we assume the user wants the same sequence just in reverse
                    self.range = range(range_start - 1, range_end - 1, -1)
            except ValueError:
                raise SyntaxError("Incorrect syntax for a for loop range, or incorrect integer specified")

        # error
        else:
            raise SyntaxError("Unrecognized syntax for a for loop range")

    def put_args(self, arg: Token):
        """
        Replaces 'self.var' inside tokens with arg.
        :param arg: argument that needs to be put
        :return: new body of the for loop, with variable replaced
        """

        # go through instructions and the instruction's tokens, and process them
        # make sure it's a copy of the body, to not modify the original
        new_body = deepcopy(self.body)
        for instruction in new_body:
            # skip labels and macros
            if isinstance(instruction, (Label, Macro)):
                continue

            # go through instruction's tokens
            for token_idx, token in enumerate(instruction):
                # if token is the same as the variable, replace it with arg
                if token.token == self.var:
                    instruction[token_idx] = arg
        return new_body


class Argument:
    def __init__(self, value: Any, type_: AsmTypes):
        """
        Contains a value (anything), and type
        :param value: argument value
        :param type_: argument type
        """

        self.value = value
        self.type = type_

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.value == other.value and self.type is other.type:
            return True

    def __repr__(self):
        if self.type is AsmTypes.INTEGER:
            return f"{self.value}"
        elif self.type is AsmTypes.POINTER:
            return f"${self.value}"
        elif self.type is AsmTypes.NAMED:
            return f"${self.value}"
