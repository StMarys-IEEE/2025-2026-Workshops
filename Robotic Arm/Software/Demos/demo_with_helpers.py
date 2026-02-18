"""Demo: program with helper functions (go_home, grab_sequence, etc.)

This demo shows how students can structure their `run_program.py` with
helper functions for clarity. Copy this file to `run_program.py` and press
`t` in MANUAL mode to run. Press `t` again to interrupt and return to
MANUAL.

The helpers return `True` on success, `False` on interrupt/error so the
main `program()` can stop early and return control to the controller.
"""


def go_home(arm):
    """Move the arm to a conservative 'home' pose.

    Returns:
        True if completed normally, False if interrupted.
    """
    print('[HELPER] Going to home position')
    # Example home moves; check interrupt after each step
    if arm.x_by_deg(-20) == 0:
        return False
    if arm.wait(0.4) == 0:
        return False

    if arm.y_by_deg(-35) == 0:
        return False
    if arm.wait(0.4) == 0:
        return False

    if arm.z_by_deg(-20) == 0:
        return False
    if arm.wait(0.4) == 0:
        return False

    if arm.grip_by_deg(20) == 0:
        return False
    if arm.wait(0.3) == 0:
        return False

    return True


def grab_sequence(arm):
    """Approach, close gripper, lift, and return success/fail."""
    print('[HELPER] Starting grab sequence')

    if arm.y_by_deg(40) == 0:
        return False
    if arm.wait(0.6) == 0:
        return False

    if arm.grip_by_deg(-30) == 0:  # close
        return False
    if arm.wait(0.5) == 0:
        return False

    if arm.z_by_deg(30) == 0:
        return False
    if arm.wait(0.6) == 0:
        return False

    return True


def place_sequence(arm):
    """Move to place position and release object."""
    print('[HELPER] Starting place sequence')

    if arm.x_by_deg(40) == 0:
        return False
    if arm.wait(0.6) == 0:
        return False

    if arm.z_by_deg(-30) == 0:
        return False
    if arm.wait(0.5) == 0:
        return False

    if arm.grip_by_deg(30) == 0:  # open
        return False
    if arm.wait(0.4) == 0:
        return False

    return True


def program(arm):
    """Main demo program which uses helper functions.

    Structure:
    1. Go home
    2. Run grab sequence
    3. Move and place sequence
    4. Return home
    """
    print('[DEMO] Demo with helpers started')

    # 1) Ensure home
    if not go_home(arm):
        print('[DEMO] Interrupted while homing')
        return

    # 2) Grab object
    if not grab_sequence(arm):
        print('[DEMO] Interrupted during grab')
        # try to stop motion and go home safely
        arm.stop()
        go_home(arm)
        return

    # 3) Place object
    if not place_sequence(arm):
        print('[DEMO] Interrupted during place')
        arm.stop()
        go_home(arm)
        return

    # 4) Return to home
    if not go_home(arm):
        print('[DEMO] Interrupted while returning home')
        return

    print('[DEMO] Demo complete — returning to MANUAL')
