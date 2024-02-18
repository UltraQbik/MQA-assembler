from asm_types import Token, Label, InstructionSet
from typing import Any


class Compiler(InstructionSet):
    def __init__(self):
        self.macros: dict[str, list[dict[str, Any]]] = {}

    def macro_unique(self, name: Token | str, argn: int):
        """
        :return: true if macro is unique, false if macro is not unique
        """

        if isinstance(name, Token):
            name = name.token
        if name in self.macros:
            for macro in self.macros[name]:
                if argn == macro["argn"]:
                    return False
        return True

    def append_macro(self, name: Token | str, args: list[Token], body: list[list[Token] | Label]):
        """
        Appends a new macro, if and only if it is a unique one
        """

        if isinstance(name, Token):
            name = name.token
        if name in self.macros:
            for macro in self.macros[name]:
                if len(args) == macro["argn"]:
                    macro["args"] = args
                    macro["body"] = body
                    return
        else:
            self.macros[name] = []
        self.macros[name].append({
                "argn": len(args),
                "args": args,
                "body": body
            }
        )

    def precompile(self, token_tree: list[Token | list]):
        """
        Precompiler method
        :param token_tree: tree of tokens
        :return: precompiled list of instructions
        """

        instruction_list: list[list[Token] | Label] = []

        # braindead coding :sunglasses:
        dummy = [-1]

        def next_token() -> Token | list | None:
            dummy[0] += 1
            if dummy[0] >= len(token_tree):
                return None
            return token_tree[dummy[0]]

        # make macros, labels and instruction words
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
                        if not self.macro_unique(name, overload_macro["argn"]):
                            raise Exception("cyclic macro")
                        self.append_macro(name, overload_macro["args"], overload_macro["body"])

            # instructions
            elif token.token in self.instruction_set:
                instruction_word = [token]
                while (tok := next_token()) != "\n":
                    instruction_word.append(tok)
                instruction_list.append(instruction_word)

            # labels
            elif token.token[-1] == ":":
                instruction_list.append(
                    Label(token.token[:-1], token.traceback)
                )

        return instruction_list
