from asm_types import Token, Label, InstructionSet


class Compiler(InstructionSet):
    def __init__(self, instructions, macros):
        # macros and instruction list
        self._macros: dict[str, list[dict]] = macros
        self._instructions: list[list[Token] | Label] = instructions

        # instruction pointer
        self._instruction_ptr: int = -1

    def _next_instruction(self) -> list[Token] | Label | None:
        """
        Returns the next instruction or None if the end of the instruction list is reached
        :return: next instruction or none
        """

        self._instruction_ptr += 1
        if self._instruction_ptr >= len(self._instructions):
            return None
        return self._instructions[self._instruction_ptr]

    def _compile(self):
        """
        The main thing that compiles the code together
        :return: none
        """
