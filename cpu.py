"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [None] * 256

        self.reg = [None] * 8
        self.reg[7] = 0xF4
        # pc: program counter
        self.pc = 0

        self.HLT  = 0b00000001
        self.LDI  = 0b10000010
        self.PRN  = 0b01000111
        self.MUL  = 0b10100010
        self.PUSH = 0b01000101
        self.POP  = 0b01000110
        self.CALL = 0b01010000
        self.RET  = 0b00010001

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

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
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
        running = True

        while running:
            # ir: instruction register
            ir = self.ram_read(self.pc)
            print('ir:', bin(ir))
            num_operands = ir >> 6  # extract # of operands

            if ir == self.LDI: # LDI R0,8
                # put 8 in register 0
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                self.reg[operand_a] = operand_b

            if ir == self.PRN: # PRN R0
                # print register 0
                operand_a = self.ram_read(self.pc + 1)
                print(self.reg[operand_a])

            if ir == self.MUL:
                operand_a = self.ram_read(self.pc + 1)
                operand_b = self.ram_read(self.pc + 2)
                self.reg[operand_a] *= self.reg[operand_b]

            # Push the value in the given register on the stack.
            # sp: stack pointer
            if ir == self.PUSH:
                # decrement stack pointer
                self.reg[7] -= 1
                # look ahead in ram to get given register number
                register_number = self.ram_read(self.pc + 1)
                # get value from register 
                number_to_push = self.reg[register_number]
                # copy into stack
                sp = self.reg[7]
                self.ram[sp] = number_to_push

            # Pop the value at the top of the stack into the given register
            # sp: stack pointer
            if ir == self.POP:
                sp = self.reg[7]
                # get value of last position of sp
                popped_value = self.ram[sp]
                # get register number
                register_number = self.ram[self.pc + 1]
                # copy into the register
                self.reg[register_number] = popped_value
                # increment sp
                self.reg[7] += 1


            if ir == self.CALL:
                # remember where to return to
                ## get address of next instruction,
                ## the one we would run if we didn't have CALL
                ## It's at pc + 2
                next_instruction_address = self.ram[self.pc + 2]
                ## push onto the stack
                ### decrement stack pointer sp
                self.reg[7] -= 1
                ### put on stack at the sp
                sp = self.reg[7]
                self.ram[sp] = next_instruction_address


                # call the subroutine (function)
                ## get address from given register
                ### get the register number
                reg_address = self.ram[self.pc + 1]
                ### look inside that register
                address_to_jump_to = self.reg[reg_address]
                ## set pc to that address
                self.pc = address_to_jump_to
                

            if ir == self.RET:
                # pop value from top of stack
                ## use sp to get value
                sp = self.reg[7]
                return_address = self.ram[sp]
                ## increment sp
                self.reg[7] += 1

                # set pc to that value
                self.pc = return_address


            if ir == self.HLT:
                running = False


            # bit shifting, bit masking
            command_sets_pc_directly = ((ir >> 4) & 0b0001) == 1

            if not command_sets_pc_directly:
                self.pc += num_operands + 1  # + 1 for the command itself

