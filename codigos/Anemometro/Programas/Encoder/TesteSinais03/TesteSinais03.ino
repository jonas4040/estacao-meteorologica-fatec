void setup() 
{
    //Instrução para colocar o gpio que iremos utilizar como saída, ou seja, podermos alterar seu valor
    //livremente para HIGH ou LOW conforme desejarmos
    pinMode(18, INPUT_PULLUP);
    pinMode(19, INPUT_PULLUP);

    Serial.begin(57600);

    // You may have to modify the next 2 lines if using other pins than A2 and A3
    PCICR |= (1 << PCIE1); // This enables Pin Change Interrupt 1 that covers the Analog input pins or Port C.
    PCMSK1 |= (1 << PCINT10) | (1 << PCINT11); // This enables the interrupt for pin 2 and 3 of Port C.
}

bool canalA = false;
bool canalB = false;
bool canalAAnt = false;
bool canalBAnt = false;

int  contadorCW = 0;
int  contadorCCW = 0;
int  contadorCWAnt = 0;
int  contadorCCWAnt = 0;

int contador = 0;
int contadorAnt = 0;

//// when not started in motion, the current state of the encoder should be 3
//int sig1 = digitalRead(_pin1);
//int sig2 = digitalRead(_pin2);
//_oldState = sig1 | (sig2 << 1);

volatile int8_t _oldState;

volatile long _position = 0;        // Internal position (4 times _positionExt)
volatile long _positionExt = 0;     // External position
volatile long _positionExtPrev = 0; // External position (used only for direction checking)

unsigned long _positionExtTime = 0;     // The time the last position change was detected.
unsigned long _positionExtTimePrev = 0; // The time the previous position change was detected.

bool exibeLinha = false;
long tempo = 0;
const int8_t KNOBDIR[] = {
    0, -1, 1, 0,
    1, 0, 0, -1,
    -1, 0, 0, 1,
    0, 1, -1, 0};


void loop() 
{
    canalA = digitalRead(18);
    canalB = digitalRead(19);
    if ((canalA != canalAAnt) || (canalB != canalBAnt))
    {
        Serial.print(canalA);
        Serial.print("-");
        Serial.print(canalB);
        Serial.print("\n");
        canalAAnt = canalA;
        canalBAnt = canalB;
    }

    if (tempo < (millis() / 1000))
    {
        Serial.println("--------------------------------------");
        tempo = millis();
    }

}
