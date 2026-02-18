"""
Teleop Keyboard Controller - Manual and Tesla Mode
Toggles between keyboard control (MANUAL) and scripted program (TESLA)
Press 't' to toggle modes, 'q' to quit
"""

import keyboard
import time
import threading
import importlib.util
from pathlib import Path
import os
from arm import RoboticArm

# Optional: list available serial ports for user selection
try:
    import serial.tools.list_ports as list_ports
except Exception:
    list_ports = None

# Import student program (will be in run_program.py)
try:
    from run_program import program
except ImportError:
    print("[ERROR] Could not import program from run_program.py")
    print("Make sure run_program.py exists in the same directory")
    program = None


    def flush_console_input():
        """Flush console input buffer to remove stray keystrokes after exit.

        Works on Windows via `FlushConsoleInputBuffer`; on POSIX uses `termios.tcflush`.
        """
        try:
            if os.name == 'nt':
                import ctypes
                kernel32 = ctypes.windll.kernel32
                STD_INPUT_HANDLE = -10
                h = kernel32.GetStdHandle(STD_INPUT_HANDLE)
                kernel32.FlushConsoleInputBuffer(h)
            else:
                import sys
                import termios
                termios.tcflush(sys.stdin, termios.TCIFLUSH)
        except Exception:
            pass


class TeleopController:
    """
    Main controller for robotic arm with dual modes.
    
    MANUAL mode: Real-time keyboard control, 50 Hz teleop streaming
    TESLA mode: Runs student-defined program with safe interruption
    """
    
    # Bit flags for keyboard keys (matches Arduino expected format)
    BIT_W = 0              # Y+ (increase Y)
    BIT_S = 1              # Y- (decrease Y)
    BIT_A = 2              # X- (decrease X)
    BIT_D = 3              # X+ (increase X)
    BIT_BRACKET_LEFT = 4   # Z- (decrease Z)
    BIT_BRACKET_RIGHT = 5  # Z+ (increase Z)
    BIT_PLUS = 6           # Gripper+ (increase gripper)
    BIT_MINUS = 7          # Gripper- (decrease gripper)
    
    MODE_MANUAL = 0
    MODE_TESLA = 1
    
    def __init__(self, arm, mode_toggle_key='t', quit_key='q'):
        """
        Initialize teleop controller.
        
        Args:
            arm (RoboticArm): Arm instance
            mode_toggle_key (str): Key to toggle modes (default 't')
            quit_key (str): Key to quit (default 'q')
        """
        self.arm = arm
        self.mode_toggle_key = mode_toggle_key
        self.quit_key = quit_key
        
        self.current_mode = self.MODE_MANUAL
        self.is_running = 1
        self.toggle_debounce_time = 0.0
        self.toggle_debounce_interval = 0.3  # 300ms debounce for 't' key
        
        # For mode switching synchronization
        self.mode_lock = threading.Lock()
        self.exit_tesla = threading.Event()
    
    def _build_flags_byte(self):
        """
        Build current flags byte based on pressed keys.
        
        Returns:
            int: 8-bit flags byte
        """
        flags = 0
        
        if keyboard.is_pressed('w'):
            flags |= (1 << self.BIT_W)
        if keyboard.is_pressed('s'):
            flags |= (1 << self.BIT_S)
        if keyboard.is_pressed('a'):
            flags |= (1 << self.BIT_A)
        if keyboard.is_pressed('d'):
            flags |= (1 << self.BIT_D)
        # Use arrow keys for the last four bits to match servo.py
        if keyboard.is_pressed('left'):
            flags |= (1 << self.BIT_BRACKET_LEFT)
        if keyboard.is_pressed('right'):
            flags |= (1 << self.BIT_BRACKET_RIGHT)
        if keyboard.is_pressed('up'):
            flags |= (1 << self.BIT_PLUS)
        if keyboard.is_pressed('down'):
            flags |= (1 << self.BIT_MINUS)
        
        return flags
    
    def _manual_mode_loop(self):
        """
        MANUAL mode: Real-time keyboard control.
        Sends 0xAA + flags at 50 Hz (every 20ms).
        Exits on 't' (toggle) or 'q' (quit) press.
        """
        print("[MANUAL] Entering manual mode. Use WASD + arrow keys to control. Press 't' for Tesla, 'q' to quit.")
        
        frame_period_us = 20000  # 50 Hz
        last_frame_us = time.time_ns() // 1000
        
        while self.is_running:
            # Check for mode toggle
            if keyboard.is_pressed(self.mode_toggle_key):
                now = time.time()
                if now - self.toggle_debounce_time > self.toggle_debounce_interval:
                    print("[MANUAL] 't' pressed - switching to Tesla mode")
                    self.toggle_debounce_time = now
                    return  # Exit manual loop, will switch mode
            
            # Check for quit
            if keyboard.is_pressed(self.quit_key):
                print("[MAIN] 'q' pressed - quitting")
                self.is_running = 0
                return
            
            # Send teleop packet at 50 Hz
            now_us = time.time_ns() // 1000
            if now_us - last_frame_us >= frame_period_us:
                last_frame_us += frame_period_us
                
                flags = self._build_flags_byte()
                self.arm.send_flags(flags)
            
            time.sleep(0.005)  # Small sleep to avoid busy-waiting
    
    def _tesla_mode_loop(self):
        """
        TESLA mode: Run student program with interruption support.
        Can be interrupted by pressing 't' again.
        Automatically returns to MANUAL when program completes.
        """
        # Dynamically load the latest `run_program.py` from disk so students
        # can copy a new file while the controller is running (e.g., via USB).
        rp_path = Path(__file__).parent / 'run_program.py'
        if not rp_path.exists():
            print("[TESLA] ERROR: run_program.py not found in controller directory")
            return

        try:
            spec = importlib.util.spec_from_file_location('run_program', str(rp_path))
            rp_mod = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(rp_mod)
            prog = getattr(rp_mod, 'program', None)
        except Exception as e:
            print(f"[TESLA] ERROR loading run_program.py: {e}")
            return

        if not prog:
            print("[TESLA] ERROR: no `program(arm)` function defined in run_program.py")
            return

        print("[TESLA] Entering Tesla mode. Running program...")
        print("[TESLA] Press 't' anytime to interrupt and return to manual mode.")
        
        # Clear interrupt flag
        self.arm.interrupt_flag.clear()
        
        # Start background thread to monitor for interruption
        exit_event = threading.Event()
        
        def monitor_interrupt():
            """Background thread: watch for 't' key and signal interruption."""
            last_toggle = time.time()
            while not exit_event.is_set():
                if keyboard.is_pressed(self.mode_toggle_key):
                    now = time.time()
                    if now - last_toggle > self.toggle_debounce_interval:
                        print("[TESLA] 't' pressed during program - interrupting...")
                        self.arm.interrupt_flag.set()
                        last_toggle = now
                        break
                
                if keyboard.is_pressed(self.quit_key):
                    print("[TESLA] 'q' pressed - quitting immediately")
                    self.arm.interrupt_flag.set()
                    self.is_running = 0
                    exit_event.set()
                    break
                
                time.sleep(0.05)
            exit_event.set()
        
        monitor_thread = threading.Thread(target=monitor_interrupt, daemon=True)
        monitor_thread.start()
        
        try:
            # Run the freshly-loaded student program
            prog(self.arm)
            
            # If we get here, program completed normally
            if not self.arm.interrupt_flag.is_set():
                print("[TESLA] Program completed successfully")
        except Exception as e:
            if not self.arm.interrupt_flag.is_set():
                print(f"[TESLA] Program error: {e}")
        
        # Signal background thread to stop
        exit_event.set()
        monitor_thread.join(timeout=1.0)
        
        # Make sure to stop motion and return to manual
        self.arm.interrupt_flag.clear()
        print("[TESLA] Stopping motors and returning to manual mode...")
        self.arm.stop()
    
    def run(self):
        """
        Main control loop. Toggles between MANUAL and TESLA modes.
        """
        print("=" * 60)
        print("Robotic Arm Teleop Controller - MANUAL and TESLA Modes")
        print("=" * 60)
        print()
        
        while self.is_running:
            if self.current_mode == self.MODE_MANUAL:
                self._manual_mode_loop()
                
                # If we exited manual mode (via 't' toggle), switch to Tesla
                if self.is_running and not self.arm.interrupt_flag.is_set():
                    # Stop motion before switching
                    self.arm.stop()
                    self.current_mode = self.MODE_TESLA
            
            elif self.current_mode == self.MODE_TESLA:
                self._tesla_mode_loop()
                
                # Always return to manual mode after Tesla (whether interrupted or completed)
                self.current_mode = self.MODE_MANUAL
                
                # Debounce: don't immediately toggle back
                time.sleep(0.4)
        
        print("[MAIN] Exiting controller")
        self.arm.close()
        print("[MAIN] Done")


def main():
    """
    Entry point: Initialize arm, set up controller, and run.
    """
    print()
    print("Starting Robotic Arm Teleop Controller...")
    print()
    
    # Prompt user for serial port (show available ports if possible)
    print()
    print("Detecting available serial ports...")
    ports = []
    if list_ports:
        try:
            ports = [p.device for p in list_ports.comports()]
        except Exception:
            ports = []

    if ports:
        # Try to extract COM numbers from names like 'COM3'
        com_numbers = []
        for p in ports:
            up = p.upper()
            if up.startswith('COM'):
                try:
                    com_numbers.append(str(int(up[3:])))
                except Exception:
                    pass

        if com_numbers:
            print("Available COM numbers: " + ", ".join(com_numbers))
        else:
            print("Available ports: " + ", ".join(ports))
    else:
        print("No serial ports detected or pyserial unable to list ports.")

    # Prompt for COM number (no default). Require numeric input like '3' -> COM3.
    while True:
        port_num = input("Enter COM port number (e.g., 3 for COM3): ").strip()
        if port_num == "":
            print("Please enter the COM port number (no default).")
            continue
        if not port_num.isdigit():
            print("Invalid input. Enter only the numeric port number (e.g., 3 for COM3).")
            continue
        port = f"COM{int(port_num)}"
        print(f"Using serial port: {port}")
        break

    # Try to connect to Arduino
    try:
        arm = RoboticArm(port=port, baud=9600)
    except Exception as e:
        print(f"[ERROR] Failed to connect to arm: {e}")
        print(f"Make sure Arduino is connected to {port} (or modify the port when prompted)")
        return
    
    # Create and run controller
    controller = TeleopController(arm, mode_toggle_key='t', quit_key='q')
    
    # Block the quit key from being delivered to the terminal (prevents echoing typed 'q')
    try:
        keyboard.block_key('q')
    except Exception:
        # If blocking fails (no permissions), continue without it
        pass

    try:
        controller.run()
    except KeyboardInterrupt:
        print("\n[MAIN] Interrupted by user")
        controller.is_running = 0
        arm.stop()
        arm.close()
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        arm.stop()
        arm.close()
        raise
    finally:
        try:
            keyboard.unblock_key('q')
        except Exception:
            pass
        # Remove any keystrokes typed while the program ran so they don't appear at the shell prompt
        flush_console_input()


if __name__ == '__main__':
    main()
