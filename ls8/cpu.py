"""CPU functionality."""
import sys
import time

# branch table lookups
ADD = 0b10100000
AND = 0b10101000
CALL = 0b01010000
CMP = 0b10100111
# DEC = 0b01100110
DIV = 0b10100011
HLT = 0b00000001
# INC = 0b01100101
# INT = 0b01010010
IRET = 0b00010011
JEQ = 0b01010101
JGE = 0b01011010
JGT = 0b01010111
JLE = 0b01011001
JLT = 0b01011000
JMP = 0b01010100
JNE = 0b01010110
# LD = 0b10000011
LDI = 0b10000010
MOD = 0b10100100
MUL = 0b10100010
# NOP = 0b00000000
NOT = 0b01101001
OR = 0b10101010
POP = 0b01000110
PRA = 0b01001000
PRN = 0b01000111
PUSH = 0b01000101
RET = 0b00010001
SHL = 0b10101100
SHR = 0b10101101
ST = 0b10000100
SUB = 0b10100001
XOR = 0b10101011

IM = 5
IS = 6

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0, 0, 0, 0, 0, 0, 0, 0xF4]
        self.pc  = 0
        self.fl = 0
        self.sp = self.reg[7]
        self.running = False
        self.ie = True # interrupts enabled flag
        
        self.branch_table = {}
        self.branch_table[ADD] = self.handle_ADD
        self.branch_table[AND] = self.handle_AND
        self.branch_table[CALL] = self.handle_CALL
        self.branch_table[CMP] = self.handle_CMP
        self.branch_table[DIV] = self.handle_DIV
        self.branch_table[HLT] = self.handle_HLT
        self.branch_table[IRET] = self.handle_IRET
        self.branch_table[JEQ] = self.handle_JEQ
        self.branch_table[JGE] = self.handle_JGE
        self.branch_table[JGT] = self.handle_JGT
        self.branch_table[JLE] = self.handle_JLE
        self.branch_table[JLT] = self.handle_JLT
        self.branch_table[JMP] = self.handle_JMP
        self.branch_table[JNE] = self.handle_JNE
        self.branch_table[LDI] = self.handle_LDI
        self.branch_table[MOD] = self.handle_MOD
        self.branch_table[MUL] = self.handle_MUL
        self.branch_table[NOT] = self.handle_NOT
        self.branch_table[OR] = self.handle_OR
        self.branch_table[POP] = self.handle_POP
        self.branch_table[PRA] = self.handle_PRA
        self.branch_table[PRN] = self.handle_PRN
        self.branch_table[PUSH] = self.handle_PUSH
        self.branch_table[RET] = self.handle_RET
        self.branch_table[SHL] = self.handle_SHL
        self.branch_table[SHR] = self.handle_SHR
        self.branch_table[ST] = self.handle_ST
        self.branch_table[SUB] = self.handle_SUB
        self.branch_table[XOR] = self.handle_XOR
        
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

        elif op == 'AND':
            self.reg[reg_a] &= self.reg[reg_b]
        
        elif op == 'CMP':
            self.flag = 0
            val_a = self.reg[reg_a]
            val_b = self.reg[reg_b]
            
            if val_a == val_b:
                self.flag = self.flag | 1 << 0
            
            elif val_a < val_b:
                self.flag = self.flag | 1 << 1
            
            else:  # val_a > val_b:
                self.flag = self.flag | 1 << 2        
        
        elif op == 'DIV':
            self.reg[reg_a] //= self.reg[reg_b]
        
        elif op == 'MOD':
            self.reg[reg_a] %= self.reg[reg_b]
        
        elif op == 'MUL':
            self.reg[reg_a] *= self.reg[reg_b]
            
        elif op == 'NOT':
            self.reg[reg_a] = (1 << 8) - 1 - self.reg[reg_a]
        
        elif op == 'OR':
            self.reg[reg_a] |= self.reg[reg_b]
        
        elif op == 'XOR':
            self.reg[reg_a] ^= self.reg[reg_b]   
        
        elif op == 'SHL':
            self.reg[reg_a] = self.reg[reg_a] << self.reg[reg_b]
        
        elif op == 'SHR':
            self.reg[reg_a] = self.reg[reg_a] >> self.reg[reg_b]
        
        elif op == 'SUB':
            self.reg[reg_a] -= self.reg[reg_b]   
            
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """
        print(f"TRACE: %02X %02X %02X | %02X %02X %02X |" % (
            self.pc,
            self.fl,
            self.ie,
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
    
    # instruction handlers
    def handle_ADD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('ADD', reg_a, reg_b)
        self.pc += 3
  
    def handle_AND(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('AND', reg_a, reg_b)
        self.pc += 3

    def handle_CALL(self):
        self.sp -= 1
        self.ram_write(self.pc + 2, self.sp)
        r = self.ram_read(self.pc + 1)
        self.pc = self.reg[r]
    
    def handle_CMP(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('CMP', reg_a, reg_b)
        self.pc += 3
    
    def handle_DIV(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('DIV', reg_a, reg_b)
        self.pc += 3
    
    def handle_HLT(self):
        self.running = False
    
    def handle_IRET(self):
        # pop registers R6-R0 off the stack
        for i in range(6, -1, -1):
            self.reg[i] = self.ram_read(self.sp)
            self.sp += 1
        
        # pop FL register off the stack
        self.fl = self.ram_read(self.sp)
        self.sp += 1
        
        # pop PC register off the stack
        self.pc = self.ram_read(self.sp)
        self.sp += 1
        
        # re-enable interrupts
        self.ie = True
    
    def handle_JEQ(self):
        r = self.ram_read(self.pc + 1)
        
        if self.flag == 0b00000001:
            self.pc = self.reg[r]
        
        else:
            self.pc += 2
    
    def handle_JGE(self):
        r = self.ram_read(self.pc + 1)
        
        if self.flag == 0b00000010 or self.flag == 0b00000001:
            self.pc = self.reg[r]
        
        else:
            self.pc += 2
    
    def handle_JGT(self):
        r = self.ram_read(self.pc + 1)
        
        if self.flag == 0b00000010:
            self.pc = self.reg[r]
        
        else:
            self.pc += 2
    
    def handle_JLE(self):
        r = self.ram_read(self.pc + 1)
        
        if self.flag == 0b00000100 or self.flag == 0b00000001:
            self.pc = self.reg[r]
        
        else:
            self.pc += 2
    
    def handle_JLT(self):
        r = self.ram_read(self.pc + 1)
        
        if self.flag == 0b00000100:
            self.pc = self.reg[r]
        
        else:
            self.pc += 2
    
    def handle_JMP(self):
        r = self.ram_read(self.pc + 1)
        self.pc = self.reg[r]

    def handle_JNE(self):
        r = self.ram_read(self.pc + 1)
        
        if self.flag != 0b00000001:
            self.pc = self.reg[r]
        
        else:
            self.pc += 2
    
    def handle_LDI(self):
        r = self.ram_read(self.pc + 1)
        value = self.ram_read(self.pc + 2)
        self.reg[r] = value
        self.pc += 3
    
    def handle_MOD(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('MOD', reg_a, reg_b)
        self.pc += 3
    
    def handle_MUL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('MUL', reg_a, reg_b)
        self.pc += 3
        
    def handle_NOT(self):
        reg_a = self.ram_read(self.pc + 1)
        self.alu('NOT', reg_a, None)
        self.pc += 2
    
    def handle_OR(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('OR', reg_a, reg_b)
        self.pc += 3
    
    def handle_POP(self):
        r = self.ram_read(self.pc + 1)
        value = self.ram_read(self.sp)
        self.reg[r] = value
        self.sp += 1
        self.pc += 2
    
    def handle_PRA(self):
        r = self.ram_read(self.pc + 1)
        value = self.reg[r]
        print(chr(value))
        self.pc += 2
    
    def handle_PRN(self):
        r = self.ram_read(self.pc + 1)
        print(self.reg[r])
        self.pc += 2
        
    def handle_PUSH(self):
        self.sp -= 1
        r = self.ram_read(self.pc + 1)
        self.ram_write(self.reg[r], self.sp)
        self.pc += 2
    
    def handle_RET(self):
        self.pc = self.ram_read(self.sp)
        self.sp += 1
        
    def handle_SHL(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('SHL', reg_a, reg_b)
        self.pc += 3
    
    def handle_SHR(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('SHR', reg_a, reg_b)
        self.pc += 3
        
    def handle_ST(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        value = self.reg[reg_b]
        self.ram_write(value, self.reg[reg_a])
        self.pc += 3
        
    def handle_SUB(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('SUB', reg_a, reg_b)
        self.pc += 3
    
    def handle_XOR(self):
        reg_a = self.ram_read(self.pc + 1)
        reg_b = self.ram_read(self.pc + 2)
        self.alu('XOR', reg_a, reg_b)
        self.pc += 3
    
    # interrupt handler
    def handle_interrupt(self, i):
        # disable further interrupts
        self.ie = False
        
        # clear the bit in the IS register
        self.reg[IS] = self.reg[IS] & ~(1 << i)
        
        # push the PC register onto the stack
        self.sp -= 1
        self.ram_write(self.pc, self.sp)
        
        # push the FL register onto the stack
        self.sp -= 1
        self.ram_write(self.pc, self.fl)
        
        # push regsiters R0-R6 onto the stack
        for j in range(7):
            self.sp -= 1
            self.ram_write(self.reg[j], self.sp)
        
        # lookup the handler in the interrupt vector table
        # and set the PC to it
        self.pc = self.ram_read(0xF8 + i)
                        
    def run(self):
        """Run the CPU."""
        self.running = True
        start_time = time.time()
        
        while self.running:
            elapsed_time = time.time() - start_time
            
            # timer interrupt
            if elapsed_time >= 1:
                start_time = time.time()
                
                # set 0 bit
                self.reg[IS] = self.reg[IS] | 1 << 0
                
            if self.ie:
                # bitwise AND the IM and IS registers
                masked_interrupts = self.reg[IM] & self.reg[IS]
                
                # check each bit from 0 to 7 to see if it is set 
                for i in range(8):
                    interrupt_happened = ((masked_interrupts >> i) & 1) == 1
                    
                    if interrupt_happened:
                        self.handle_interrupt(i)
                        break
            
            ir = self.ram_read(self.pc)
            
            if ir in self.branch_table:
                self.branch_table[ir]()
            
            else:
                print('invalid instruction')
                self.trace()
                break