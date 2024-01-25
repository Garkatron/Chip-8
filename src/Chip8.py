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

# IMPORTS
from Opcodes import Opcodes as Opc, Utils
from random import randint as random
from Screen import Screen
import pygame
import sys

# Manipulation
OPCODE_NNN  = Utils.OPCODE_NNN
OPCODE_KK   = Utils.OPCODE_KK
OPCODE_N    = Utils.OPCODE_N
OPCODE_P    = Utils.OPCODE_P
OPCODE_X    = Utils.OPCODE_X
OPCODE_Y    = Utils.OPCODE_Y
memset      = Opc.memset

# Classes
class Chip8:
    
    def __init__(self) -> None:

        # * Cpu
        self.pc = 0                                      # Change to a regular integer

        # * Memory
        self.MEM_SIZE = 4096                             # How much mem can handle the chip
        self.memory = [0] * self.MEM_SIZE                # Mem as buffer

        # * Registers22
        self.v = [0] * 16                                # 16 General purpose registers
        self.i = 0                                       # Special register

        # * Stack
        self.stack = [0] * 16                            # Stack can hold 16 - 16 bits
        self.sp = 0                                      # Stack pointer

        # * Timers
        self.delay_timer = 0
        self.sound_timer = 0

        # * External
        self.screen = Screen                             # Assuming Screen is a class
        self.clock = pygame.time.Clock()
        
        # * Fuentes
        fonts = [ 
            0xF0, 0x90, 0x90, 0x90, 0xF0, # 0
            0x20, 0x60, 0x20, 0x20, 0x70, # 1
            0xF0, 0x10, 0xF0, 0x80, 0xF0, # 2
            0xF0, 0x10, 0xF0, 0x10, 0xF0, # 3
            0x90, 0x90, 0xF0, 0x10, 0x10, # 4
            0xF0, 0x80, 0xF0, 0x10, 0xF0, # 5
            0xF0, 0x80, 0xF0, 0x90, 0xF0, # 6
            0xF0, 0x10, 0x20, 0x40, 0x40, # 7
            0xF0, 0x90, 0xF0, 0x90, 0xF0, # 8
            0xF0, 0x90, 0xF0, 0x10, 0xF0, # 9
            0xF0, 0x90, 0xF0, 0x90, 0x90, # A
            0xE0, 0x90, 0xE0, 0x90, 0xE0, # B
            0xF0, 0x80, 0x80, 0x80, 0xF0, # C
            0xE0, 0x90, 0x90, 0x90, 0xE0, # D
            0xF0, 0x80, 0xF0, 0x80, 0xF0, # E
            0xF0, 0x80, 0xF0, 0x80, 0x80  # F
        ]

        for i in range(len(fonts)):
            self.memory[i] = fonts[i]

        # * Opcodes
        self.opcodes: dict = {
            # CLS
            0x0: Opc.zero_branch,

            # JP nnn: set program counter to nnn
            0x1: Opc.jump_to_address,

            # CALL
            0x2: Opc.call,

            # SE (skip equal) x, kk: if V[x] == kk -> pc+=2
            0x3: Opc.skip_equal,

            # SNE (skip not equal) x, kk if V[x] != kk -> pc+=2
            0x4: Opc.skip_not_equal,

            # SE x, y: V[x]==V[y] -> pc +=2
            0x5: Opc.skip_equal_vx_vy,

            # LD x, kk: V[x] = kk
            0x6: Opc.load_vx_kk,

            # ADD x, kk: V[x] = V[x] + kk
            0x7: Opc.add_vx_kk,

            # Arithmetic operator
            0x8: Opc.arithmetic_operator,

            # SNE x, y: V[x] != V[y]
            0x9: Opc.skip_not_equal_vx_vy,

            # LD i, x: I = nnn 
            0xA: Opc.load_i,

            # JP V0, nnn: pc = V[0] + nnn
            0xB: Opc.jump_to_address,

            # RND
            0xC: Opc.c_random,

            # DRW
            0xD: Opc.draw,

            # SKP / SKNP
            0xE: Opc.e_branch,

            # Franch
            0xF: Opc.f_branch,
        }

        # * Process
        memset(self.memory, 0x00, self.MEM_SIZE)
        memset(self.stack, 0x00, 16)
        memset(self.v, 0x00, 16)

    def exec_step (self) -> None:

        if self.pc < len(self.memory):
            opcode = (self.memory[self.pc] << 8) | self.memory[self.pc + 1]

            b = opcode & 0xF000
            extracted = int(hex(b)[:3],16)

            func = self.opcodes[extracted]
            re = func(self,opcode)

            return f"""[pc]: {self.pc} | [Hex]: {hex(opcode)} - {hex(extracted)} | [mem]: {hex(self.memory[self.pc])}       
# ! [Result]      : {str(re)}
"""
        else:
            self.pc = 0x200
            return "Error: Program counter out of bounds."

    def load (self, rom_path) -> None:
        """Charge rom by rom file path

        Args:
            rom_path (_type_): _description_
        """
        debug_txt = ""

        with open(rom_path, 'rb') as f:
            rom = f.read()

        for i, byte in enumerate(rom):
            self.memory[0x200 + i] = byte
            print(hex(byte), end=" ")

        self.pc = 0x200
        
    def update (self) -> str:
        """_summary_

        Returns:
            str: _description_
        """
        r = self.exec_step()
        #self.pc = (self.pc + 2) & 0xFFF
        return r
    
    def upd_inpt(self) -> bool:
        """_summary_

        Returns:
            bool: _description_
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("QUIT")
                return False
        return True
    
    def loop(self) -> None:
        """The loop of the chip
        """
        
        #with open("D:\Proyectos\Chip-8\src\debug\debug2.txt", 'w') as f:
        #    for c in self.memory:
        #        f.write(str(c)+"!"+hex(c))

        # * local funcs
        upd_logic = self.update
        upd_inpt = self.upd_inpt
        # *
        
        self.screen = Screen()
        debug_txt = ""
        
        running = True
        
        while running:
            
            running = upd_inpt()
            
            debug_txt += "\n"+ upd_logic()

            self.screen.update()
            
            self.clock.tick(1000)
        
        else:
        
            print("terminated")
            
            with open(r"D:\Proyectos\Chip-8\src\debug\debug.txt","w") as f:
                f.write(debug_txt)
            
            pygame.quit()
            sys.exit()
        

    