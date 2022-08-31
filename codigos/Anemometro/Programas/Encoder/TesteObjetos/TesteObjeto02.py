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
        

posCW = [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]

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

iCanalA = canalA.value()
iCanalB = canalB.value()
_oldState = (iCanalA | iCanalB << 1)
print(_oldState)

_position = 0
_positionExt = 0
_positionExtPrev = 0
_positionExtTimePrev = 0;
_positionExtTime = 0;
p = 0

tempos = []

while True:
    iCanalA = canalA.value()
    iCanalB = canalB.value()
    thisState = iCanalA | (iCanalB << 1)

    if (_oldState != thisState):
        _position += posCW[thisState | (_oldState << 2)]
        _oldState = thisState

    if (thisState == 0):
        _positionExt = _position >> 2;
        _positionExtTimePrev = _positionExtTime;
        _positionExtTime = time.time();

    if (iCanalA != canalAAnt) or (iCanalB != canalBAnt):
        canalAAnt = iCanalA
        canalBAnt = iCanalB
        exibeLinha = True

    if ((tempoAnterior + 10) < time.time()):
        tempoAnterior = time.time()
        tempos.append(time.time_ns())
        if(exibeLinha):
            print("_____________________________")
            p = _position / 2
            print(p)
            print(tempos[len(tempos) - 1])
            exibeLinha = False
    
