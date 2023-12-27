GLOBAL_INSTRUCTION_SET: None | dict = None


def read_instruction_set():
    global GLOBAL_INSTRUCTION_SET
    GLOBAL_INSTRUCTION_SET = {}
    with open("instruction_set.mqi", "r") as file:
        instruction_set = file.read().replace("\r\n", "\n").split("\n")
        for instruction in instruction_set:
            if not instruction:
                continue

            decoded_instruction = instruction.split(" - ")
            if decoded_instruction[1] == "/":
                continue

            GLOBAL_INSTRUCTION_SET[decoded_instruction[1]] = {
                "index": decoded_instruction[0],
                "arguments": decoded_instruction[2]
            }

    for item, val in GLOBAL_INSTRUCTION_SET.items():
        print(f"{item: <4} | {val}")


def assemble_code(code: str):
    def separate_tokens() -> list:
        token = ""
        token_list = []

        char_ptr = 0
        char = None
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
            elif char != " " and char != "\n":
                token += char
        if token:
            token_list.append(token)
            token_list.append("\n")
        return token_list

    def build_token_tree(token_list: list):
        tree = {"main": []}
        scope = "main"

        for token in token_list:
            if token[-1] == ":":
                scope = token[:-1]
                tree[scope] = []
            else:
                tree[scope].append(token)

        return tree

    tok_list = separate_tokens()
    tok_tree = build_token_tree(tok_list)
    print(tok_tree)
