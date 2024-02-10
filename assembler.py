class Assembler:
    def __init__(self):
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

        token = ""
        self.token_list = []

        char_ptr = 0
        while char_ptr < len(self.code):
            # get next character
            char = self.code[char_ptr]
            char_ptr += 1

            if char == " " and token != "":
                self.token_list.append(token)
                token = ""
            elif char in "\n," and token != "":
                self.token_list.append(token)
                self.token_list.append(char)
                token = ""
            elif char in "({[]})":
                if token != "":
                    self.token_list.append(token)
                    token = ""
                self.token_list.append(char)
            elif char != " " and char != "\n":
                token += char
        if token:
            self.token_list.append(token)
            self.token_list.append("\n")

    def _delete_comments(self):
        """
        Removes the comments to not clutter the token list
        :return: none
        """

        new_token_list = []
        commented = False
        for token in self.token_list:
            if token == ";":
                commented = True
                continue
            elif token == "\n":
                commented = False
            if not commented:
                new_token_list.append(token)
        self.token_list = new_token_list

    def _build_token_tree(self, token_list: list):
        """
        Builds the token tree
        :param token_list: yes
        :return: none
        """

        tree = []
        index = 0
        while index < len(token_list):
            token = token_list[index]
            index += 1

            if token in "({[":
                scope = []
                nesting = 0
                while index < len(token_list):
                    token = token_list[index]
                    index += 1

                    if token in "]})" and nesting == 0:
                        tree.append(self._build_token_tree(scope))
                        break
                    elif token in "]})":
                        nesting -= 1
                    elif token in "({[":
                        nesting += 1

                    scope.append(token)
            else:
                tree.append(token)

        return tree
