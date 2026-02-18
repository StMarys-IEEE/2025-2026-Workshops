/*
 * Robotic Arm Multi-Servo PWM Controller - Refactored OOP Version
 * Arduino Nano - 4 Servo Control System
 * 
 * Key Mappings:
 * A/D = X-axis (servo index 0)
 * W/S = Y-axis (servo index 1)
 * [/] = Z-axis (servo index 2)
 * -/+ = Grabber (servo index 3)
 * 
 * Position Boundaries:
 * - Lower Bound: 2000 microseconds
 * - Upper Bound: 1000 microseconds
 * - Start Position: 1500 microseconds
 * - Step Size: 20 microseconds
 */

// ============================================================================
// UpdatePosition Class - Handles position updates and boundary checking
// ============================================================================
class UpdatePosition {
  private:
    int lowerBound;
    int upperBound;
    int stepSize;
    
  public:
    // Constructor
    UpdatePosition(int lower, int upper, int step) {
      lowerBound = lower;
      upperBound = upper;
      stepSize = step;
    }
    
    // Update position based on direction
    // direction: 1 for positive, -1 for negative, 0 for hold
    int update(int currentPos, int direction) {
      if (direction == 0) {
        return currentPos;  // No movement
      }
      
      int newPos = currentPos + (direction * stepSize);
      
      // Boundary checking (note: upper bound is actually smaller value)
      if (newPos < upperBound) {
        newPos = upperBound;
      }
      if (newPos > lowerBound) {
        newPos = lowerBound;
      }
      
      return newPos;
    }
    
    // Getters and setters
    void setStepSize(int newStep) {
      stepSize = newStep;
    }
    
    int getStepSize() {
      return stepSize;
    }
    
    void setBounds(int lower, int upper) {
      lowerBound = lower;
      upperBound = upper;
    }
    
    int getLowerBound() {
      return lowerBound;
    }
    
    int getUpperBound() {
      return upperBound;
    }
};

// ============================================================================
// ServoAxis Class - Encapsulates servo control
// ============================================================================
class ServoAxis {
  private:
    int pin;
    String axisName;
    int currentPos;
    UpdatePosition* positionUpdater;
    
  public:
    // Constructor
    ServoAxis(int servoPin, String name, int startPos, UpdatePosition* updater) {
      pin = servoPin;
      axisName = name;
      currentPos = startPos;
      positionUpdater = updater;
      
      pinMode(pin, OUTPUT);
    }
    
    // Default constructor
    ServoAxis() {
      pin = 0;
      axisName = "";
      currentPos = 1500;
      positionUpdater = nullptr;
    }
    
    // Initialize (for array declaration)
    void init(int servoPin, String name, int startPos, UpdatePosition* updater) {
      pin = servoPin;
      axisName = name;
      currentPos = startPos;
      positionUpdater = updater;
      
      pinMode(pin, OUTPUT);
    }
    
    // Update position based on direction
    void updatePosition(int direction) {
      if (positionUpdater != nullptr) {
        currentPos = positionUpdater->update(currentPos, direction);
      }
    }
    
    // Output PWM pulse to servo
    void outputPWM() {
      digitalWrite(pin, HIGH);
      delayMicroseconds(currentPos);
      digitalWrite(pin, LOW);
    }
    
    // Set absolute position (clamped to bounds)
    void setCurrentPosition(int pos) {
      if (positionUpdater != nullptr) {
        int upper = positionUpdater->getUpperBound();
        int lower = positionUpdater->getLowerBound();
        if (pos < upper) {
          pos = upper;
        }
        if (pos > lower) {
          pos = lower;
        }
      }
      currentPos = pos;
    }
    
    // Getters
    int getCurrentPosition() {
      return currentPos;
    }
    
    String getAxisName() {
      return axisName;
    }
    
    int getPin() {
      return pin;
    }
};

// ============================================================================
// Global Constants
// ============================================================================

// Servo pin assignments
const int SERVO_X_PIN = 9;       // X-axis (A/D keys)
const int SERVO_Y_PIN = 10;      // Y-axis (W/S keys)
const int SERVO_Z_PIN = 11;      // Z-axis (LEFT/RIGHT keys)
const int SERVO_GRIPPER_PIN = 6; // Gripper (UP/DOWN keys)

// Position parameters
const int LOWER_BOUND = 2400;  // Extended range upper limit
const int UPPER_BOUND = 600;   // Extended range lower limit
const int START_POS = 1500;
const int STEP_SIZE = 20;

// Timing parameters
const unsigned long FRAME_PERIOD_US = 20000;  // 50 Hz servo refresh rate

// ============================================================================
// Global Objects
// ============================================================================

// Create UpdatePosition objects (one shared for all servos, or individual if needed)
UpdatePosition posUpdaterX(LOWER_BOUND, UPPER_BOUND, STEP_SIZE);
UpdatePosition posUpdaterY(LOWER_BOUND, UPPER_BOUND, STEP_SIZE);
UpdatePosition posUpdaterZ(LOWER_BOUND, UPPER_BOUND, STEP_SIZE);
UpdatePosition posUpdaterGripper(LOWER_BOUND, UPPER_BOUND, STEP_SIZE);

// Array of 4 servos: [X, Y, Z, Gripper]
ServoAxis servos[4];

// Movement direction for each servo (1 = positive, -1 = negative, 0 = hold)
int servoDirections[4] = {0, 0, 0, 0};

unsigned long lastFrameUs = 0;

// ============================================================================
// Setup Function
// ============================================================================

void setup() {
  Serial.begin(9600);
  
  // Initialize servo array
  // Index 0: X-axis (A/D)
  servos[0].init(SERVO_X_PIN, "X-Axis", START_POS, &posUpdaterX);
  
  // Index 1: Y-axis (W/S)
  servos[1].init(SERVO_Y_PIN, "Y-Axis", START_POS, &posUpdaterY);
  
  // Index 2: Z-axis ([/])
  servos[2].init(SERVO_Z_PIN, "Z-Axis", START_POS, &posUpdaterZ);
  
  // Index 3: Gripper (-/+)
  servos[3].init(SERVO_GRIPPER_PIN, "Gripper", START_POS, &posUpdaterGripper);
  
  lastFrameUs = micros();
  
  Serial.println("===========================================");
  Serial.println("Robotic Arm Initialized - Bitmapped Input");
  Serial.println("===========================================");
  Serial.println("Receiving bitmapped signals from Python:");
  Serial.println("  Byte 1: 0xAA (START)");
  Serial.println("  Byte 2: Flags byte");
  Serial.println("Key Mapping:");
  Serial.println("  W/S: Y-Axis (increase/decrease)");
  Serial.println("  A/D: X-Axis (decrease/increase)");
  Serial.println("  [/]: Z-Axis (decrease/increase)");
  Serial.println("  -/+: Gripper (decrease/increase)");
  Serial.println("===========================================");
  Serial.println();
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // ---- 1) Read and dispatch packets ----
  // Multiple protocols supported:
  // 0xAA <flags>           - Teleop bitmapped input
  // 0xAB <axis> <h> <l>    - Delta microseconds (signed int16)
  // 0xAC <axis> <h> <l>    - Absolute position (unsigned uint16)
  // 0xAD                   - STOP command
  
  if (Serial.available() >= 1) {
    byte packetType = Serial.peek();  // Peek to check type
    
    // ---- TELEOP PACKET (0xAA) ----
    if (packetType == 0xAA && Serial.available() >= 2) {
      Serial.read();  // Consume 0xAA
      byte flags = Serial.read();
      
      // Reset all directions
      for (int i = 0; i < 4; i++) {
        servoDirections[i] = 0;
      }
      
      // Extract bits and map to servo directions
      // Servo 0 (X-axis): bit2=A(decrease), bit3=D(increase)
      if (flags & (1 << 2)) servoDirections[0] = -1;  // A pressed
      if (flags & (1 << 3)) servoDirections[0] = 1;   // D pressed
      
      // Servo 1 (Y-axis): bit0=W(increase), bit1=S(decrease)
      if (flags & (1 << 0)) servoDirections[1] = 1;   // W pressed
      if (flags & (1 << 1)) servoDirections[1] = -1;  // S pressed
      
      // Servo 2 (Z-axis): bit4=bracket-left(decrease), bit5=bracket-right(increase)
      if (flags & (1 << 4)) servoDirections[2] = -1;  // [ pressed
      if (flags & (1 << 5)) servoDirections[2] = 1;   // ] pressed
      
      // Servo 3 (Gripper): bit7=minus(decrease), bit6=plus(increase)
      if (flags & (1 << 7)) servoDirections[3] = -1;  // - pressed
      if (flags & (1 << 6)) servoDirections[3] = 1;   // + pressed
    }
    
    // ---- DELTA PACKET (0xAB) ----
    // Need start + axis + hi + lo => 4 bytes total available
    else if (packetType == 0xAB && Serial.available() >= 4) {
      Serial.read();  // Consume 0xAB
      byte axis = Serial.read();
      byte deltaHi = Serial.read();
      byte deltaLo = Serial.read();
      
      if (axis >= 0 && axis <= 3) {
        // Reconstruct signed int16 delta
        int16_t delta = ((int16_t)deltaHi << 8) | deltaLo;
        int newPos = servos[axis].getCurrentPosition() + delta;
        servos[axis].setCurrentPosition(newPos);
        Serial.println("OK");
      } else {
        Serial.println("ERR BAD_AXIS");
      }
    }
    
    // ---- ABSOLUTE POSITION PACKET (0xAC) ----
    // Need start + axis + hi + lo => 4 bytes total available
    else if (packetType == 0xAC && Serial.available() >= 4) {
      Serial.read();  // Consume 0xAC
      byte axis = Serial.read();
      byte posHi = Serial.read();
      byte posLo = Serial.read();
      
      if (axis >= 0 && axis <= 3) {
        // Reconstruct unsigned uint16 position
        uint16_t pos = ((uint16_t)posHi << 8) | posLo;
        servos[axis].setCurrentPosition((int)pos);
        Serial.println("OK");
      } else {
        Serial.println("ERR BAD_AXIS");
      }
    }
    
    // ---- STOP PACKET (0xAD) ----
    else if (packetType == 0xAD) {
      Serial.read();  // Consume 0xAD
      
      // Stop all motion: set all directions to 0
      for (int i = 0; i < 4; i++) {
        servoDirections[i] = 0;
      }
      Serial.println("OK");
    }
  }
  
  // ---- 2) Run servo frame at 50 Hz ----
  unsigned long nowUs = micros();
  if (nowUs - lastFrameUs >= FRAME_PERIOD_US) {
    lastFrameUs += FRAME_PERIOD_US;
    
    // Update and output all servos
    for (int i = 0; i < 4; i++) {
      servos[i].updatePosition(servoDirections[i]);
      servos[i].outputPWM();
    }
  }
}

// ============================================================================
// Helper Functions
// ============================================================================
// (No helper functions needed - all control is via bitmapped serial input)
