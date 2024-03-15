
class Encoder:
    """"""
    def __init__(self, pinA, pinB, timer, chan_A, chan_B):
        self.pinA = pinA
        self.pinB = pinB
        self.timer = timer
        self.chan_A = chan_A
        self.chan_B = chan_B
        self.position = 0
        self.last_val = 0
        self.current_val = 0
        self.AR = 65535
    
    def read(self):
        
        ######
        self.current_val = self.timer.counter()
        self.delta = self.current_val - self.last_val
        delta_abs = self.delta
        if self.delta >= (self.AR+1)/2:
            self.delta -= self.AR+1
        elif self.delta <= -(self.AR+1)/2:
            self.delta += self.AR+1    

        self.last_val = self.current_val
        self.position += self.delta
        return self.position
    
    def zero(self):
        self.position = 0
        

if __name__ == "__main__":
    
    import utime
    import motor_driver as moto
    
    pinA = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
    pinB = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)

    timer = pyb.Timer(4, prescaler=1, period=65535)
    chan_A = timer.channel(1, pyb.Timer.ENC_AB, pin=pinA)
    chan_B = timer.channel(2, pyb.Timer.ENC_AB, pin=pinB)
    
    enc1 = Encoder(pinA, pinB, timer, chan_A, chan_B)
    
    pinA_2 = pyb.Pin(pyb.Pin.board.PC6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
    pinB_2 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)

    timer_2 = pyb.Timer(8, prescaler=1, period=65535)
    chan_A_2 = timer_2.channel(1, pyb.Timer.ENC_AB, pin=pinA_2)
    chan_B_2 = timer_2.channel(2, pyb.Timer.ENC_AB, pin=pinB_2)
    
    enc2 = Encoder(pinA_2, pinB_2, timer_2, chan_A_2, chan_B_2)
    
    enPin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
    in2_pin = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
    in1_pin = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
    timmy = pyb.Timer(3, freq=20000) # Initialize timer
    ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
    ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
    
    moe = moto.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg)
    
    moe.set_duty_cycle(-50)
    while True:
        print(enc2.read())
        utime.sleep(0.2)
    moe.set_duty_cycle(0)
        
    
    
    