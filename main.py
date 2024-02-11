from tokenizer import Tokenizer
from asm_types import Token


def print_recursive(token_list: list[Token | list], nesting: int = 0):
    for item in token_list:
        if isinstance(item, list):
            print_recursive(item, nesting + 1)
            continue
        if item == "\n":
            continue
        print(f"{item.traceback: >4}{'\t' * nesting} | {item.token}")


def main():
    asm = Tokenizer()
    with open("test_program.mqa", "r") as file:
        asm.tokenize(file.read())

    print_recursive(asm.token_tree)


if __name__ == '__main__':
    main()
