##########################################################
#==  ROTINA PARA LEITURA DE DADOS DE DISPOSITIVOS I2C  ==#
##########################################################

#-- importação de objetos de uso no programa
from machine import Pin, I2C
from time import sleep_ms


#-- Instancia objeto I2C com os pinos SCL e SDA definidos
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

#-- Função localiza dispositivos, e retorna a quantidade
#   encontrada
def localizaDispI2C():
    print('Procura por dispositivos I2C na rede...')
    devices = i2c.scan()
    if len(devices) == 0:
        print("Nenhum dispositivo encontrado!")
    else:
        print('Quantidade de dispositivos I2C encontrados:',len(devices))

    for device in devices: 
        print("Endereço decimal: ",device," | Endereço hexadecimal: ",hex(device))
    return devices

#-- A lista "devices" possui um array de dispositivos encontrados
devices = localizaDispI2C()

b = ""

#-- Caso tenha sido encontrado algum dispositivo...
if len(devices) > 0:
    i = 0

    #-- Loop infinito caso exista algum dispositivo...
    while (True):

        #-- Varre todos os dispositivos da rede e "pega" o 
        #   que eles estão escrevendo no intervalo de 1 segundo
        for i in devices: 
            buffer = i2c.readfrom(i, 15)             # lê 18 bytes do periférico endereçado como "i"
            
            for j in buffer:
                b = b + chr(j)
            print("Buffer:",b)                      # Imprime o buffer lido
            b = ""
            sleep_ms(1000)
