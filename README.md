# Garbage Collect Robot
>A network-controlled, garbage collecting robot, developed for the Raspberry Pi. Developed by John Matson in spring 2020 for BCIT's ELEX 4699, taught by Craig Hennesey.

## Usage
Current functionality includes local and remote motor control using a num-pad. Program also streams video over the network to the remote client. To operate the robot via local control, run robot.py on the Raspberry Pi. To operate the robot via remote control, connect the Pi and the remote to the same network, run robot.py on the Raspberry Pi, and run robotClient.py on the remote device of choice.

Robot controls are as follows:
* 1 : soft left
* 2 : reverse
* 3 : soft right
* 4 : hard left
* 5 : forward
* 6 : hard right
* \+ : servo up
* \- : servo down

Be aware that currently servo controls are not functioning properly. Also, as of yet, the robot only opperates in manual mode. Autonomous mode may be added in a future release.

## Implementation
KBHit.py is included to capture keyboard input without hitting return.

Code is implemented using the asyncio library to allow for mutiple simultaneous socket connections and motor control. All blocking functions should be called using await.
