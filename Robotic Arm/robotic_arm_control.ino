/*
 * Robotic Arm Multi-Servo PWM Controller - Refactored OOP Version
 * Arduino Nano - 4 Servo Control System
 * 
 * Key Mappings:
 * A/D = X-axis (servo index 0)
 * W/S = Y-axis (servo index 1)
 * LEFT/RIGHT = Z-axis (servo index 2)
 * UP/DOWN = Grabber (servo index 3)
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
const int LOWER_BOUND = 2000;
const int UPPER_BOUND = 1000;
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
  
  // Index 2: Z-axis (LEFT/RIGHT)
  servos[2].init(SERVO_Z_PIN, "Z-Axis", START_POS, &posUpdaterZ);
  
  // Index 3: Gripper (UP/DOWN)
  servos[3].init(SERVO_GRIPPER_PIN, "Gripper", START_POS, &posUpdaterGripper);
  
  lastFrameUs = micros();
  
  Serial.println("===========================================");
  Serial.println("Robotic Arm Initialized - OOP Version 2.0");
  Serial.println("===========================================");
  Serial.println("Controls:");
  Serial.println("  X-Axis:  A (decrease) / D (increase)");
  Serial.println("  Y-Axis:  W (increase) / S (decrease)");
  Serial.println("  Z-Axis:  [ (decrease) / ] (increase)");
  Serial.println("  Gripper: - (decrease) / = (increase)");
  Serial.println("===========================================");
  Serial.println();
  
  // Optional: Customize individual axis step sizes
  // posUpdaterY.setStepSize(15);  // Make Y-axis move slower
}

// ============================================================================
// Main Loop
// ============================================================================

void loop() {
  // ---- 1) Read input and set directions ----
  if (Serial.available() > 0) {
    char key = Serial.read();
    
    // Reset all directions
    for (int i = 0; i < 4; i++) {
      servoDirections[i] = 0;
    }
    
    // Process key input
    processKeyInput(key);
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
// Key Input Processing
// ============================================================================

void processKeyInput(char key) {
  switch (key) {
    // X-Axis control (A/D)
    case 'a':
    case 'A':
      servoDirections[0] = -1;  // Decrease
      Serial.print("X-Axis: ");
      Serial.println(servos[0].getCurrentPosition());
      break;
      
    case 'd':
    case 'D':
      servoDirections[0] = 1;   // Increase
      Serial.print("X-Axis: ");
      Serial.println(servos[0].getCurrentPosition());
      break;
    
    // Y-Axis control (W/S)
    case 'w':
    case 'W':
      servoDirections[1] = 1;   // Increase
      Serial.print("Y-Axis: ");
      Serial.println(servos[1].getCurrentPosition());
      break;
      
    case 's':
    case 'S':
      servoDirections[1] = -1;  // Decrease
      Serial.print("Y-Axis: ");
      Serial.println(servos[1].getCurrentPosition());
      break;
    
    // Z-Axis control (LEFT/RIGHT represented as [ and ])
    case '[':  // LEFT key
      servoDirections[2] = -1;  // Decrease
      Serial.print("Z-Axis: ");
      Serial.println(servos[2].getCurrentPosition());
      break;
      
    case ']':  // RIGHT key
      servoDirections[2] = 1;   // Increase
      Serial.print("Z-Axis: ");
      Serial.println(servos[2].getCurrentPosition());
      break;
    
    // Gripper control (UP/DOWN represented as - and =)
    case '-':  // DOWN key
      servoDirections[3] = -1;  // Decrease (close)
      Serial.print("Gripper: ");
      Serial.println(servos[3].getCurrentPosition());
      break;
      
    case '=':  // UP key
      servoDirections[3] = 1;   // Increase (open)
      Serial.print("Gripper: ");
      Serial.println(servos[3].getCurrentPosition());
      break;
    
    // Status display
    case 'p':
    case 'P':
      printStatus();
      break;
    
    // Reset all servos to start position
    case 'r':
    case 'R':
      resetAllServos();
      break;
      
    default:
      // Unknown key - do nothing
      break;
  }
}

// ============================================================================
// Helper Functions
// ============================================================================

void printStatus() {
  Serial.println("\n=== Current Servo Positions ===");
  for (int i = 0; i < 4; i++) {
    Serial.print(servos[i].getAxisName());
    Serial.print(": ");
    Serial.print(servos[i].getCurrentPosition());
    Serial.println(" us");
  }
  Serial.println("================================\n");
}

void resetAllServos() {
  Serial.println("Resetting all servos to start position...");
  for (int i = 0; i < 4; i++) {
    servos[i].init(servos[i].getPin(), servos[i].getAxisName(), START_POS, 
                   (i == 0) ? &posUpdaterX : 
                   (i == 1) ? &posUpdaterY : 
                   (i == 2) ? &posUpdaterZ : &posUpdaterGripper);
  }
  printStatus();
}
