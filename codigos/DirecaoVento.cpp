#include <Wire.h>
#include <Arduino.h>

//commit de teste jonas

int direcao[8] = {0, 45, 90, 135, 180, 225, 270, 315};
int direcaoInt = 0;

void setup(){
	Serial.begin(9600);
	Wire.begin(10);
	Wire.onRequest(respostaI2c);
	attachInterrupt(0 , mudancaDeEstado, RISING);
}

void loop(){
	delay(99999999999);
}

void respostaI2c(){
	Wire.write(direcaoInt);
}

void mudancaDeEstado(){
	for (int i = 3; i <= 10; i++){
      if (digitalRead(i)){
          direcaoInt = direcao[i-3];
          Serial.println(direcaoInt);
          break;
      }
  	}
}
