Demos folder — drop-in student examples

These example scripts are *not* run directly by the controller. To run a demo, copy the demo file you want to `run_program.py` in the `Robotic Arm/` folder (or copy its contents into the existing `run_program.py`).

Included demos:

- `demo_indefinite.py` — runs indefinitely until interrupted by pressing `t` (useful for testing interrupt behavior).
- `demo_blink_gripper.py` — opens and closes the gripper repeatedly until interrupted.
- `demo_sweep_axes.py` — sweeps X/Y/Z back and forth until interrupted.
- `demo_with_helpers.py` — example structured program with helper functions (`go_home`, `grab_sequence`, `place_sequence`).

Usage:
1. Copy a demo to the controller folder and rename to `run_program.py`.
2. In MANUAL mode press `t` to execute it. Press `t` again to interrupt and return to MANUAL.

Safety: always be ready to call `arm.stop()` and remove power if motion becomes unsafe.
