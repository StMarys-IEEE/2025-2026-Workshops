"""Demo: sweep X/Y/Z axes back and forth until interrupted

Moves each axis by small amounts in a ping-pong pattern. Designed to be
cooperative with the controller's interrupt mechanism (uses `arm.wait`).
"""

def program(arm):
    print('[DEMO] Sweep axes demo — press t to stop')

    # simple sweep parameters
    steps = [10, -10, 15, -15]
    idx = 0

    while True:
        dx = steps[idx % len(steps)]
        dy = steps[(idx+1) % len(steps)]
        dz = steps[(idx+2) % len(steps)]

        if arm.x_by_deg(dx) == 0:
            print('[DEMO] Interrupted during x move')
            break
        if arm.y_by_deg(dy) == 0:
            print('[DEMO] Interrupted during y move')
            break
        if arm.z_by_deg(dz) == 0:
            print('[DEMO] Interrupted during z move')
            break

        if arm.wait(0.6) == 0:
            print('[DEMO] Interrupted during wait')
            break

        idx += 1
        if idx % 8 == 0:
            print('[DEMO] sweep cycles:', idx)

    print('[DEMO] Exiting demo — returning to MANUAL')
