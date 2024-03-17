"""!
@file main.py
    This file is uploaded to a Nucleo STM32 to control the "Brendan and the Jo(h)nathans"
    NERF turret. The file is written to cooperatively multitask, using a thermal camera,
    DC motor with closed loop PI control, and servomotor.

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
    @brief   Accepts camera input via I2C.
    @details Camera processing. Takes a picture after 5 seconds, when the target is frozen.
             Filters data, omitting rows and columns on the edges of the frame to focus on the target.
    """
    
    t1_state = 0
    
    while(True):
        
        # State 0: INIT - Set up camera
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

            # Select MLX90640 camera I2C address, normally 0x33, and check the bus
            i2c_address = 0x33
            scanhex = [f"0x{addr:X}" for addr in i2c_bus.scan()]

            # Create the camera object and set it up in default mode
            camera = mlx_cam.MLX_Cam(i2c_bus)
            camera._camera.refresh_rate = 10.0
            i = 0
            wait_cam = 200 # total wait = wait_cam*task_period = 4 s
            t1_state = 1
            
        # State 1: TAKE PICTURE  
        elif (t1_state == 1):
            
            # Keep trying to get an image
            
            if i < wait_cam: # cooperatively holds Task 1 in this state until 5 seconds
                i += 1       # has passed and a picture should be taken
            else:
                image = None
                while not image:
                    image = camera.get_image_nonblocking() # take picture
                t1_state = 2
            yield 0
        
        # State 2: DATA PROCESSING
        elif (t1_state == 2):
            print('FREEZE')                             # runs function in camera class
            val = camera.get_csv(image, limits=(0, 99)) # to get average hot pixel value
            my_share.put(round(val*100)) # magnifies pixel value to store as a whole number  
            print('VAL',val)
            gc.collect()
            t1_state = 3
            yield 0
         
        # State 3: WAIT
        elif (t1_state == 3):
            
            t1_state = 3 # holds camera task, no more pictures to be taken
            yield 0
            

def task2_fun():
    """!
    @brief   Motor control: both panning axis and trigger-pull servo.
    @details After initializing motor, the panning axis spins 180 deg.
             Both flywheels are turned on.
             Panning motor turns gun according to setpoint from thermal camera.
             Servo pulls trigger and returns to neutral position.
    
    """
    
    t2_state = 0
    
    while(True):
        
        # State 0: INIT - Set up motors
        if (t2_state == 0):
            
            # Panning Motor Initialization
            enPin = pyb.Pin(pyb.Pin.board.PA10, pyb.Pin.OUT_PP) # Initialize pin en_pin
            in2_pin = pyb.Pin(pyb.Pin.board.PB4, pyb.Pin.OUT_PP) # Initialize pin in2_pin
            in1_pin = pyb.Pin(pyb.Pin.board.PB5, pyb.Pin.OUT_PP) # Initialize pin in1_pin
            timmy = pyb.Timer(3, freq=20000) # Initialize timer
            ch_pos = timmy.channel(2, pyb.Timer.PWM, pin=in2_pin) # Initialize positive direction timer channel
            ch_neg = timmy.channel(1, pyb.Timer.PWM, pin=in1_pin) # Initialize negative direction timer channel
            moe = motor_driver.MotorDriver(enPin, in2_pin, in1_pin, timmy, ch_pos, ch_neg)
            
            # Panning Motor Encoder Initialization
            pinA = pyb.Pin(pyb.Pin.board.PB6, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
            pinB = pyb.Pin(pyb.Pin.board.PB7, pyb.Pin.AF_PP, pull=pyb.Pin.PULL_NONE, af=pyb.Pin.AF1_TIM2)
            timer = pyb.Timer(4, prescaler=1, period=65535)
            chan_A = timer.channel(1, pyb.Timer.ENC_AB, pin=pinA)
            chan_B = timer.channel(2, pyb.Timer.ENC_AB, pin=pinB)
            enc = encoder_reader.Encoder(pinA, pinB, timer, chan_A, chan_B)
            
            # Create controller instance, kp = 0.075, ki = 0.001
            con = motor_controller.Controller(0.075, 0.001, start)
            
            start = 730       # encoder value for 180 degree turn
            wait_fire = 350   # total wait = wait_fire*task_period = 3.5 s
            setpoint = start  # define setpoint variable
            moved = 0         # create variable to track number of motor movements
            
            # Flywheel PWM Initialization
            enPin_f = pyb.Pin(pyb.Pin.board.PC1, pyb.Pin.OUT_PP) # Initialize pin en_pin
            in2_pin_f = pyb.Pin(pyb.Pin.board.PA0, pyb.Pin.OUT_PP) # Initialize pin in2_pin
            in1_pin_f = pyb.Pin(pyb.Pin.board.PA1, pyb.Pin.OUT_PP) # Initialize pin in1_pin
            timmy_f = pyb.Timer(5, freq=20000) # Initialize timer
            ch_pos_f = timmy_f.channel(1, pyb.Timer.PWM, pin=in2_pin_f) # Initialize positive direction timer channel
            ch_neg_f = timmy_f.channel(2, pyb.Timer.PWM, pin=in1_pin_f) # Initialize negative direction timer channel
            fly = motor_driver.MotorDriver(enPin_f, in2_pin_f, in1_pin_f, timmy_f, ch_pos_f, ch_neg_f)
            
            # Turn on nerf gun flywheel
            fly.set_duty_cycle(50)
            
            t2_state = 1
        
        # State 1: MOVE/FIRE
        elif (t2_state == 1):
            
            con.clear_esum(0) # clears esum (for integral control)
            hold = 0          # reset hold value
            for i in range(80):
                moe.set_duty_cycle(con.run(setpoint,enc.read())) # provide PWM to panning motor
                print(enc.read())
                if abs( setpoint - enc.read() ) < 10: # if the error is less than 10 encoder
                    if hold > 4:                      # values, then this if statement is
                        print('DONE')                 # entered. If the error is less than 10
                        break                         # for 5 consecutive calls, the control
                    else:                             # loop breaks.
                        hold += 1
                      
                yield 0
            moe.set_duty_cycle(0) # set PWM to 0 when motor has reached the setpoint
            old_sp = setpoint
            t2_state = 2
            n = 0
            
            if moved == 1: # only happens after the motor has made its aim correction
                
                time.sleep_ms(100)
                pinC7 = pyb.Pin(pyb.Pin.board.PC7, pyb.Pin.OUT_PP) # initialize PC7 for output
                pinC7.value(0)
                time.sleep_ms(20)
                
                # 20 ms pulse with 2 ms high - pull trigger in
                pinC7.value(1)
                time.sleep_us(2000)
                pinC7.value(0)
                time.sleep_ms(18)
                
                # Wait to allow trigger to move through full trigger pull
                time.sleep_ms(300)
                
                # Rapid on-off to interrupt previous signal pulse
                pinC7.value(1)
                pinC7.value(0)
                
                # 20 ms pulse with 0.5 ms high - release trigger
                pinC7.value(1)
                time.sleep_us(500)
                pinC7.value(0)
                time.sleep_ms(19)
                
                # Wait to allow servo to fully release the trigger
                time.sleep_ms(100)
                
                # Rapid on-off to stop the servo at trigger edge
                pinC7.value(1)
                pinC7.value(0)
                
                # Wait, then set flywheel to off
                time.sleep_ms(200)
                fly.set_duty_cycle(0)
                moved += 1 # increases moved so that the gun doesn't fire a second time
                
            else:
                moved += 1 # increases moved so that the firing sequence will happen
                           # after the movement from camera data has occured
            
            yield 0
        
        # State 2: WAIT
        elif (t2_state == 2):
            
            if n < wait_fire: # cooperatively holds motor task for 5 seconds until
                n += 1        # the camera has taken its picture and processed the data
            else:
                val = my_share.get() # assigns share data as val
                
                # Translation of camera data to new setpoint
                if val < 1450:
                    setpoint = enc.read()+0.055*(val-1450) # Calibration for moving left
                else:
                    setpoint = enc.read()+0.075*(val-1450) # Calibration for moving right
                print('SP',setpoint)
                con.set_Ki(0.1) # Set higher ki value for smaller movements
                t2_state = 1
            yield 0

 
# This share holds a signed short (16-bit) integer
my_share = task_share.Share ('h', name="My Share")
 
# In another task, read data from the share

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

    
