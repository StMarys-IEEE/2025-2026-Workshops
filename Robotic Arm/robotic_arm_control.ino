/*
 * Robotic Arm Multi-Servo PWM Controller
 * Arduino Nano - 4 Servo Control System
 * 
 * Key Mappings (powers of 2 for combination detection):
 * W = 1    (X-axis forward)
 * A = 2    (Z-axis left)
 * S = 4    (X-axis backward)
 * D = 8    (Z-axis right)
 * UP = 16  (Y-axis up)
 * DOWN = 32 (Y-axis down)
 * LEFT = 64 (Gripper open)
 * RIGHT = 128 (Gripper close)
 */

// Servo pin assignments (Arduino Nano digital pins)
const int SERVO_Z_PIN = 9;   // Z-axis rotation (A/D keys)
const int SERVO_X_PIN = 10;  // X-axis movement (W/S keys)
const int SERVO_Y_PIN = 11;  // Y-axis up/down (UP/DOWN keys)
const int SERVO_GRIPPER_PIN = 6; // Gripper (LEFT/RIGHT keys)

// Servo position ranges (in microseconds)
const int CENTER = 1500;
const int MIN_POS = 500;
const int MAX_POS = 2500;

// Gripper specific positions
const int GRIPPER_OPEN = 1000;
const int GRIPPER_CLOSED = 2000;
const int GRIPPER_CENTER = 1500;

// Movement parameters
const int STEP_SIZE = 10;  // Speed of servo movement (microseconds per frame)
const unsigned long FRAME_PERIOD_US = 20000;  // 50 Hz servo refresh rate
const unsigned long HOLD_TIMEOUT_MS = 150;    // Time before servo locks position

// Current and target positions for each servo
struct ServoState {
  int currentPos;
  int targetPos;
  int pin;
};

ServoState servoZ = {CENTER, CENTER, SERVO_Z_PIN};
ServoState servoX = {CENTER, CENTER, SERVO_X_PIN};
ServoState servoY = {CENTER, CENTER, SERVO_Y_PIN};
ServoState servoGripper = {GRIPPER_CENTER, GRIPPER_CENTER, SERVO_GRIPPER_PIN};

unsigned long lastCmdTimeMs = 0;
unsigned long lastFrameUs = 0;

// Key bit values (powers of 2)
const int KEY_W = 1;
const int KEY_A = 2;
const int KEY_S = 4;
const int KEY_D = 8;
const int KEY_UP = 16;
const int KEY_DOWN = 32;
const int KEY_LEFT = 64;
const int KEY_RIGHT = 128;

void setup() {
  // Initialize servo pins
  pinMode(SERVO_Z_PIN, OUTPUT);
  pinMode(SERVO_X_PIN, OUTPUT);
  pinMode(SERVO_Y_PIN, OUTPUT);
  pinMode(SERVO_GRIPPER_PIN, OUTPUT);
  
  Serial.begin(9600);
  
  // Set initial positions
  servoZ.currentPos = CENTER;
  servoZ.targetPos = CENTER;
  servoX.currentPos = CENTER;
  servoX.targetPos = CENTER;
  servoY.currentPos = CENTER;
  servoY.targetPos = CENTER;
  servoGripper.currentPos = GRIPPER_CENTER;
  servoGripper.targetPos = GRIPPER_CENTER;
  
  lastCmdTimeMs = millis();
  lastFrameUs = micros();
}

void loop() {
  // ---- 1) Read input and determine key combination ----
  if (Serial.available() > 0) {
    int keyCombination = Serial.read();
    
    processKeyCommand(keyCombination);
    lastCmdTimeMs = millis();
  }
  
  // ---- 2) If no recent input, lock servos at current position ----
  if (millis() - lastCmdTimeMs > HOLD_TIMEOUT_MS) {
    servoZ.targetPos = servoZ.currentPos;
    servoX.targetPos = servoX.currentPos;
    servoY.targetPos = servoY.currentPos;
    servoGripper.targetPos = servoGripper.currentPos;
  }
  
  // ---- 3) Run servo frame at 50 Hz ----
  unsigned long nowUs = micros();
  if (nowUs - lastFrameUs >= FRAME_PERIOD_US) {
    lastFrameUs += FRAME_PERIOD_US;
    
    // Update and output all servos
    updateAndOutputServo(servoZ);
    updateAndOutputServo(servoX);
    updateAndOutputServo(servoY);
    updateAndOutputServo(servoGripper);
  }
}

void processKeyCommand(int keyCombination) {
  // Z-axis control (A/D keys - bits 2 and 8)
  if (keyCombination & KEY_A) {
    servoZ.targetPos = MIN_POS;  // Rotate left
  }
  if (keyCombination & KEY_D) {
    servoZ.targetPos = MAX_POS;  // Rotate right
  }
  
  // X-axis control (W/S keys - bits 1 and 4)
  if (keyCombination & KEY_W) {
    servoX.targetPos = MAX_POS;  // Move forward
  }
  if (keyCombination & KEY_S) {
    servoX.targetPos = MIN_POS;  // Move backward
  }
  
  // Y-axis control (UP/DOWN keys - bits 16 and 32)
  if (keyCombination & KEY_UP) {
    servoY.targetPos = MAX_POS;  // Move up
  }
  if (keyCombination & KEY_DOWN) {
    servoY.targetPos = MIN_POS;  // Move down
  }
  
  // Gripper control (LEFT/RIGHT keys - bits 64 and 128)
  if (keyCombination & KEY_LEFT) {
    servoGripper.targetPos = GRIPPER_OPEN;  // Open gripper
  }
  if (keyCombination & KEY_RIGHT) {
    servoGripper.targetPos = GRIPPER_CLOSED;  // Close gripper
  }
  
  // Handle special combinations if needed
  // Example: W + D pressed together = 1 + 8 = 9
  // You can add specific behaviors for certain combinations here
  if (keyCombination == (KEY_W | KEY_D)) {
    // Diagonal forward-right movement
    servoX.targetPos = MAX_POS;
    servoZ.targetPos = MAX_POS;
  }
}

void updateAndOutputServo(ServoState &servo) {
  // Ramp current position toward target position
  if (servo.currentPos < servo.targetPos) {
    servo.currentPos += STEP_SIZE;
    if (servo.currentPos > servo.targetPos) {
      servo.currentPos = servo.targetPos;
    }
  } else if (servo.currentPos > servo.targetPos) {
    servo.currentPos -= STEP_SIZE;
    if (servo.currentPos < servo.targetPos) {
      servo.currentPos = servo.targetPos;
    }
  }
  
  // Clamp to safe bounds
  int clampedPos = servo.currentPos;
  if (clampedPos < MIN_POS) clampedPos = MIN_POS;
  if (clampedPos > MAX_POS) clampedPos = MAX_POS;
  
  // Output PWM pulse
  digitalWrite(servo.pin, HIGH);
  delayMicroseconds(clampedPos);
  digitalWrite(servo.pin, LOW);
  // Note: The remaining LOW time is handled by the frame timing
}
