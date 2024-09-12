import board
import time
import digitalio
from adafruit_lsm6ds.lsm6dsox import LSM6DSOX as LSM6DS
from busio import I2C
from adafruit_lis3mdl import LIS3MDL
from adafruit_debouncer import Debouncer

i2c = I2C(board.SCL, board.SDA)  # Create library object using our Bus I2C port
accel_gyro = LSM6DS(i2c)
mag = LIS3MDL(i2c)

# Button 1 ON OFF
pin1 = digitalio.DigitalInOut(board.D6)
pin1.direction = digitalio.Direction.INPUT
pin1.pull = digitalio.Pull.UP
switch1 = Debouncer(pin1)

# Button 2 START
pin2 = digitalio.DigitalInOut(board.D5)
pin2.direction = digitalio.Direction.INPUT
pin2.pull = digitalio.Pull.UP
switch2 = Debouncer(pin2)

print("Calculating Bias. Center Position and Tilt of Glove and hit Start")
start = False
on = True
while start is False:
    switch1.update()
    if switch1.fell:
        on = not on

    if on:
        switch2.update()
        if switch2.fell:
            acceleration = accel_gyro.acceleration
            ax_bias = acceleration[0]
            ay_bias = acceleration[1]
            az_bias = acceleration[2]
            gyro = accel_gyro.gyro
            gx_bias = gyro[0]
            gy_bias = gyro[1]
            gz_bias = gyro[2]

            start = True
print("Bias Calculated.")
print(
    "Acceleration Bias: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2"
    .format(ax_bias, ay_bias, az_bias))
print(
    "Gyro Bias: X:{0:7.2f}, Y:{1:7.2f}, Z:{2:7.2f} m/s^2"
    .format(gx_bias, gy_bias, gz_bias))

dT = 0.033
cooldown = 0
position = 7
tilt_cooldown = 0
rotation = 0
while True:
    # Update
    switch1.update()
    if switch1.fell:
        on = not on

    if on:
        gyro = accel_gyro.gyro
        gx = gyro[0] - gx_bias
        gy = gyro[1] - gy_bias
        gz = gyro[2] - gz_bias

        acceleration = accel_gyro.acceleration
        ax = acceleration[0] - ax_bias
        ay = acceleration[1] - ay_bias
        az = acceleration[2] - az_bias

        switch2.update()
        if switch2.fell:
            acceleration = accel_gyro.acceleration
            ax_bias = acceleration[0]
            ay_bias = acceleration[1]
            az_bias = acceleration[2]
            gyro = accel_gyro.gyro
            gx_bias = gyro[0]
            gy_bias = gyro[1]
            gz_bias = gyro[2]

        x_tilt = abs(ay) > 1.0 or abs(az) > 1.0 or abs(
            gz) > 0.5 or abs(gy) > 0.5 or abs(gx) > 0.5
        cooldown -= 1
        tilt_cooldown -= 1

        if not x_tilt and cooldown < 0:
            if ax < -1.0:
                print("move_right()")
                position += 1
                if position > 15:
                    position = 15
                cooldown = 6

            if ax > 1.0:
                print("move_left()")
                position -= 1
                if position < 0:
                    position = 0
                cooldown = 6

        if tilt_cooldown < 0:
            if ay > 2.5:
                print("rotation()")
                rotation += 1
                if rotation > 3:
                    rotation = 0
                tilt_cooldown = 10

            if ay < -2.5:
                print("drop()")
                tilt_cooldown = 20

        output = ""
        for x in range(0, position):
            output += "[ ]"

        if rotation == 0:
            output += "[|]"
        elif rotation == 1:
            output += "[/]"
        elif rotation == 2:
            output += "[-]"
        elif rotation == 3:
            output += "[\\]"

        for x in range(position, 16):
            output += "[ ]"

        # print("x_Tilt = {0}   Acceleration: X:{1:7.2f}, Y:{2:7.2f}, Z:{3:7.2f} m/s^2"
        #      .format(x_tilt, ax, ay, az, *gyro))
        # print("Tilt = {0}   Gyro: X:{1:7.2f}, Y:{2:7.2f}, Z:{3:7.2f} rad/s"
        #       .format(tilt, ax, ay, az, *gyro))
        # print("Tilt = {0} Cooldown = {1}".format(x_tilt, cooldown))
        print(output)

        time.sleep(dT)
