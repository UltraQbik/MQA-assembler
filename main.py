import assembler


def main():
    assembler.read_instruction_set()
    with open("test_program.mqa", "r") as file:
        print(
            assembler.assemble_code(file.read())
        )


if __name__ == '__main__':
    main()
