#include <Wire.h>
//#include <stdlib.h>

int pinA = 4; // Conectado no CLK do encoder KY-040
int pinB = 2; // Conectado no DT do encoder KY-040
int contadorPosEncoder = 100;
int ultimoPinoA;
int valorA;

String strValor;
char a[15] = "               ";

void setup() {
  Wire.begin(8);                // join i2c bus with address #8
  Wire.onRequest(requestEvent); // register event

  pinMode (pinA,INPUT_PULLUP);
  pinMode (pinB,INPUT_PULLUP);
  
  //-- Memoriza posição inicial do Canal A
  ultimoPinoA = digitalRead(pinA);
}

void loop() {
    valorA = digitalRead(pinA);
    if (valorA != ultimoPinoA)            //-- Verifica se o encoder girou
    { 
        //-- Caso o encoder tenha girado, avalia em qual direção isso ocorreu
        if (digitalRead(pinB) != valorA)  //-- Caso o canal A atuou primeiro, significa que está no sentido horário
            contadorPosEncoder++;
        else                              //-- Caso o canal B atuou primeiro, significa que está no sentido anti-horário
            contadorPosEncoder--;
    }
    //strValor = sprintf("%d", contadorPosEncoder);
    strValor = String(contadorPosEncoder);
    ultimoPinoA = valorA;
}

// function that executes whenever data is requested by master
// this function is registered as an event, see setup()
void requestEvent() {
  int8_t i = 0;
  int8_t alg = 0;
  int8_t resto = 9;
  int8_t divisor = 10;

  while (resto != 0)
  {
      resto = (contadorPosEncoder % divisor);
      a[14-i] = 48 + resto;
      i++;
      divisor *= 10;
  }

//
//  for (i = 0; i < 15; i++)
//  {
//      a[14-i] = strValor.charAt(i);
//  }
  Wire.write(a);
  // as expected by master
}
