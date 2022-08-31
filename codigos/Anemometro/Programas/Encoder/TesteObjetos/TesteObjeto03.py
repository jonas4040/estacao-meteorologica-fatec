from machine import Pin
import time

#==============================#
#==== Definição de classes ====#
#==============================#

#-- classe Anemometro ---------#
class Anemometro:
    def __init__(self, canalA, canalB):
        self.__canalA = canalA
        self.__canalB = canalB
    
    @property
    def canalA(self):
        return self.__canalA

    @property
    def canalB(self):
        return self.__canalB
    
    @canalA.setter
    def set_canalA(self, canalA):
        self.__canalA = canalA

    @canalA.getter
    def get_canalA(self):
        return self.__canalA

    @canalB.setter
    def set_canalB(self, canalB):
        self.__canalB = canalB

    @canalB.getter
    def get_canalB(self):
        return self.__canalB

    def getPosition(self, posicao):
        posCanalA = 1

#-- classe Encoder ---------#
class Encoder:
    def __init__(self, canalA, canalB):
        self.__canalA = Pin(canalA, Pin.IN, Pin.PULL_UP)
        self.__canalB = Pin(canalB, Pin.IN, Pin.PULL_UP)

        self.__estadoCanalA = self.__canalA.value()
        self.__estadoCanalB = self.__canalB.value()

        self.__estadoAnterior = (self.__estadoCanalA | self.__estadoCanalB << 1)
        self.__posCW = [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]

        self.__posicao = 0;


    def checaMudanca(self):

        self.__estadoCanalA = self.__canalA.value()
        self.__estadoCanalB = self.__canalB.value()

        self.__estadoAtual = (self.__estadoCanalA | self.__estadoCanalB << 1)

        if (self.__estadoAtual != self.__estadoAnterior):
            self.__estadoAnterior = self.__estadoAtual
            return True
        else:
            return False

    def computaMudanca(self):

        if (self.checaMudanca()):
            self.__posicao += pos[self.__estadoAtual | (self.__estadoAnterior << 2)]

        return self.__posicao

encoder = Encoder(18, 19)


led02  = Pin(2, Pin.OUT)

exibeLinha = False
tempoAnterior = 0

tempos = []

p = 0

while True:


    if (encoder.checaMudanca()):
        canalAAnt = iCanalA
        canalBAnt = iCanalB
        exibeLinha = True

    if ((tempoAnterior + 10) < time.time()):
        tempoAnterior = time.time()
        tempos.append(time.time_ns())
        if(exibeLinha):
            print("_____________________________")
            p = encoder.computaMudanca() / 2
            print(p)
            print(tempos[len(tempos) - 1])
            exibeLinha = False
    
