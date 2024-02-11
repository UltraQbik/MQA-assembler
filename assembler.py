from asm_types import Token


class Assembler:
    def __init__(self, token_tree):
        self.token_tree: list[Token | list] = token_tree

        self.token_ptr: int = -1

    def _next_token(self, offset: int = 1) -> Token | list:
        """
        Returns next token from the token tree
        :param offset: offset for the token pointer
        :return: the next item on the token list
        """

        self.token_ptr += offset
        return self.token_tree[self.token_ptr]

    def assemble(self):
        """
        Goes through all the tokens, and assembles them
        :return: none
        """

        pass

    def _assemble(self):
        """
        Goes through all the tokens, and assembles them
        :return: none
        """

        pass
