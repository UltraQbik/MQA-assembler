from argparse import ArgumentParser
from copy import deepcopy
from ._asm_types import *
from ._mqis import *


class Compiler:
    KEYWORDS: set[str] = {"FOR", "ASSIGN", "LEN", "ENUMERATE"}

    def __init__(self, parser_args: ArgumentParser):
        """
        The main compiler class
        """

        self.tree: TScope | None = None
        self.main: IScope = IScope(list(), BType.MISSING)

        self.macros: dict[str, dict[int, Macro]] = {}

        self._parser = parser_args

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

    def process_for_loop(self, args: Token | TScope, range_: Token, body: TScope) -> IScope:
        """
        Processes the for loop.
        :param args: argument / arguments that will be used in a for loop
        :param range_: range that will be applied to 'args'
        :param body: body of the for loop
        :returns: instruction scope
        """

        pass

    def process_keyword(self, keyword: str):
        """
        Processes keywords.
        :param keyword: keyword that needs to be processed
        :return: value after it's processed
        """

        # assign
        if keyword == "ASSIGN":
            pass

        # for loop
        elif keyword == "FOR":
            args = self.tree.next()

            # check IN keyword
            token = self.tree.next()
            if not (isinstance(token, Token) and token.token == "IN"):
                raise SyntaxError("Incorrect for loop define")

            range_ = self.tree.next()
            if not isinstance(range_, Token):
                raise SyntaxError("Incorrect for loop range")

            body = self.tree.next()
            if not (isinstance(body, TScope) and body.btype is BType.CURVED):
                raise SyntaxError("Expected a '{'")

            for instruction in self.process_for_loop(args, range_):
                self.main.append(instruction)

        # LEN
        elif keyword == "LEN":
            pass

        # ENUMERATE
        elif keyword == "ENUMERATE":
            pass

        else:
            raise NotImplementedError(f"Keyword '{keyword}' is not yet implemented")

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

            # keyword
            elif token.token in self.KEYWORDS:
                self.process_keyword(token.token)

            else:
                raise NameError(f"Undefined instruction '{token.token}'")

        print()

        return deepcopy(self.main)
