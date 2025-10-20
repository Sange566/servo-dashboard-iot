import RPi.GPIO as GPIO
import time

servo_pin = 18
btn_left = 23
btn_right = 24
step = 60
min_angle = 0
max_angle = 180

def run_servo(event_queue):
    # Local angle variable
    angle = 90  # start centered

    GPIO.setmode(GPIO.BCM)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(btn_left, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(btn_right, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    pwm = GPIO.PWM(servo_pin, 50)
    pwm.start(0)

    def set_angle(a):
        duty = 2 + (a / 18)
        pwm.ChangeDutyCycle(duty)
        time.sleep(0.3)

    def smooth_move(target_angle):
        nonlocal angle
        step_size = 10
        if target_angle > angle:
            for a in range(angle, target_angle + 1, step_size):
                pwm.ChangeDutyCycle(2 + a / 18)
                time.sleep(0.03)
        else:
            for a in range(angle, target_angle - 1, -step_size):
                pwm.ChangeDutyCycle(2 + a / 18)
                time.sleep(0.03)
        angle = target_angle

    try:
        set_angle(angle)
        event_queue.put({"action": "Start", "angle": angle})
        while True:
            if GPIO.input(btn_left) == GPIO.LOW and angle > min_angle:
                new_angle = max(min_angle, angle - step)
                smooth_move(new_angle)
                event_queue.put({"action": "Rotated Left", "angle": angle})
                time.sleep(0.3)
            if GPIO.input(btn_right) == GPIO.LOW and angle < max_angle:
                new_angle = min(max_angle, angle + step)
                smooth_move(new_angle)
                event_queue.put({"action": "Rotated Right", "angle": angle})
                time.sleep(0.3)
    finally:
        pwm.stop()
        GPIO.cleanup()
