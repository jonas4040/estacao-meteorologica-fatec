int pinA = 18; // Conectado no CLK do encoder KY-040
int pinB = 19; // Conectado no DT do encoder KY-040
int contadorPosEncoder = 0;
int ultimoPinoA;
int valorA;
boolean sentidoHorario;
void setup() {
    pinMode (pinA,INPUT_PULLUP);
    pinMode (pinB,INPUT_PULLUP);

    //-- Memoriza posição inicial do Canal A
    ultimoPinoA = digitalRead(pinA);
    Serial.begin (57600);
    Serial.print("Inicializando...");
}

void loop() {
    valorA = digitalRead(pinA);
    if (valorA != ultimoPinoA)            //-- Verifica se o encoder girou
    { 
        //-- Caso o encoder tenha girado, avalia em qual direção isso ocorreu
        if (digitalRead(pinB) != valorA)  //-- Caso o canal A atuou primeiro, significa que está no sentido horário
        {
            contadorPosEncoder ++;
            sentidoHorario = true;
        }
        else                              //-- Caso o canal B atuou primeiro, significa que está no sentido anti-horário
        {
            sentidoHorario = false;
            contadorPosEncoder--;
        }
        Serial.print ("Sentido: ");

        if (sentidoHorario)
        {
            Serial.println ("horário");
        }
        else
        {
            Serial.println("anti-horário");
        }

        Serial.print("Posição do encoder: ");
        Serial.println(contadorPosEncoder);

    }
    ultimoPinoA = valorA;
}
