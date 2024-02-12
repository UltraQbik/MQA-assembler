from asm_types import Token


class Assembler:
    def __init__(self, token_tree):
        self._token_tree: list[Token | list] = token_tree

        # pointer to the current token
        self._token_ptr: int = -1

        # instructions
        self._instructions: list[list[Token]] | None = None

        # macros
        self._macros: dict[str, list[dict]] | None = None

        # jump / call labels
        self._labels: dict[str, int] | None = None

        # instruction set
        self._instruction_set: dict[str, int] | None = None
        self._load_instruction_set()

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

    def assemble(self):
        """
        Goes through all the tokens, and assembles them
        :return: none
        """

        try:
            self._assemble()
        except Exception as exc:
            print(f"An exception have occurred;\n\t{exc}\nline: {self._next_token(0).traceback}")

    def _assemble(self):
        """
        Goes through all the tokens, and assembles them
        :return: none
        """

        # reset things
        self._instructions: list[list[Token]] = []
        self._macros: dict[str, list[dict]] = {}
        self._labels: dict[str, int] = {}

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
                    raise SyntaxError("Invalid syntax")

                # next token should be an argument list
                macro_args = self._next_token()

                # if it's not of type list => raise an error
                if not isinstance(macro_args, list):
                    raise SyntaxError("Invalid syntax")

                # delete the commas
                macro_args = [x for x in macro_args if x != ","]

                # next token should be the body of the macro
                macro_body = self._next_token()

                # if it's not of type list => raise an error
                if not isinstance(macro_body, list):
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
