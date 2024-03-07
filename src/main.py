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
import utime as time
from machine import Pin, I2C
from mlx90640 import MLX90640
from mlx90640.calibration import NUM_ROWS, NUM_COLS, IMAGE_SIZE, TEMP_K
from mlx90640.image import ChessPattern, InterleavedPattern
import mlx_cam
import task_share

def task1_fun():
    """!
    Camera processing.
    """
    
    t1_state = 0
    
    while(True):
        
        #print('Task 1 =',t1_state)
        
        # State 0: Set up camera
        if (t1_state == 0):
            
            moved = 0
            
            import gc

            # The following import is only used to check if we have an STM32 board such
            # as a Pyboard or Nucleo; if not, use a different library
            try:
                from pyb import info

            # Oops, it's not an STM32; assume generic machine.I2C for ESP32 and others
            except ImportError:
                # For ESP32 38-pin cheapo board from NodeMCU, KeeYees, etc.
                i2c_bus = I2C(1, scl=Pin(22), sda=Pin(21))

            # OK, we do have an STM32, so just use the default pin assignments for I2C1
            else:
                i2c_bus = I2C(1)

            #print("MXL90640 Easy(ish) Driver Test")

            # Select MLX90640 camera I2C address, normally 0x33, and check the bus
            i2c_address = 0x33
            scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]
            #print(f"I2C Scan: {scanhex}")

            # Create the camera object and set it up in default mode
            camera = mlx_cam.MLX_Cam(i2c_bus)
            #print(f"Current refresh rate: {camera._camera.refresh_rate}")
            camera._camera.refresh_rate = 10.0
            #print(f"Refresh rate is now:  {camera._camera.refresh_rate}")
            i = 0
            t1_state = 1
            
        # State 1: Wait for picture    
        elif (t1_state == 1):
            # Keep trying to get an image; this could be done in a task, with
            # the task yielding repeatedly until an image is available
            
            if i < 500:
                i += 1
            else:
                image = None
                while not image:
                    image = camera.get_image_nonblocking()
                t1_state = 2
            yield 0
        
        # State 2: Get position value
        elif (t1_state == 2):
            print('FREEZE')
            val = camera.get_csv(image, limits=(0, 99))
            my_share.put(round(val*100))
            print('VAL',val)
            gc.collect()
            #print(f"Memory: {gc.mem_free()} B free")
            t1_state = 3
            yield 0
         
        # State 3: Camera wait state 
        elif (t1_state == 3):
            
            t1_state = 3
            yield 0
            

def task2_fun():
    """!
    Panning motor control
    """
    
    t2_state = 0
    
    while(True):
        
        #print('Task 2 =',t2_state)
        
        if (t2_state == 0):
            
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
            
            start = 750
            con = motor_controller.Controller(0.2, start)
            setpoint = start
            t2_state = 1
            
        elif (t2_state == 1):
            
            for i in range(80):
                moe.set_duty_cycle(con.run(setpoint,enc.read()))
                #con.meas_time(time.ticks_ms())
                #con.meas_pos(enc.read())
                if abs(con.run(setpoint,enc.read())) < 10:
                    print('DONE')
                    break
                yield 0
            moe.set_duty_cycle(0)
            old_sp = setpoint
            t2_state = 2
            n = 0
            yield 0
                
        elif (t2_state == 2):
            
            if n < 250:
                n += 1
            else:
                val = my_share.get()
                setpoint = start+0.1*(val-1400)
                print('SP',setpoint)
                t2_state = 1
            yield 0


def task3_fun():
    """!
    Servo control
    """
    
    t3_state = 0
    
    while(True):
        
        if (t3_state == 0):
            yield
            
            
        elif (t3_state == 1):
            yield
            
                
        elif (t3_state == 2):
            yield
            


 
# This share holds a signed short (16-bit) integer
my_share = task_share.Share ('h', name="My Share")
 
# In another task, read data from the share


# Create a share and a queue to test function and diagnostic printouts
# share0 = task_share.Share('h', thread_protect=False, name="Share 0")
# q0 = task_share.Queue('L', 16, thread_protect=False, overwrite=False,
#                       name="Queue 0")

t1_state = 0
t2_state = 0
t3_state = 0

# Create the tasks. If trace is enabled for any task, memory will be
# allocated for state transition tracing, and the application will run out
# of memory after a while and quit. Therefore, use tracing only for 
# debugging and set trace to False when it's not needed
task1 = cotask.Task(task1_fun, name="Task_1", priority=1, period=10)
task2 = cotask.Task(task2_fun, name="Task_2", priority=5, period=20)
task3 = cotask.Task(task3_fun, name="Task_3", priority=3, period=20)

cotask.task_list.append(task1)
cotask.task_list.append(task2)
cotask.task_list.append(task3)

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

    
