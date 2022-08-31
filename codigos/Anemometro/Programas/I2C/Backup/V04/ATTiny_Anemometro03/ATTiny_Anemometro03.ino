#include <Wire.h>
#include <RotaryEncoder.h>

int pinA = 4; // Conectado no CLK do encoder KY-040
int pinB = 2; // Conectado no DT do encoder KY-040
int contadorPosEncoder = 0;
int ultimoPinoA;
int valorA;

String strValor;
char a[15] = "000000000000000";

RotaryEncoder encoder(pinA, pinB, RotaryEncoder::LatchMode::TWO03);
void setup() {
  Serial.begin(115200);
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event

  pinMode (pinA,INPUT_PULLUP);
  pinMode (pinB,INPUT_PULLUP);
  
  //-- Memoriza posição inicial do Canal A
  ultimoPinoA = digitalRead(pinA);
}

void loop() {
    static int pos = 0;
    encoder.tick();

    int contadorPosEncoder = encoder.getPosition();
    if (pos != contadorPosEncoder) {
  //    Serial.print("pos:");
  //    Serial.print(contadorPosEncoder);
  //    Serial.print(" dir:");
  //    Serial.println((int)(encoder.getDirection()));
        pos = contadorPosEncoder;
    }
  
    if (contadorPosEncoder < 0) contadorPosEncoder *= -1;
    int dividendo = contadorPosEncoder;
    int divisor = 10;
    int resto = 9;
    int8_t i = 0;

    while (1)
    {
        resto = dividendo % divisor;
        dividendo = dividendo / divisor;
        if ((dividendo == 0) && (resto == 0)) break;
        a[14-i] = 48 + resto;
        i++;
    }
    ultimoPinoA = valorA;
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
