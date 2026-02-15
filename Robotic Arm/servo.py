import serial
import keyboard
import time

# 1) Connect to Arduino
ser = serial.Serial('COM7', 9600)
time.sleep(2)  # Arduino often resets when serial opens

# 2) Constants
START = 0xAA
FRAME_DT = 0.02  # 20 ms = 50 Hz

# 3) 50 Hz loop
next_t = time.perf_counter()

while True:
    flags = 0

    # Bit mapping (8 keys -> 8 bits)
    # bit0 W, bit1 S, bit2 A, bit3 D, bit4 [, bit5 ], bit6 +, bit7 -
    if keyboard.is_pressed('w'):     flags |= (1 << 0)
    if keyboard.is_pressed('s'):     flags |= (1 << 1)
    if keyboard.is_pressed('a'):     flags |= (1 << 2)
    if keyboard.is_pressed('d'):     flags |= (1 << 3)
    if keyboard.is_pressed('left'):     flags |= (1 << 4)
    if keyboard.is_pressed('right'):     flags |= (1 << 5)
    if keyboard.is_pressed('up'):     flags |= (1 << 6)
    if keyboard.is_pressed('down'):     flags |= (1 << 7)

    # Send exactly once per frame (start byte + flags byte)
    ser.write(bytes([START, flags]))

    # Wait until the next 20ms boundary
    next_t += FRAME_DT
    sleep_time = next_t - time.perf_counter()
    if sleep_time > 0:
        time.sleep(sleep_time)
    else:
        next_t = time.perf_counter()
