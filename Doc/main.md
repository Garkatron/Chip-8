# ARQUITECTURA CHIP-8

## [Recursos]:

>Documentacion wikipedia[here](https://es.wikipedia.org/wiki/CHIP-8)
>"Tutorial" [here](https://www.makigas.es/series/construyendo-un-emulador-chip-8)
>Documentacion Github [here](https://github.com/mattmikolay/chip-8)
>Chat GPT [here](chat.openai.com)

## [Origen]

> CHIP-8 es un lenguaje de programación interpretado, desarrollado por Joseph
> Weisbecker. Fue inicialmente usado en los microcomputadores de 8 bits COSMAC VIP y Telmac 1800 a mediados de 1970. Los programas de CHIP-8 corren sobre una máquina virtual de CHIP-8. Esto se hizo así para que los video juegos fueran más fáciles de programar en otros computadores.

> Aproximadamente 20 años después el CHIP-8 reapareció, pero esta vez, aparecieron diversos intérpretes para algunos modelos de calculadoras gráficas. Como era de esperar, desde finales de 1980 en adelante, esos dispositivos de mano tienen mucho más poder de cálculo que los microcomputadores de mediados de 1970.

## TODO

>* [X] VARS
>* [ ] OPCODE
>* [ ] ...
>* [ ] ...
>* [ ] ...

# DESCRIPCION

## [CPU]

```python

import numpy as np
pc = np.uint16(0)

```

## [ALU]

    ...

```python




```


## [MEMORIA]

    **(MEM-SIZE)**: 
    
    Has a range of [0x00] to [0xFFF] exactly [3.584Bytes]
    The origina interpreter was located from 0x00 to 0x1FF this shouldent used by programs.
    
    Its standard for chip-8 begin from 0x200 (512)
    For ETI 660 pc starts in 0x600
```
    **(Map)**:
    +---------------+= 0xFFF (4095) End of Chip-8 RAM
    |               |
    |               |
    |               |
    |               |
    |               |
    | 0x200 to 0xFFF|
    |     Chip-8    |
    | Program / Data|
    |     Space     |
    |               |
    |               |
    |               |
    +- - - - - - - -+= 0x600 (1536) Start of ETI 660 Chip-8 programs
    |               |
    |               |
    |               |
    +---------------+= 0x200 (512) Start of most Chip-8 programs
    | 0x000 to 0x1FF|
    | Reserved for  |
    |  interpreter  |
    +---------------+= 0x000 (0) Start of Chip-8 RAM
```

```python

from array import array

mem_size = 4096
memory: Array = array('B', [0] * mem_size)

```

## [REGISTROS]

    **(V)**:
        V0-VF [16r de 8b]
        Funciona como registro de estado, se usa como carry flag para instrucciones
        aritmeticas.
        Tambien puede funcionar como detector de colisiones en sprites.

    **(I)**:
        16bits ancho, se usa con varios opcodes que usan operaciones de memoria.
        De los 16 bits, este solo usa 12 menores y los 4 mayores son para la carga de fuentes.

```python

import numpy as np
from array import array

V: Array = array('B', [0] * 16)
I = np.uint16(0)

```

## [PILA | STACK]

    Solo se usa para almacenar direcciones que seran usadas mas tarde, al regresar una subrutina.
    12 niveles de profundidad.

```python

from array import array

Stack: Array = array('B', [0] * 16)
sp = np.uint16(0)

```

## [Timers]

    El CHIP-8 tiene 2, estos corren hasta llagar a 0 y lo hacen a 60 hertz.

    **(T_Delay)**: se usa para sincronizar eventos de juegos. Este puede ser escrito y leido.

    **(T_Sound)**: Usado para efectos de sonido, cuando no es 0 hace beep.

```python

import numpy as np

delay_timer = np.uint8(0)
sound_timer = np.uint8(0)

```

## [Entrada]

    Teclado hexadecimal, 16 teclas de 0 - F, Se usan 3 opcodes para detectar la entrada.

## [Graficos & Sonido]

    **(Pantalla)**: 64 x 32 p, color monocromo 2 colores. Los pixeles se pintan de 8px w a 1-15px h

```python

import pygame
import sys

```

    El indicador de acarreo o carry flag (VF) se pone a 1 si cualquier pixel de la pantalla se borra (se pasa de 1 a 0) mientras un pixel se está pintando.

## [Tabla de instrucciones]

    35 Instrucciones, cada tiene tamaño 2B estan en hex

| Símbolo | Uso                  |
| -------- | -------------------- |
| NNN      | Dirección           |
| N        | Constante 4b         |
| X & Y    | Registro 4b          |
| PC       | Contador de programa |

| Opcode | Explicación                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| ------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 0NNN   | Salta a un código de rutina en NNN. Se usaba en los viejos computadores que implementaban Chip-8. Los intérpretes actuales lo ignoran.                                                                                                                                                                                                                                                                                                                                                                        |
| 00E0   | Limpia la pantalla.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 00EE   | Retorna de una subrutina. Se decrementa en 1 el*Stack Pointer* (SP). El intérprete establece el *Program Counter* como la dirección donde apunta el SP en la Pila.                                                                                                                                                                                                                                                                                                                                        |
| 1NNN   | Salta a la dirección NNN. El intérprete establece el*Program Counter* a NNN.                                                                                                                                                                                                                                                                                                                                                                                                                                |
| 2NNN   | Llama a la subrutina NNN. El intérprete incrementa el*Stack Pointer* , luego pone el actual PC en el tope de la Pila. El PC se establece a NNN.                                                                                                                                                                                                                                                                                                                                                              |
| 3XNN   | Salta a la siguiente instrucción si VX = NN. El intérprete compara el registro VX con el NN, y si son iguales, incrementa el PC en 2.                                                                                                                                                                                                                                                                                                                                                                         |
| 4XKK   | Salta a la siguiente instrucción si VX != KK. El intérprete compara el registro VX con el KK, y si no son iguales, incrementa el PC en 2.                                                                                                                                                                                                                                                                                                                                                                     |
| 5XY0   | Salta a la siguiente instrucción si VX = VY. El intérprete compara el registro VX con el VY, y si no son iguales, incrementa el PC en 2.                                                                                                                                                                                                                                                                                                                                                                      |
| 6XKK   | Hace VX = KK. El intérprete coloca el valor KK dentro del registro VX.                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| 7XKK   | Hace VX = VX + KK. Suma el valor de KK al valor de VX y el resultado lo deja en VX.                                                                                                                                                                                                                                                                                                                                                                                                                             |
| 8XY0   | Hace VX = VY. Almacena el valor del registro VY en el registro VX.                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| 8XY1   | Hace VX = VX OR VY.Realiza un[bitwise OR](https://es.wikipedia.org/wiki/Bitwise_OR "Bitwise OR") (OR Binario) sobre los valores de VX y VY, entonces almacena el resultado en VX. Un OR binario compara cada uno de los bit respectivos desde 2 valores, y si al menos uno es verdadero (1), entonces el mismo bit en el resultado es 1. De otra forma es 0.                                                                                                                                                          |
| 8XY2   | Hace VX = VX AND VY.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 8XY3   | Hace VX = VX XOR VY.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            |
| 8XY4   | Suma VY a VX. VF se pone a 1 cuando hay un acarreo (carry), y a 0 cuando no.                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| 8XY5   | VY se resta de VX. VF se pone a 0 cuando hay que restarle un dígito al número de la izquierda, más conocido como "pedir prestado" o borrow, y se pone a 1 cuando no es necesario.                                                                                                                                                                                                                                                                                                                            |
| 8XY6   | Establece VF = 1 o 0 según bit menos significativo de VX. Divide VX por 2.                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 8XY7   | Si VY > VX => VF = 1, sino 0. VX = VY - VX.                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| 8XYE   | Establece VF = 1 o 0 según bit más significativo de VX. Multiplica VX por 2.                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| 9XY0   | Salta a la siguiente instrucción si VX != VY.                                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ANNN   | Establece I = NNN.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                              |
| BNNN   | Salta a la ubicación V[0]+ NNN.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
| CXKK   | Establece VX = un Byte Aleatorio AND KK.                                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| DXYN   | Pinta un sprite en la pantalla. El intérprete lee N bytes desde la memoria, comenzando desde el contenido del registro I. Y se muestra dicho byte en las posiciones VX, VY de la pantalla.A los sprites que se pintan se le aplica XOR con lo que está en pantalla. Si esto causa que algún pixel se borre, el registro VF se setea a 1, de otra forma se setea a 0. Si el sprite se posiciona afuera de las coordenadas de la pantalla, dicho sprite se le hace aparecer en el lado opuesto de la pantalla. |
| EX9E   | Salta a la siguiente instrucción si valor de VX coincide con tecla presionada.                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| EXA1   | Salta a la siguiente instrucción si valor de VX no coincide con tecla presionada (soltar tecla).                                                                                                                                                                                                                                                                                                                                                                                                               |
| FX07   | Establece Vx = valor del delay timer.                                                                                                                                                                                                                                                                                                                                                                                                                                                                           |
| FX0A   | Espera por una tecla presionada y la almacena en el registro.                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
| FX15   | Establece Delay Timer = VX.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| FX18   | Establece Sound Timer = VX.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| FX1E   | Índice = Índice + VX.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| FX29   | Establece I = VX * largo Sprite Chip-8.                                                                                                                                                                                                                                                                                                                                                                                                                                                                         |
| FX33   | Guarda la representación de VX en formato humano. Poniendo las centenas en la posición de memoria I, las decenas en I + 1 y las unidades en I + 2                                                                                                                                                                                                                                                                                                                                                             |
| FX55   | Almacena el contenido de V0 a VX en la memoria empezando por la dirección I                                                                                                                                                                                                                                                                                                                                                                                                                                    |
| FX65   | Almacena el contenido de la dirección de memoria I en los registros del V0 al VX                                                                                                                                                                                                                                                                                                                                                                                                                               |

```python

opcodes: dict = {
    0x00: function call
}

# How to execute
return_value = opcodes[0x00](args)

```

## [ROM/S]

    ...
    ...
    ...
    ...
