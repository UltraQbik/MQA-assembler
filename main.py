from assembler import Assembler


def main():
    asm = Assembler()
    with open("test_program.mqa", "r") as file:
        asm.assemble(file.read())

    def print_recursive(token_list: list, nesting: int = 0):
        for item in token_list:
            if isinstance(item, list):
                print_recursive(item, nesting+1)
                continue
            if item == "\n":
                continue
            print(f"{item.code_line: >4}{'\t' * nesting} | {item.token}")

    print_recursive(asm.token_list)


if __name__ == '__main__':
    main()
