from tokenizer import Tokenizer
from compiler import Compiler


def main():
    with open("test_program.mqa", "r") as file:
        token_tree = Tokenizer(file.read()).token_tree

    compiler = Compiler()
    instruction_list = compiler.compile(token_tree)

    for instruction in instruction_list:
        print(*instruction)


if __name__ == '__main__':
    main()
