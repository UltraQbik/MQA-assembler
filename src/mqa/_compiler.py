from copy import deepcopy

from ._asm_types import *
from ._mqis import *


class Compiler:
    def __init__(self):
        """
        The main compiler class
        """

        self.tree: TScope | None = None
        self.main_scope: IScope = IScope([], BType.MISSING)
        self.macros: dict[str, dict[int, IScope]] = {}

    def process_macros(self):
        """
        Processes macros inside of main scope
        """

        while (token := self.tree.next()) is not None:
            if isinstance(token, TScope):
                continue

            # macros
            if token.value == "macro":
                # fetch values
                self.tree.pop()
                macro_name = self.tree.pop()
                macro_args = self.tree.pop()
                macro_body = self.tree.pop()

                # checks
                # name
                if isinstance(macro_name, Token):
                    macro_name = macro_name.value
                else:
                    raise SyntaxError("Incorrect macro name")

                # arguments
                if isinstance(macro_args, TScope) and macro_args.btype is BType.ROUND:
                    macro_args = macro_args.body
                elif isinstance(macro_args, TScope):
                    raise SyntaxError("Expected a '('")
                else:
                    raise SyntaxError("Incorrect macro definition")

                # body
                if not (isinstance(macro_body, TScope) and macro_body.btype is BType.CURVED):
                    raise SyntaxError("Expected a '{'")

                # make a macro
                if macro_name not in self.macros:
                    self.macros[macro_name] = {}
                if len(macro_args) in self.macros[macro_name]:
                    print("WARN: macro redefine")

                sub_compiler = Compiler()
                sub_compiler.macros = deepcopy(self.macros)
                self.macros[macro_name][len(macro_args)] = IScope(
                    sub_compiler.compile(macro_body, False), BType.MISSING)

        # reset pointer
        self.tree.set_pointer()

    def make_labels(self):
        """
        Makes labels
        """

        while (token := self.tree.next()) is not None:
            # skip other scopes
            if isinstance(token, TScope):
                continue

            # labels
            if token.value[-1] == ":":
                self.tree[self.tree.pointer] = Label(token.value[:-1], token.traceback)

        # reset pointer
        self.tree.set_pointer()

    def compile(self, tree: TScope, main=True) -> Any:
        """
        Main compile method for token scopes
        :param tree: token tree
        :param main: is the scope - main scope
        :return: IScope
        """

        # copy imported tree into self
        self.tree = deepcopy(tree)

        # process macros
        self.process_macros()

        # make labels
        self.make_labels()

        # go through tokens, and process them
        while (token := self.tree.next()) is not None:
            # append labels and continue
            if isinstance(token, Label):
                self.main_scope.append(token)
                continue

            # skip newlines
            if token.value == "\n":
                continue

            if token.value in InstructionSet.instruction_set:
                opcode = self.tree.pop()
                value = self.tree.pop()
                self.main_scope.append(
                    Instruction(opcode.opcode, value.value, tb=token.traceback))

        return []
