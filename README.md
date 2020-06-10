An autonomous, garbage collecting robot, developed for the
Raspberry Pi.

Current functionality includes local and remote motor control
using a num-pad. Program also streams video over the network
to the remote client. To control the robot remotely, run
robot.py on the Raspberry Pi, then run robotClient.py on the
remote device of choice.

Robot controls are as follows:
1: soft left
2: reverse
3: soft right
4: hard left
5: forward
6: hard right
+: servo up
-: servo down

Code is implemented using the asyncio library to allow for
simultaneous mutiple socket connections and motor control.
All blocking functions should be called using await.

Be aware that currently servo controls are not functioning
properly. Also, as of yet, the robot only opperates in
manual mode. Autonomous mode may be added in a future
release.

Written by John Matson in spring 2020 for BCIT's ELEX 4699,
taught by Craig Hennesey.
