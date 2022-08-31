void setup() 
{
    pinMode(16, INPUT_PULLUP); // A2 - Clock
    pinMode(17, INPUT_PULLUP); // A3 - Data

    Serial.begin(57600);

    // Interrupções nos pinos A2 e A3
    PCICR |= (1 << PCIE1);
    PCMSK1 |= (1 << PCINT10) | (1 << PCINT11); // Ativa interrupções para os pinos 2 e 3 do PORT C.
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
    if (contador != contadorAnt)
    {
        contadorCWAnt = contadorCW;
        contadorCCWAnt = contadorCCW;

        contadorAnt = contador;
        Serial.print(contador);
        Serial.print("\n");
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
