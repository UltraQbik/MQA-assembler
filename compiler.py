from asm_types import *
from typing import Any


class Compiler(InstructionSet):
    def __init__(self):
        self.macros: dict[str, list[Macro]] = {}

    def macro_unique(self, name: Token | str, argn: int) -> bool:
        """
        :return: true if macro is unique, false if macro is not unique
        """

        if isinstance(name, Token):
            name = name.token
        if name in self.macros:
            for macro in self.macros[name]:
                if argn == macro.argn:
                    return False
        return True

    def append_macro(self, name: Token | str, args: list[Token], body: list[list[Token] | Label]) -> None:
        """
        Appends a new macro, if and only if it is a unique one
        """

        if isinstance(name, Token):
            name = name.token
        if name in self.macros:
            for macro in self.macros[name]:
                if len(args) == macro.argn:
                    macro.args = args
                    macro.body = body
                    return
        else:
            self.macros[name] = []
        self.macros[name].append(
            Macro(
                name=name,
                args=args,
                body=body
            )
        )

    def get_macro(self, name: Token | str, argn: int, copy=True) -> Macro:
        """
        Returns macro body with the given name and the amount of arguments
        :param name: macro name
        :param argn: number of arguments the macro has
        :param copy: if the macro is a copy. Default=True
        :return: macro body
        """

        if isinstance(name, Token):
            name = name.token

        if name in self.macros:
            for macro in self.macros[name]:
                if argn == macro.argn:
                    if copy:
                        return macro.__copy__()
                    else:
                        return macro

    def precompile(self, token_tree: list[Token | list]):
        """
        Precompiler method
        :param token_tree: tree of tokens
        :return: precompiled list of instructions
        """

        instruction_list: list[list[Token] | Label | Macro] = []

        # braindead coding :sunglasses:
        dummy = [-1]

        def next_token() -> Token | list | None:
            dummy[0] += 1
            if dummy[0] >= len(token_tree):
                return None
            return token_tree[dummy[0]]

        # go through tokens to define all macros first (to not cause any errors)
        while (token := next_token()) is not None:
            if isinstance(token, list):
                continue

            # macros
            if token == "macro":
                macro_name = next_token()
                if not isinstance(macro_name, Token):
                    raise SyntaxError("incorrect macro name")

                macro_args = next_token()
                if not isinstance(macro_args, list):
                    raise SyntaxError("expected an argument list")
                macro_args = [x for x in macro_args if x != ","]

                macro_body = next_token()
                if not isinstance(macro_body, list):
                    raise SyntaxError("expected a '{'")

                macro_compiler = Compiler()
                macro_body = macro_compiler.precompile(macro_body)
                self.append_macro(macro_name, macro_args, macro_body)

                for name, macro in macro_compiler.macros.items():
                    for overload_macro in macro:
                        if not self.macro_unique(name, overload_macro.argn):
                            raise Exception("cyclic macro")
                        self.append_macro(name, overload_macro.args, overload_macro.body)

        # reset the token pointer
        dummy[0] = -1

        # make macros, labels and instruction words
        while (token := next_token()) is not None:
            if isinstance(token, list):
                continue

            # skip macro definitions
            if token == "macro":
                next_token()
                next_token()
                next_token()
                continue

            # instructions
            if token.token in self.instruction_set:
                instruction_word = [token]
                while (tok := next_token()) != "\n":
                    instruction_word.append(tok)
                instruction_list.append(instruction_word)

            elif token.token in self.macros:
                macro_name = token.token
                macro_args = next_token()
                if not isinstance(macro_args, list):
                    raise SyntaxError()
                macro_args = [x for x in macro_args if x != ","]

                macro = self.get_macro(macro_name, len(macro_args))
                print(macro.put_args(*macro_args).body)

            # labels
            elif token.token[-1] == ":":
                instruction_list.append(
                    Label(token.token[:-1], token.traceback)
                )

        return instruction_list
