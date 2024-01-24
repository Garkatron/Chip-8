import pygame
import sys
import random

# Inicializar Pygame    
class Screen:

    def __init__(self) -> None:

        scale_factor = 12

        width = 64 
        height = 32
        
        scaled_height = height * scale_factor
        scaled_width = width * scale_factor

        total_pixels = width * height

        grid_size = int(total_pixels ** 0.5)
        self.pixel_size = 400 // grid_size 

        self.pixel_array: list = [[ 0 for _ in range(width)]for _ in range(height)]


        self.screen = pygame.display.set_mode((scaled_width, scaled_height))
        pygame.display.set_caption("Píxeles Aleatorios")

        # Ajustar espacio alrededor de la cuadrícula para centrarla
        self.offset_x = (scaled_width - width * self.pixel_size) // 2
        self.offset_y = (scaled_height - height * self.pixel_size) // 2

        self.run = True

    def draw_pixels (self) -> None:
        for y, row in enumerate(self.pixel_array):
            for x, color in enumerate(row):
                pixel_rect = pygame.Rect(x * self.pixel_size, y * self.pixel_size, self.pixel_size, self.pixel_size)
                pygame.draw.rect(self.screen, (color*255,color*255,color*255), (self.offset_x + x * self.pixel_size, self.offset_y + y * self.pixel_size, self.pixel_size, self.pixel_size), 0) 

    

    def update (self) -> None:

        self.draw_pixels()
        pygame.display.flip()
        

if __name__ == "__main__":
    s = Screen()
    