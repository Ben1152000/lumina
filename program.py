from collections import deque

class ProgramError(Exception):
    pass

class Program:

    def __init__(self, name: str, data: bytes, locked: bool = False, debug: bool = False):
        self.name = name
        self.data = data
        self.locked = locked
        self.debug = debug

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
            0xc: self.swap,
            0xd: self.dump,
            0xe: self.yield_,
            0xf: self.twobyte,
        }
        
        self.reset()

    def reset(self):
        self.stack = deque()
        self.pc = 0
    
    # execute current instruction
    def step(self):
        if (self.debug):
            print(f"\tpc: {self.pc}")
            print(f"\tstack: {self.stack}")
        instruction = self.data[self.pc]
        opcode = (instruction & 0xf0) >> 4
        if opcode not in self.OPCODES:
            raise ProgramError(f"Invalid opcode: {opcode}")
        self.OPCODES[opcode]()
        self.pc += 1

    def execute(self):
        while True:
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
        if not len(self.stack) > arg:
            raise ProgramError(f"Cannot peek beyond stack index.")
        if arg == 0:
            self.stack.popleft()
        else:
            del self.stack[arg]
    
    def PUSH(self):
        if (self.debug):
            print('PUSH')
        instruction = self.data[self.pc]
        arg = instruction & 0x0f
        if arg != 0:
            self.pc += 1
            arg = self.data[self.pc]
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

    def JMP(self):
        if (self.debug):
            print('JMP')
        self.pc = self.read_short() - 1

    def JZ(self):
        if (self.debug):
            print('JZ')
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        if self.stack.popleft() == 0:
            self.pc = self.read_short() - 1

    def JNZ(self):
        if (self.debug):
            print('JNZ')
        if len(self.stack) < 1:
            raise ProgramError(f"Not enough items in stack.")
        if self.stack.popleft() != 0:
            self.pc = self.read_short() - 1

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
        self.stack.appendleft(self.stack.popleft() + self.stack.popleft())

    def SUB(self):
        if (self.debug):
            print('\tSUB')
        self.stack.appendleft(self.stack.popleft() - self.stack.popleft())

    def DIV(self):
        if (self.debug):
            print('\tDIV')
        self.stack.appendleft(self.stack.popleft() // self.stack.popleft())

    def MUL(self):
        if (self.debug):
            print('\tMUL')
        self.stack.appendleft(self.stack.popleft() * self.stack.popleft())

    def MOD(self):
        if (self.debug):
            print('\tMOD')
        self.stack.appendleft(self.stack.popleft() % self.stack.popleft())

    def AND(self):
        if (self.debug):
            print('\tAND')
        self.stack.appendleft(self.stack.popleft() & self.stack.popleft())

    def OR(self):
        if (self.debug):
            print('\tOR')
        self.stack.appendleft(self.stack.popleft() | self.stack.popleft())

    def XOR(self):
        if (self.debug):
            print('\tXOR')
        self.stack.appendleft(self.stack.popleft() ^ self.stack.popleft())

    def GT(self):
        if (self.debug):
            print('\tGT')
        self.stack.appendleft(self.stack.popleft() > self.stack.popleft())

    def GTE(self):
        if (self.debug):
            print('\tGTE')
        self.stack.appendleft(self.stack.popleft() >= self.stack.popleft())

    def LT(self):
        if (self.debug):
            print('\tLT')
        self.stack.appendleft(self.stack.popleft() < self.stack.popleft())

    def LTE(self):
        if (self.debug):
            print('\tLTE')
        self.stack.appendleft(self.stack.popleft() <= self.stack.popleft())

    def EQ(self):
        if (self.debug):
            print('\tEQ')
        self.stack.appendleft(self.stack.popleft() == self.stack.popleft())

    def NEQ(self):
        if (self.debug):
            print('\tNEQ')
        self.stack.appendleft(self.stack.popleft() != self.stack.popleft())

    def SHL(self):
        if (self.debug):
            print('\tSHL')
        self.stack.appendleft(self.stack.popleft() << self.stack.popleft())

    def SHR(self):
        if (self.debug):
            print('\tSHR')
        self.stack.appendleft(self.stack.popleft() >> self.stack.popleft())

    def get_length(self):
        if (self.debug):
            print('\tget_length')
        self.stack.appendleft(0)

    def get_wall_time(self):
        if (self.debug):
            print('\tget_wall_time')

    def get_precise_time(self):
        if (self.debug):
            print('\tget_precise_time')

    def set_pixel(self):
        if (self.debug):
            print('\tset_pixel')

    def show(self):
        if (self.debug):
            print('\tshow')

    def random_int(self):
        if (self.debug):
            print('\trandom_int')

    def get_pixel(self):
        if (self.debug):
            print('\tget_pixel')

    def set_all_pixels(self):
        if (self.debug):
            print('\tset_all_pixels')

    def swap(self):
        if (self.debug):
            print('\tswap')

    def dump(self):
        if (self.debug):
            print('\tdump')

    def yield_(self):
        if (self.debug):
            print('\tyield_')

    def twobyte(self):
        if (self.debug):
            print('\ttwobyte')



if __name__ == "__main__":
    
    with open('example.bin', 'rb') as binary:
        data = binary.read()
    
    program = Program(
        name = 'example',
        data = data,
        debug = True
    )

    program.execute()