from copy import deepcopy
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

        self.token = value

        self._traceback = tb

    @property
    def traceback(self):
        return self._traceback

    def __eq__(self, other):
        if isinstance(other, Token):
            return self.token == other.token
        elif isinstance(other, str):
            return self.token == other
        return False

    def __repr__(self):
        return self.token.__repr__()


class Label(Token):
    """
    Special kind of token
    """


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
    def __init__(self, body: list, btype: BType):
        """
        Some kind of scope
        :param body: list of some things
        :param btype: bracket type
        """

        self.body: list = body
        self.btype: BType = btype

        self.pointer: int = -1

    def next(self) -> Any:
        """
        :return: next item in the scope or None if the scope has ended
        """

        self.pointer += 1
        if self.pointer >= self.body.__len__():
            return None
        return self.body[self.pointer]

    def pop(self) -> Any:
        """
        Pops next item on the list
        :return: next item on the list
        """

        return self.body.pop(self.pointer)

    def append(self, item) -> None:
        """
        Appends item to body
        """

        self.body.append(item)

    def set_ptr(self, val: int = -1):
        """
        Sets the pointer to some token
        :param val: integer
        """

        self.pointer = val

    def unify(self, other):
        if isinstance(other, Scope):
            self.body += other.body
        else:
            raise TypeError("No.")

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

    def __len__(self):
        return self.body.__len__()

    def __iter__(self):
        return self.body.__iter__()

    def __getitem__(self, item):
        if isinstance(item, int):
            return self.body[item]
        raise TypeError

    def __setitem__(self, key, value):
        if isinstance(key, int):
            self.body[key] = value
        else:
            raise TypeError

    def __copy__(self):
        return self.__class__(deepcopy(self.body), self.btype)


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


class Macro(IScope):
    """
    A macro scope
    """

    def __init__(self, body: list, btype: BType, args: TScope):
        super().__init__(body, btype)

        self.args: TScope = args