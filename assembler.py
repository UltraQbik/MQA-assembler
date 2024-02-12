from asm_types import Token, Label


class Assembler:
    def __init__(self, token_tree):
        self._token_tree: list[Token | list] = token_tree

        # pointer to the current token
        self._token_ptr: int = -1

        # pointer to the current instruction
        self._instruction_ptr: int = -1

        # instructions
        self._instructions: list[list[Token] | Label] | None = None

        # macros
        self._macros: dict[str, list[dict]] | None = None

        # jump / call labels
        self._labels: dict[str, int] | None = None

        # instruction set
        self._instruction_set: dict[str, int] | None = None
        self._load_instruction_set()

        # exceptions traceback
        self._traceback: int = 0

    def _load_instruction_set(self):
        """
        Loads the MQ instruction set (MQIS)
        :return: none
        """

        # initiate instruction set to be an empty dict
        self._instruction_set = {}

        # read Mini Quantum's instruction set
        with open("mqis", "r") as file:
            # go through each line and yes
            for idx, line in enumerate(file):
                if line != "\n":
                    self._instruction_set[line[:-1]] = idx

    def _reset_token_pointer(self):
        """
        Resets the token pointer to -1
        :return: none
        """
        self._token_ptr = -1

    def _next_token(self, offset: int = 1) -> Token | list | None:
        """
        Returns next token from the token tree
        :param offset: offset for the token pointer
        :return: the next item on the token list or None when the end of the tree is reached
        """

        self._token_ptr += offset
        if self._token_ptr >= len(self._token_tree):
            return None
        return self._token_tree[self._token_ptr]

    def _reset_instruction_pointer(self):
        """
        Resets the instruction pointer to -1
        :return: none
        """

        self._instruction_ptr = -1

    def _next_instruction(self, offset: int = 1) -> list[Token] | Label | None:
        """
        Returns next instruction from self._instructions
        :param offset: offset for the instruction pointer
        :return: the next item in the self._instructions or None when the end of the list is reached
        """

        self._instruction_ptr += offset
        if self._instruction_ptr >= len(self._instructions):
            return None
        return self._instructions[self._instruction_ptr]

    def assemble(self):
        """
        Goes through all the tokens, and assembles them
        :return: none
        """

        try:
            self._precompile()
            self._compile_and_link()
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

        self._reset_token_pointer()
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
                if macro_name in self._instruction_set:
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
            elif token.token in self._instruction_set or token.token in self._macros:
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

    def _compile_and_link(self):
        """
        Function that compiles and links things together ~~forever~~
        :return: none
        """

        # clear labels
        self._labels: dict[str, int] = {}

        self._reset_instruction_pointer()
        while (instruction := self._next_instruction()) is not None:
            # skip labels for now
            if isinstance(instruction, Label):
                continue

            # macros
            if instruction[0] in self._macros:
                macro_name = instruction[0]
                macro_argn = len(instruction[1])

                # search for the macro with the same amount of arguments
                macro_body = None
                for macro in self._macros[macro_name.token]:
                    if macro["argn"] == macro_argn:
                        macro_body = macro["body"]
                        break

                # if that macro wasn't found => raise an error
                if macro_body is None:
                    self._traceback = macro_name.traceback
                    raise TypeError(f"Incorrect amount of arguments for macro '{macro_name}'")

        # # Labels
        # self._reset_instruction_pointer()
        # while (instruction := self._next_instruction()) is not None:
        #     if isinstance(instruction, Label):
        #         self._labels[instruction.token] = self._instruction_ptr
