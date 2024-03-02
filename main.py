import sys
from compiler import Compiler


def main(argv):
    if len(argv) == 1:
        print("This is a simple compiler for Mini Quantum.\n"
              "Current version: 1.0.0\n\n"
              "\t-i / --input [filename]\t\t\t\tinput file (one that needs to be compiled)\n"
              "\t-o / --output [filename]\t\t\t\toutput file (compiled readable mnemonics "
              "(to which you want to write the result)\n"
              "\t--json\t\t\t\twill create a scrap mechanic blueprint with program card\n"
              "\t--byte\t\t\t\twill output just bytecode\n\n"
              "Examples:\n"
              "\tmqc -i code.mqa.txt\n\t- compiles the code and outputs it to 'compiled_code.mqa.txt'\n"
              "\tmqc -i code.mqa.txt -o compiled.txt\n\t- compiles the code and outputs it to 'compiled.txt'\n"
              )


# def main():
#     with open("test_program.mqa", "r") as file:
#         code = file.read()
#
#     compiler = Compiler()
#     instruction_list = compiler.compile(code)
#
#     if instruction_list is None:
#         exit(-1)
#     for instruction in instruction_list:
#         print(*instruction)


if __name__ == '__main__':
    main(sys.argv)
