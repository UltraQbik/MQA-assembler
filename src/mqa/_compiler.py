from ._asm_types import *
from ._mqis import *


class Compiler:
    def __init__(self):
        """
        The main compiler class
        """

        self.main_scope_macros = {}
