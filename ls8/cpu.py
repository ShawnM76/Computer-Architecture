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
        self.flag = [0] * 8

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
                    # Convert binary string to integer
                    value = int(num, 2)
                    # save/write appropriate data to RAM
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
        elif op == "CMP":  # Flags = FL they are internal registers
            # FL 0b00000LGE
            # If register A is greater than registerB, set the Greater-than G flag to 1, otherwise set it to 0.
            if self.register[reg_a] < self.register[reg_b]:
                self.flag[5] = 1  # L
                self.flag[6] = 0  # G
                self.flag[7] = 0  # E

            # If they are equal, set the Equal E flag to 1, other set it to 0.
            # If regA = regB: set Equal [E] flag to 1 (True)
            elif self.register[reg_a] == self.register[reg_b]:
                self.flag[5] = 0  # L
                self.flag[6] = 0  # G
                self.flag[7] = 1  # E

            # If registerA is less than register B, set the Less-than L flag to 1, otherwise 0.
            # If regA > regB: set Greater [G] flag to 1 (true)
            elif self.register[reg_a] > self.register[reg_b]:
                self.flag[5] = 0  # L
                self.flag[6] = 1  # G
                self.flag[7] = 0  # E
            else:
                pass
                # if flag = 0b00000000

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
        ADD = 0b10100000
        POP = 0b01000110
        PUSH = 0b01000101
        CALL = 0b01010000
        RET = 0b00010001
        CMP = 0b10100111
        JMP = 0b01010100
        JEQ = 0b01010101
        JNE = 0b01010110

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

            elif ir == ADD:
                self.alu("ADD", operand_a, operand_b)
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
                # reg == 1st argument
                reg = operand_a
                # grab the values we are putting on the reg
                val = self.register[reg]
                # Decrement the SP
                self.register[SP] -= 1
                # Copy/write value in given register to address pointed to by SP
                self.ram_write(self.register[SP], val)
                # Increment PC by 2
                self.pc += 2

            elif ir == POP:
                # reg == 1st argument
                reg = operand_a
                # grab the values we are putting on the register
                val = self.ram[self.register[SP]]
                self.register[reg] = val
                # Increment SP
                self.register[SP] += 1
                # Increment PC by 2
                self.pc += 2

            elif ir == CALL:
                # address of instruction directly after CALL is pushed into stack
                val = self.pc + 2
                # PC is set to the address stored in the given register
                reg_index = operand_a

                subroutine_address = self.register[reg_index]
                self.register[SP] -= 1
                self.ram[self.register[SP]] = val

                # jump to that location in RAM --> execute the 1st instruction in the subroutine
                self.pc = subroutine_address

            elif ir == RET:
                # return for the subroutine
                return_address = self.register[SP]
                # Pop the value from the top of the stack and store it in the PC
                self.pc = self.ram_read(return_address)
                # Increment the SP by 1
                self.register[SP] += 1

            elif ir == CMP:
                # Compare 2 values (2 arguments: regA & regB)
                # Saw is cheatsheet this can be done in ALU. Use ALU here
                self.alu("CMP", operand_a, operand_b)
                # print("Register in CMP", self.reg)
                # print(f"Flag: {self.flag}")
                # print("--------------------")

                self.pc += 3

            elif ir == JMP:
                # Jump to the address stored in the given register
                print(f'JMP Register Address {operand_a}')
                # set the PC to the address stored in the given register
                self.pc = self.register[operand_a]
                print(f'JMP PC address {self.pc}')
                # print("--------------------")
            elif ir == JEQ:

                # print(f"CMP: {CMP}, E: {E}")
                # if [E] flag is true:
                if self.flag[7] == 1:
                    self.pc = self.register[operand_a]
                    # print(f'JEQ PC address {self.pc}')
                else:
                    print("Else statement")
                    self.pc += 2

            elif ir == JNE:
                # if [E] flag is clear
                if self.flag[7] != 1:
                    # jump to the address stored in the given register
                    self.pc = self.register[operand_a]
                    print(f'JNE PC address {self.pc}')
                else:
                    self.pc += 2

            else:
                print(f"Error, unknown command {ir}")
                sys.exit(1)
