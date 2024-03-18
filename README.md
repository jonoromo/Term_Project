# Term_Project

Introduction

Brendan and the Jo(h)nathans NERF turret was the term project for the second mechatronics class at Cal Poly. The goal of this turret was to use closed-loop motor control and a thermal camera to detect a target, aim, and fire a foam dart automatically. The finished product is shown in Figure 1.

![first plot](https://github.com/jonoromo/Term_Project/blob/main/Figure%201.png)

Hardware Overview

The main panning axis is driven by a Pololu #4743 12V DC motor with a 50:1 gearbox. Because the gear ratio is slowing down the motor’s rotation to 60 rpm, a 90o bevel gear train with a 1:1 ratio was chosen to avoid reducing the speed further. Worm gears were considered because of their avoidance of backwards driving, but bevel gears were chosen over worm gears because worm gear sets could not be found in a 1:1 ratio.

