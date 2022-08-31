#include <Wire.h>
#include <RotaryEncoder.h>

int pinA = 1; // Conectado no CLK do encoder KY-040
int pinB = 4; // Conectado no DT do encoder KY-040
int contadorPosEncoder = 0;
int ultimoPinoA;
int valorA;

String strValor;
char a[15] = "000000000000000";

RotaryEncoder encoder(pinA, pinB);
void setup() {
    Serial.begin(115200);
    Wire.begin(8);                // join i2c bus with address #8
    Wire.onRequest(requestEvent); // register event

    // You may have to modify the next 2 lines if using other pins than A2 and A3
    //PCICR |= (1 << PCIE1); // This enables Pin Change Interrupt 1 that covers the Analog input pins or Port C.
    GIMSK |= (1 << PCIE); // This enables Pin Change Interrupt 1 that covers the Analog input pins or Port C.
    PCMSK |= (1 << PCINT1) | (1 << PCINT4); // This enables the interrupt for pin 2 and 3 of Port C.
}

ISR(PCINT0_vect) {
    encoder.tick(); // just call tick() to check the state.
}

void loop() {
    static int pos = 0;
    encoder.tick();

    int newPos = encoder.getPosition();
    if (pos != newPos) {
        contadorPosEncoder++;
        pos = newPos;
    }

    if (contadorPosEncoder < 0) contadorPosEncoder *= -1;
    int dividendo = contadorPosEncoder;
    int divisor = 10;
    int resto = 0;
    int8_t i = 0;

    while (1)
    {
        resto = dividendo % divisor;
        dividendo = dividendo / divisor;
        if ((dividendo == 0) && (resto == 0)) break;
        a[14-i] = 48 + resto;
        i++;
    }
}

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {

    Wire.write(a);
    contadorPosEncoder = 0;
    for (int8_t i = 0; i < 15; i++)
        a[i] = '0';
  // as expected by master
}
