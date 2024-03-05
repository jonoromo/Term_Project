"""!
@file main.py
    This file was adapted from a multitasking example to allow for two
    motors to be controlled simultaneously. 

@author JR Ridgely
@author Brendan Stratford
@author Johnathan Waldmire
@author Jonathan Romeo
@date   2021-Dec-15 JRR Created from the remains of previous example
@copyright (c) 2015-2021 by JR Ridgely and released under the GNU
    Public License, Version 2. 
"""

import gc
import pyb
import cotask
import task_share
import motor_driver
import encoder_reader
import motor_controller
import utime
        
def task1_fun():
    """!
    Controls one motor to reach a specified angle as quickly as possible with no overshoot.
    A finite state machine is implemented so that the motor only performs one step response
    and then transitions to a "wait" state (State 2).
    """
    
    t1_state = 0
    
    while(True):
        
        if (t1_state == 0):
            
            # Get references to the share and queue which have been passed to this task
            enPin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
            in2_pin = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
            in1_pin = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
            timmy = pyb.Timer(3, freq=20000) # Initialize timer
            ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
            ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
            
            moe = motor_driver.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg)
            
            pinA = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
            pinB = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)

            timer = pyb.Timer(4, prescaler=1, period=65535)
            chan_A = timer.channel(1, pyb.Timer.ENC_AB, pin=pinA)
            chan_B = timer.channel(2, pyb.Timer.ENC_AB, pin=pinB)
            
            enc = encoder_reader.Encoder(pinA, pinB, timer, chan_A, chan_B)
            
            con = motor_controller.Controller(0.06, 330)
            setpoint = 0
            t1_state = 1
            
        elif (t1_state == 1):
            
            #setpoint = 200
            setpoint = -200
            for i in range(60):
                moe.set_duty_cycle(con.run(setpoint,enc.read()))
                con.meas_time(utime.ticks_ms())
                con.meas_pos(enc.read())
                yield 0
            moe.set_duty_cycle(0)   
            con.print_results()
            t1_state = 2
            yield 0
                
        elif (t1_state == 2):
            
            t1_state = 2
            yield 0


def task2_fun():
    """!
    Controls one motor to reach a specified angle as quickly as possible with no overshoot.
    A finite state machine is implemented so that the motor only performs one step response
    and then transitions to a "wait" state (State 2).
    """
    
    t2_state = 0
    
    while(True):
        
        if (t2_state == 0):
            
            # Get references to the share and queue which have been passed to this task
            enPin = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
            in2_pin = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
            in1_pin = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
            timmy = pyb.Timer(5, freq=20000) # Initialize timer
            ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
            ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
            
            moe_2 = motor_driver.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg)
            
            pinA = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
            pinB = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)

            timer = pyb.Timer(4, prescaler=1, period=65535)
            chan_A = timer.channel(1, pyb.Timer.ENC_AB, pin=pinA)
            chan_B = timer.channel(2, pyb.Timer.ENC_AB, pin=pinB)
            
            enc_2 = encoder_reader.Encoder(pinA, pinB, timer, chan_A, chan_B)
            
            con_2 = motor_controller.Controller(0.06, 100)
            setpoint = 0
            t2_state = 1
            
        elif (t2_state == 1):
            
            setpoint += 100
            for i in range(60):
                moe_2.set_duty_cycle(con_2.run(setpoint,enc_2.read()))
                con_2.meas_time(utime.ticks_ms())
                con_2.meas_pos(enc_2.read())
                yield 0
            moe_2.set_duty_cycle(0)   
            con_2.print_results()
            t2_state = 2
            yield 0
                
        elif (t2_state == 2):
            
            t2_state = 2
            yield 0


# Create a share and a queue to test function and diagnostic printouts
# share0 = task_share.Share('h', thread_protect=False, name="Share 0")
# q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
#                       name="Queue 0")

t1_state = 0
t2_state = 0

# Create the tasks. If trace is enabled for any task, memory will be
# allocated for state transition tracing, and the application will run out
# of memory after a while and quit. Therefore, use tracing only for 
# debugging and set trace to False when it's not needed
task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=10)
task2 = cotask.Task(task2_fun, name="Task_2", priority=2, period=20)

cotask.task_list.append(task1)
cotask.task_list.append(task2)

# Run the memory garbage collector to ensure memory is as defragmented as
# possible before the real-time scheduler is started
gc.collect()

# Run the scheduler with the chosen scheduling algorithm. Quit if ^C pressed
while True:
    try:
        cotask.task_list.pri_sched()
    except KeyboardInterrupt:
        break

# Print a table of task data and a table of shared information data
# print('\n' + str (cotask.task_list))
# print(task_share.show_all())
# print(task1.get_trace())
# print('')
