// This sketch prints received IR signals to the serial monitor
// IR Library: https://github.com/Arduino-IRremote/Arduino-IRremote

#include <IRremote.hpp>
#define IR_RECEIVE_PIN 7

void setup() {
  Serial.begin(9600);
  IrReceiver.begin(IR_RECEIVE_PIN, DISABLE_LED_FEEDBACK);
}

void loop() {
  if (IrReceiver.decode()) {
    Serial.println(IrReceiver.decodedIRData.decodedRawData, HEX);
    IrReceiver.resume();
  }
}
