#include <RotaryEncoder.h>

// Setup a RoraryEncoder for pins A2 and A3:
RotaryEncoder encoder(A2, A3);

void setup()
{
    Serial.begin(57600);
    Serial.println("SimplePollRotator example for the RotaryEncoder library.");

    // You may have to modify the next 2 lines if using other pins than A2 and A3
    PCICR |= (1 << PCIE1); // This enables Pin Change Interrupt 1 that covers the Analog input pins or Port C.
    PCMSK1 |= (1 << PCINT10) | (1 << PCINT11); // This enables the interrupt for pin 2 and 3 of Port C.

} // setup()
// The Interrupt Service Routine for Pin Change Interrupt 1
// This routine will only be called on any signal change on A2 and A3: exactly where we need to check.

ISR(PCINT1_vect) {
    encoder.tick(); // just call tick() to check the state.
}

// Read the current position of the encoder and print out when changed.
void loop()
{
    static int pos = 0;
    int newPos = encoder.getPosition();
    if (pos != newPos) {
        Serial.print(newPos);
        Serial.println();
        pos = newPos;
        // Just to show, that long lasting procedures don't break the rotary encoder:
        // When newPos is 66 the ouput will freeze, but the turned positions will be recognized even when not polled.
        // The interrupt still works.
        // The output is correct 6.6 seconds later.
        if (newPos == 66)
            delay(6600);
    } // if
} // loop ()
// The End
