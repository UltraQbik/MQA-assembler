from asm_types import Token, Label, InstructionSet


class Assembler:
    def __init__(self, token_tree):
        self._token_tree: list[Token | list] = token_tree

        # pointer to the current token
        self._token_ptr: int = -1

        # pointer to the current instruction
        self._instruction_ptr: int = -1

        # jump / call labels
        self._labels: dict[str, int] | None = None

        # exceptions traceback
        self._traceback: int = 0

    # def _compile_and_link(self):
    #     """
    #     Function that compiles and links things together ~~forever~~
    #     :return: none
    #     """
    #
    #     # clear labels
    #     self._labels: dict[str, int] = {}
    #
    #     self._reset_instruction_pointer()
    #     while (instruction := self._next_instruction()) is not None:
    #         # skip labels for now
    #         if isinstance(instruction, Label):
    #             continue
    #
    #         # macros
    #         if instruction[0] in self._macros:
    #             macro_name = instruction[0]
    #             macro_argn = len(instruction[1])
    #
    #             # search for the macro with the same amount of arguments
    #             macro_body = None
    #             for macro in self._macros[macro_name.token]:
    #                 if macro["argn"] == macro_argn:
    #                     macro_body = macro["body"]
    #                     break
    #
    #             # if that macro wasn't found => raise an error
    #             if macro_body is None:
    #                 self._traceback = macro_name.traceback
    #                 raise TypeError(f"Incorrect amount of arguments for macro '{macro_name}'")
    #
    #     # # Labels
    #     # self._reset_instruction_pointer()
    #     # while (instruction := self._next_instruction()) is not None:
    #     #     if isinstance(instruction, Label):
    #     #         self._labels[instruction.token] = self._instruction_ptr


class Precompiler(InstructionSet):
    def __init__(self, token_tree: list[Token | list]):
        # token tree
        self._token_tree: list[Token | list] = token_tree

        # token pointer
        self._token_ptr: int = -1

        # macros and instruction list
        self._macros: dict[str, list[dict]] | None = None
        self._instructions: list[list[Token] | Label] | None = None

        # traceback
        self._traceback: int = 0

    @property
    def macros(self) -> dict[str, list[dict]]:
        return self._macros

    @property
    def instructions(self) -> list[list[Token] | Label]:
        return self._instructions

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

    def _precompile_ex(self):
        """
        Precompiles the token tree
        :return: none
        """

        try:
            self._precompile()
        except Exception as exc:
            print(f"An exception have occurred;\n\t{exc} at line: {self._traceback}")

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
                if macro_name in self.instruction_set:
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

                # append new macro
                if macro_name.token not in self._macros:
                    self._macros[macro_name.token] = []
                self._macros[macro_name.token].append(
                    {
                        "argn": len(macro_args),
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
