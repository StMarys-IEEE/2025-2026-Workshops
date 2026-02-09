import serial
import keyboard
import time

ser = serial.Serial('COM7', 9600)  # change COM port

while True:
    if keyboard.is_pressed('a'):
        ser.write(b'a')
    elif keyboard.is_pressed('d'):
        ser.write(b'd')
    #time.sleep(0.05)
