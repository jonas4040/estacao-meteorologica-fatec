from machine import Pin, I2C

class RoTW(object):
    def __init__(self, i2c, endereco, compensacao):
        self.__endereco = endereco
        self.__compensacao = compensacao
        #self.__i2c = I2C(scl = Pin(22), sda = Pin(21), freq=400000) # configuração do i2c para o RoTW
        self.__i2c = i2c
        self.__habilitar = False
        #verificação para ver se o RoTW foi encontrado
        if endereco in self.__i2c.scan():
            print("RoTW encontrado")
            self.__habilitar = True
        else:
            print("RoTW não encontrado")
            
    def lerValor(self):
        if self.__habilitar == True:
            self.__i2c.scan()
            self.__direcao = int.from_bytes(self.__i2c.readfrom(self.__endereco, 1, 2), "BIG") # lê o valor do i2c, e converte para graus, de 0 a 360
            self.__direcao *= 45
            self.__direcao +=  self.__compensacao
            
            if self.__direcao >= 360:
                self.__direcao -= 360
            elif self.__direcao < 0:
                self.__direcao += 360

            if  self.__direcao > 337 or self.__direcao <= 22:
                self.__direcao_str = "N"
            elif self.__direcao <= 67:
                self.__direcao_str = "NE"
            elif self.__direcao <= 113:
                self.__direcao_str = "E"
            elif self.__direcao <= 158:
                self.__direcao_str = "SE"
            elif self.__direcao <= 203:
                self.__direcao_str = "S"
            elif self.__direcao <= 248:
                self.__direcao_str = "SO"
            elif self.__direcao <= 293:
                self.__direcao_str = "O"
            elif self.__direcao <= 337:
                self.__direcao_str = "NO"
            return self.__direcao_str
        else:
            return 0
            
        
