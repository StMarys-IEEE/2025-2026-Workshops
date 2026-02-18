
"""Simple Tesla-mode student program.

This file exposes a single function `program(arm)` that will be called
when entering TESLA mode. Keep it short and clear; edit this function
with your sequence of moves. Documentation for available `arm` methods
should be written separately (as you planned).
"""

def program(arm):
    """Example pick-and-place sequence (concise).

    Args:
        arm: `RoboticArm` instance provided by the controller.
    """
    print("[PROGRAM] Start")

    # Approach object
    arm.x_by_deg(30)
    arm.wait(0.5)
    arm.y_by_deg(40)
    arm.wait(0.5)

    # Grab
    arm.grip_by_deg(-20)  # close
    arm.wait(0.5)

    # Lift and move
    arm.z_by_deg(30)
    arm.wait(0.8)
    arm.x_by_deg(-30)
    arm.wait(0.5)

    # Release
    arm.grip_by_deg(20)  # open
    arm.wait(0.5)

    print("[PROGRAM] Complete")
