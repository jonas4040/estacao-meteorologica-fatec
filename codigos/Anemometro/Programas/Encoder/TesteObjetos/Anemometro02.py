from machine import Pin
import time
import math

#==============================#
#==== Definição de classes ====#
#==============================#

#-- classe Anemometro ---------#
class Anemometro:
    def __init__(self, comprimentoHaste):
        self.__tempoInicial = time.time()

        self.__ultimoTempo = 0
        self.__comprimentoHaste = comprimentoHaste

    @property
    def tempoAtual(self):
        return time.time()

    @property
    def ultimoTempo(self):
        return self.__ultimoTempo

    @property
    def comprimentoHaste(self):
        return self.__comprimentoHaste

    #-- retorna o deslocamento da concha do anemômetro, em centímetros.
    #   difPulsos: representa a quantidade de pulsos do encoder.
    #   raio: representa o cumprimento da haste da concha do anemômetro, em centímetros.
    #   PPR: representa a quantidade de pulsos por revolução que possui o encoder.
    def deslocamento(self, difPulsos, raio, PPR):
        return (2 * math.pi * raio * difPulsos / PPR)

    def mPorSegundo(self, difTempo, deslocamentoCm):
        difTempoH = difTempo
        return (deslocamentoCm / 100 / difTempoH)

    def kmPorHora(self, difTempo, deslocamentoCm):
        deslocamentoKm = deslocamentoCm / 100000
        difTempoH = difTempo / 3600
        return (deslocamentoKm / difTempoH)

#-- classe Encoder ------------#
class Encoder:
    def __init__(self, canalA, canalB, PPR):
        self.__canalA = Pin(canalA, Pin.IN, Pin.PULL_UP)
        self.__canalB = Pin(canalB, Pin.IN, Pin.PULL_UP)
        self.__PPR = PPR

        self.__estadoCanalA = self.__canalA.value()
        self.__estadoCanalB = self.__canalB.value()

        self.__estadoAnterior = (self.__estadoCanalA | self.__estadoCanalB << 1)
        self.__pos = [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]

        self.__pulsos = 0;

        self.__estadoCanalA = 0
        self.__estadoCanalB = 0
        self.__estadoAtual = 0
        self.__estadoAnterior = 0

    @property
    def PPR(self):
        return self.__PPR

    def computaMudanca(self):

        self.__estadoCanalA = self.__canalA.value()
        self.__estadoCanalB = self.__canalB.value()

        self.__estadoAtual = (self.__estadoCanalA | self.__estadoCanalB << 1)

        if (self.__estadoAtual != self.__estadoAnterior):
            self.__pulsos += self.__pos[self.__estadoAtual | (self.__estadoAnterior << 2)]
            self.__estadoAnterior = self.__estadoAtual
        else:
            self.__pulsos = 0

        return self.__pulsos


encoder    = Encoder(18, 19, 20)
anemometro = Anemometro(40);

tempoAtual = time.time()
tempoAnterior = time.time()
difTempo = 0

pulsosAtual = 0;
pulsosAnterior = 0;
difPulsos = 0

deslocamentoCm = 0
mPorSegundo = 0
kmPorHora = 0

while True:

    pulsosAtual += encoder.computaMudanca()
    tempoAtual = time.time()

    if (pulsosAtual != pulsosAnterior):
        if ((tempoAnterior + 1) < tempoAtual):

            difTempo = ((tempoAtual - tempoAnterior))
            difPulsos = ((pulsosAtual - pulsosAnterior) / 4)
            pulsosAnterior = (pulsosAtual)
            tempoAnterior = (tempoAtual)

            deslocamentoCm = anemometro.deslocamento(difPulsos, anemometro.comprimentoHaste, encoder.PPR)
            kmPorHora = anemometro.kmPorHora(difTempo, deslocamentoCm)
            mPorSegundo = anemometro.mPorSegundo(difTempo, deslocamentoCm)

            print("Deslocamento em pulsos.....:", difPulsos)
            print("Deslocamento em centímetros:", deslocamentoCm)
            print("Metros por segundo.........:", mPorSegundo)
            print("KM por hora................:", kmPorHora)

            print("_____________________________________")


    
