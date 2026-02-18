"""
RoboticArm Library - Provides interface for manual and scripted control
Supports both teleop (0xAA flags) and scripted protocols (0xAB delta, 0xAC absolute, 0xAD stop)
"""

import serial
import struct
import time
import threading

class RoboticArm:
    """
    Interface to control a 4-axis robotic arm via serial communication.
    
    Attributes:
        port (str): Serial port name (e.g., 'COM6')
        baud (int): Baud rate (default 9600)
        us_per_deg (dict): Microseconds per degree for each axis
        interrupt_flag (threading.Event): Flag to interrupt Tesla mode
    """
    
    AXIS_X = 0
    AXIS_Y = 1
    AXIS_Z = 2
    AXIS_GRIPPER = 3
    
    # Packet types
    PKT_TELEOP = 0xAA      # Flags-based teleop
    PKT_DELTA = 0xAB       # Signed delta in microseconds
    PKT_ABSOLUTE = 0xAC    # Unsigned absolute position
    PKT_STOP = 0xAD        # Stop command
    
    # Position bounds
    UPPER_BOUND = 600      # Lower microsecond value (max rotation one direction)
    LOWER_BOUND = 2400     # Higher microsecond value (max rotation other direction)
    
    def __init__(self, port='COM6', baud=9600):
        """
        Initialize robotic arm controller.
        
        Args:
            port (str): Serial port (e.g., 'COM6', '/dev/ttyUSB0')
            baud (int): Baud rate (default 9600)
        
        Raises:
            SerialException: If port cannot be opened
        """
        self.port = port
        self.baud = baud
        self.ser = None
        self.interrupt_flag = threading.Event()
        
        # Default: 10 microseconds per degree for all axes
        self.us_per_deg = {
            self.AXIS_X: 10,
            self.AXIS_Y: 10,
            self.AXIS_Z: 10,
            self.AXIS_GRIPPER: 10
        }
        
        try:
            self.ser = serial.Serial(port, baud, timeout=1.0)
            time.sleep(0.5)  # Wait for Arduino to reset
            self._flush_serial()
            print(f"[RoboticArm] Connected to {port} at {baud} baud")
        except serial.SerialException as e:
            raise serial.SerialException(f"Failed to open {port}: {e}")
    
    def close(self):
        """Close serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("[RoboticArm] Serial connection closed")
    
    def _flush_serial(self):
        """Flush any pending data in receive buffer."""
        if self.ser and self.ser.is_open:
            while self.ser.in_waiting:
                self.ser.read(1)
    
    def _read_response(self, timeout_sec=1.5):
        """
        Read response from Arduino.
        
        Args:
            timeout_sec (float): Timeout in seconds
        
        Returns:
            str: Response line (stripped), or None on timeout
        """
        start = time.time()
        while time.time() - start < timeout_sec:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8', errors='ignore').strip()
                if line:
                    return line
            time.sleep(0.01)
        return None
    
    def send_flags(self, flags):
        """
        Send teleop flags packet (0xAA + flags).
        Used for real-time manual control.
        
        Args:
            flags (int): 8-bit flags byte (bits mapped to keyboard inputs)
        
        Returns:
            int: 1 if sent successfully, 0 on error
        """
        if not self.ser or not self.ser.is_open:
            print("[RoboticArm] ERROR: Serial port not open")
            return 0
        
        try:
            packet = bytes([self.PKT_TELEOP, flags & 0xFF])
            self.ser.write(packet)
            return 1
        except Exception as e:
            print(f"[RoboticArm] ERROR sending flags: {e}")
            return 0
    
    def stop(self):
        """
        Send STOP packet (0xAD) - immediately halt all motion.
        Waits for "OK" response.
        
        Returns:
            int: 1 if successful, 0 on error/timeout
        """
        if not self.ser or not self.ser.is_open:
            print("[RoboticArm] ERROR: Serial port not open")
            return 0
        
        self._flush_serial()
        
        try:
            packet = bytes([self.PKT_STOP])
            print(f"[RoboticArm] sending STOP: {packet.hex()}")
            self.ser.write(packet)
            response = self._read_response()
            
            if response and "OK" in response:
                return 1
            else:
                print(f"[RoboticArm] STOP: No OK response (got '{response}')")
                return 0
        except Exception as e:
            print(f"[RoboticArm] ERROR sending STOP: {e}")
            return 0
    
    def move_us(self, axis, delta_us):
        """
        Send relative movement command (0xAB + axis + delta).
        Moves axis by signed delta (in microseconds).
        
        Args:
            axis (int): 0=X, 1=Y, 2=Z, 3=Gripper
            delta_us (int): Signed delta in microseconds (-32768 to +32767)
        
        Returns:
            int: 1 if successful, 0 on error/timeout
        
        Raises:
            ValueError: If axis invalid
        """
        if self.interrupt_flag.is_set():
            return 0
        
        if axis < 0 or axis > 3:
            print(f"[RoboticArm] ERROR: Invalid axis {axis}")
            raise ValueError(f"Axis must be 0-3, got {axis}")
        
        if not self.ser or not self.ser.is_open:
            print("[RoboticArm] ERROR: Serial port not open")
            return 0
        
        self._flush_serial()
        
        try:
            # Clamp delta to int16 range
            delta_clamped = max(-32768, min(32767, delta_us))
            delta_hi = (delta_clamped >> 8) & 0xFF
            delta_lo = delta_clamped & 0xFF
            
            packet = bytes([self.PKT_DELTA, axis, delta_hi, delta_lo])
            print(f"[RoboticArm] sending DELTA: {packet.hex()}")
            self.ser.write(packet)
            response = self._read_response()
            
            if response and "OK" in response:
                return 1
            elif response and "ERR" in response:
                print(f"[RoboticArm] move_us error response: {response}")
                return 0
            else:
                print(f"[RoboticArm] move_us: No OK response (got '{response}')")
                return 0
        except Exception as e:
            print(f"[RoboticArm] ERROR in move_us: {e}")
            return 0
    
    def set_us(self, axis, pos_us):
        """
        Send absolute position command (0xAC + axis + position).
        Sets axis to absolute position (in microseconds, 600-2400).
        
        Args:
            axis (int): 0=X, 1=Y, 2=Z, 3=Gripper
            pos_us (int): Absolute position in microseconds (0-65535)
        
        Returns:
            int: 1 if successful, 0 on error/timeout
        
        Raises:
            ValueError: If axis invalid
        """
        if self.interrupt_flag.is_set():
            return 0
        
        if axis < 0 or axis > 3:
            print(f"[RoboticArm] ERROR: Invalid axis {axis}")
            raise ValueError(f"Axis must be 0-3, got {axis}")
        
        if not self.ser or not self.ser.is_open:
            print("[RoboticArm] ERROR: Serial port not open")
            return 0
        
        # Clamp position to bounds
        pos_clamped = max(self.UPPER_BOUND, min(self.LOWER_BOUND, pos_us))
        
        self._flush_serial()
        
        try:
            pos_hi = (pos_clamped >> 8) & 0xFF
            pos_lo = pos_clamped & 0xFF
            
            packet = bytes([self.PKT_ABSOLUTE, axis, pos_hi, pos_lo])
            print(f"[RoboticArm] sending ABS: {packet.hex()}")
            self.ser.write(packet)
            response = self._read_response()
            
            if response and "OK" in response:
                return 1
            elif response and "ERR" in response:
                print(f"[RoboticArm] set_us error response: {response}")
                return 0
            else:
                print(f"[RoboticArm] set_us: No OK response (got '{response}')")
                return 0
        except Exception as e:
            print(f"[RoboticArm] ERROR in set_us: {e}")
            return 0
    
    def x_by_deg(self, degrees, us_per_deg_override=None):
        """
        Move X axis by relative degrees.
        
        Args:
            degrees (float): Degrees to move
            us_per_deg_override (float): Override default microseconds per degree
        
        Returns:
            int: 1 if successful, 0 on error
        """
        us_per_deg = us_per_deg_override if us_per_deg_override else self.us_per_deg[self.AXIS_X]
        delta_us = int(degrees * us_per_deg)
        return self.move_us(self.AXIS_X, delta_us)
    
    def y_by_deg(self, degrees, us_per_deg_override=None):
        """
        Move Y axis by relative degrees.
        
        Args:
            degrees (float): Degrees to move
            us_per_deg_override (float): Override default microseconds per degree
        
        Returns:
            int: 1 if successful, 0 on error
        """
        us_per_deg = us_per_deg_override if us_per_deg_override else self.us_per_deg[self.AXIS_Y]
        delta_us = int(degrees * us_per_deg)
        return self.move_us(self.AXIS_Y, delta_us)
    
    def z_by_deg(self, degrees, us_per_deg_override=None):
        """
        Move Z axis by relative degrees.
        
        Args:
            degrees (float): Degrees to move
            us_per_deg_override (float): Override default microseconds per degree
        
        Returns:
            int: 1 if successful, 0 on error
        """
        us_per_deg = us_per_deg_override if us_per_deg_override else self.us_per_deg[self.AXIS_Z]
        delta_us = int(degrees * us_per_deg)
        return self.move_us(self.AXIS_Z, delta_us)
    
    def grip_by_deg(self, degrees, us_per_deg_override=None):
        """
        Move gripper by relative degrees.
        
        Args:
            degrees (float): Degrees to move
            us_per_deg_override (float): Override default microseconds per degree
        
        Returns:
            int: 1 if successful, 0 on error
        """
        us_per_deg = us_per_deg_override if us_per_deg_override else self.us_per_deg[self.AXIS_GRIPPER]
        delta_us = int(degrees * us_per_deg)
        return self.move_us(self.AXIS_GRIPPER, delta_us)
    
    def wait(self, seconds):
        """
        Wait for specified duration (in seconds).
        Can be interrupted by setting interrupt_flag.
        
        Args:
            seconds (float): Duration to wait
        
        Returns:
            int: 1 if completed normally, 0 if interrupted
        """
        start = time.time()
        while time.time() - start < seconds:
            if self.interrupt_flag.is_set():
                return 0  # Interrupted
            time.sleep(0.05)
        return 1  # Completed normally
    
    def set_us_per_deg(self, axis, us_per_deg):
        """
        Configure microseconds-per-degree conversion for an axis.
        
        Args:
            axis (int): 0=X, 1=Y, 2=Z, 3=Gripper
            us_per_deg (float): Conversion factor
        """
        if axis >= 0 and axis <= 3:
            self.us_per_deg[axis] = us_per_deg
        else:
            print(f"[RoboticArm] WARNING: Invalid axis {axis} for set_us_per_deg")
