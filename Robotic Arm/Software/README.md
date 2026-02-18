# Robotic Arm (student repo)

This folder contains the controller and example student template for the 4-axis robotic arm.

What students need:

- Edit only `run_program.py` with a function `program(arm)`.
- Copy your `run_program.py` into this folder (USB drop-in works).
- Run the controller and press `t` to execute your latest program.

Files of interest:

- `teleop_keyboard.py` — main controller (runs on the PC)
- `arm.py` — high-level Python API for the arm
- `run_program.py` — student script (edit this)
- `servo_test/servo_test.ino` — Arduino sketch to upload to the Nano
- `SETUP_AND_USAGE.md` — full instructions and quick start

Quick start:

```bash
# Install once
pip install pyserial keyboard

# Start controller
python teleop_keyboard.py
```

See `SETUP_AND_USAGE.md` for more detail and safety notes.
