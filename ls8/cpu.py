"""CPU functionality."""
import sys

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.pc  = 0
        self.sp = 7
        self.running = False
        
        self.branch_table = {}
        self.branch_table[HLT] = self.handle_HLT
        self.branch_table[LDI] = self.handle_LDI
        self.branch_table[PRN] = self.handle_PRN
        self.branch_table[MUL] = self.handle_MUL
        self.branch_table[PUSH] = self.handle_PUSH
        self.branch_table[POP] = self.handle_POP

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
    
    def handle_HLT(self, *args):
        self.running = False
    
    def handle_LDI(self, *args):
        self.reg[args[0]] = args[1]
        self.pc += 3
    
    def handle_PRN(self, *args):
        print(self.reg[args[0]])
        self.pc += 2
    
    def handle_MUL(self, *args):
        self.alu('MUL', args[0], args[1])
        self.pc += 3
    
    def handle_PUSH(self, *args):
        self.reg[self.sp] -= 1
        self.ram[self.reg[self.sp]] = self.reg[args[0]]
        self.pc += 2
    
    def handle_POP(self, *args):
        self.reg[args[0]] = self.ram[self.reg[self.sp]]
        self.reg[self.sp] += 1
        self.pc += 2

    def run(self):
        """Run the CPU."""
        self.running = True
        
        while self.running:
            ir = self.ram_read(self.pc)
            operand_a = self.ram_read(self.pc + 1)
            operand_b = self.ram_read(self.pc + 2)
            
            if ir in self.branch_table:
                self.branch_table[ir](operand_a, operand_b)
            else:
                print('invalid instruction')
                self.pc += 1
                pass