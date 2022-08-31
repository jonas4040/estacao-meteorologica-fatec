void setup() 
{
    //Instrução para colocar o gpio que iremos utilizar como saída, ou seja, podermos alterar seu valor
    //livremente para HIGH ou LOW conforme desejarmos
    pinMode(16, INPUT_PULLUP);
    pinMode(17, INPUT_PULLUP);

    Serial.begin(57600);

    // You may have to modify the next 2 lines if using other pins than A2 and A3
    PCICR |= (1 << PCIE1); // This enables Pin Change Interrupt 1 that covers the Analog input pins or Port C.
    PCMSK1 |= (1 << PCINT10) | (1 << PCINT11); // This enables the interrupt for pin 2 and 3 of Port C.
}

bool CanalA = false;
bool CanalB = false;
bool CanalAAnt = false;
bool CanalBAnt = false;

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

const int8_t KNOBDIR[] = {
    0, -1, 1, 0,
    1, 0, 0, -1,
    -1, 0, 0, 1,
    0, 1, -1, 0};


ISR(PCINT1_vect) {
    contador = tick();
}

void loop() 
{
    //if ((contadorCWAnt != contadorCW) || (contadorCCW != contadorCCWAnt))
    if (contador != contadorAnt)
    {
        contadorCWAnt = contadorCW;
        contadorCCWAnt = contadorCCW;

        contadorAnt = contador;
        Serial.print(contador);
        Serial.print("\n");

//        Serial.print(contadorCW);
//        Serial.print("-");
//        Serial.print(contadorCCW);
//        Serial.print("\n");
//        Serial.print(CanalA);
//        Serial.print("-");
//        Serial.print(CanalB);
//        Serial.print("\n");
    }
}

long tick(void)
{
  int sig1 = digitalRead(16);
  int sig2 = digitalRead(17);
  int8_t thisState = sig1 | (sig2 << 1);

  if (_oldState != thisState) {
    _position += KNOBDIR[thisState | (_oldState << 2)];
    _oldState = thisState;

    if (thisState == 0) {
      // The hardware has 4 steps with a latch on the input state 0
      _positionExt = _position >> 2;
      _positionExtTimePrev = _positionExtTime;
      _positionExtTime = millis();
    }

  } // if
  return _position;
} // tick()

uint8_t Analisa()
{
    CanalA = digitalRead(18);
    CanalB = digitalRead(19);

    if ((CanalAAnt == 0) && (CanalA == 1))
    {
        CanalAAnt = CanalA;
        return 1;
    }

    if ((CanalBAnt == 0) && (CanalB == 1))
    {
        CanalBAnt = CanalB;
        return -1;
    }

}
