
from random import randint as random
from Screen import Screen

class Utils:
    # * OPCODES MANIPULATION FUNCS

    # ? Used to manimulate opcodes with specific structure and extract data
    def OPCODE_NNN (opcode)  :  return opcode & 0xFFF         # ? Extracts 12 bits more lower of the opcode (NNN)
    def OPCODE_KK  (opcode)  :  return opcode & 0xFF          # ? Extracts 8 bits more lower of the opcode (KK)
    def OPCODE_N   (opcode)  :  return opcode & 0xF           # ? Extracts 4 bits more lower of the opcode (N)
    def OPCODE_P   (opcode)  :  return opcode >> 12           # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 12 bits right and after applys mask ti to obtain 4 bits more important bits and return the result
    def OPCODE_X   (opcode)  :  return (opcode >> 8) & 0xF    # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 8 bits right and after applys mask ti to obtain 4 bits more important bits and return the result
    def OPCODE_Y   (opcode)  :  return (opcode >> 4) & 0xF    # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 4 bits right and after applys mask ti to obtain 4 bits less important bits and return the result

    def nothing(anything): print("NOTHING: ", anything)

OPCODE_NNN = Utils.OPCODE_NNN
OPCODE_KK = Utils.OPCODE_KK
OPCODE_N = Utils.OPCODE_N
OPCODE_P = Utils.OPCODE_P
OPCODE_X = Utils.OPCODE_X
OPCODE_Y = Utils.OPCODE_Y

class Opcodes:

    def memset (buffer, value: int, size):
        """[ Set ] in [ buffer ] for [ size ]

        Args:
            buffer (_type_): _description_
            value (int): _description_
            size (_type_): _description_
        """
        for i in range(size):
            buffer[i] = value

    def jump_to_address (mac, opcode) -> str:
        """Función para JP nnn: set program counter to nnn

        Args:
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        mac.pc = OPCODE_NNN(opcode)
        return f"Jump to address: [{hex(OPCODE_NNN(opcode))}] current pc: [{mac.pc}]"

    def skip_equal (mac, opcode) -> str:
        """Función para SE (skip equal) x, kk: if V[x] == kk -> pc+=2

        Args:
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] == OPCODE_KK(opcode):
            mac.pc = (mac.pc + 2) & 0xfff
        return f"skip equal x: [{OPCODE_X(opcode)}] == kk: [{OPCODE_KK(opcode)}]"

    def skip_not_equal (mac, opcode) -> str:
        """Función para SNE (skip not equal) x, kk if V[x] != kk -> pc+=2

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] != OPCODE_KK(opcode):
            mac.pc = (mac.pc + 2) & 0xfff
            
            return f"load vx kk, x: {mac.v[OPCODE_X(opcode)]} kk: {OPCODE_KK(opcode)}"
        else:
            return f"Error: load vx kk, x: {mac.v[OPCODE_X(opcode)]} kk: {OPCODE_KK(opcode)}"

    def skip_equal_vx_vy (mac, opcode) -> str:
        """Función para SE x, y: V[x]==V[y] -> pc +=2

        Args:
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] == mac.v[OPCODE_Y(opcode)]:
            mac.pc = (mac.pc + 2) & 0xfff
        return f"skip equal vx: {mac.v[OPCODE_X(opcode)]} == vy: {mac.v[OPCODE_Y(opcode)]} "

    def load_vx_kk (mac, opcode) -> str:
        """Función para LD x, kk: V[x] = kk

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.v[OPCODE_X(opcode)] = OPCODE_KK(opcode)
        
        return f"load vx kk, x: {mac.v[OPCODE_X(opcode)]} kk: {OPCODE_KK(opcode)}"

    def add_vx_kk (mac, opcode) -> str:
        """Función para ADD x, kk: V[x] = V[x] + kk

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.v[OPCODE_X(opcode)] = (mac.v[OPCODE_X(opcode)] + OPCODE_KK(opcode)) & 0xFF
        return f"add vx: {mac.v[OPCODE_X(opcode)]} kk: {1}"

    def skip_not_equal_vx_vy (mac, opcode) -> str:
        """Función para SNE x, y: V[x] != V[y]

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] != mac.v[OPCODE_Y(opcode)]:
            mac.pc = (mac.pc + 2) & 0xFFFF
        return f"skip_not_equal vx: {mac.v[OPCODE_X(opcode)]} != vy: {OPCODE_Y(opcode)} "

    def load_i (mac, opcode) -> str:
        """Función para LD i, x: I = nnn 

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.i = OPCODE_NNN(opcode)
        return f"load i [{mac.i}] = nnn: [{OPCODE_NNN(opcode)}]"

    def load_i_v0_nnn (mac, opcode) -> str:
        """Función para JP V0, nnn: pc = V[0] + nnn

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.pc = (mac.v[0] + OPCODE_NNN(opcode)) & 0xFFF
        return f"load i pc: [{mac.pc}] = v[0]: {mac.v[0]} + nnn: [{OPCODE_NNN(opcode)}]"

    def c_random (mac, opcode):
        # RND x, kk: v[x] = random() % kk (mascara de bits)
        """_summary_

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.v[OPCODE_X(opcode)] = random(0,9) & OPCODE_KK(opcode)
        return "rnd"

    def draw (mac, opcode) -> str:
        """
        DRW: x, y, n
        
        Draw sprite on v[x] v[y]
        n rows = n
        sprite path [i]

        Returns:
            str: _description_
        """
        def draw_screen (mac, vx, vy, sprite) -> bool:
            """_summary_

            Args:
                vx (int): _description_
                vy (int): _description_
                sprite ( bin [] ): _description_

            Returns:
                bool: _description_
            """

            collision = False

            spriteBits = []
            for i in sprite:
                binary = bin(i)
                line = list(binary[2:])
                fillNum = 8 - len(line)
                line = ['0'] * fillNum + line
                spriteBits.append(line)

            for i in range(len(spriteBits)):
                for j in range(8):
                    try:
                        if mac.screen.pixel_array[vy+i][vx+j] == 1 and int(sprite[i][j]) == 1:
                            collision=True
                        mac.screen.pixel_array[vy+i][vx+j] = mac.screen.pixel_array[vy+i][vx+j] ^ int(spriteBits[i][j]) 
                    except:
                        continue
            return collision

        N = OPCODE_N(opcode)
        Vx = OPCODE_X(opcode)
        Vy = OPCODE_Y(opcode)

        addr = mac.i
        sprite = mac.memory[addr: addr + N]

        if draw_screen(mac, mac.v[Vx], mac.v[Vy], sprite):
            mac.v[15] = 1
            return f"sprite {sprite} | px: {Vx} py: {Vy} | n: {N} | addr: {addr} | collision"            
        else:
            mac.v[15] = 0
            return f"sprite {sprite} | px: {Vx} py: {Vy} | n: {N} | addr: {addr}"

    def call (mac, opcode) -> str:
        """Call nnn, stack[sp++] = pc, pc =nnn

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        
        if mac.sp < 15:
            mac.sp += 1
            mac.stack[mac.sp] = mac.pc
            mac.pc = OPCODE_NNN(opcode)
            return f"current pc: [{mac.pc}] sp current: [{mac.sp}] [stack]: {mac.stack[mac.sp]}"
        else: return f"[sp above 16]"

    def zero_branch (mac, opcode) -> str:
        """_summary_

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        match opcode:
            case 0x00E0:
                for i in range(len(mac.screen.pixel_array)):
                    for j in range(i):
                        mac.screen.pixel_array[i][j]=0
                
                return f"CLS {opcode}"
            
            case 0x00EE:
                mac.sp -= 1
                mac.pc = mac.stack[mac.sp]
                mac.pc += 2
                    
                return f"ZB {opcode}"
        return f"ZERO BRANCH"

    def arithmetic_operator (mac, opcode) -> str:
        """_summary_

        Args:
            mac (_type_): _description_
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        x = OPCODE_X(opcode)
        y = OPCODE_Y(opcode)

        match OPCODE_N (opcode):

            # 8XY0 LD: set V[x] = V[y]
            case 0: mac.v[x] = mac.v[y]

            # 8XY1: OR: set V[x] |= V[y]
            case 1: mac.v[x] |= mac.v[y]

            # 8XY1: AND: set V[x] &= V[y]
            case 2: mac.v[x] &= mac.v[y]

            # 8XY3: XOR: set V[x] ^= V[y]
            case 3: mac.v[x] ^= mac.v[y]

            # 8XY4: ADD: set V[x] += V[y] v[15] carry flag
            case 4: 
                mac.v[15] = mac.v[x] > ((mac.v[x]+mac.v[y]) & 0xFF)
                mac.v[x] += mac.v[y]

            # 8XY5: SUB: set v[x] -= V[y] - v[15] is borrow flag
            case 5:
                mac.v[15] = (mac.v[x] > mac.v[y]) & 0xFF
                mac.v[x] -= mac.v[y]

            # 8XY6: SHR: shifts right V[x], LSB vit goes to V[15]
            case 6:
                mac.v[15] = (mac.v[x] & 1)
                mac.v[x] >>= mac.v[y]

            # 8XY7: SUBN: set v[x] -= V[y] - v[16] is borrow flag
            case 7:
                mac.v[15] = (mac.v[x] > mac.v[y]!=0) 
                mac.v[x] = mac.v[y] - mac.v[y]

            # 8X0E: SHL: Shifts left V[x], MSB bit goes to V[15]
            case 0xE:
                mac.v[15] = ((mac.v[x] & 0x80) != 0)
                mac.v[x] <<= 1

    def f_branch (mac, opcode) -> str:
        """_summary_

        Args:
            mac (_type_): _description_
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        x = OPCODE_X(opcode)
        y = OPCODE_Y(opcode)
        
        match OPCODE_KK (opcode):
            
            # LD V[x], DT: V[x] = DT
            case 0x07:
                mac.v[x] = mac.delay_timer
                mac.pc += 2
                
            # Wait for a key press, store the value of the key in Vx.
            case 0x0A:
                mac.pc += 2

            
            # LD DT, v[x]: DT = v[x]
            case 0x15:
                mac.delay_timer = mac.v[x]
                mac.pc += 2

            # BEEP!, LD ST, v[x] -> ST = v[x]
            case 0x18:
                mac.stack = mac.v[x]
                mac.pc += 2
                
            # ADD i, v: i += v[x]
            case 0x1E:
                mac.i += mac.v[x]
                mac.pc += 2
                
            # LD F, Set I = location of sprite for digit Vx.
            case 0x29:
                mac.i = mac.v[x]
                mac.pc += 2
                
            # LD B, Vx, Store BCD representation of Vx in memory locations I, I+1, and I+2.
            case 0x33:
                val = mac.v[x]
                
                ones = (val%10)
                tens = (val//10)%10
                hundreds = (val//100)%10
                
                mac.memory[mac.i] = hundreds
                mac.memory[mac.i + 1] = tens
                mac.memory[mac.i + 2] = ones

                mac.pc += 2
                return f"i {mac.memory[mac.i]} 0 i+1| {mac.memory[mac.i+1]} |i+2 {mac.memory[mac.i+2]}"

            # LD [i] Vx, Store registers V0 through Vx in memory starting at location I.
            case 0x55:
                for i in range(x+1):
                    mac.memory[(mac.i + i) & 0xFFF] = mac.v[i]

                mac.i = i + x + 1
                mac.pc += 2

            
            # Fx65 - LD Vx, [I] Read registers V0 through Vx from memory starting at location I.
            # The interpreter reads values from memory starting at location I into registers V0 through Vx.
            case 0x65:
                for i in range(x):
                    mac.v[i] = mac.memory[mac.i+i]

                mac.i = mac.i + x + 1
                mac.pc += 2