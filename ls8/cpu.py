"""CPU functionality."""

import sys


class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.register = [0] * 8
        self.pc = 0
        self.sp = 7  # Stack Pointer

    def ram_read(self, address):
        return self.ram[address]

    def ram_write(self, address, value):
        self.ram[address] = value

    def load(self, filename):
        """Load a program into memory."""
        print("Loading", filename)

        try:
            address = 0

            # open file
            with open(filename) as f:
                for line in f:
                    # ignore the hashtag
                    comment_split = line.split('#')
                    # .strip() will get rid of any spaces
                    num = comment_split[0].strip()
                    if num == "":
                        continue

                    value = int(num, 2)

                    self.ram_write(address, value)

                    address += 1
        except FileNotFoundError:
            print(f"{sys.arg[0]}: {filename} not found")

        # address = 0

        # # For now, we've just hardcoded a program:

        # program = [
        #     # From print8.ls8
        #     0b10000010, # LDI R0,8
        #     0b00000000,
        #     0b00001000,
        #     0b01000111, # PRN R0
        #     0b00000000,
        #     0b00000001, # HLT
        # ]

        # for instruction in program:
        #     self.ram[address] = instruction
        #     address += 1

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.register[reg_a] += self.register[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.register[reg_a] *= self.register[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""
        LDI = 0b10000010
        PRN = 0b01000111
        HLT = 0b00000001
        MUL = 0b10100010
        POP = 0b01000110
        PUSH = 0b01000101

        running = True

        while running:
            # reads the memory address that stored in register PC
            ir = self.ram_read(self.pc)
            SP = self.sp

            # Use ram_read to read the bytes at PC + 1 and PC + 2 from ram variables operand_a and operand_b
            # which are equivalent to each other
            # operand_a: 00000000 --> R0 (register at index 0 in memory) is equal to
            # operand_b: 00001000 --> The value 8

            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)

            if ir == LDI:
                self.register[operand_a] = operand_b
                self.pc += 3

            elif ir == MUL:  # --> Multiply the values  using ALU
                # use ALU --> what arguments does it take
                self.alu("MUL", operand_a, operand_b)
                self.pc += 3

            # --> /Print to the console the decimal integer value that is stored in the given register.
            elif ir == PRN:
                reg = self.ram_read(self.pc + 1)
                self.register[reg]
                print(f"{self.register[reg]} in now in the register")
                self.pc += 2

            elif ir == HLT:  # Halt --> halt operations
                print("Operations have been halted")
                running = False
                self.pc += 1

            elif ir == PUSH:
                # 1st argument
                reg = operand_a
                # grab the values we are putting on the register
                val = self.register[reg]
                # Decrement the SP
                self.register[SP] -= 1
                # Copy and write the value in given register to address pointed to by SP
                self.ram_write(self.register[SP], val)
                # Increment PC by 2
                self.pc += 2

            elif ir == POP:
                # reg is 1st argument
                reg = operand_a
                # grab the value we are putting in the register
                val = self.ram[self.register[SP]]
                self.register[reg] = val
                # Increment SP
                self.register[SP] += 1
                self.pc += 2

            else:
                print(f"Error, unkown command {ir}")
                sys.exit(1)
