from ._asm_types import *
from ._mqis import *


class Compiler:
    def __init__(self):
        """
        The main compiler class
        """

        self.main_scope: IScope = IScope([], BType.MISSING)
        self.main_scope_macros = {}

    def compile(self, tree: TScope, main=True):
        """
        Main compile method for token scopes
        :param tree: token tree
        :param main: is the scope - main scope
        :return: IScope
        """

        pass
