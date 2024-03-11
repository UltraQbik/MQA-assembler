from ._asm_types import *
from ._mqis import *


class Compiler(InstructionSet):
    @staticmethod
    def die(message: str, traceback: int, exception):
        raise exception(f"{message}\n  line {traceback}")

    @classmethod
    def process_scope_macros(cls, token_tree: list[list[Token] | Token]) -> dict[str, dict[int, Macro]]:
        """
        Returns a table of this scope's macros (with macro overloading). Modifies the token tree to delete
        already defined macros.
        Not recursive
        :param token_tree: tree of tokens
        :return: table of macros
        """

        # macros
        macros: dict[str, dict[int, Macro]] = {}

        # token pointer
        token_ptr = [-1]

        # token fetching function
        def next_token() -> list[Token] | Token | None:
            token_ptr[0] += 1
            if token_ptr[0] >= len(token_tree):
                return None
            return token_tree[token_ptr[0]]

        # go through each token and make macros
        while (token := next_token()) is not None:
            # skip sub-lists
            if isinstance(token, list):
                continue

            # macro
            if token.token == "macro":
                # load all macro things
                macro_name = next_token()
                macro_args = next_token()
                macro_body = next_token()

                # get rid of macro define
                token_ptr[0] -= 3
                token_tree.pop(token_ptr[0])
                token_tree.pop(token_ptr[0])
                token_tree.pop(token_ptr[0])
                token_tree.pop(token_ptr[0])

                # check if macro name is a token, and not a string
                if not isinstance(macro_name, Token):
                    raise SyntaxError("Expected a macro name")

                # check if macro args is a list of tokens, and not just a token
                if not isinstance(macro_args, list):
                    raise SyntaxError("Expected a '('")

                # check if macro body is a list of tokens
                if not isinstance(macro_body, list):
                    raise SyntaxError("Expected a '{'")

                # check if macro is already present
                if macro_name.token in macros:
                    # check if macros have same amount of arguments
                    if macros[macro_name.token].get(len(macro_args)) is not None:
                        print(f"WARN: You are overloading a macro '{macro_name}' with the same number of arguments")
                else:
                    macros[macro_name.token] = {}

                # add new macro
                macros[macro_name.token][len(macro_args)] = Macro(
                    name=macro_name.token,
                    args=macro_args,
                    body=cls.compile(macro_body, "macro")
                )

        return macros

    @classmethod
    def process_scope_labels(cls, token_tree: list[list[Token] | Token]) -> dict[str, Label]:
        """
        Returns a table of labels. Modifies the token tree to preserve unique labels
        Not recursive
        :param token_tree: 
        :return:
        """

        # table of labels
        labels: dict[str, Label] = {}

        # token pointer
        token_ptr = [-1]

        # token fetching function
        def next_token() -> list[Token] | Token | None:
            token_ptr[0] += 1
            if token_ptr[0] >= len(token_tree):
                return None
            return token_tree[token_ptr[0]]

        # go through tokens and find labels
        while (token := next_token()) is not None:
            # skip sub-lists
            if isinstance(token, list):
                continue

            # check if it's a label
            if token.token[-1] == ":":
                label_name = token.token[:-1]
                if label_name in labels:
                    print(f"WARN: redefining existing label '{label_name}'")

                label_class = Label(label_name, token.traceback)
                labels[label_name] = label_class

                # this may cause problems (?)
                token_tree[token_ptr[0]] = label_class

        # reset token pointer
        token_ptr[0] = -1

        # go through tokens and process label pointers
        while (token := next_token()) is not None:
            # skip sub-lists
            if isinstance(token, list):
                continue

            if token.token[0] == "$":
                if not token.token[1].isdigit():
                    if token.token[1:] not in labels:
                        raise NameError(f"Undefined label '{token}'")
                    token_tree[token_ptr[0]] = labels[token.token[1:]]

        return labels

    @classmethod
    def compile(cls, token_tree: list[list[Token] | Token], scope="main") -> list[list[Token | Argument]]:
        """
        Compiles the token_tree.
        :param token_tree: tree of tokens
        :param scope: scope which is being compiled. Default = main
        :return: list of instructions
        """

        # labels and macros
        labels = cls.process_scope_labels(token_tree)
        macros = cls.process_scope_macros(token_tree)

        # instruction list
        instruction_list = []

        # token pointer
        token_ptr = [-1]

        # token fetching function
        def next_token() -> list[Token] | Token | None:
            token_ptr[0] += 1
            if token_ptr[0] >= len(token_tree):
                return None
            return token_tree[token_ptr[0]]

        # go through tokens and compile the code
        while (token := next_token()) is not None:
            # labels
            if isinstance(token, Label):
                instruction_list.append(token)
                continue

            # if it's a newline
            if token.token == "\n":
                continue

            # instruction mnemonic token
            if token.token in cls.instruction_set:
                instruction_word = [token]
                while (instruction_token := next_token()).token != "\n":
                    instruction_word.append(instruction_token)
                instruction_list.append(instruction_word)

            # macros
            elif token.token in macros:
                macro_name = token.token
                macro_args = next_token()

                # check if macro_args is an instance of a list
                if not isinstance(macro_args, list):
                    raise SyntaxError(f"Expected a '('")

                # check if a macro with this name exists
                if macro_name not in macros:
                    raise NameError(f"Undefined macro '{macro_name}'")

                # check if macro with the same number of args is present
                if macros[macro_name].get(len(macro_args)) is None:
                    raise TypeError(f"Macro '{macro_name}' with this amount of arguments "
                                    f"({len(macro_args)}) doesn't exist")

                macro = macros[macro_name][len(macro_args)].__copy__()
                macro.put_args(*macro_args)
                instruction_list += macro.body

            # otherwise raise a name error
            else:
                raise NameError(f"Undefined instruction word '{token}'")

        # if we are processing the macro => we are done here
        if scope != "main":
            return instruction_list

        cls.process_instructions(instruction_list)

        return instruction_list

    @classmethod
    def process_instructions(cls, instruction_list: list[list[Token | Argument] | Label]):
        """
        Processes the instruction list.
        Makes jump labels and token arguments
        :param instruction_list: list of instructions
        """

        # instruction pointer
        instruction_ptr = [-1]

        # instruction fetching function
        def next_instruction() -> list[Token | Argument] | Label | None:
            instruction_ptr[0] += 1
            if instruction_ptr[0] >= len(instruction_list):
                return None
            return instruction_list[instruction_ptr[0]]

        # inserts new instruction
        def insert_instruction(idx: int, opcode: Token, value, type_: AsmTypes):
            instruction_list.insert(idx, [opcode, Argument(value, type_)])

        # labels
        labels: dict[int, LabelPointer] = {}

        # go through instructions and process labels
        while (instruction := next_instruction()) is not None:
            # make a table entry
            if isinstance(instruction, Label):
                labels[id(instruction)] = LabelPointer(instruction_ptr[0])

                # pop the label from instruction list
                instruction_list.pop(instruction_ptr[0])
                instruction_ptr[0] -= 1
                continue

        # reset instruction pointer
        instruction_ptr[0] = -1

        # go through instruction and process arguments
        # integers here are not limited to 8 bits
        while (instruction := next_instruction()) is not None:
            # go through instruction arguments, and process them
            for token_idx, token in enumerate(instruction):
                # skip mnemonics for now
                if token_idx == 0:
                    continue

                # process labels
                if isinstance(token, Label):
                    instruction[token_idx] = Argument(labels[id(token)], AsmTypes.NAMED)

                # if the token is a pointer
                elif token.token[0] == "$":
                    # if it's a numeric pointer
                    instruction[token_idx] = Argument(int(token.token[1:], base=0), AsmTypes.POINTER)

                # if the token is just a number
                else:
                    instruction[token_idx] = Argument(int(token.token, base=0), AsmTypes.INTEGER)

        # reset instruction pointer
        instruction_ptr[0] = -1

        # code pages
        cache_page = 0
        new_cache_page = 0
        rom_page = 0
        new_rom_page = 0

        # go through instruction and process arguments & check / insert instructions
        while (instruction := next_instruction()) is not None:
            # check mnemonics
            # manual change cache page
            if instruction[0] == "CCP":
                # change cache page
                cache_page = instruction[1].value
                new_cache_page = cache_page

            # manual change rom page
            elif instruction[0] == "CRP":
                # change rom page
                rom_page = instruction[1].value
                new_rom_page = rom_page

            # any jump instruction
            elif instruction[0] in ["JMP", "JMPP", "JMPZ", "JMPN", "JMPC", "CALL"]:
                # instructions that go to different address in ROM
                # NOTE: this most likely will not work in some cases
                if isinstance(instruction[1].value, LabelPointer):
                    new_rom_page = instruction[1].value.value >> 8
                else:
                    new_rom_page = instruction[1].value >> 8

            # any other instruction
            else:
                # if instruction has any arguments
                if len(instruction) > 1:
                    new_cache_page = instruction[1].value >> 8

            if cache_page != new_cache_page or rom_page != new_rom_page:
                # insert instruction if the cache_page != new_cache_page
                if cache_page != new_cache_page:
                    # update page
                    cache_page = new_cache_page

                    # insert instruction and account for it
                    insert_instruction(
                        instruction_ptr[0],
                        Token("CCP", instruction[0].traceback),
                        new_cache_page, AsmTypes.INTEGER)

                # insert instruction if the rom_page != new_rom_page
                if rom_page != new_rom_page:
                    # update page
                    rom_page = new_rom_page

                    # insert instruction and account for it
                    insert_instruction(
                        instruction_ptr[0],
                        Token("CRP", instruction[0].traceback),
                        new_cache_page, AsmTypes.INTEGER)

                # update instruction pointer
                instruction_ptr[0] += 1

                # update label pointers
                for label_id, label_idx in labels.items():
                    # if label index is below current instruction pointer, then the label index is not affected
                    if label_idx.value < instruction_ptr[0]:
                        continue

                    # otherwise update the label pointer, and shift it by 1
                    labels[label_id].value += 1

            # if instruction has any arguments & the arg is not a label
            if len(instruction) > 1 and instruction[1].type is not AsmTypes.NAMED:
                # fix it to 8bit integer
                instruction[1].value = instruction[1].value & 255

        # replace label pointers with ints
        for instruction in instruction_list:
            if len(instruction) > 1 and isinstance(instruction[1].value, LabelPointer):
                instruction[1].value = instruction[1].value.value

    @classmethod
    def get_bytecode(cls, instruction_list: list[list[Token | Argument]]) -> bytes:
        """
        Translates the instruction list into bytes
        :param instruction_list: list of instructions
        :return: bytes
        """

        # list of instruction bytes
        byte_code: bytes = bytes()

        for instruction in instruction_list:
            # decode the instruction
            opcode = cls.instruction_set[instruction[0].token]

            # if the instruction has any arguments (ex. LRA 10, argument 10)
            # decode data and memory_flag
            if len(instruction) > 1:
                data = instruction[1].value
                if instruction[1].type is AsmTypes.POINTER or instruction[1].type is AsmTypes.NAMED:
                    memory_flag = 1
                else:
                    memory_flag = 0

            # else, data and memory_flag are 0
            else:
                data = 0
                memory_flag = 0

            # instruction consists of 3 parts
            # memory_flag   - 1 bit
            # data          - 8 bits
            # opcode        - 7 bits
            # ==========================
            # total         - 16 bits

            # make instruction one 16 bit value
            value = (memory_flag << 15) + (data << 7) + opcode

            # bytes are 8 bits, so, split the value into 2 bytes
            value_high = (value & 0b1111_1111_0000_0000) >> 8
            value_low = value & 0b0000_0000_1111_1111

            # append 2 bytes to the list
            byte_code += bytes([value_high, value_low])

        return byte_code
