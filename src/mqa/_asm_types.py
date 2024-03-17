from enum import Enum
from typing import Any, Iterable


class BType(Enum):
    """ Bracket Type """

    MISSING = 0
    ROUND = 1
    CURVED = 2
    SQUARE = 3


class Token:
    def __init__(self, value: Any, tb: int = 0):
        """
        Special kind of string
        :param value: value that the token holds
        :param tb: traceback line
        """

        self.value = value

        self._traceback = tb

    def __repr__(self):
        return self.value.__repr__()


class Instruction:
    def __init__(self, opcode: str, value: Any | None = None, memory_flag: bool = False, tb: int = 0):
        """
        An instruction word
        :param opcode: assembly mnemonic
        :param value: argument that will be used
        :param memory_flag: cache or ROM
        :param tb: traceback line
        """

        self.opcode: str = opcode
        self.value: int = value if value is not None else 0
        self.flag = memory_flag

        self._traceback = tb

    @property
    def traceback(self):
        return self._traceback

    def __repr__(self):
        if self.flag:
            return f"{self.opcode} ${self.value}"
        return f"{self.opcode} {self.value}"


class Scope:
    def __init__(self, body: Any, btype: BType):
        """
        Some kind of scope
        :param body: list of some things
        :param name: name of the scope
        """

        self.body = body
        self.btype = btype

    def __repr__(self):
        match self.btype:
            case BType.MISSING:
                return f"<{self.body.__repr__()}>"
            case BType.ROUND:
                return f"({self.body.__repr__()})"
            case BType.CURVED:
                return f"{{{self.body.__repr__()}}}"
            case BType.SQUARE:
                return f"[{self.body.__repr__()}]"

    def __iter__(self):
        return self.body.__iter__()


class TScope(Scope):
    """
    Token Scope.
    Scope that has tokens in it
    """


class IScope(Scope):
    """
    Instruction Scope.
    Scope that has instructions in it
    """

    def replace(self, old, new):
        """
        Replaces old tokens with new ones
        :param old: old
        :param new: new
        :return: self
        """

        for instruction in self.body:
            if instruction.value == old:
                instruction.value = new
        return self

