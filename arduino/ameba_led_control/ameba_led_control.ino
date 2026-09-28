const int BLUE_LED = LED_B;   // AMB82-MINI 板載藍燈 (D23)
const int GREEN_LED = LED_G;  // AMB82-MINI 板載綠燈 (D24)

bool blueOn = false;
bool greenOn = false;

void setLedState(const char* side, bool on) {
  if (strcmp(side, "left") == 0) {
    blueOn = on;
    digitalWrite(BLUE_LED, on ? HIGH : LOW);
  } else {
    greenOn = on;
    digitalWrite(GREEN_LED, on ? HIGH : LOW);
  }
}

// 閃爍 times 次後恢復原本的亮滅狀態
void blinkLeds(bool blue, bool green, int times) {
  for (int i = 0; i < times; i++) {
    if (blue) digitalWrite(BLUE_LED, HIGH);
    if (green) digitalWrite(GREEN_LED, HIGH);
    delay(250);
    if (blue) digitalWrite(BLUE_LED, LOW);
    if (green) digitalWrite(GREEN_LED, LOW);
    delay(250);
  }
  digitalWrite(BLUE_LED, blueOn ? HIGH : LOW);
  digitalWrite(GREEN_LED, greenOn ? HIGH : LOW);
}

void setup() {
  Serial.begin(115200);
  pinMode(BLUE_LED, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  digitalWrite(BLUE_LED, LOW);
  digitalWrite(GREEN_LED, LOW);
  Serial.println("Ameba Mini LED ready");
}

void loop() {
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "left_on") {
      setLedState("left", true);
      Serial.println("left_on: blue LED ON");
    } else if (cmd == "right_on") {
      setLedState("right", true);
      Serial.println("right_on: green LED ON");
    } else if (cmd == "left_off") {
      setLedState("left", false);
      Serial.println("left_off: blue LED OFF");
    } else if (cmd == "right_off") {
      setLedState("right", false);
      Serial.println("right_off: green LED OFF");
    } else if (cmd == "left_blink") {
      blinkLeds(true, false, 3);
      Serial.println("left_blink: blue LED blinked 3 times");
    } else if (cmd == "right_blink") {
      blinkLeds(false, true, 3);
      Serial.println("right_blink: green LED blinked 3 times");
    } else if (cmd == "both_blink") {
      blinkLeds(true, true, 3);
      Serial.println("both_blink: both LEDs blinked 3 times");
    } else {
      Serial.println("ignored");
    }
  }
}
