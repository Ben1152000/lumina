import re, sys, argparse
from functools import reduce
from lark import Lark
from program import Program


class ParseError(Exception):
    pass


class Assembler:

    OPCODES = {
        "POP": 0x00,
        "PUSHZ": 0x10,
        "PUSHB": 0x11,
        "PEEK": 0x20,
        "PUSHW": 0x31,
        "JMP": 0x40,
        "JZ": 0x50,
        "JNZ": 0x60,
        "INC": 0x70,
        "DEC": 0x71,
        "NOT": 0x72,
        "NEG": 0x73,
        "SHL8": 0x74,
        "SHR8": 0x75,
        "ADD": 0x80,
        "SUB": 0x81,
        "DIV": 0x82,
        "MUL": 0x83,
        "MOD": 0x84,
        "AND": 0x85,
        "OR": 0x86,
        "XOR": 0x87,
        "GT": 0x88,
        "GTE": 0x89,
        "LT": 0x8A,
        "LTE": 0x8B,
        "EQ": 0x8C,
        "NEQ": 0x8D,
        "SHL": 0x8E,
        "SHR": 0x8F,
        "FLOOR": 0x90,
        "CEIL": 0x91,
        "SIN": 0x92,
        "COS": 0x93,
        "FDIV": 0x9F,
        "get_length": 0xE0,
        "get_wall_time": 0xE1,
        "get_precise_time": 0xE2,
        "set_pixel": 0xE3,
        "show": 0xE4,
        "random_int": 0xE5,
        "get_pixel": 0xE6,
        "set_all_pixels": 0xE7,
        "sleep": 0xF9,
        "exit": 0xFA,
        "error": 0xFB,
        "swap": 0xFC,
        "dump": 0xFD,
        "yield": 0xFE,
        "two_byte": 0xFF,
    }

    FUNCT = {"POP", "PEEK"}  # instructions that use funct [5:8]

    ARGS = {
        "PUSHB": [1],
        "PUSHW": [4],
        "JMP": [2],
        "JZ": [2],
        "JNZ": [2],
    }

    parser = Lark(
        "%import common.WS\n"
        "%ignore WS\n"
        "%import common.SH_COMMENT\n"
        "%ignore SH_COMMENT\n"
        "%import common.INT -> DEC\n"
        "%import common.CNAME\n"
        'INT : ("+"|"-")? (/[0-9]+/ | /0[bB][01]+/ | /0[oO][0-7]+/ | /0[xX][0-9a-fA-F]+/)\n'
        "LABEL : CNAME\n"
        "INST : CNAME\n"
        'line : (LABEL ":")? (INST (INT | LABEL)? ("," (INT | LABEL))*)?',
        start="line",
    )

    @staticmethod
    def assemble(source):
        tokens = reduce(
            lambda tokens, tree: tokens + (tree.children),
            map(Assembler.parser.parse, source.split("\n")),
            list(),
        )  # use lark to parse source string

        pointer = 0  # pointer to byte index
        labels = dict(
            map(
                lambda token: (token.value, None),
                filter(lambda token: token.type == "LABEL", tokens),
            )
        )  # map from label to index
        jumps = dict()
        data = bytearray()

        iterator = iter(tokens)
        token = next(iterator, None)
        while token:
            if token.type == "LABEL":
                labels[token.value] = pointer
            elif token.type == "INST":
                if token.value not in Assembler.OPCODES:
                    raise ParseError(f"Invalid instruction: {token.value}")
                opcode = Assembler.OPCODES[token.value]
                if token.value in Assembler.FUNCT:
                    funct = next(iterator, None)
                    if funct is None or funct.type != "INT":
                        raise ParseError(
                            f"Expected argument for {token.value} instruction."
                        )
                    opcode += int(funct, 0)
                data += bytes([opcode])
                pointer += 1
                if token.value in Assembler.ARGS:
                    for size in Assembler.ARGS[token.value]:
                        arg = next(iterator, None)
                        if arg is None:
                            raise ParseError(
                                f"Expected argument for {token.value} instruction."
                            )
                        if arg.type == "INT":
                            value = int(arg, 0)
                        elif arg.type == "LABEL":
                            if arg.value not in labels:
                                raise ParseError(
                                    f"Cannot jump to unused label: {arg.value}"
                                )
                            if labels[arg.value] is None:  # label not defined yet
                                value = 0xADDE  # placeholder for forward jumps
                                jumps[pointer] = arg.value
                            else:
                                value = labels[arg.value]
                        else:
                            raise ParseError(
                                f"Invalid argument type for {token.value} instruction."
                            )
                        try:
                            data += value.to_bytes(size, "little")
                            pointer += size
                        except OverflowError as exception:
                            raise ParseError(
                                f"Argument {arg.value} is too large, expected {size} bytes."
                            ) from exception
            else:
                raise ParseError(f"Unexpected token: {token.value}")
            token = next(iterator, None)

        for jump, label in jumps.items():
            addr = labels[label]
            data[jump : jump + 2] = addr.to_bytes(2, "little")

        return data


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile", default=None, metavar="file", type=str)
    parser.add_argument("-o", type=str, metavar="file", dest="outfile")
    args = parser.parse_args()

    with open(args.infile, "r") as sourcefile:
        source = sourcefile.read()
    binary = Assembler.assemble(source)
    if args.outfile:
        with open(args.outfile, "wb") as progfile:
            progfile.write(binary)
    else:
        sys.stdout.buffer.write(binary)
