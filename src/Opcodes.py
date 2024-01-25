
from random import randint as random
from Screen import Screen

class Utils:
    # * OPCODES MANIPULATION FUNCS

    # ? Used to manimulate opcodes with specific structure and extract data
    @staticmethod
    def OPCODE_NNN (opcode) -> int :  return opcode & 0x0FFF         # ? Extracts 12 bits more lower of the opcode (NNN)
    @staticmethod
    def OPCODE_KK  (opcode) -> int :  return opcode & 0xFF          # ? Extracts 8 bits more lower of the opcode (KK)
    @staticmethod
    def OPCODE_N   (opcode) -> int :  return opcode & 0xF           # ? Extracts 4 bits more lower of the opcode (N)
    @staticmethod
    def OPCODE_P   (opcode) -> int :  return opcode >> 12           # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 12 bits right and after applys mask ti to obtain 4 bits more important bits and return the result
    @staticmethod
    def OPCODE_X   (opcode) -> int :  return (opcode >> 8) & 0xF    # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 8 bits right and after applys mask ti to obtain 4 bits more important bits and return the result
    @staticmethod
    def OPCODE_Y   (opcode) -> int :  return (opcode >> 4) & 0xF    # ? Extracts 4 bits correspondent of register X of the opcode. Do desplacement of 4 bits right and after applys mask ti to obtain 4 bits less important bits and return the result  
    @staticmethod
    def pc_next (mac) -> None: mac.pc = (mac.pc + 2) & 0xfff

OPCODE_NNN = Utils.OPCODE_NNN
OPCODE_KK = Utils.OPCODE_KK
OPCODE_N = Utils.OPCODE_N
OPCODE_P = Utils.OPCODE_P
OPCODE_X = Utils.OPCODE_X
OPCODE_Y = Utils.OPCODE_Y
pc_next = Utils.pc_next

class Opcodes:

    @staticmethod
    def nothing(anything): print("NOTHING: ", anything) 

    @staticmethod
    def memset (buffer, value: int, size) -> None:
        """Set [ value ] in [ buffer ] for [ size ]

        Args:
            buffer (_type_): _description_
            value (int): _description_
            size (_type_): _description_
        """
        for i in range(size):
            buffer[i] = value

    @staticmethod
    def zero_branch (mac, opcode) -> str:
        """Contains 0x0 init opcodes

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        match opcode:
            case 0x0:
                pc_next(mac)
                return f"0x0NNN {opcode}"

            case 0x00E0:
                for i in range(len(mac.screen.pixel_array)):
                    for j in range(len(mac.screen.pixel_array[i])):
                        mac.screen.pixel_array[i][j] = 0
                
                pc_next(mac)
                return f"CLS {opcode}"
            
            case 0x00EE:
                mac.sp -= 1
                mac.pc = mac.stack[mac.sp]
                pc_next(mac)
                    
                return f"ZB {opcode}"

        return f"ZERO BRANCH"

    @staticmethod
    def jump_to_address (mac, opcode) -> str:
        """Función para JP nnn: set program counter to nnn

        Args:
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        mac.pc = OPCODE_NNN(opcode)
        return f"Jump to address: [{hex(OPCODE_NNN(opcode))}] current pc: [{mac.pc}]"

    @staticmethod
    def call (mac, opcode) -> str:
        """2NNN Call nnn, stack[sp++] = pc, pc =nnn

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        if mac.sp < 15:
            mac.sp += 1
            mac.stack[mac.sp] = mac.pc
            mac.pc = OPCODE_NNN(opcode)

        return f"Current pc: [{mac.pc}] sp current: [{mac.sp}] [stack]: {mac.stack[mac.sp]}"

    @staticmethod
    def skip_equal (mac, opcode) -> str:
        """The interpreter compares register Vx to kk, and if they are equal, increments the program counter by 2.

        Args:
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] == OPCODE_KK(opcode):
            pc_next(mac)
        pc_next(mac)
        return f"skip equal x: [{OPCODE_X(opcode)}] == kk: [{OPCODE_KK(opcode)}]"

    @staticmethod
    def skip_not_equal (mac, opcode) -> str:
        """The interpreter compares register Vx to kk, and if they are not equal, increments the program counter by 2.
        
        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] != OPCODE_KK(opcode):
            pc_next(mac)
            
            return f"load vx kk, x: {mac.v[OPCODE_X(opcode)]} kk: {OPCODE_KK(opcode)}"

        pc_next(mac)
        
    @staticmethod
    def skip_equal_vx_vy (mac, opcode) -> str:
        """Skip next instruction if Vx = Vy.

        Args:
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] == mac.v[OPCODE_Y(opcode)]:
            pc_next(mac)
        pc_next(mac)
        return f"skip equal vx: {mac.v[OPCODE_X(opcode)]} == vy: {mac.v[OPCODE_Y(opcode)]} "

    @staticmethod
    def load_vx_kk (mac, opcode) -> str:
        """The interpreter puts the value kk into register Vx.

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.v[OPCODE_X(opcode)] = OPCODE_KK(opcode)
        pc_next(mac)
        return f"load vx kk, x: {mac.v[OPCODE_X(opcode)]} kk: {OPCODE_KK(opcode)}"

    @staticmethod
    def add_vx_kk (mac, opcode) -> str:
        """Función para ADD x, kk: V[x] = V[x] + kk

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.v[OPCODE_X(opcode)] = (mac.v[OPCODE_X(opcode)] + OPCODE_KK(opcode)) & 0xFF
        pc_next(mac)
        return f"add vx: {mac.v[OPCODE_X(opcode)]} kk: {1}"

    @staticmethod
    def load_i_v0_nnn (mac, opcode) -> str:
        """Función para JP V0, nnn: pc = V[0] + nnn

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.pc = (mac.v[0] + OPCODE_NNN(opcode)) & 0xFFF
        
        return f"load i pc: [{mac.pc}] = v[0]: {mac.v[0]} + nnn: [{OPCODE_NNN(opcode)}]"

    @staticmethod
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
            case 0: mac.v[x] = mac.v[y]; pc_next(mac)

            # 8XY1: OR: set V[x] |= V[y]
            case 1: mac.v[x] |= mac.v[y]; pc_next(mac)

            # 8XY1: AND: set V[x] &= V[y]
            case 2: mac.v[x] &= mac.v[y]; pc_next(mac)

            # 8XY3: XOR: set V[x] ^= V[y]
            case 3: mac.v[x] ^= mac.v[y]; pc_next(mac)

            # 8XY4: ADD: set V[x] += V[y] v[15] carry flag
            case 4: 
                r = mac.v[x] + mac.v[y]
                mac.v[x] = r & 0xFF
                mac.v[15] = int(r > 0xFF)
                pc_next(mac)
                return f"8XY4 carry flag: {int(r > 0xFF)}"

            # 8XY5: Set Vx = Vx - Vy, set VF = NOT borrow.
            case 5:
                mac.v[15] = int(mac.v[x] > mac.v[y])
                mac.v[x] = mac.v[x] - mac.v[y]
                mac.v[x] &= 0xFF  # Para asegurarse de que el resultado esté en el rango de un byte (0x00 - 0xFF)
                pc_next(mac)
                return f"8XY5 carry flag: {int(r > 0xFF)}"

            # 8XY6: SHR: shifts right V[x], LSB vit goes to V[15]
            case 6:
                mac.v[15] = (mac.v[x] & 1)
                mac.v[x] >>= mac.v[y]
                pc_next(mac)
            # 8XY7: Set Vx = Vy - Vx, set VF = NOT borrow.

            case 7:
                mac.v[15] = int(mac.v[x] > mac.v[y]!=0)
                mac.v[x] = mac.v[y] - mac.v[x]
                pc_next(mac)
            # 8X0E: SHL: Shifts left V[x], MSB bit goes to V[15]
            case 0xE:
                mac.v[15] = ((mac.v[x] & 0x80) != 0)
                mac.v[x] <<= 1
                pc_next(mac)
                return f"0xE carry flag: {((mac.v[x] & 0x80) != 0)}"
            
        return "Arithmetic"

    @staticmethod
    def skip_not_equal_vx_vy (mac, opcode) -> str:
        """Skip next instruction if Vx != Vy.

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        if mac.v[OPCODE_X(opcode)] != mac.v[OPCODE_Y(opcode)]:
            pc_next(mac)
        pc_next(mac)

        return f"skip_not_equal vx: {mac.v[OPCODE_X(opcode)]} != vy: {OPCODE_Y(opcode)} "

    @staticmethod
    def load_i (mac, opcode) -> str:
        """Función para LD i, x: I = nnn 

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.i = OPCODE_NNN(opcode)
        pc_next(mac)
        return f"load i [{mac.i}] = nnn: [{OPCODE_NNN(opcode)}]"

    @staticmethod
    def c_random (mac, opcode):
        # RND x, kk: v[x] = random() % kk (mascara de bits)
        """_summary_

        Args:
            opcode (hex): _description_

        Returns:
            str: _description_
        """
        mac.v[OPCODE_X(opcode)] = random(0,0xFF) & OPCODE_KK(opcode)
        pc_next(mac)
        return "rnd"

    @staticmethod
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
            pc_next(mac)
            return f"sprite {sprite} | px: {Vx} py: {Vy} | n: {N} | addr: {addr} | collision"            
        else:
            mac.v[15] = 0
            pc_next(mac)
            return f"sprite {sprite} | px: {Vx} py: {Vy} | n: {N} | addr: {addr}"

    @staticmethod
    def e_branch(mac, opcode) -> str:
        """Two instructions, EX9E & EXA1
        
        EX9E: Skip next instruction if key with the value of Vx is pressed.
        
        EXA1: Skip next instruction if key with the value of Vx is not pressed.
        
        Args:
            mac (_type_): _description_
            opcode (_type_): _description_

        Returns:
            str: _description_
        """
        match OPCODE_KK(opcode):
            
            # Skip next instruction if key with the value of Vx is pressed.
            case 0x9E:
                mac.pc += 2
            
            # Skip next instruction if key with the value of Vx is not pressed.
            case 0xA1:
                mac.pc += 2

    @staticmethod
    def f_branch (mac, opcode) -> str:
        """0xF Init opcodes

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
                pc_next(mac)
                
            # Wait for a key press, store the value of the key in Vx.
            case 0x0A:
                pc_next(mac)
            
            # LD DT, v[x]: DT = v[x]
            case 0x15:
                mac.delay_timer = mac.v[x]
                pc_next(mac)

            # BEEP!, LD ST, v[x] -> ST = v[x]
            case 0x18:
                mac.stack = mac.v[x]
                pc_next(mac)

            # ADD i, v: i += v[x]
            case 0x1E:
                s = mac.i + mac.v[x];
                if s > 0xFFF:
                    mac.v[0xF] = 1
                else:
                    mac.v[0xF] = 0;
                mac.i += mac.v[x];
                pc_next(mac)
                
            # LD F, Set I = location of sprite for digit Vx.
            case 0x29:
                mac.i = 0x50 + (mac.v[x] & 0xF) * 5
                pc_next(mac)
                
            # LD B, Vx, Store BCD representation of Vx in memory locations I, I+1, and I+2.
            case 0x33:
                val = mac.v[x]
                
                ones = (val%10)
                tens = (val//10)%10
                hundreds = (val//100)
                
                mac.memory[mac.i]     = mac.v[hundreds]
                mac.memory[mac.i + 1] = mac.v[tens]
                mac.memory[mac.i + 2] = mac.v[ones]

                pc_next(mac)
                return f"i {mac.memory[mac.i]} 0 i+1| {mac.memory[mac.i+1]} |i+2 {mac.memory[mac.i+2]}"

            # LD [i] Vx, Store registers V0 through Vx in memory starting at location I.
            case 0x55:
                for i in range(x+1):
                    mac.memory[(mac.i + i)&0xFFF] = mac.v[i]
                pc_next(mac)
            # Fx65 - LD Vx, [I] Read registers V0 through Vx from memory starting at location I.
            # The interpreter reads values from memory starting at location I into registers V0 through Vx.
            case 0x65:
                for i in range(x+1):
                    mac.v[i] = mac.memory[mac.i+i & 0xFFF]
                pc_next(mac)
                #mac.i = mac.i + x + 1
                #mac.pc += 2
        return f"f_branch"