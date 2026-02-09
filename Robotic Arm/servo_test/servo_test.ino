int currentPos = 1500;
int targetPos  = 1500;

const int center = 1500;
const int left   = 500;
const int right  = 2500;

const int stepPos = 10;                 // microseconds per frame (speed knob)
const unsigned long framePeriodUs = 20000;  // 50 Hz
const unsigned long holdTimeoutMs = 150;    // key "released" after this silence

unsigned long lastCmdTimeMs = 0;
unsigned long lastFrameUs   = 0;

const int servoPin = 9;

void setup()
{
  pinMode(servoPin, OUTPUT);
  Serial.begin(9600);

  currentPos = center;
  targetPos  = center;
  lastCmdTimeMs = millis();
  lastFrameUs   = micros();
}

void loop()
{
  // ---- 1) Read any available input, set TARGET only ----
  while (Serial.available() > 0)
  {
    int c = Serial.read();

    if (c == 'D' || c == 'd')
    {
      targetPos = right;
      lastCmdTimeMs = millis();
    }
    else if (c == 'A' || c == 'a')
    {
      targetPos = left;
      lastCmdTimeMs = millis();
    }
  }

  // ---- 2) If no recent input, LOCK at current position (no return to center) ----
  if (millis() - lastCmdTimeMs > holdTimeoutMs)
  {
    targetPos = currentPos;
  }

  // ---- 3) Run exactly one servo frame every 20 ms ----
  unsigned long nowUs = micros();
  if (nowUs - lastFrameUs >= framePeriodUs)
  {
    lastFrameUs += framePeriodUs; // keeps a steady cadence

    // Ramp currentPos toward targetPos by stepPos
    if (currentPos < targetPos)
    {
      currentPos += stepPos;
      if (currentPos > targetPos) currentPos = targetPos;
    }
    else if (currentPos > targetPos)
    {
      currentPos -= stepPos;
      if (currentPos < targetPos) currentPos = targetPos;
    }

    // Clamp to safe bounds
    if (currentPos < left)  currentPos = left;
    if (currentPos > right) currentPos = right;

    // Output one pulse this frame
    digitalWrite(servoPin, HIGH);
    delayMicroseconds(currentPos);
    digitalWrite(servoPin, LOW);
    delayMicroseconds((int)framePeriodUs - currentPos);
  }
}
