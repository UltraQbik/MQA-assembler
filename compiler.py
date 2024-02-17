import copy
from asm_types import Token, Label, InstructionSet


class Compiler(InstructionSet):
    def __init__(self, instructions, macros):
        # macros and instruction list
        self._macros: dict[str, list[dict]] = macros
        self._instructions: list[list[Token | list] | Label] = instructions
        self._new_instructions: list[list[Token | list] | Label] = []

        # instruction pointer
        self._instruction_ptr: int = -1

        # traceback
        self._traceback: int = 0

        # compile
        self._compile()

    @property
    def traceback(self) -> int:
        return self._traceback

    def _next_instruction(self) -> list[Token | list] | Label | None:
        """
        Returns the next instruction or None if the end of the instruction list is reached
        :return: next instruction or none
        """

        self._instruction_ptr += 1
        if self._instruction_ptr >= len(self._instructions):
            return None
        return self._instructions[self._instruction_ptr]

    def _get_macro(self, name: str, argn: int) -> dict | None:
        """
        Gets the macro by name and the argument number (argn)
        :return: dictionary containing the macro, or None if nothing was found
        """

        # if the macro doesn't exist
        if name not in self._macros:
            return None

        # go through all macros, and compare the argn numbers
        for macro in self._macros[name]:
            if macro["argn"] == argn:
                return macro

        # if macro was not found with that amount of arguments
        return None

    def _compile(self):
        """
        The main thing that compiles the code together
        :return: none
        """

        while (instruction := self._next_instruction()) is not None:
            # skip labels (will be done later)
            if isinstance(instruction, Label):
                self._new_instructions.append(instruction)
                continue

            if isinstance(instruction[0], list):
                self._new_instructions.append(instruction)
                continue

            # macro
            if instruction[0].token in self._macros:
                macro_args = instruction[1]

                if not isinstance(macro_args, list):
                    self._traceback = instruction[0].traceback
                    raise SyntaxError("Invalid syntax")

                macro_args = [x for x in macro_args if x != ","]

                macro = self._get_macro(instruction[0].token, len(macro_args))

                if macro is None:
                    self._traceback = instruction[0].traceback
                    raise TypeError("Too many arguments")

                macro_body = copy.deepcopy(macro["body"])
                for macro_instruction in macro_body:
                    for idx, token in enumerate(macro_instruction):
                        if token.token not in macro["args"]:
                            continue

                        index = macro["args"].index(token.token)
                        macro_instruction[idx] = macro_args[index]

                # append instructions of macro to the list of compiled ish instructions
                self._new_instructions += macro_body

            # keyword instructions (LRA, SRA, JMP, etc.)
            elif instruction[0].token in self.instruction_set:
                self._new_instructions += instruction
