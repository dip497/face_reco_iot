from gpiozero import AngularServo
from time import sleep
servo = AngularServo(18,initial_angle=0,min_pulse_width=0.0005,max_pulse_width=0.0025)

while (True):
    print("yes")
    servo.angle = 0
    sleep(2)
    print("yes2")
    servo.angle = -90
    sleep(2)
    servo.angle = 90
    sleep(2)