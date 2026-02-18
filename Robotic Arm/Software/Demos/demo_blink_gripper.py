"""Demo: blink the gripper open/close until interrupted

This demo repeatedly opens and closes the gripper every 0.6s. Press `t` to
interrupt (controller will set interrupt flag and the demo will exit).
"""

def program(arm):
    print('[DEMO] Blink gripper demo — press t to stop')

    while True:
        if arm.grip_by_deg(-25) == 0:
            print('[DEMO] Interrupted during close')
            break
        if arm.wait(0.6) == 0:
            print('[DEMO] Interrupted during wait')
            break

        if arm.grip_by_deg(25) == 0:
            print('[DEMO] Interrupted during open')
            break
        if arm.wait(0.6) == 0:
            print('[DEMO] Interrupted during wait')
            break

    print('[DEMO] Exiting demo — returning to MANUAL')
