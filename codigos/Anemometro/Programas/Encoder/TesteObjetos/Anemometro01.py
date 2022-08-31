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
    #   difPosicao: representa a quantidade de pulsos do encoder.
    #   raio: representa o cumprimento da haste da concha do anemômetro, em centímetros.
    #   PPR: representa a quantidade de pulsos por revolução que possui o encoder.
    def deslocamento(self, difPosicao, raio, PPR):
        return (2 * math.pi * raio * difPosicao / PPR)

    def kmPorHora(self, difTempoMs, deslocamentoCm):
        deslocamentoKm = deslocamentoCm / 100000
        difTempoH = difTempoMs / 1000 / 3600
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

        self.__posicao = 0;

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
            self.__posicao += self.__pos[self.__estadoAtual | (self.__estadoAnterior << 2)]
            self.__estadoAnterior = self.__estadoAtual
        else:
            self.__posicao = 0

        return self.__posicao


encoder = Encoder(18, 19, 20)
anemometro = Anemometro(40);


led02  = Pin(2, Pin.OUT)

exibeLinha = False
tempoAtualNs = time.time_ns()
tempoAnteriorNs = time.time_ns()
difTempoMs = 0

tempos = []
posicao = 0
posicaoAnterior = 0;
difPosicao = 0

deslocamentoCm = 0
kmPorHora = 0

while True:

    posicao += encoder.computaMudanca() / 4


    if ((tempoAnteriorNs/1000000 + 4) < time.time()):

        tempoAtualNs = time.time_ns()
        difTempoMs = (tempoAtualNs - tempoAnteriorNs) / 1000
        difPosicao = posicao - posicaoAnterior
        if (difPosicao < 0):
            difPosicao = difPosicao * -1
        deslocamentoCm = anemometro.deslocamento(difPosicao, anemometro.comprimentoHaste, encoder.PPR)
        kmPorHora = anemometro.kmPorHora(difTempoMs, deslocamentoCm)
        posicaoAnterior = posicao
        tempoAnteriorNs = tempoAtualNs - tempoAnteriorNs
        exibeLinha = True
        print(posicao)
        print(deslocamentoCm)
        print(kmPorHora)
        if(exibeLinha):
            print("_____________________________")
            exibeLinha = False

    
