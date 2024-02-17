from asm_types import Token, Label, InstructionSet


class Compiler(InstructionSet):
    def __init__(self, instructions, macros):
        # macros and instruction list
        self._macros: dict[str, list[dict]] = macros
        self._instructions: list[list[Token | list] | Label] = instructions

        # instruction pointer
        self._instruction_ptr: int = -1

        # compile
        self._compile()

    def _next_instruction(self) -> list[Token | list] | Label | None:
        """
        Returns the next instruction or None if the end of the instruction list is reached
        :return: next instruction or none
        """

        self._instruction_ptr += 1
        if self._instruction_ptr >= len(self._instructions):
            return None
        return self._instructions[self._instruction_ptr]

    def _get_macro(self, name: str, argn: int):
        """
        Gets the macro by name and the argument number (argn)
        :return: dictionary containing the macro
        """

        pass

    def _compile(self):
        """
        The main thing that compiles the code together
        :return: none
        """

        while (instruction := self._next_instruction()) is not None:
            # skip labels (will be done later)
            if isinstance(instruction, Label):
                continue

            if isinstance(instruction[0], list):
                continue

            # macro
            if instruction[0].token in self._macros:
                macro_args = instruction[1]

                if not isinstance(macro_args, list):
                    self._traceback = instruction[0].traceback
                    raise SyntaxError("Invalid syntax")

                macro_args = [x for x in macro_args if x != ","]

                print(macro_args)

