"""CPU functionality."""

import sys

HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
ADD  = 0b10100000 
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""


        self.ram = [None] * 256

        self.reg = [None] * 8

        # stack pointer
        self.reg[7] = 0xF4

        # pc: program counter
        self.pc = 0
        self.running = True

        # equal bit
        self.equal = False

        self.branchtable = {}
        self.branchtable[HLT] = self.hlt
        self.branchtable[LDI] = self.ldi
        self.branchtable[PRN] = self.prn
        self.branchtable[PUSH] = self.push
        self.branchtable[POP] = self.pop
        self.branchtable[CALL] = self.call
        self.branchtable[RET] = self.ret
        self.branchtable[JMP] = self.jmp
        self.branchtable[JEQ] = self.jeq
        self.branchtable[JNE] = self.jne


    def hlt(self, _, __):
        self.running = False


    def ldi(self, operand_a, operand_b):
        # put 8 in register 0
        self.reg[operand_a] = operand_b


    def prn(self, operand_a, _):
        # PRN R0
        # print register 0
        print(self.reg[operand_a])


    def push(self, operand_a, _):
        # Push the value in the given register on the stack.
        # sp: stack pointer
        # decrement stack pointer
        # look ahead in ram to get given register number
        # get value from register 
        # copy into stack
        self.reg[7] -= 1
        sp = self.reg[7]

        # operand_a is address of register holding the value
        value = self.reg[operand_a]

        # put into memory
        self.ram[sp] = value

        # shorter version
        # self.ram[sp] = self.reg[operand_a]


    def pop(self, operand_a, _):
        # Pop the value at the top of the stack into the given register
        # sp: stack pointer
        # get value of last position of sp
        sp = self.reg[7]
        value = self.ram[sp]
        # copy into the register
        self.reg[operand_a] = value
        # increment sp
        self.reg[7] += 1


    def call(self, operand_a, _):
        # decrement sp
        self.reg[7] -= 1
        sp = self.reg[7]
        # get address for RET
        return_address = self.pc + 2
        # put in memory
        self.ram[sp] = return_address

        destination_address = self.reg[operand_a]
        self.pc = destination_address


    # pop value from top of stack
    def ret(self, _, __):
        # pop from stack
        sp = self.reg[7]
        value = self.ram[sp]
        # set pc to value popped from stack
        self.pc = value
        # increment sp
        self.reg[7] += 1


    # Jump to the given register
    def jmp(self, operand_a, _):
        self.pc = self.reg[operand_a]


    # If equal flag is set (true), jump to the address stored in the given register.
    def jeq(self, operand_a, _):
        if self.equal == True:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2


    # If equal flag is false jump to the address stored in the given register.
    def jne(self, operand_a, _):
        if self.equal == False:
            self.pc = self.reg[operand_a]
        else:
            self.pc += 2


    # accept the address to read and return the value stored there
    # mar: Memory address register, the address that is being read
    def ram_read(self, mar):
        return self.ram[mar]

    # accept a value to write, and the address to write it to.
    # mar: Memory address register, the address that is being read
    # mdr: Memory data register, the data that is being written
    def ram_write(self, mar, mdr):
        self.ram[mar] = mdr

    def load(self):
        """Load a program into memory."""

        if len(sys.argv) < 2:
            print("Need a file to open.")
            sys.exit()

        address = 0

        try:
            with open(sys.argv[1]) as file:
                for line in file:
                    comment_split = line.split("#")
                    possible_num = comment_split[0]

                    if possible_num == '':
                        continue

                    if possible_num[0] == '1' or possible_num[0] == '0':
                        num = possible_num[:8]
                        self.ram[address] = int(num, 2)
                        address += 1
        except FileNotFoundError:
            print("File not found")
            sys.exit()


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == MUL:
            self.reg[reg_a] *= self.reg[reg_b]

        elif op == ADD:
            self.reg[reg_a] += self.reg[reg_b]

        elif op == CMP:
            if self.reg[reg_a] == self.reg[reg_b]:
                self.equal = True
            else:
                self.equal = False

        else:
            raise Exception("Unsupported ALU operation")


    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            #self.fl,
            #self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        while self.running:
            # ir: instruction register
            ir = self.ram_read(self.pc)

            # extract operands
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            # update program counter
            # look at first two bits of instruction
            # if the command sets the PC directly, then don't
            sets_pc_directly = (ir >> 4) & 0b0001

            if not sets_pc_directly:
                self.pc += 1 + (ir >> 6)

            # if ir is an ALU command, send to ALU
            is_alu_command = ((ir >> 5) & 0b001) == 1

            if is_alu_command:
                self.alu(ir, operand_a, operand_b)

            else:
                self.branchtable[ir](operand_a, operand_b)

