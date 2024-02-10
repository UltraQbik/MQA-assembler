from assembler import Assembler


def main():
    asm = Assembler()
    with open("test_program.mqa", "r") as file:
        asm.assemble(file.read())
    print(asm.token_list)


if __name__ == '__main__':
    main()
