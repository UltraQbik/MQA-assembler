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

    def __repr__(self):
        return f"@{self.token}"


class Instruction:
    def __init__(self, opcode: str | Token, value: Any | None = None, memory_flag: bool = False, tb: int = 0):
        """
        An instruction word
        :param opcode: assembly mnemonic
        :param value: argument that will be used
        :param memory_flag: cache or ROM
        :param tb: traceback line
        """

        self.opcode: str = opcode if not isinstance(opcode, Token) else opcode.token
        self.flag = memory_flag

        if isinstance(value, Token) and not isinstance(value, Label):
            self.value = value.token
        elif value is None:
            self.value = 0
        else:
            self.value = value

        self._traceback = tb

    @property
    def traceback(self):
        return self._traceback

    def __repr__(self):
        if self.flag:
            return f"{self.opcode} ${self.value}"
        return f"{self.opcode} {self.value}"


class Pointer:
    def __init__(self, value: int):
        """
        Pointer class
        """

        self.value = value

    def __repr__(self):
        return f"*{self.value}"


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

    def pop(self, index=None) -> Any:
        """
        Pops next item on the list
        :return: next item on the list
        """

        if index is None:
            return self.body.pop(self.pointer)
        return self.body.pop(index)

    def append(self, item) -> None:
        """
        Appends item to body
        """

        self.body.append(item)

    def insert(self, index: int, item: Any) -> None:
        """
        Appends item to body
        """

        self.body.insert(index, item)

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
            # skip labels
            if isinstance(instruction, Label):
                continue

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
