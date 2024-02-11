from typing import Any


class Token:
    def __init__(self, token: str, code_line: int):
        """
        Token class for the proper traceback.
        Acts mostly as just a string
        :param token: just a string
        :param code_line: line at which the token was defined
        """

        self.token: str = token
        self.code_line: int = code_line

    def __contains__(self, item):
        return item in self.token

    def __eq__(self, other):
        return self.token == other

    def __repr__(self):
        return self.token.__repr__()

    def __str__(self):
        return self.token


class Tokenizer:
    def __init__(self):
        """
        The main tokenizer class.
        It spits the code into tokens
        """

        self.code: str | None = None
        self.token_tree: list[Token | Any] | None = None

    def tokenize(self, code: str):
        """
        Spaghetti code that assembles the code!
        I know it's stupid, but I don't know how to make it better
        :param code: Mini Quantum Assembly code
        :return: none
        """

        self.code = code

        # separate the code into tokens
        self._separate_tokens()

        # delete comments
        self._delete_comments()

        # delete duplicate newlines
        self._remove_newlines()

        # create a token tree
        self.token_tree = self._build_token_tree(self.token_tree)

    def _separate_tokens(self):
        """
        Separates the tokens
        :return: none
        """

        # create token string
        token = ""

        # initialize token list
        self.token_tree = []

        # initialize character pointer to 0
        char_ptr = 0
        code_line = 1
        while char_ptr < len(self.code):
            # get next character
            char = self.code[char_ptr]
            char_ptr += 1

            # code line
            if char == "\n":
                code_line += 1

            # spaces between things
            if char == " " and token != "":
                self.token_tree.append(Token(token, code_line))
                token = ""

            # new lines
            elif char in "\n," and token != "":
                self.token_tree.append(Token(token, code_line))
                self.token_tree.append(Token(char, code_line))
                token = ""

            # brackets
            elif char in "({[]})":
                if token != "":
                    self.token_tree.append(Token(token, code_line))
                    token = ""
                self.token_tree.append(Token(char, code_line))

            # anything else
            elif char != " " and char != "\n":
                token += char

        # if there is still a token at the end of the file
        if token:
            self.token_tree.append(Token(token, code_line))
            self.token_tree.append(Token("\n", code_line))

    def _delete_comments(self):
        """
        Removes the comments to not clutter the token list
        :return: none
        """

        # create new token list
        new_token_list = []
        commented = False
        for token in self.token_tree:
            # deletus everything after the ';'
            if token == ";":
                commented = True
                continue

            # if the newline is found, it's not a comment anymore
            elif token == "\n":
                commented = False

            # if the thing is not commented, then put it on the new token list
            if not commented:
                new_token_list.append(token)

        # yes
        self.token_tree = new_token_list

    def _build_token_tree(self, token_list: list):
        """
        Builds the token tree
        :param token_list: yes
        :return: none
        """

        # the token tree
        tree = []

        # current token index
        index = 0
        while index < len(token_list):
            # fetch current token
            token = token_list[index]
            index += 1

            # when we find an opening bracket, create a new scope
            if str(token) in "({[":
                scope = []
                nesting = 0
                prev_index = token_list[index].code_line
                while index < len(token_list):
                    # fetch inner scope token
                    token = token_list[index]
                    index += 1

                    # if another opening bracket of same type is found => increment the nesting variable
                    # break out of the loop only when the nesting is 0 and the closing bracket is found
                    if str(token) in "]})" and nesting == 0:
                        tree.append(self._build_token_tree(scope))
                        break
                    elif str(token) in "]})":
                        nesting -= 1
                    elif str(token) in "({[":
                        nesting += 1

                    # append tokens to the local scope
                    scope.append(token)

                # if the end of the code was reached => die.
                else:
                    raise SyntaxError(f"No closing bracket was found; line {prev_index}")
            else:
                # append tokens to the global scope
                tree.append(token)
        # return the token tree (or a local scope)
        return tree

    def _remove_newlines(self):
        """
        Removes duplicate newlines
        :return: none
        """

        # set index to 0
        index = 0
        while index < len(self.token_tree)-1:
            # if there are 2 newlines in a row, delete the first one
            if self.token_tree[index] == "\n" and self.token_tree[index + 1] == "\n":
                self.token_tree.pop(index)

            # otherwise go to the next index
            else:
                index += 1
