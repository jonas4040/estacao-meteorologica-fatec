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
    
    __posCW = [0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0]

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
        


fatecAnemometro = Anemometro(18, 19)
canalA = Pin(fatecAnemometro.canalA, Pin.IN, Pin.PULL_UP)
canalB = Pin(fatecAnemometro.canalB, Pin.IN, Pin.PULL_UP)

led02  = Pin(2, Pin.OUT)

canalAAnt = 0
canalBAnt = 0
exibeLinha = False
tempoAnterior = 0
print(fatecAnemometro.canalA)
print(fatecAnemometro.canalB)

while True:
    iCanalA = canalA.value()
    iCanalB = canalB.value()
    if (iCanalA != canalAAnt) or (iCanalB != canalBAnt):
        print("Canal A: ", iCanalA)
        print("Canal B: ", iCanalB)
        canalAAnt = iCanalA
        canalBAnt = iCanalB
        exibeLinha = True
    if (tempoAnterior < time.time()):
        tempoAnterior = time.time()
        if(exibeLinha):
            print("_____________________________")
            exibeLinha = False
    
