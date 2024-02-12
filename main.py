from tokenizer import Tokenizer
from assembler import Assembler, Precompiler
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
    with open("test_program.mqa", "r") as file:
        tokenizer = Tokenizer(file.read())

    precompiler = Precompiler(tokenizer.token_tree)

    print(precompiler.macros)
    print(precompiler.instructions)


if __name__ == '__main__':
    main()
