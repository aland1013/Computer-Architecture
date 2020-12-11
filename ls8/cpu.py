"""CPU functionality."""
import sys
import time

HLT = 0b00000001
LDI = 0b10000010
PRN = 0b01000111
ADD = 0b10100000
MUL = 0b10100010
PUSH = 0b01000101
POP = 0b01000110
CALL = 0b01010000
RET = 0b00010001
ST = 0b10000100
IRET = 0b00010011
JMP = 0b01010100
PRA = 0b01001000

IM = 5
IS = 6

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.pc  = 0
        self.sp = self.reg[7]
        self.running = False
        self.interrupts_enabled = True
        
        self.branch_table = {}
        self.branch_table[HLT] = self.handle_HLT
        self.branch_table[LDI] = self.handle_LDI
        self.branch_table[PRN] = self.handle_PRN
        self.branch_table[ADD] = self.handle_ADD
        self.branch_table[MUL] = self.handle_MUL
        self.branch_table[PUSH] = self.handle_PUSH
        self.branch_table[POP] = self.handle_POP
        self.branch_table[CALL] = self.handle_CALL
        self.branch_table[RET] = self.handle_RET
        self.branch_table[ST] = self.handle_ST
        self.branch_table[IRET] = self.handle_IRET
        self.branch_table[JMP] = self.handle_JMP
        self.branch_table[PRA] = self.handle_PRA

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
    
    def handle_HLT(self):
        self.running = False
    
    def handle_LDI(self):
        r = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[r] = value
        self.pc += 3
    
    def handle_PRN(self):
        r = self.ram_read(self.pc + 1)
        print(self.reg[r])
        self.pc += 2
    
    def handle_ADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('ADD', reg_a, reg_b)
        self.pc += 3
    
    def handle_MUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3
    
    def handle_PUSH(self):
        self.sp -= 1
        r = self.ram_read(self.pc + 1)
        self.ram_write(self.reg[r], self.sp)
        self.pc += 2
    
    def handle_POP(self):
        r = self.ram_read(self.pc + 1)
        value = self.ram_read(self.sp)
        self.reg[r] = value
        self.sp += 1
        self.pc += 2
    
    def handle_CALL(self):
        self.sp -= 1
        self.ram_write(self.pc + 2, self.sp)
        r = self.ram_read(self.pc + 1)
        self.pc = self.reg[r]
    
    def handle_RET(self):
        self.pc = self.ram_read(self.sp)
        self.sp += 1
        
    def handle_ST(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        value = self.reg[reg_b]
        self.ram_write(value, self.reg[reg_a])
        self.pc += 3
    
    def handle_IRET(self):
        for i in range(6, -1, -1):
            self.reg[i] = self.ram_read(self.sp)
            self.sp += 1
        self.pc = self.ram_read(self.sp)
        self.sp += 1
        self.interrupts_enabled = True
    
    def handle_JMP(self):
        r = self.ram_read(self.pc + 1)
        self.pc = self.reg[r]
        
    def handle_PRA(self):
        r = self.ram_read(self.pc + 1)
        value = self.reg[r]
        print(chr(value))
        self.pc += 2

    def run(self):
        """Run the CPU."""
        self.running = True
        start_time = time.time()
        
        while self.running:
            elapsed_time = time.time() - start_time
            if elapsed_time >= 1:
                start_time = time.time()
                self.reg[IS] = self.reg[IS] | 1 << 0
                
            if self.interrupts_enabled:
                masked_interrupts = self.reg[IM] & self.reg[IS]
                
                for i in range(8):
                    interrupt_happened = ((masked_interrupts >> i) & 1) == 1
                    
                    if interrupt_happened:
                        self.interrupts_enabled = False
                        
                        self.reg[IS] = self.reg[IS] & ~(1 << i)
                        
                        self.sp -= 1
                        self.ram_write(self.pc, self.sp)
                        
                        
                        for j in range(7):
                            self.sp -= 1
                            self.ram_write(self.reg[j], self.sp)
                        
                        self.pc = self.ram_read(0xF8 + i)
                        
                        break
            
            ir = self.ram_read(self.pc)
            
            if ir in self.branch_table:
                self.branch_table[ir]()
            else:
                print('invalid instruction')
                self.trace()
                break