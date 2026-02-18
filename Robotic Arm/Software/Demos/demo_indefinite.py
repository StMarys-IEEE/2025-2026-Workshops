"""Demo: run indefinitely until interrupted (press 't')

Copy this file to `Robotic Arm/run_program.py` and press `t` in MANUAL mode.
The controller will call `program(arm)`; pressing `t` sets the interrupt flag
and all `arm` methods will return 0. Use `arm.wait()` which returns 0 when
interrupted to cooperatively stop.
"""

def program(arm):
    print('[DEMO] Indefinite loop started — press t to stop')

    i = 0
    while True:
        # Example action: small X wiggle every loop
        res = arm.x_by_deg(5)
        if res == 0:
            print('[DEMO] Interrupted during x_by_deg')
            break

        # wait() is interruptible; will return 0 if user presses 't'
        if arm.wait(0.5) == 0:
            print('[DEMO] Interrupted during wait')
            break

        # undo the wiggle
        if arm.x_by_deg(-5) == 0:
            print('[DEMO] Interrupted during x_by_deg(reverse)')
            break

        if arm.wait(0.5) == 0:
            print('[DEMO] Interrupted during wait')
            break

        i += 1
        if i % 10 == 0:
            print(f'[DEMO] still running — cycles={i}')

    print('[DEMO] Exiting demo — returning to MANUAL')
