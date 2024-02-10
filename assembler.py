def separate_tokens(code: str) -> list:
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
        elif char in "\n," and token != "":
            token_list.append(token)
            token_list.append(char)
            token = ""
        elif char in "({[]})":
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


def delete_comments(token_list: list):
    new_token_list = []
    commented = False
    for token in token_list:
        if token == ";":
            commented = True
            continue
        elif token == "\n":
            commented = False
        if not commented:
            new_token_list.append(token)
    return new_token_list


def build_token_tree(token_list: list):
    tree = []

    index = 0
    while index < len(token_list):
        token = token_list[index]
        index += 1

        if token in "({[":
            bracket = token
            opposite_bracket = {"(": ")", "{": "}", "[": "]"}[bracket]

            scope = []
            nesting = 0
            while index < len(token_list):
                token = token_list[index]
                index += 1

                if token == opposite_bracket and nesting == 0:
                    tree.append(build_token_tree(scope))
                    break
                elif token == opposite_bracket:
                    nesting -= 1
                elif token == bracket:
                    nesting += 1

                scope.append(token)
            else:
                raise SyntaxError("no closing bracket")
        else:
            tree.append(token)

    return tree


def assemble_code(code: str):
    tok_list = separate_tokens(code)
    print(tok_list)
    tok_list = delete_comments(tok_list)
    print(tok_list)
    tok_tree = build_token_tree(tok_list)
    print(tok_tree)
