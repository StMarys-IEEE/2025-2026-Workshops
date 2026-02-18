
"""Student Tesla program template (concise and well commented).

This file must define one function named `program(arm)`.
The controller dynamically loads `run_program.py` when you press `t` in
MANUAL mode and calls `program(arm)`. Keep your program focused and
use `arm.wait()` between moves so the arm has time to respond.

Notes for students:
- Do not import `teleop_keyboard` or try to start the controller from
  inside this file. This file is a script module executed by the
  controller.
- Each `arm` call returns `1` on success or `0` on error/interrupt.
- If you need to stop early, return from `program()`; pressing `t`
  during execution will interrupt and return control to MANUAL mode.

Available methods (short examples):
- `arm.x_by_deg(deg)` — move X axis by degrees
- `arm.y_by_deg(deg)` — move Y axis by degrees
- `arm.z_by_deg(deg)` — move Z axis by degrees
- `arm.grip_by_deg(deg)` — move gripper by degrees
- `arm.move_us(axis, delta_us)` — low-level: move in microseconds
- `arm.set_us(axis, pos_us)` — set absolute microsecond position
- `arm.wait(sec)` — interruptible wait
- `arm.stop()` — emergency stop

Example `program(arm)` below — copy and modify for your assignment.
"""

def program(arm):
    """Simple pick-and-place example.

    This example is deliberately conservative (small moves + waits).
    Edit degrees and waits to fit your mechanical setup.
    """

    print("[PROGRAM] Start — pick and place demo")

    # Move X forward, then Y toward the object
    arm.x_by_deg(20)
    # `arm.wait()` is interruptible; it returns 0 if the user pressed 't'
    # (or if an error occurred). If interrupted, return early so the
    # controller can switch back to MANUAL mode.
    if arm.wait(0.4) == 0:
        return

    arm.y_by_deg(35)
    # same interrupt check after the move
    if arm.wait(0.4) == 0:
        return

    # Close gripper (negative moves close in this setup)
    arm.grip_by_deg(-20)
    # check for interruption while waiting for gripper to move
    if arm.wait(0.4) == 0:
        return

    # Lift and translate back
    arm.z_by_deg(25)
    # moving the Z axis — wait and allow interruption
    if arm.wait(0.6) == 0:
        return

    arm.x_by_deg(-20)
    # final translation back; keep checking for interrupts between steps
    if arm.wait(0.5) == 0:
        return

    # Open gripper to release
    arm.grip_by_deg(20)
    arm.wait(0.4)

    print("[PROGRAM] Complete — returning to MANUAL mode")
