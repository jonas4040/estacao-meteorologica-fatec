#include <Wire.h>
#include <RotaryEncoder.h>

#define TAM_BUFFER          15
#define POS_DIRECAO         10
#define MODO_DEBUG          0

int pinA = 1; // Conectado no CLK do encoder KY-040
int pinB = 4; // Conectado no DT  do encoder KY-040
int contadorPosEncoder = 0;

char bufTransmissao[TAM_BUFFER] = "000000000000000";

RotaryEncoder encoder(pinA, pinB);

ISR(PCINT0_vect)
{
    encoder.tick(); // just call tick() to check the state.
}
void setup() {
    Wire.begin(0x08);                // Estabelece que o dispositivo terá endereço 8
    Wire.onRequest(requestEvent);    // Registra o serviço para a solicitação I2C

    //-- Registradores para a interrução nos pinos PB1 e PB4
    GIMSK |= (1 << PCIE);                   // Habilita interrupção nos pinos PB
    PCMSK |= (1 << PCINT1) | (1 << PCINT4); // Configura os pinos PB1 e PB4 para uma interrupção de mudança de estado
}

void loop() {
    static int pos = 0;
    char direcao[1] = "N";
    encoder.tick();

    int newPos = encoder.getPosition();
    if (pos != newPos)
    {
        if (newPos < pos)
            direcao[1] = 'S';

        contadorPosEncoder++;
        pos = newPos;
    }

    int dividendo = contadorPosEncoder;
    int divisor = 10;
    int8_t resto = 0;
    int8_t i = 0;

    while (1)
    {
        resto = dividendo % divisor;
        dividendo = dividendo / divisor;
        if ((dividendo == 0) && (resto == 0)) break;
        bufTransmissao[TAM_BUFFER-i-1] = 48 + resto;
        i++;
    }
    bufTransmissao[POS_DIRECAO] = direcao[1];
}

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {

    Wire.write(bufTransmissao);
    contadorPosEncoder = 0;
    for (int8_t i = 0; i < TAM_BUFFER; i++)
        bufTransmissao[i] = '0';
  // as expected by master
}
