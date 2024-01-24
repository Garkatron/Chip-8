from ctypes import c_void_p, c_int, memset, c_long, byref
from sdl2 import (
    SDL_Init, SDL_Quit, SDL_INIT_VIDEO, SDL_WINDOWPOS_CENTERED, SDL_WINDOW_SHOWN,
    SDL_WINDOW_OPENGL, SDL_Renderer, SDL_CreateWindow, SDL_CreateRenderer,
    SDL_RENDERER_ACCELERATED, SDL_DestroyRenderer, SDL_DestroyWindow,
    SDL_INIT_EVERYTHING, SDL_PollEvent, SDL_QUIT, SDL_Event, SDL_WaitEvent,
    SDL_Texture, SDL_LockTexture, SDL_CreateTexture, SDL_PIXELFORMAT_RGB888,
    SDL_TEXTUREACCESS_STREAMING, SDL_UnlockTexture, SDL_RenderClear, SDL_RenderCopy, SDL_RenderPresent
)
if __name__ == "__main__":
    
    SDL_Init(SDL_INIT_VIDEO)
    
    # ? Window config
    win = SDL_CreateWindow(
        b"CHIP-8",  # Agregado el prefijo 'b' para indicar una cadena de bytes
        SDL_WINDOWPOS_CENTERED,
        SDL_WINDOWPOS_CENTERED,
        640,
        360,
        SDL_WINDOW_SHOWN | SDL_WINDOW_OPENGL  # Corregido el uso de '|' para combinar las banderas
    )
    
    
    rnd = SDL_CreateRenderer(win, -1, SDL_RENDERER_ACCELERATED)
    
    pitch   : c_long        = c_long(0)
    pixels  : c_void_p      = c_void_p()
    texture : SDL_Texture   = SDL_CreateTexture(rnd, SDL_PIXELFORMAT_RGB888, SDL_TEXTUREACCESS_STREAMING, 64,32)
    
    # Lock texture
    SDL_LockTexture(texture, None, pixels, byref(pitch))
    memset(pixels, 0x80, 32 * pitch.value)

    SDL_UnlockTexture(texture)
    
    # ? Loop config
    running: bool = True
    ev: SDL_Event = SDL_Event()
    
    # ? Window refresh loop
    while running:
        SDL_WaitEvent(ev)
        if ev.type == SDL_QUIT:
            running = False
        
        SDL_RenderClear(rnd)
        SDL_RenderCopy(rnd, texture, None ,None)
        SDL_RenderPresent(rnd)


    # ? Destroy window
    SDL_DestroyRenderer(rnd)
    SDL_DestroyWindow(win)
    SDL_Quit()
