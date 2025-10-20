import evdev
import RPi.GPIO as GPIO
import time
import sys

# === Pin Setup ===
servo_pin = 18  # BCM 18
GPIO.setmode(GPIO.BCM)
GPIO.setup(servo_pin, GPIO.OUT)

# Setup PWM for servo (50 Hz)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

# === Servo Setup ===
angle = 90          # Start centered
min_angle = 0
max_angle = 180

# Step size and update rate
BASE_STEP = 30           # degrees per incremental move
UPDATE_INTERVAL = 0.02  # 50 Hz update

# Deadzone and center for analog stick
STICK_CENTER = 128
DEADZONE = 5

# === Helper Function ===
def set_angle(a):
    """Move servo to a specific angle immediately."""
    duty = 2 + (a / 18)
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.01)

# === Controller Setup ===
controller = evdev.InputDevice("/dev/input/event8")
print(f"✅ Using controller: {controller.name} at {controller.path}")

# Track input states
left_x = STICK_CENTER
x_pressed = False
circle_pressed = False
last_update = time.time()

try:
    set_angle(angle)
    print(f"Starting at {angle}°")

    for event in controller.read_loop():
        # === Update analog stick value ===
        if event.type == evdev.ecodes.EV_ABS and event.code == evdev.ecodes.ABS_X:
            left_x = event.value

        # === Update button states ===
        elif event.type == evdev.ecodes.EV_KEY:
            if event.code == evdev.ecodes.BTN_SOUTH:  # X button
                x_pressed = event.value == 1
            elif event.code == evdev.ecodes.BTN_EAST:  # Circle button
                circle_pressed = event.value == 1

        # === Continuous movement logic ===
        current_time = time.time()
        if current_time - last_update >= UPDATE_INTERVAL:
            # Movement from analog stick
            if left_x < STICK_CENTER - DEADZONE and angle > min_angle:
                angle = max(min_angle, angle - BASE_STEP)
                set_angle(angle)
            elif left_x > STICK_CENTER + DEADZONE and angle < max_angle:
                angle = min(max_angle, angle + BASE_STEP)
                set_angle(angle)

            # Movement from buttons
            if x_pressed and angle > min_angle:
                angle = max(min_angle, angle - BASE_STEP)
                set_angle(angle)
            elif circle_pressed and angle < max_angle:
                angle = min(max_angle, angle + BASE_STEP)
                set_angle(angle)

            last_update = current_time

        # Optional: print live status
        sys.stdout.write(
            f"\rLeft stick X: {left_x} | X pressed: {x_pressed} | Circle pressed: {circle_pressed} | Servo angle: {angle}°   "
        )
        sys.stdout.flush()

except KeyboardInterrupt:
    print("\n❌ Program interrupted")

finally:
    pwm.stop()
    GPIO.cleanup()
