"""CPU functionality."""
import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.pc  = 0
        self.running = False

    def load(self, filename):
        """Load a program into memory."""

        address = 0
        
        program = []
        
        try:
            with open(filename) as f:
                for line in f:
                    comment_split = line.split('#')
                    maybe_bin_num = comment_split[0]
                    
                    try:
                        x = int(maybe_bin_num, 2)
                        program.append(x)
                    
                    except:
                        continue
                    
        except FileNotFoundError:
            print('file not found')
            
        for instruction in program:
            self.ram[address] = instruction
            address += 1


    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        #elif op == "SUB": etc
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
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

    def ram_read(self, MAR):
        return self.ram[MAR]
    
    def ram_write(self, MDR, MAR):
        self.ram[MAR] = MDR

    def run(self):
        """Run the CPU."""
        self.running = True
        
        while self.running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            
            self.execute_instruction(ir, operand_a, operand_b)
                
    def execute_instruction(self, ir, operand_a, operand_b):
        if ir == HLT:
            self.running = False
        elif ir == LDI:
            self.reg[operand_a] = operand_b
            self.pc += 2
        elif ir == PRN:
            print(self.reg[operand_a])
            self.pc += 1
        elif ir == MUL:
            self.alu('MUL', operand_a, operand_b)
            self.pc += 2
        else:
            print('invalid instruction')
            pass
            
        self.pc += 1
    