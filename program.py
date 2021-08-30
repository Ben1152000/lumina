from collections import deque
from pixels import Pixels
from time import time, sleep
import math

class ProgramError(Exception):
    pass

class Program:

    def __init__(self, name: str, data: bytes, debug: bool = False):
        self.name = name
        self.data = data
        self.debug = debug

        self.pixels = Pixels()

        self.OPCODES = {
            0x0: self.POP,
            0x1: self.PUSH,
            0x2: self.PEEK,
            0x3: self.PUSHI,
            0x4: self.JMP,
            0x5: self.JZ,
            0x6: self.JNZ,
            0x7: self.UNARY,
            0x8: self.BINARY,
            0x9: self.FLOAT,
            0xe: self.USER,
            0xf: self.SPECIAL,
        }

        self.UNARY_FUNCTS = {
            0x0: self.INC,
            0x1: self.DEC,
            0x2: self.NOT,
            0x3: self.NEG,
            0x4: self.SHL8,
            0x5: self.SHR8,
        }

        self.BINARY_FUNCTS = {
            0x0: self.ADD,
            0x1: self.SUB,
            0x2: self.DIV,
            0x3: self.MUL,
            0x4: self.MOD,
            0x5: self.AND,
            0x6: self.OR,
            0x7: self.XOR,
            0x8: self.GT,
            0x9: self.GTE,
            0xa: self.LT,
            0xb: self.LTE,
            0xc: self.EQ,
            0xd: self.NEQ,
            0xe: self.SHL,
            0xf: self.SHR,
        }

        self.FLOAT_FUNCTS = {
            0x0: self.FLOOR,
            0x1: self.CEIL,
            0x2: self.SIN,
            0x3: self.COS,
            0xf: self.FDIV,
        }

        self.USER_FUNCTS = {
            0x0: self.get_length,
            0x1: self.get_wall_time,
            0x2: self.get_precise_time,
            0x3: self.set_pixel,
            0x4: self.show,
            0x5: self.random_int,
            0x6: self.get_pixel,
            0x7: self.set_all_pixels,
        }

        self.SPECIAL_FUNCTS = {
            0x9: self.sleep,
            0xa: self.exit,
            0xb: self.error,
            0xc: self.swap,
            0xd: self.dump,
            0xe: self.yield_,
            0xf: self.twobyte,
        }
        
        self.reset()

    def reset(self):
        self.stack = deque()
        self.pc = 0
        self.running = True
    
    # execute current instruction
    def step(self):
        instruction = self.data[self.pc]
        opcode = (instruction & 0xf0) >> 4
        if opcode not in self.OPCODES:
            raise ProgramError(f"Invalid opcode: {opcode}")
        if (self.debug):
            print(f"\tpc: {self.pc} ({hex(self.pc)})")
            print(f"\tinst: {hex(instruction)}")
            data = self.data[self.pc : self.pc + 4]
            print(f"\tdata: {' '.join([hex(datum) for datum in data])}")
            print(f"\tstack: {self.stack}")
        self.OPCODES[opcode]()
        self.pc += 1
        if not self.pc < len(self.data):
            self.running = False

    def execute(self):
        while self.running:
            self.step()
    
    # read byte from data
    def read_byte(self):
        self.pc += 1
        if not self.pc < len(self.data):
            raise ProgramError("Unexpected EoF, byte requested.")
        return self.data[self.pc]

    # read short from data
    def read_short(self):
        return self.read_byte() + (self.read_byte() << 8)

    # read word from data
    def read_word(self):
        return self.read_byte() \
            + (self.read_byte() << 8) \
            + (self.read_byte() << 16) \
            + (self.read_byte() << 24)

    def POP(self):
        if (self.debug):
            print('POP')
        instruction = self.data[self.pc]
        arg = instruction & 0x0f
        if len(self.stack) < arg:
            raise ProgramError(f"Cannot pop beyond stack index.")
        for i in range(arg):
            del self.stack[0]
    
    def PUSH(self):
        if (self.debug):
            print('PUSH')
        instruction = self.data[self.pc]
        arg = instruction & 0x0f
        if arg != 0:
            arg = self.read_byte()
        self.stack.appendleft(arg)

    def PEEK(self):
        if (self.debug):
            print('PEEK')
        instruction = self.data[self.pc]
        arg = instruction & 0x0f
        if not len(self.stack) > arg:
            raise ProgramError(f"Cannot peek beyond stack index.")
        val = self.stack[arg]
        self.stack.appendleft(val)

    def PUSHI(self):
        if (self.debug):
            print('PUSHI')
        instruction = self.data[self.pc]
        arg = instruction & 0x0f
        if arg != 0:
            arg = self.read_word()
        self.stack.appendleft(arg)

    def JMP(self):
        if (self.debug):
            print('JMP')
        self.pc = self.read_short() - 1

    def JZ(self):
        if (self.debug):
            print('JZ')
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        if self.stack[0] == 0:
            self.pc = self.read_short() - 1
        else:
            self.pc += 2

    def JNZ(self):
        if (self.debug):
            print('JNZ')
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        if self.stack[0] != 0:
            self.pc = self.read_short() - 1
        else:
            self.pc += 2

    def UNARY(self):
        if (self.debug):
            print('UNARY')
        instruction = self.data[self.pc]
        funct = instruction & 0x0f
        if funct not in self.UNARY_FUNCTS:
            raise ProgramError(f"Invalid unary funct: {funct}")
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        self.UNARY_FUNCTS[funct]()

    def BINARY(self):
        if (self.debug):
            print('BINARY')
        instruction = self.data[self.pc]
        funct = instruction & 0x0f
        if funct not in self.BINARY_FUNCTS:
            raise ProgramError(f"Invalid binary funct: {funct}")
        if len(self.stack) < 2:
            raise ProgramError(f"Not enough items in stack.")
        self.BINARY_FUNCTS[funct]()

    def FLOAT(self):
        if (self.debug):
            print('FLOAT')
        instruction = self.data[self.pc]
        funct = instruction & 0x0f
        if funct not in self.FLOAT_FUNCTS:
            raise ProgramError(f"Invalid binary funct: {funct}")
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        self.FLOAT_FUNCTS[funct]()

    def USER(self):
        if (self.debug):
            print('USER')
        instruction = self.data[self.pc]
        funct = instruction & 0x0f
        if funct not in self.USER_FUNCTS:
            raise ProgramError(f"Invalid user funct: {funct}")
        self.USER_FUNCTS[funct]()

    def SPECIAL(self):
        if (self.debug):
            print('SPECIAL')
        instruction = self.data[self.pc]
        funct = instruction & 0x0f
        if funct not in self.SPECIAL_FUNCTS:
            raise ProgramError(f"Invalid special funct: {funct}")
        self.SPECIAL_FUNCTS[funct]()

    def INC(self):
        if (self.debug):
            print('\tINC')
        self.stack.appendleft(self.stack.popleft() + 1)

    def DEC(self):
        if (self.debug):
            print('\tDEC')
        self.stack.appendleft(self.stack.popleft() - 1)

    def NOT(self):
        if (self.debug):
            print('\tNOT')
        self.stack.appendleft(~self.stack.popleft())

    def NEG(self):
        if (self.debug):
            print('\tNEG')
        self.stack.appendleft(int(not self.stack.popleft()))

    def SHL8(self):
        if (self.debug):
            print('\tSHL8')
        self.stack.appendleft(self.stack.popleft() << 8)

    def SHR8(self):
        if (self.debug):
            print('\tSHR8')
        self.stack.appendleft(self.stack.popleft() >> 8)

    def ADD(self):
        if (self.debug):
            print('\tADD')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left + right)

    def SUB(self):
        if (self.debug):
            print('\tSUB')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left - right)

    def DIV(self):
        if (self.debug):
            print('\tDIV')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left // right)

    def MUL(self):
        if (self.debug):
            print('\tMUL')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left * right)

    def MOD(self):
        if (self.debug):
            print('\tMOD')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left % right)

    def AND(self):
        if (self.debug):
            print('\tAND')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left & right)

    def OR(self):
        if (self.debug):
            print('\tOR')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left | right)

    def XOR(self):
        if (self.debug):
            print('\tXOR')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left ^ right)

    def GT(self):
        if (self.debug):
            print('\tGT')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left > right)

    def GTE(self):
        if (self.debug):
            print('\tGTE')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left >= right)

    def LT(self):
        if (self.debug):
            print('\tLT')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left < right)

    def LTE(self):
        if (self.debug):
            print('\tLTE')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left <= right)

    def EQ(self):
        if (self.debug):
            print('\tEQ')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left == right)

    def NEQ(self):
        if (self.debug):
            print('\tNEQ')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left != right)

    def SHL(self):
        if (self.debug):
            print('\tSHL')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left << right)

    def SHR(self):
        if (self.debug):
            print('\tSHR')
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(left >> right)

    def FLOOR(self):
        if (self.debug):
            print('\tFLOOR')
        self.stack.appendleft(math.floor(self.stack.popleft()))

    def CEIL(self):
        if (self.debug):
            print('\tCEIL')
        self.stack.appendleft(math.ceil(self.stack.popleft()))

    def SIN(self):
        if (self.debug):
            print('\tSIN')
        self.stack.appendleft(math.sin(self.stack.popleft()))

    def COS(self):
        if (self.debug):
            print('\tCOS')
        self.stack.appendleft(math.cos(self.stack.popleft()))

    def FDIV(self):
        if (self.debug):
            print('\tFDIV')
        if len(self.stack) < 2:
            raise ProgramError(f"Not enough items in stack.")
        right = self.stack.popleft()
        left = self.stack.popleft()
        self.stack.appendleft(float(left) / float(right))

    def get_length(self):
        if (self.debug):
            print('\tget_length')
        self.stack.appendleft(self.pixels.length())

    def get_wall_time(self):
        if (self.debug):
            print('\tget_wall_time')
        self.stack.appendleft(int(time()))

    def get_precise_time(self):
        if (self.debug):
            print('\tget_precise_time')
        self.stack.appendleft(int(time() * 1000))

    def set_pixel(self):
        if (self.debug):
            print('\tset_pixel')
        if len(self.stack) < 2:
            raise ProgramError(f"Not enough items in stack.")
        color = self.stack.popleft()
        b = (color & 0xff0000) >> 16
        g = (color & 0x00ff00) >> 8
        r = (color & 0x0000ff)
        i = self.stack[0]
        self.pixels.set_pixel(r, g, b, i)

    def show(self):
        if (self.debug):
            print('\tshow')
        self.pixels.show()

    def random_int(self):
        if (self.debug):
            print('\trandom_int')
        self.stack.appendleft(4)
        # stub

    def get_pixel(self):
        if (self.debug):
            print('\tget_pixel')
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        self.stack.appendleft(self.pixels.get_pixel(self.stack[0]))

    def set_all_pixels(self):
        if (self.debug):
            print('\tset_all_pixels')
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        color = self.stack.popleft()
        b = (color & 0xff0000) >> 16
        g = (color & 0x00ff00) >> 8
        r = (color & 0x0000ff)
        self.pixels.set_all_pixels(r, g, b)

    def sleep(self):
        if (self.debug):
            print('\tsleep')
        sleep(float(self.stack.popleft()) / 1000.0)

    def exit(self):
        if (self.debug):
            print('\texit')
        self.running = False
        self.terminate()

    def error(self):
        if (self.debug):
            print('\terror')
        raise ProgramError(f"An error was raised at instruction {self.pc}")

    def swap(self):
        if (self.debug):
            print('\tswap')
        # stub

    def dump(self):
        if (self.debug):
            print('\tdump')
        print(self.stack)

    def yield_(self):
        if (self.debug):
            print('\tyield_')
        # stub

    def twobyte(self):
        if (self.debug):
            print('\ttwobyte')
        # stub

    def terminate(self):
        self.pixels.shutdown()
        self.reset()

if __name__ == "__main__":
    
    try:
        name = 'rainbow'

        with open(f'programs/{name}.bin', 'rb') as binary:
            data = binary.read()
        
        program = Program(
            name = name,
            data = data,
            debug = False,
        )

        program.running = True

        program.execute()

    except KeyboardInterrupt:
        program.terminate()