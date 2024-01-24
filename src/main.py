from Chip8 import Chip8
import cProfile

# ? To execute
if __name__=="__main__":
    
    # * Rom to execute
    # LETTERS-TEST
    rom = r"E:\Proyectos\Chip-8\src\roms\TICTAC"
    
    # * Instancing chip8
    chip8 = Chip8()
    
    # * Running rom
    chip8.load(rom)
    
    # * Chip loop
    chip8.loop()