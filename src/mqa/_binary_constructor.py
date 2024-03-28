from ._asm_types import *
from ._mqis import *


MQ_VERSION = b'1.1 '


class Constructor:
    @staticmethod
    def generate_bytes(includes: list[str], instruction_list: IScope, verbose: bool = False) -> bytes:
        """
        Generates the executable .mqa file with header
        :param includes: list of included extensions
        :param instruction_list: list of instruction
        :param verbose: should it be verbose
        :return: bytes
        """

        #               |                    : 10 bytes total
        #               | cpuVersion         : 4  bytes - "1.1 "
        # little_endian | includeSectionSize : 2  bytes - amount of bytes in include section
        # little_endian | assemblySectionSize: 4  bytes - amount of bytes in code
        # little_endian | includeSectionData : N  bytes - the include data
        # little_endian | assemblySectionData: N  bytes - the code data

        # create data array
        data = bytearray()

        # cpuVersion
        data += MQ_VERSION

        # includeSectionSize
        data += b'--'

        # assemblySectionSize
        data += b'----'

        # section start
        section_start = len(data)

        # includeSectionData
        for include in includes:
            data += include.encode("ASCII") + b'\n'

        # change includeSectionSize
        include_section_size = (len(data) - section_start)
        data[4:6] = include_section_size.to_bytes(2, "little")

        # section start
        section_start = len(data)

        # assemblySectionData
        for instruction in instruction_list:
            # make instruction one 16 bit value
            value = instruction.flag << 15
            value += instruction.value << 7
            value += InstructionSet.instruction_set[instruction.opcode]

            # append 2 bytes to the list
            data += value.to_bytes(2, "little")

        # change assemblySectionSize
        assembly_section_size = len(data) - section_start
        data[6:10] = assembly_section_size.to_bytes(4, "little")

        # if verbose
        if verbose:
            print("Header start:")
            print(f"\tcpuVersion:          {MQ_VERSION.decode('ASCII').strip()}")
            print(f"\tincludeSectionSize:  {include_section_size}")
            print(f"\tassemblySectionSize: {assembly_section_size}")
            print("Header end.")
            print(f"Total size: {len(data)} bytes")

        # return the data
        return data
