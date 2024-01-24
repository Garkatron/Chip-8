"""
    * ------------------------------------------------------------------------- *
        ! chip8 is a CHIP-8 emulator done in python
        ! This code is based on <https://github.com/danirod/chip8>
        ! Copyright (C) 2024-2025 Matias Gulias Carrascal alias Deus/Garkatron, mail <masitacarg@gmail.com>
    * ------------------------------------------------------------------------- *
        ? This program is free software: you can redistribute it and/or modify
        ? it under the terms of the GNU General Public License as published by
        ? the Free Software Foundation, either version 3 of the License, or
        ? (at your option) any later version.
        
        ? This program is distributed in the hope that it will be useful,
        ? but WITHOUT ANY WARRANTY; without even the implied warranty of
        ? MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
        ? GNU General Public License for more details.
        
        ? You should have received a copy of the GNU General Public License
        ? along with this program.  If not, see <http://www.gnu.org/licenses/>.
    * ------------------------------------------------------------------------- *
"""

# * IMPORTS

from array import array as Array
from ctypes import c_uint16, c_uint8
import random
from Screen import Screen
import pygame
import sys

# * OPCODES MANIPULATION FUNCS

# ? Used to manimulate opcodes with specific structure and extract data
def OPCODE_NNN (opcode)  :  return opcode & 0xFFF         # ? Extracts 12 bits more lower of the opcode (NNN)
def OPCODE_KK  (opcode)  :  return opcode & 0xFF          # ? Extracts 8 bits more lower of the opcode (KK)
def OPCODE_N   (opcode)  :  return opcode & 0xF           # ? Extracts 4 bits more lower of the opcode (N)
def OPCODE_P   (opcode)  :  return opcode >> 12           # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 12 bits right and after applys mask ti to obtain 4 bits more important bits and return the result
def OPCODE_X   (opcode)  :  return (opcode >> 8) & 0xF    # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 8 bits right and after applys mask ti to obtain 4 bits more important bits and return the result
def OPCODE_Y   (opcode)  :  return (opcode >> 4) & 0xF    # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 4 bits right and after applys mask ti to obtain 4 bits less important bits and return the result

def nothing(anything): print("NOTHING: ", anything)

# * MEM MANIPULATION

# ? Set [value] in [buffer] for [size]
def memset (buffer, value: int, size):
    for i in range(size):
        buffer[i] = value

# ? Classes
class Chip8:
    
    def __init__(self) -> None:

        # * Cpu
        self.pc: c_uint16 = c_uint16(200)

        # * Memory
        self.MEM_SIZE : int   = 4096                            # How much mem can handle the chip
        self.memory   : Array = Array('B', [0] * self.MEM_SIZE) # Mem as buffer

        # * Registers22
        self.v : Array  = Array('B', [0] * 16)                  # 16 General purpose registers
        self.i : c_uint16 = c_uint16(0)                             # Special register

        # * Stack
        self.stack : Array  = Array('B', [0] * 16)              # Stack can hold 16 - 16 bit values
        self.sp    : c_uint16 = c_uint16(0)                         # Stack pointer

        # * Timers
        self.delay_timer : c_uint8 = c_uint8(0)
        self.sound_timer : c_uint8 = c_uint8(0)

        # * External
        self.screen: Screen = Screen

        # * Opcodes
        self.opcodes: dict = {
                
            # CLS
            0x0: (self.zero_branch, "0x000"),

            # JP nnn: set program counter to nnn
            0x1: (self.jump_to_address, "JP nnn: set program counter to nnn"),

            # CALL
            0x2: (self.call, "CALL"),

            # SE (skip equal) x, kk: if V[x] == kk -> pc+=2
            0x3: (self.skip_equal, "SE (skip equal) x, kk"),

            # SNE (skip not equal) x, kk if V[x] != kk -> pc+=2
            0x4: (self.skip_not_equal, "SNE (skip not equal) x, kk"),

            # SE x, y: V[x]==V[y] -> pc +=2
            0x5: (self.skip_equal_vx_vy, "SE (skip equal) x, y"),

            # LD x, kk: V[x] = kk
            0x6: (self.load_vx_kk, "LD x, kk"),

            # ADD x, kk: V[x] = V[x] + kk
            0x7: (self.add_vx_kk, "ADD x, kk"),

            0x8: (self.arithmetic_operator, "ALU"),

            # SNE x, y: V[x] != V[y]
            0x9: (self.skip_not_equal_vx_vy, "SNE x, y"),

            # LD i, x: I = nnn 
            0xA: (self.load_i, "LD i, x: I"),

            # JP V0, nnn: pc = V[0] + nnn
            0xB: (self.load_i_v0_nnn, "JP V0, nnn"),

            # RND
            0xC: (self.c_random, "RND"),

            # DRW
            0xD: (self.draw, "DRW D000"),

            # SKP / SKNP
            0xE: (self.skip_key, "SKP/SKNP"),

            #
            0xF: (self.f_branch, "F000"),

        }

        # * Process
        # ? Fill all register in 0x00
        
        memset(self.memory, 0x00, self.MEM_SIZE)
        memset(self.stack, 0x00, 16)
        memset(self.v, 0x00, 16)

    # * Functions

    # ? Aritmetic logih Unit
    def arithmetic_operator (self, opcode):
        
        x = OPCODE_X(opcode)
        y = OPCODE_Y(opcode)

        match OPCODE_N(opcode):

            # 8XY0 LD: set V[x] = V[y]
            case 0: self.v[x] = self.v[y]

            # 8XY1: OR: set V[x] |= V[y]
            case 1: self.v[x] |= self.v[y]

            # 8XY1: AND: set V[x] &= V[y]
            case 2: self.v[x] &= self.v[y]

            # 8XY3: XOR: set V[x] ^= V[y]
            case 3: self.v[x] ^= self.v[y]

            # 8XY4: ADD: set V[x] += V[y] v[15] carry flag
            case 4: 
                self.v[15] = self.v[x] > ((self.v[x]+self.v[y]) & 0xFF)
                self.v[x] += self.v[y]

            # 8XY5: SUB: set v[x] -= V[y] - v[15] is borrow flag
            case 5:
                self.v[15] = (self.v[x] > self.v[y]) & 0xFF
                self.v[x] -= self.v[y]

            # 8XY6: SHR: shifts right V[x], LSB vit goes to V[15]
            case 6:
                self.v[15] = (self.v[x] & 1)
                self.v[x] >>= self.v[y]

            # 8XY7: SUBN: set v[x] -= V[y] - v[16] is borrow flag
            case 7:
                self.v[16] = (self.v[x] > self.v[y]!=0) 
                self.v[x] = self.v[y] - self.v[y]

            # 8X0E: SHL: Shifts left V[x], MSB bit goes to V[15]
            case 0xE:
                self.v[15] = ((self.v[x] & 0x80) != 0)
                self.v[x] <<= 1
                
    def f_branch (self, opcode):
        
        x = OPCODE_X(opcode)
        y = OPCODE_Y(opcode)
        
        match OPCODE_KK(opcode):
            
            # LD V[x], DT: V[x] = DT
            case 0x07:
                self.v[x] = self.delay_timer
            
            case 0x0A:
                pass
            
            # LD DT, v[x]: DT = v[x]
            case 0x15:
                self.delay_timer = self.v[x]
            
            # BEEP!, LD ST, v[x] -> ST = v[x]
            case 0x18:
                self.stack = self.v[x]
                
            # ADD i, v: i += v[x]
            case 0x1E:
                self.i += self.v[x]
                
            # LD F
            case 0x29:
                pass
                
            # LD B
            case 0x33:
                pass
            
            # LD [i]
            case 0x55:
                pass
            
            # LD x [i]
            case 0x65:
                pass
    

    
    def execute_opcode (self, opcode):
        print((opcode&0xF000 >> 12))
        if ((opcode&0xF000 >> 12)) in self.opcodes:
            f, debug = self.opcodes[(opcode&0xF000 >> 12)]
            f(opcode)
            
            return f"| {hex(opcode)} | {opcode:<12} | {debug}"

        else:        
        
            return "Unknow: " + str(hex(opcode)) + " " + str(opcode) 
    
    def exec_step (self):
        print(self.pc)
        print(self.memory[(self.pc + 1 )])
        opcode = (self.memory[(self.pc + 1 ) & 0xFFF]<<8) | self.memory[(self.pc + 1)&0xFFF]
        return self.execute_opcode(opcode)
    
    def run (self, rom_path) -> int:
        debug_txt=""
        trs=0x200
        with open(rom_path, 'rb') as f:
            rom = f.read()
        
        # ?
        for i, byte in enumerate(rom):
            print(hex(byte&0xF000 >> 12))
            self.memory[0x200 + i] = byte
            trs+=i
            
        self.pc = 0x200
        
        self.screen = Screen()
        f=open(r"D:\Proyectos\Chip-8\src\debug.txt","w")
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    f.close()
                    pygame.quit()
                    sys.exit()
            r=self.exec_step()
            debug_txt+= "\n"+r
            self.pc += 2
            f.write(debug_txt+"\n")

            self.screen.loop()
            
            
            


    
    # Función para JP nnn: set program counter to nnn
    def jump_to_address (self, opcode):
        self.pc = OPCODE_NNN(opcode)
        return f"Jump to address: {hex(OPCODE_NNN(opcode))}"

    # Función para SE (skip equal) x, kk: if V[x] == kk -> pc+=2
    def skip_equal (self, opcode):
        if self.v[OPCODE_X(opcode)] == OPCODE_KK(opcode):
            self.pc = (self.pc + 2) & 0xfff

    # Función para SNE (skip not equal) x, kk if V[x] != kk -> pc+=2
    def skip_not_equal (self, opcode):
        if self.v[OPCODE_X(opcode)] != OPCODE_KK(opcode):
            self.pc = (self.pc + 2) & 0xfff

    # Función para SE x, y: V[x]==V[y] -> pc +=2
    def skip_equal_vx_vy (self, opcode):
        if self.v[OPCODE_X(opcode)] == self.v[OPCODE_Y(opcode)]:
            self.pc = (self.pc + 2) & 0xfff

    # Función para LD x, kk: V[x] = kk
    def load_vx_kk (self, opcode):
        self.v[OPCODE_X(opcode)] = OPCODE_KK(opcode)

    # Función para ADD x, kk: V[x] = V[x] + kk
    def add_vx_kk (self, opcode):
        self.v[OPCODE_X(opcode)] = (self.v[OPCODE_X(opcode)] + OPCODE_KK(opcode)) & 0xFF

    # Función para SNE x, y: V[x] != V[y]
    def skip_not_equal_vx_vy (self, opcode):
        if self.v[OPCODE_X(opcode)] != self.v[OPCODE_Y(opcode)]:
            self.pc = (self.pc + 2) & 0xFFF

    # Función para LD i, x: I = nnn 
    def load_i (self, opcode):
        self.i = OPCODE_NNN(opcode)

    # Función para JP V0, nnn: pc = V[0] + nnn
    def load_i_v0_nnn (self, opcode):
        self.pc = (self.v[0] + OPCODE_NNN(opcode)) & 0xFFF

    # Función para RND
    def c_random (self, opcode):
        # RND x, kk: v[x] = random() % kk (mascara de bits)
        self.v[OPCODE_X(opcode)] = random() & OPCODE_KK(opcode)
    # Función para DRW
    def draw (self, opcode):
        """
        DRW: x, y, n
        
        Draw sprite on v[x] v[y]
        n rows = n
        sprite path [i]

    
        """
        for j in range(OPCODE_N(opcode)):
            sprite: c_uint8 = self.memory[self.i+j]
            
            for  i in range(7):
                px: int = (self.v[OPCODE_X(opcode)] + i) & 63
                py: int = (self.v[OPCODE_Y(opcode)] + j) & 31
                
                # if is on
                self.screen.pixel_array[64 * py + px] = (sprite & ( 1 << (7-i))) != 0
                print(self.screen.pixel_array[64 * py + px])
    # Función para SKP / SKNP
    def skip_key (self, opcode):
        pass  # Puedes completar esta función según sea necesario
    
    def clear_display (self, opcode):
        self.screen.clear()
    
    def call (self, opcode):
        # call nnn, stack[sp++] = pc, pc =nnn
        if self.sp.value < len(self.stack)-1:
            self.sp.value += c_uint16(1).value
            self.stack[self.sp.value] = self.pc
        
        self.pc = OPCODE_NNN(opcode)
        
    def zero_branch (self, opcode):
        match opcode:
            case 0x00E0:
                self.screen.clear()
            case 0x00EE:
                if self.sp > 0:
                    self.pc = self.stack[self.sp-1]
                