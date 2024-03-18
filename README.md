# Term_Project

## Introduction

Brendan and the Jo(h)nathans NERF turret was the term project for the second mechatronics class at Cal Poly. The goal of this turret was to use closed-loop motor control and a thermal camera to detect a target, aim, and fire a foam dart automatically. The finished product is shown in Figure 1.

![Figure 1](https://github.com/jonoromo/Term_Project/blob/main/Figure%201.png)

## Hardware Overview

The main panning axis is driven by a Pololu #4743 12V DC motor with a 50:1 gearbox. Because the gear ratio is slowing down the motor’s rotation to 60 rpm, a 90o bevel gear train with a 1:1 ratio was chosen to avoid reducing the speed further. Worm gears were considered because of their avoidance of backwards driving, but bevel gears were chosen over worm gears because worm gear sets could not be found in a 1:1 ratio.

![Figure 2](https://github.com/jonoromo/Term_Project/blob/main/Figure%202.png)

Figure 2. CAD isolation of bevel geartrain. 

Bevel gears were selected to place the motor close to the table datum while not interfering with the gun’s panning axis. Due to the distance between the bearing and the top bevel gear, runout in the bearing is magnified. This limited the achievable accuracy of our PI controller. A future improvement would be to use a more precise bearing, or a motor with a smaller gear reduction to decrease the pinion diameter and bring the gear closer to the bearing and reduce the runout.

Imprecision in the gear and bearing made position calibration difficult as well. Before each duel, the gun was referenced against a square to start from a repeatable point.  

The motors used in the project were powered via a benchtop power supply set to 12V 1A. A motor driver attached to the nucleo distributed 12V power to the panning motor and the flywheels in the gun. The Nucleo was used to power the encoder on the panning motor as well as the servo used to pull the trigger (our original intention was to power the servo through the motor driver, but after testing we decided it was okay for it to be powered through the Nucleo due to its short operating time). The servo was controlled via an output pin on the nucleo, and the panning motor encoder value was read from input pins on the Nucleo to provide our software with a means to control the position of the panning motor. Figure 3 includes a full wiring diagram for the components used in our term project.

![Figure 3](https://github.com/jonoromo/Term_Project/blob/main/Figure%203.png)

Figure 3: Wiring Diagram

## Software Overview

With each weekly lab assignment, pieces of code were written, and hardware was implemented building up to the term project. The motor controller class was upgraded from proportional only control to include both proportional and integral control. The main pieces are as follows: motor controller, including driving the DC motor and reading its encoder, tuning the closed-loop proportional and integral gains, cooperative multitasking to drive two motors simultaneously, and finally configuring the thermal camera using inter-integrated circuit (I2C). All software documentation can be found at https://jonoromo.github.io/Term_Project/index.html. The main program that we used to control the nerf turret was designed with two tasks consisting of multiple states. Task 1 was responsible for all camera operations, including taking the image after 5 seconds and processing the data to provide usable information for the motor. Task 2 contained all the code for controlling the panning axis motor, controlling the firing servo, and turning on the flywheel for the nerf gun. Figure 4 shows the task diagram for our main program file. Figures 5 and 6 contain state transition diagrams for Task 1 and Task 2 respectively.

![Figure 4](https://github.com/jonoromo/Term_Project/blob/main/Figure%204.jpg)

Figure 4. Overall Task Diagram

![Figure 5](https://github.com/jonoromo/Term_Project/blob/main/Figure%205.jpg)

Figure 5. Task 1 State Transition Diagram

![Figure 6](https://github.com/jonoromo/Term_Project/blob/main/Figure%206.jpg)

Figure 6. Task 2 State Transition Diagram

## Results

The turret performed well, tracking the target and firing after the initial 5 seconds. Accuracy was hit-or-miss, largely due to backlash in our gears and play in the bearing. Each piece of the turret was tested individually: the initial 180o turn was approximated by eye. By outputting ASCII characters from the thermal camera, we found which way was “up,” and determined that we wanted the camera as close as possible to the target to improve resolution. The ASCII image also revealed that we could omit rows on the top and bottom to eliminate heat from ceiling lights and dead zones on the table, respectively. 

Pivoting the turret a correct amount of encoder counts corresponding to the image on the thermal camera involved a process of trial and error. Due to backlash in the motor gearbox and the bevel gears, we needed different calibration constants depending whether the turret was continuing in the same direction as the initial 180o turn or reversing the other direction. This workaround could have been avoided if our geartrain was more accurate.

## Recommendations

Our method of translating the data from the camera to a setpoint for the motor could be improved upon as future work for this device. The method we used involved normalizing the pixel value to the center line, then amplifying that value by a calibration constant and adding it to the current encoder value. This method worked fairly well to get the motor to move a reliable amount based on how far the target was from center. An alternate method could be to define 7 different angle positions across the range of target positions. Since there is such a small window of movement, these set positions would be able to hit a target if they are in that range of angles. The data from the motor would define which angle range the target is located in and provide a corresponding setpoint for the motor. This method would improve the repeatability of our turret’s panning movements with tested setpoints that are achievable by our hardware.



