class Assembler:
    def __init__(self):
        """
        The main assembler class.
        It assembles the code, does the macros, variable assigns, jump pointers, etc.
        """

        self.code: str | None = None
        self.token_list: list | None = None

    def assemble(self, code: str):
        """
        Spaghetti code that assembles the code!
        I know it's stupid, but I don't know how to make it better
        :param code: Mini Quantum Assembly code
        :return: none
        """

        self.code = code
        self._separate_tokens()
        self._delete_comments()
        self.token_list = self._build_token_tree(self.token_list)

    def _separate_tokens(self):
        """
        Separates the tokens
        :return: none
        """

        # create token string
        token = ""

        # initialize token list
        self.token_list = []

        # initialize character pointer to 0
        char_ptr = 0
        while char_ptr < len(self.code):
            # get next character
            char = self.code[char_ptr]
            char_ptr += 1

            # spaces between things
            if char == " " and token != "":
                self.token_list.append(token)
                token = ""

            # new lines
            elif char in "\n," and token != "":
                self.token_list.append(token)
                self.token_list.append(char)
                token = ""

            # brackets
            elif char in "({[]})":
                if token != "":
                    self.token_list.append(token)
                    token = ""
                self.token_list.append(char)

            # anything else
            elif char != " " and char != "\n":
                token += char

        # if there is still a token at the end of the file
        if token:
            self.token_list.append(token)
            self.token_list.append("\n")

    def _delete_comments(self):
        """
        Removes the comments to not clutter the token list
        :return: none
        """

        # create new token list
        new_token_list = []
        commented = False
        for token in self.token_list:
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
        self.token_list = new_token_list

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
            if token in "({[":
                scope = []
                nesting = 0
                while index < len(token_list):
                    # fetch inner scope token
                    token = token_list[index]
                    index += 1

                    # if another opening bracket of same type is found => increment the nesting variable
                    # break out of the loop only when the nesting is 0 and the closing bracket is found
                    if token in "]})" and nesting == 0:
                        tree.append(self._build_token_tree(scope))
                        break
                    elif token in "]})":
                        nesting -= 1
                    elif token in "({[":
                        nesting += 1

                    # append tokens to the local scope
                    scope.append(token)

                # if the end of the code was reached => die.
                else:
                    raise SyntaxError("No closing bracket was found;")
            else:
                # append tokens to the global scope
                tree.append(token)
        # return the token tree (or a local scope)
        return tree
