from copy import deepcopy
from ._asm_types import *
from ._mqis import *


class Compiler:
    KEYWORDS: set[str] = {"FOR", "ASSIGN", "LEN", "ENUMERATE"}

    def __init__(self):
        """
        The main compiler class
        """

        self.tree: TScope | None = None
        self.main: IScope = IScope(list(), BType.MISSING)

        self.macros: dict[str, dict[int, Macro]] = {}

    def process_macros_and_labels(self):
        """
        Processes scope macros
        """

        self.tree.set_ptr()
        while (token := self.tree.next()) is not None:
            # skip sub-scopes
            if isinstance(token, TScope):
                continue

            # macros
            if token.token == "macro":
                # fetch values
                self.tree.pop()
                macro_name = self.tree.pop()
                macro_args = self.tree.pop()
                macro_body = self.tree.pop()

                # perform checks
                # name check
                if isinstance(macro_name, Token):
                    macro_name = macro_name.token
                else:
                    raise SyntaxError("Incorrect macro definition")

                # arguments check
                if not isinstance(macro_args, TScope) or macro_args.btype is not BType.ROUND:
                    raise SyntaxError("Excepted a '('")

                # body check
                if not isinstance(macro_body, TScope) or macro_body.btype is not BType.CURVED:
                    raise SyntaxError("Expected a '{'")

                # adding a macro
                if macro_name not in self.macros:
                    self.macros[macro_name] = {}
                if len(macro_args) in self.macros[macro_name]:
                    print("WARN: macro redefinition")

                sub_compiler = Compiler()
                sub_compiler.macros = deepcopy(self.macros)
                self.macros[macro_name][len(macro_args)] = Macro(
                    sub_compiler.compile(macro_body, False),
                    BType.MISSING,
                    macro_args
                )

            # labels
            elif token.token[-1] == ":":
                self.tree[self.tree.pointer] = Label(token.token[:-1], token.traceback)

    def compile(self, tree: TScope, is_main=True) -> Any:
        """
        Main compile method for token scopes
        :param tree: token tree
        :param is_main: is the scope - main scope
        :return: IScope
        """

        # set input tree
        self.tree = deepcopy(tree)

        # process macros and labels
        self.process_macros_and_labels()

        print(self.tree)

        self.tree.set_ptr()
        while (token := self.tree.next()) is not None:
            # append labels and continue
            if isinstance(token, Label):
                self.main.append(token)
                continue

            # skip newlines
            if token.token == "\n":
                continue

            # mnemonics
            if token.token in InstructionSet.instruction_set:
                instruction_word = [token]
                while (itoken := self.tree.next()).token != "\n":
                    instruction_word.append(itoken)
                self.main.append(Instruction(
                    instruction_word[0],
                    instruction_word[1] if len(instruction_word) > 1 else Token('0', token.traceback)
                ))

            # macros
            elif token.token in self.macros:
                # fetch data
                macro_name: Token = self.tree.pop()
                macro_args = self.tree.pop()

                # checks
                if not isinstance(macro_args, TScope) and macro_args.btype is not BType.ROUND:
                    raise SyntaxError("Expected a '('")

                if len(macro_args) not in self.macros[macro_name.token]:
                    raise NameError(f"Undefined macro {macro_name}")

                macro = deepcopy(self.macros[macro_name.token][len(macro_args)])
                for idx, arg in enumerate(macro.args):
                    macro.replace(arg, macro_args[idx])
                self.main.body += macro.body

        print()

        return deepcopy(self.main)
