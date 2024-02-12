from asm_types import Token, Label, InstructionSet


class Compiler(InstructionSet):
    def __init__(self, token_tree: list[Token | list], **kwargs):
        # token tree
        self._token_tree: list[Token | list] = token_tree

        # token pointer
        self._token_ptr: int = -1

        # macros and instruction list
        self._macros: dict[str, list[dict]] | None = None
        self._instructions: list[list[Token] | Label] | None = None

        # traceback
        self._traceback: int = 0

        # set the kwargs
        setattr(self, "_macros", kwargs.get("macros"))
        setattr(self, "_instructions", kwargs.get("instructions"))

        # precompile the given token tree
        self._precompile()

    @property
    def traceback(self) -> int:
        return self._traceback

    def _next_token(self) -> Token | list | None:
        """
        Returns the next token from the token tree or None if the end of the token tree is reached
        :return: next token from the token tree
        """

        self._token_ptr += 1
        if self._token_ptr >= len(self._token_tree):
            return None
        return self._token_tree[self._token_ptr]

    @staticmethod
    def _generate_macro_name(macro: Token, argn: int):
        return f"{macro.token}_{argn}"

    def _precompile(self):
        """
        Goes through all the tokens, and assembles them.
        Creates macros, puts all the instructions, labels and macros into self._instructions
        :return: none
        """

        # reset things
        self._instructions: list[list[Token] | Label] = []
        self._macros: dict[str, list[dict]] = {}

        while (token := self._next_token()) is not None:
            # skip token lists
            if isinstance(token, list):
                continue

            # macro keyword
            if token == "macro":
                # next token should be a name of the macro
                macro_name = self._next_token()

                # if it's not of type Token => raise an error
                if not isinstance(macro_name, Token):
                    self._traceback = token.traceback
                    raise SyntaxError("Invalid syntax")

                # warning when macro name is the same as the name of one of the instructions
                if macro_name.token in self.instruction_set:
                    print(f"warn: macro '{macro_name}' has the same name as one of the instruction")

                # next token should be an argument list
                macro_args = self._next_token()

                # if it's not of type list => raise an error
                if not isinstance(macro_args, list):
                    self._traceback = token.traceback
                    raise SyntaxError("Invalid syntax")

                # delete the commas
                macro_args = [x for x in macro_args if x != ","]

                # next token should be the body of the macro
                macro_body = self._next_token()

                # if it's not of type list => raise an error
                if not isinstance(macro_body, list):
                    self._traceback = token.traceback
                    raise SyntaxError("Invalid syntax")

                # precompile the macro body
                macro_precompiler = Compiler(
                    token_tree=macro_body,
                    macros=self._macros,
                    instructions=self._instructions
                )
                macro_body = macro_precompiler._instructions

                # generate macro name
                macro_name = self._generate_macro_name(macro_name, len(macro_args))

                # append new macro
                if macro_name not in self._macros:
                    self._macros[macro_name] = []
                self._macros[macro_name].append(
                    {
                        "args": macro_args,
                        "body": macro_body
                    }
                )

            # instructions and macros
            elif token.token in self.instruction_set or token.token in self._macros:
                # empty instruction list
                instruction = list()

                # append instruction name to instruction list
                instruction.append(token)

                # append tokens to the instruction list while the token is not equal to newline
                while (tok := self._next_token()) != "\n":
                    instruction.append(tok)

                self._instructions.append(instruction)

            # labels
            elif token.token[-1] == ":":
                self._instructions.append(Label(token.token[:-1], token.traceback))
