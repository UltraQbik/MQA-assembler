def assemble_code(code: str):
    def separate_tokens() -> list:
        token = ""
        token_list = []

        char_ptr = 0
        while char_ptr < len(code):
            # get next character
            char = code[char_ptr]
            char_ptr += 1

            if char == " " and token != "":
                token_list.append(token)
                token = ""
            elif char == "\n" and token != "":
                token_list.append(token)
                token_list.append("\n")
                token = ""
            elif char in "({[]});":
                if token != "":
                    token_list.append(token)
                    token = ""
                token_list.append(char)
            elif char != " " and char != "\n":
                token += char
        if token:
            token_list.append(token)
            token_list.append("\n")
        return token_list

    def build_token_tree(token_list: list):
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
                        tree.append(build_token_tree(scope))
                        break
                    elif token in "]})":
                        nesting -= 1
                    elif token in "({[":
                        nesting += 1

                    scope.append(token)
            else:
                tree.append(token)

        return tree

    tok_list = separate_tokens()
    tok_tree = build_token_tree(tok_list)
    print(tok_tree)
