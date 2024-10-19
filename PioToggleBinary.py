###############################################################################################
# pio101824toggle.py  Use a toggle button to change direction (increment<-> decrement) of a   #
#                       4 led binary counter.                                                 #
#  X register: current counter, stored in OSR; then X holds the delay. After delay, counter   #
#              is restored from OSR.                                                          #
#  Y register: direction (incrementing or decrementing of counter). Y=0: decrementing         #
#                                                                  Y=nonzero: incrementing    #
#  Pin(15): toggle button  Each press changes direction of counter (increment<->decrement)    #
#  GPIO 00-03:  4 led binary counter; changes increment or decrement with each button press   #                                                       #
############################################################################################### 

from machine import Pin
from rp2 import asm_pio, PIO, StateMachine

pin15 = Pin(15, Pin.IN, Pin.PULL_DOWN) # toggle direction button, increment <-> decrement

@asm_pio(out_init = (PIO.OUT_LOW, ) *4, set_init = PIO.OUT_LOW, out_shiftdir = PIO.SHIFT_RIGHT)
def pio_prog():
    set(x, 0b1111)  # x: initialize counter
    set(y, 0)       # y: direction: 0 = decrement, non-zero = increment
    label('begin')
    mov(pins, x)    # display current counter 
    in_(x,4)        # save current counter in isr
    mov(osr, isr)   # save current counter to osr
    in_(null, 32)   # reset isr for reuse
    set(x, 0b11111) # x: delay amount to slow update of leds; counter saved in  osr
    label('delay')  
    jmp(pin, 'toggle_press') [31]  # check if toggle button pressed during delay
    jmp(x_dec, 'delay')      [31]  # delay until x=0
    out(x,4)        # x: current counter from osr;  delay is over, restore counter 
    jmp(not_y, 'decrement')  # decrement x:counter
    jmp('increment')         # didn't decrement, so it incremented
    label('toggle_press')
    wait(0, pin, 0)        # wait for toggle button to be released
    mov(y, invert(y))        # button toggled: change direction in y    
    out(x,4)                 # restore counter to x from osr
    jmp(not_y, 'decrement')  # check y for direction: increment or decrement
    label('increment')
    mov(x, invert(x))        # to increment x: invert x, decrement x, then invert x
    jmp(x_dec, 'next')
    label('next')
    mov(x, invert(x))        # counter x incremented by one
    jmp('begin')
    label('decrement')
    jmp(x_dec, 'begin')      # counter x decremented by one
    
sm0 = StateMachine(0, pio_prog, freq = 2000, jmp_pin = pin15, out_base = Pin(0), in_base = pin15)
sm0.active(1)
