from Chip8 import Chip8
import cProfile

# ? To execute
if __name__=="__main__":
    
    # * Rom to execute
    rom = r"D:\Proyectos\Chip-8\src\roms\LETTERS-TEST"
    
    # * Instancing chip8
    chip8 = Chip8()
    
    # * Running rom
    chip8.load(rom)
    
    # * Chip loop
    chip8.loop()