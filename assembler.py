from asm_types import Token


class Assembler:
    def __init__(self, token_tree):
        self._token_tree: list[Token | list] = token_tree

        # pointer to the current token
        self._token_ptr: int = -1

        # macros
        self.macros: dict[str, list[dict]] | None = None

    def _reset_token_pointer(self):
        """
        Resets the token pointer to -1
        :return:
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

        # reset the macros
        self.macros: dict[str, list[dict]] = {}

        self._reset_token_pointer()
        while (token := self._next_token()) is not None:
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
                if macro_name.token not in self.macros:
                    self.macros[macro_name.token] = []
                self.macros[macro_name.token].append(
                    {
                        "argn": len(macro_args),
                        "args": macro_args,
                        "body": macro_body
                    }
                )
