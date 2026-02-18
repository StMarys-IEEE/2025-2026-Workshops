# Robotic Arm — Quick Student Guide

This controller supports two ways to control the 3-axis arm:

- Manual mode: real-time keyboard control
- Tesla mode: run a student script (`run_program.py`) that calls the `arm` API

Press `t` to toggle modes; press `q` to quit.

## Quick Start

1. Upload the Arduino sketch: open `servo_test/servo_test.ino` in the Arduino IDE and upload to the Nano (select correct COM port).
2. Install Python deps (run once):

```bash
pip install pyserial keyboard
```

3. Start the controller from the `Robotic Arm/` folder:

```bash
python teleop_keyboard.py
```

When prompted, enter the COM port number (e.g. `3` for `COM3`).

## Manual Controls (use while in MANUAL mode)

- W / S : move Y axis (up / down)
- A / D : move X axis (left / right)
- ← / → : move Z axis (left / right)
- ↑ / ↓ : gripper open / close
- t : switch to TESLA mode (run `run_program.py`)
- q : quit the controller

Notes: teleop packets are streamed at 50 Hz while in MANUAL mode.

## Tesla Mode — Student Workflow

Students only need to create or update `run_program.py` and copy it into the `Robotic Arm/` folder (USB drop-in works). The controller will load the latest `run_program.py` each time you press `t` and run its `program(arm)` function.

Template (save as `run_program.py`):

```python
def program(arm):
    # simple example: approach, grab, move, release
    arm.x_by_deg(30)
    arm.wait(0.5)
    arm.y_by_deg(40)
    arm.wait(0.5)
    arm.grip_by_deg(-20)  # close
    arm.wait(0.5)
    arm.z_by_deg(30)
    arm.wait(0.8)
    arm.grip_by_deg(20)   # open
    arm.wait(0.5)

    print('Program complete')
```

Important: the controller looks for a function named `program(arm)`; if the file has syntax errors or no `program`, the controller will print an error and return to MANUAL mode.

## Available `arm` Methods (brief)

- `arm.x_by_deg(deg)` — move X axis by degrees
- `arm.y_by_deg(deg)` — move Y axis by degrees
- `arm.z_by_deg(deg)` — move Z axis by degrees
- `arm.grip_by_deg(deg)` — move gripper by degrees
- `arm.move_us(axis, delta_us)` — move axis by microseconds (signed delta)
- `arm.set_us(axis, pos_us)` — set absolute position (microseconds)
- `arm.wait(seconds)` — interruptible wait
- `arm.stop()` — emergency stop
- `arm.set_us_per_deg(axis, us_per_deg)` — adjust conversion

All `arm` calls return `1` on success and `0` on error or when interrupted by pressing `t`.

## Troubleshooting (short)

- If the keyboard library fails: run the terminal as Administrator on Windows.
- If the COM port fails to open: verify the port in Device Manager and enter the correct COM number when prompted.
- If Arduino does not respond to a packet: check USB cable, baud rate (9600), and re-upload the sketch.

## Safety

- Always be ready to call `arm.stop()` or remove power if motion becomes unsafe.
- Respect mechanical limits and do not force servos beyond their range.

That's it — students only need to edit `run_program.py` and press `t` to run their code.
