"""!
@file motor_controller.py
    This file contains class Controller which implements a closed loop PI motor controller. 

@author Brendan Stratford
@author Johnathan Waldmire
@author Jonathan Romeo
@date   3/17/2024
"""
class Controller:
    """!
    Implements PI control for a DC motor. Gain values and a desired encoder value set point are specified upon initialization. Works with the motor driver class to control the motor PWM signal.
    """
    
    def __init__(self, k_p, k_i, sp):
        """!
        Initialize variables and make them discoverable within the class.
        Create empty lists for time and position.
        @param k_p: proportional gain value
        @param sp setpoint: the angle [encoder counts]
        @param resp_time: response time list: the time our program has been
        running. Incremented by .1s from 0s until setpoint is reached.
        @param resp_pos: response position list: reads encoder position for
        every response time increment, stored in a list.
        """
        self.k_p = k_p
        self.k_i = k_i
        self.sp = sp
        self.resp_time = []
        self.resp_pos = []
        
    def clear_esum(self, esum):
        """!
        Redundant function to allow user to set a different setpoint. 
        @param sp: setpoint: the desired position [encoder counts]
        """
        self.esum = esum
    
    def run(self, sp, act):
        """!
        Defines and returns PWM. Takes setpoint and current encoder reading,
        and returns a PWM signal telling the motor how hard to work to get to the
        desired position.
        @param sp: setpoint: the desired position [encoder counts]
        @param act: actual encoder reading [encoder counts]
        """
        err = sp - act
        self.esum += err
        if self.esum > 20000:
            self.esum = 20000
        
        if abs(err) < 10:
            PWM = self.k_p*(err) - self.k_i*(self.esum)
        elif abs(err) > 50:
            PWM = self.k_p*(err) + self.k_i*(self.esum)
        else:
            PWM = self.k_p*(err) + self.k_i*(self.esum)
        
        return PWM
    
    def set_setpoint(self, sp):
        """!
        Redundant function to allow user to set a different setpoint. 
        @param sp: setpoint: the desired position [encoder counts]
        """
        self.sp = sp
        
    def set_Kp(self, k_p):
        """!
        Redundant function to allow user to set a different proportional gain.
        @param k_p: proportional gain value
        """
        self.k_p = k_p
        
    def set_Ki(self, k_i):
        """!
        Redundant function to allow user to set a different proportional gain.
        @param k_p: proportional gain value
        """
        self.k_i = k_i
        
    def meas_time(self, time):
        """!
        Measures time by appending the current time to a list of response times.
        @param time: appends time, corresponding to the utime count every 0.1s
        (assigned below)
        """
        self.resp_time.append(time) # appends time, corresponding to the
                                    # utime count every 0.1s (assigned below)
        
    def meas_pos(self, pos):
        """!
        Measures position by recording the encoder's current position, every 0.1s.
        @param pos: found by using the read function of encoder_reader
        """
        self.resp_pos.append(pos)
    
    def print_results(self):
        """!
        Matches time data to position data and prints the two lists when called.
        """
        init_time = self.resp_time[0]
        for i in range(len(self.resp_time)-1):
            self.resp_time[i] -= init_time
            print(f'{self.resp_time[i]},{self.resp_pos[i]}')
        
if __name__ == "__main__":
    import motor_driver as moto
    import encoder_reader
    import utime
    
#     enPin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
#     in2_pin = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
#     in1_pin = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
#     timmy = pyb.Timer(3, freq=20000) # Initialize timer
#     ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
#     ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
#     
#     moe = moto.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg)
#     
#     pinA = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
#     pinB = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
# 
#     timer = pyb.Timer(4, prescaler=1, period=65535)
#     chan_A = timer.channel(1, pyb.Timer.ENC_AB, pin=pinA)
#     chan_B = timer.channel(2, pyb.Timer.ENC_AB, pin=pinB)
#     
#     enc = encoder_reader.Encoder(pinA, pinB, timer, chan_A, chan_B)
#     
#     con = Controller(0.1, 100)
#     for i in range(50):
#         moe.set_duty_cycle(con.run(1000,enc.read()))
#         con.meas_time(utime.ticks_ms())
#         con.meas_pos(enc.read())
#         utime.sleep_ms(10)
#         if con.run(100,enc.read()) < 10:
#             break
#     moe.set_duty_cycle(0)   
#     con.print_results()
    
    
               
    
    # Get references to the share and queue which have been passed to this task
    enPin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
    in2_pin = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
    in1_pin = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
    timmy = pyb.Timer(3, freq=20000) # Initialize timer
    ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
    ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
    
    moe = moto.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg)
    
    pinA = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
    pinB = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)

    timer = pyb.Timer(4, prescaler=1, period=65535)
    chan_A = timer.channel(1, pyb.Timer.ENC_AB, pin=pinA)
    chan_B = timer.channel(2, pyb.Timer.ENC_AB, pin=pinB)
    
    enc = encoder_reader.Encoder(pinA, pinB, timer, chan_A, chan_B)
    
    con = Controller(0.2, 100)
    setpoint = 1000
    
    for i in range(100):
        moe.set_duty_cycle(con.run(setpoint,enc.read()))
        con.meas_time(utime.ticks_ms())
        con.meas_pos(enc.read())
        utime.sleep_ms(10)
        if con.run(setpoint,enc.read()) < 10:
            break
    moe.set_duty_cycle(0)
    con.print_results()
