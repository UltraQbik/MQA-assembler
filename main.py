from compiler import Compiler


def main():
    with open("test_program.mqa", "r") as file:
        code = file.read()

    compiler = Compiler()
    instruction_list = compiler.compile(code)

    if instruction_list is None:
        exit(-1)
    for instruction in instruction_list:
        print(*instruction)


if __name__ == '__main__':
    main()
