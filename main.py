from tokenizer import Tokenizer
from assembler import Assembler
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
    tokenizer = Tokenizer()
    with open("mandelbrot_set.mqa", "r") as file:
        tokenizer.tokenize(file.read())

    asm = Assembler(tokenizer.token_tree)
    asm.assemble()

    print(asm._macros)
    print(asm._instructions)


if __name__ == '__main__':
    main()
