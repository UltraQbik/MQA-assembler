from tokenizer import Tokenizer
from compiler import Compiler
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

    compiler = Compiler(tokenizer.token_tree)

    print(compiler._macros)
    print(compiler._instructions)


if __name__ == '__main__':
    main()
