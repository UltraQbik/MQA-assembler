import os
import argparse
from . import Compiler, Tokenizer, Constructor


parser = argparse.ArgumentParser(prog="mqa", description="Compiles Mini Quantum CPU source files.")
parser.add_argument("input", type=str, help="source file")
parser.add_argument("-o", "--output", type=str, help="output file")
parser.add_argument("-j", "--json", help="creates a blueprint for Scrap Mechanic", action="store_true")
parser.add_argument("-v", "--verbose", help="verbose prints", action="store_true")
args = parser.parse_args()


def code_compile(code: str):
    """
    Compiles the given code.
    :param code: code string
    :return: instruction list
    """

    token_list = Tokenizer.tokenize(code)
    token_tree = Tokenizer.build_token_tree(token_list)
    instruction_list = Compiler.compile(token_tree)

    return instruction_list


def die(message=None):
    """
    Dies with some kind of message.
    :param message: message with which the program will do the die thing
    """

    if message is not None:
        print(f"ERROR: {message}")
    exit(1)


def main():
    # file reading
    if not os.path.isfile(args.input):
        die(f"file '{args.input}' not found")
    with open(args.input, "r", encoding="utf8") as file:
        code = file.read()

    # compilation
    instruction_list = code_compile(code)

    # if we want to see the compiled instructions
    if args.verbose:
        print("Instructions start:")
        # how many digits does the length of list have
        line_count_offset = len(instruction_list.__len__().__str__())
        for idx, instruction in enumerate(instruction_list):
            mnemonic = instruction[0].token
            argument = instruction[1] if len(instruction) > 1 else ""
            print(f"\t{idx: >{line_count_offset}} | {mnemonic} {argument}")
        print("Instructions end.")

    # file creation
    output_filename = args.output
    if output_filename is None:
        # 'compiled_{file}'
        output_filename = "compiled_" + os.path.splitext(os.path.basename(args.input))[0]
        output_filename += ".mqa"

    # append .mqa to end of the file, if it doesn't have it
    if os.path.splitext(output_filename)[1] == "":
        output_filename += ".mqa"

    # write bytes to a file
    with open(output_filename, "wb") as file:
        file.write(
            Constructor.generate_bytes([], instruction_list, verbose=args.verbose)
        )


if __name__ == '__main__':
    main()
