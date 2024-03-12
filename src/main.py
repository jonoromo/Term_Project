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
            wait_cam = 200
            t1_state = 1
            
        # State 1: Wait for picture    
        elif (t1_state == 1):
            # Keep trying to get an image; this could be done in a task, with
            # the task yielding repeatedly until an image is available
            
            if i < wait_cam:
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
            
            start = 730
            wait_fire = 350
            con = motor_controller.Controller(0.075, 0.001, start)
            setpoint = start
            t2_state = 1
            moved = 0
            
            enPin_f = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP) # Initialize pin en_pin (PA10)
            in2_pin_f = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) # Initialize pin in2_pin (PB5)
            in1_pin_f = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP) # Initialize pin in1_pin (PB4)
            timmy_f = pyb.Timer(5, freq=20000) # Initialize timer
            ch_pos_f = timmy_f.channel(1, pyb.Timer.PWM, pin=in2_pin_f) # Initialize positive direction timer channel
            ch_neg_f = timmy_f.channel(2, pyb.Timer.PWM, pin=in1_pin_f) # Initialize negative direction timer channel
            
            fly = motor_driver.MotorDriver(enPin_f, in2_pin_f, in1_pin_f, timmy_f, ch_pos_f, ch_neg_f)
            fly.set_duty_cycle(50)
            
        elif (t2_state == 1):
            
            con.clear_esum(0)
            hold = 0
            for i in range(80):
                moe.set_duty_cycle(con.run(setpoint,enc.read()))
                print(enc.read())
                if abs( setpoint - enc.read() ) < 15:
                    if hold > 4:
                        print('DONE')
                        break
                    else:
                        hold += 1
                      
                yield 0
            moe.set_duty_cycle(0)
            old_sp = setpoint
            t2_state = 2
            n = 0
            
            if moved == 1:
                
                time.sleep_ms(100)
                pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP)
                pinC7.value(0)
                time.sleep_ms(20)

                pinC7.value(1)
                time.sleep_us(2000)
                pinC7.value(0)
                time.sleep_ms(18)

                time.sleep_ms(300)

                pinC7.value(1)
                pinC7.value(0)

                pinC7.value(1)
                time.sleep_us(500)
                pinC7.value(0)
                time.sleep_ms(19)

                time.sleep_ms(100)

                pinC7.value(1)
                pinC7.value(0)
                time.sleep_ms(200)
                fly.set_duty_cycle(0)
                moved += 1
                
            else:
                moved += 1
            
            yield 0
                
        elif (t2_state == 2):
            
            if n < wait_fire:
                n += 1
            else:
                val = my_share.get()
                if val < 1450:
                    setpoint = enc.read()+0.055*(val-1450)
                else:
                    setpoint = enc.read()+0.075*(val-1450)
                print('SP',setpoint)
                con.set_Ki(0.1)
                t2_state = 1
            yield 0

 
# This share holds a signed short (16-bit) integer
my_share = task_share.Share ('h', name="My Share")
 
# In another task, read data from the share


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
task1 = cotask.Task(task1_fun, name="Task_1", priority=2, period=20)
task2 = cotask.Task(task2_fun, name="Task_2", priority=1, period=10)

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

    
