from argparse import Namespace
from ._asm_types import *
from ._mqis import *


# all known packages
# TODO: add the ability to fetch package list directly from MQE package
AVAILABLE_PACKAGES: set[str] = {
    "FileManager",
    "DisplayManager"
}


class Compiler:
    KEYWORDS: set[str] = {"FOR", "ASSIGN", "LEN", "ENUMERATE", "INCLUDE", "__WRITE_STR__"}
    RETURNING_KEYWORDS: set[str] = {"LEN", "ENUMERATE"}

    def __init__(self, parser_args: Namespace):
        """
        The main compiler class
        """

        self.tree: TScope | None = None
        self.main: IScope = IScope(list(), BType.MISSING)
        self.includes: list[str] = list()

        self.labels: dict[str, Pointer] = dict()
        self.macros: dict[str, dict[int, Macro]] = dict()
        self.define: dict[str, Token] = dict()

        self._parser = parser_args

    def process_macros_and_labels(self):
        """
        Processes scope macros
        """

        self.tree.set_ptr()
        while (token := self.tree.next()) is not None:
            # skip sub-scopes and labels
            if isinstance(token, TScope | Label):
                continue

            # macros
            if token.token == "macro":
                # fetch values
                self.tree.pop()
                macro_name = self.tree.pop()
                macro_args = self.tree.pop()
                macro_body = self.tree.pop()

                # perform checks
                # name check
                if isinstance(macro_name, Token):
                    macro_name = macro_name.token
                else:
                    raise SyntaxError("Incorrect macro definition")

                # arguments check
                if not isinstance(macro_args, TScope) or macro_args.btype is not BType.ROUND:
                    raise SyntaxError("Excepted a '('")

                # body check
                if not isinstance(macro_body, TScope) or macro_body.btype is not BType.CURVED:
                    raise SyntaxError("Expected a '{'")

                # adding a macro
                if macro_name not in self.macros:
                    self.macros[macro_name] = {}
                if len(macro_args) in self.macros[macro_name]:
                    print("WARN: macro redefinition")

                # initiate a sub-compiler class for a macro
                sub_compiler = self.make_sub_compiler()

                # create a macro
                self.macros[macro_name][len(macro_args)] = Macro(
                    sub_compiler.compile(macro_body, False),
                    BType.MISSING,
                    macro_args
                )

            # labels
            elif token.token[-1] == ":":
                lbl = Label(token.token[:-1], token.traceback)
                self.tree[self.tree.pointer] = lbl

                def replace(old, new, scope: TScope):
                    for idx, t in enumerate(scope):
                        if isinstance(t, Label):
                            continue

                        if isinstance(t, TScope):
                            replace(old, new, t)
                            continue

                        t: Token
                        if t.token[1:] == old:
                            scope[idx] = new

                replace(lbl, Label(lbl, token.traceback), self.tree)

    def make_sub_compiler(self):
        """
        Creates a copy of itself
        """

        # initiate a sub-compiler class for a macro
        sub_compiler = Compiler(self._parser)

        # carry labels, macros and defines inside
        sub_compiler.macros.update(deepcopy(self.macros))
        sub_compiler.define.update(deepcopy(self.define))

        return sub_compiler

    def process_for_loop(self, args: Token | TScope, range_: Token | int | list[tuple], body: TScope) -> IScope:
        """
        Processes the for loop.
        :param args: argument / arguments that will be used in a for loop
        :param range_: range that will be applied to 'args'
        :param body: body of the for loop
        :returns: instruction scope
        """

        # check
        if not isinstance(args, TScope) and isinstance(range_, list):
            raise SyntaxError("Unable to unpack 1 value to multiple arguments")

        # create a sub-compiler
        sub_compiler = self.make_sub_compiler()

        # compile the body
        compiled_body: IScope = sub_compiler.compile(body, False)

        # TODO: make optimized for memory version
        instruction_scope = IScope(list(), BType.MISSING)

        # string ranges
        if isinstance(range_, Token) and range_.token[0] == range_.token[-1] == "\"":
            args: Token
            for char in range_.token[1:-1]:
                body_copy = deepcopy(compiled_body)
                body_copy.replace(args.token, ord(char))
                instruction_scope.unify(body_copy)

        # integer ranges
        elif isinstance(range_, Token):
            split_range = range_.token.split("..")

            # checks
            if len(split_range) > 2:
                raise SyntaxError("Incorrectly defined range")

            try:
                range_start = int(split_range[0], base=0)
                range_end = int(split_range[1], base=0)
            except ValueError:
                raise SyntaxError("Unable to convert an integer range number")

            if range_start < range_end:
                range__ = range(range_start, range_end)
            else:
                range__ = range(range_start - 1, range_end - 1, -1)

            args: Token
            for i in range__:
                body_copy = deepcopy(compiled_body)
                body_copy.replace(args.token, i)
                instruction_scope.unify(body_copy)

        # single integer range
        elif isinstance(range_, int):
            args: Token
            for i in range(range_):
                body_copy = deepcopy(compiled_body)
                body_copy.replace(args.token, i)
                instruction_scope.unify(body_copy)

        # enumerate
        elif isinstance(range_, list) and isinstance(args, TScope):
            # yes, we assume there are only 2 args
            for idx, char in range_:
                body_copy = deepcopy(compiled_body)

                body_copy.replace(args[0].token, idx)
                body_copy.replace(args[1].token, ord(char))

                instruction_scope.unify(body_copy)
        else:
            raise NotImplementedError("Something went wrong?")

        return instruction_scope

    def process_keyword(self, keyword: Token):
        """
        Processes keywords.
        :param keyword: keyword that needs to be processed
        :return: value after it's processed
        """

        # assign
        if keyword.token == "ASSIGN":
            arg = self.tree.next()

            # check
            if not isinstance(arg, Token):
                raise NotImplementedError("Only string assignments are allowed")

            to_assign = self.tree.next()
            if isinstance(to_assign, Token) and to_assign.token in self.RETURNING_KEYWORDS:
                to_assign = self.process_keyword(to_assign)

            self.define[arg.token] = to_assign

            def replace(old, new, scope):
                for idx, t in enumerate(scope):
                    if isinstance(t, TScope):
                        replace(old, new, t)
                        continue

                    if not isinstance(t, Token):
                        continue

                    if t == old:
                        scope[idx] = new

            replace(arg, to_assign, self.tree)

        # for loop
        elif keyword.token == "FOR":
            # fetch the name(s) for the variable(s)
            args = self.tree.next()

            if isinstance(args, TScope) and args.btype is not BType.ROUND:
                raise SyntaxError("Expected a '('")

            # check IN keyword
            token = self.tree.next()
            if not (isinstance(token, Token) and token.token == "IN"):
                raise SyntaxError("Incorrect for loop define")

            range_ = self.tree.next()
            if isinstance(range_, Token):
                if range_.token in self.RETURNING_KEYWORDS:
                    range_ = self.process_keyword(range_)
                elif range_.token[0] == range_.token[-1] == "\"":
                    pass
                elif range_.token.find("..") == -1:
                    try:
                        range_ = int(range_.token, base=0)
                    except ValueError:
                        raise ValueError("Unable to convert single value range")
            else:
                raise SyntaxError("Incorrect for loop range")

            body = self.tree.next()
            if not (isinstance(body, TScope) and body.btype is BType.CURVED):
                raise SyntaxError("Expected a '{'")

            # append instructions to the list of instructions
            self.main.unify(self.process_for_loop(args, range_, body))

        # LEN
        elif keyword.token == "LEN":
            # fetch the next argument
            arg = self.tree.next()

            # checks
            if not isinstance(arg, Token):
                raise TypeError(f"Unable to return length of '{arg}'")

            if arg.token[0] == arg.token[-1] == "\"":
                return len(arg.token)-2
            raise TypeError("Unable to return length for a non string argument")

        # ENUMERATE
        elif keyword.token == "ENUMERATE":
            # fetch the next argument
            arg = self.tree.next()

            if isinstance(arg, Token) and arg.token[0] == arg.token[-1] == "\"":
                return list(enumerate(arg.token[1:-1]))
            else:
                raise NotImplementedError(f"Unable to construct a sequence for {arg.__class__}")

        # INCLUDE
        elif keyword.token == "INCLUDE":
            # package name
            arg = self.tree.next()

            if not isinstance(arg, Token):
                raise SyntaxError("Incorrect package name")

            if arg.token not in AVAILABLE_PACKAGES:
                print(f"WARN: included package '{arg.token}' is not recognized by current version of the compiler")

            # append the included package name
            self.includes.append(arg.token)

        # __WRITE_STR__
        elif keyword.token == "__WRITE_STR__":
            # get arguments for a built-in function
            pointer = self.tree.next()
            string = self.tree.next()

            # checks
            if not isinstance(pointer, Token):
                raise TypeError(f"Incorrect type '{pointer.__class__}'")
            if not isinstance(string, Token):
                raise TypeError(f"Incorrect type '{string.__class__}")

            try:
                pointer = int(pointer.token, base=0)
            except ValueError:
                raise TypeError("Incorrect argument")

            if not (string.token[0] == string.token[-1] == "\""):
                raise TypeError("Incorrect argument")

            sorted_string = [(x, ord(y)) for x, y in enumerate(string.token[1:-1])]
            sorted_string.sort(key=lambda x: x[1])

            # just ignore empty strings
            if len(sorted_string) == 0:
                return

            acc_value = -1
            for item in sorted_string:
                # if the character in ACC is different
                if acc_value != item[1]:
                    acc_value = item[1]
                    self.main.append(
                        Instruction("LRA", acc_value, tb=keyword.traceback))

                # NOTE: the address will exceed 8bit integer limit,
                # but it will be fixed in the next step of compilation
                address = item[0] + pointer

                # append store instruction
                self.main.append(
                    Instruction("SRA", address, tb=keyword.traceback))

        else:
            raise NotImplementedError(f"Keyword '{keyword.token}' is not yet implemented")

    def compile(self, tree: TScope, is_main=True) -> Any:
        """
        Main compile method for token scopes
        :param tree: token tree
        :param is_main: is the scope - main scope
        :return: IScope
        """

        # set input tree
        self.tree = deepcopy(tree)

        # process macros and labels
        self.process_macros_and_labels()

        self.tree.set_ptr()
        while (token := self.tree.next()) is not None:
            # append labels and continue
            if isinstance(token, Label):
                self.main.append(token)
                continue

            # skip newlines
            if token.token == "\n":
                continue

            # mnemonics
            if token.token in InstructionSet.instruction_set:
                instruction_word = [token]
                while (itoken := self.tree.next()).token != "\n":
                    instruction_word.append(itoken)
                self.main.append(Instruction(
                    instruction_word[0].token,
                    instruction_word[1].token if len(instruction_word) > 1 else 0
                ))

            # macros
            elif token.token in self.macros:
                # fetch data
                macro_name: Token = self.tree.pop()
                macro_args = self.tree.pop()

                # checks
                if not isinstance(macro_args, TScope) and macro_args.btype is not BType.ROUND:
                    raise SyntaxError("Expected a '('")

                if len(macro_args) not in self.macros[macro_name.token]:
                    raise NameError(f"Undefined macro {macro_name}")

                macro = deepcopy(self.macros[macro_name.token][len(macro_args)])
                arg: Token
                for idx, arg in enumerate(macro.args):
                    macro.replace(arg.token, macro_args[idx].token)
                self.main.body += macro.body

            # keywords
            elif token.token in self.KEYWORDS:
                self.process_keyword(token)

            else:
                raise NameError(f"Undefined instruction '{token.token}'")

        # sub-scopes are done here
        if not is_main:
            return deepcopy(self.main)

        # process instruction arguments
        for instruction in self.main:
            # already processed ints and labels
            if isinstance(instruction, Label) or isinstance(instruction.value, int | Label):
                continue

            # pointers
            if instruction.value[0] == "$":
                # try to convert string integer to normal integer
                try:
                    instruction.value = int(instruction.value[1:], base=0)
                except ValueError:
                    raise ValueError("Incorrect pointer value")

                # set memory flag to be true (as this is a pointer)
                instruction.flag = True

            # generic string integers
            elif isinstance(instruction.value, str):
                # try to convert string integer to normal integer
                try:
                    instruction.value = int(instruction.value, base=0)
                except ValueError:
                    raise ValueError("Incorrect integer value")

            # something went wrong
            else:
                raise Exception("Something went wrong")

        # optimize instructions
        self.optimize_instructions()

        # place all the labels
        self.place_labels()

        return deepcopy(self.main)

    def optimize_instructions(self):
        """
        Optimizes away unnecessary instructions
        """

        # value in accumulator
        acc = 0

        # is the instruction non-modifying
        no_modify = True

        # save the old pointer value
        old_ptr = self.main.pointer
        self.main.set_ptr()

        while (instruction := self.main.next()) is not None:
            # skip labels
            if isinstance(instruction, Label):
                continue

            if instruction.opcode == "LRA":
                # if there are no modifying instructions before previous load
                # remove this instruction
                if acc == instruction.value and no_modify:
                    self.main.pop()

                # update the value in the accumulator
                acc = instruction.value

                # update no_modify
                no_modify = True

            # if the instruction is not in the list of non modifying instructions
            elif instruction.opcode not in InstructionSet.non_modifying_instructions:
                # then set no_modify to be false, as the ACC may change
                no_modify = False

        # return back
        self.main.set_ptr(old_ptr)

    def shift_labels(self, offset: int = 1, index: int | None = None):
        """
        Shifts labels by given offset
        :param offset: amount by which to shift (default is 1)
        :param index: from which index to shift (default is self.main.pointer)
        """

        if index is None:
            index = self.main.pointer

        for lbl_id, lbl_idx in self.labels.items():
            if lbl_idx.value > index:
                self.labels[lbl_id].value += offset

    def place_labels(self):
        """
        Places pointers in correct places
        """

        # save old pointer value
        old_ptr = self.main.pointer
        self.main.set_ptr()

        # label table
        while (instruction := self.main.next()) is not None:
            if isinstance(instruction, Label):
                lbl: Label = self.main.pop()
                self.labels[lbl.token] = Pointer(self.main.pointer)

        # reset pointer
        self.main.set_ptr()

        # go through list of instructions, and find those which have labels as arguments
        while (instruction := self.main.next()) is not None:
            # if it's not a label, skip
            if not isinstance(instruction.value, Label):
                continue

            # replace label with a pointer
            instruction.value = self.labels[instruction.value.token]

        # reset pointer
        self.main.set_ptr()

        # ROM page
        rom_page = 0
        new_rom_page = 0

        while (instruction := self.main.next()) is not None:
            # check if the instruction is a jump of some kind
            if instruction.opcode in ["JMP", "JMPP", "JMPZ", "JMPN", "JMPC", "CALL"]:
                if isinstance(instruction.value, Pointer):
                    new_rom_page = instruction.value.value >> 8
                else:
                    print("WARN: don't use static jump pointers, as this may cause problems")
                    new_rom_page = instruction.value >> 8

            # check for manual rom page change instructions
            elif instruction.opcode == "CRP":
                new_rom_page = instruction.value >> 8

            # check that the new rom page does not exceed 16 bit limit (upper 8 bits)
            if new_rom_page > 255:
                raise ResourceWarning("Jump index exceeds 16 bit integer limit")

            # if the new rom page is not equal to current one
            if rom_page != new_rom_page:
                self.main.insert(
                    self.main.pointer,
                    Instruction("CRP", new_rom_page, False))
                self.shift_labels()

        # make everything integer
        for instruction in self.main:
            # replace pointer with just integer
            if isinstance(instruction.value, Pointer):
                instruction.value = instruction.value.value

        # get old pointer value
        self.main.set_ptr(old_ptr)
