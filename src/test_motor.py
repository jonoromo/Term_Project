# Testing Motor Driver

import motor_driver as moto
import utime

if __name__ == "__main__":
    
    enPin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
    in2_pin = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
    in1_pin = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
    timmy = pyb.Timer(3, freq=20000) # Initialize timer
    ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
    ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
    
    moe = moto.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg) # Create instance of motor driver
                                                                           # class as moe
    while True:
        moe.set_duty_cycle (50)
        utime.sleep(2)
        moe.set_duty_cycle (0)
        utime.sleep(2)
        moe.set_duty_cycle (100)
        utime.sleep(2)
        moe.set_duty_cycle (0)
        utime.sleep(2)
        moe.set_duty_cycle (-50)
        utime.sleep(2)
        moe.set_duty_cycle (0)
        utime.sleep(2)
        moe.set_duty_cycle (-100)
        utime.sleep(2)
        moe.set_duty_cycle (0)
        utime.sleep(2)