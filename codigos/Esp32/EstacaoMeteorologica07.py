##########################################################
#==  Projeto....: Estação Meteorológica                ==#
#==  Instituição: FATEC-JD - Sistemas Embarcados       ==#
#==  Data.......: Maio/2022                            ==#
##########################################################

#== Importação de classes gerais de uso no programa
from machine import Pin, I2C
from time import time, sleep

#== Classes específicas do projeto (sensores)
from anemometro import Anemometro
from mpl3115a2 import MPL3115A2
from aht import AHT2x
from ccs811 import CCS811
from RoTW import RoTW

#==============================================#
#============   Bloco de Funções   ============#
#==============================================#

#-- Função: localizaDispI2C()
#-- Descrição: Localiza dispositivos I2C na rede e retorna uma
#   lista contendo os dispositivos encontrados
def localizaDispI2C():
    print('Procura por dispositivos I2C na rede...')
    dispositivos = i2c.scan()
    if len(dispositivos) == 0:
        print("Nenhum dispositivo encontrado!")
    else:
        print('Quantidade de dispositivos I2C encontrados:',len(dispositivos))

    for dispositivo in dispositivos: 
        print("Endereço decimal: ",dispositivo," | Endereço hexadecimal: ",hex(dispositivo))
    return dispositivos

def altimetro(): 
    mpl = MPL3115A2(i2c, mode=MPL3115A2.ALTITUDE)#modo altímetro 
    altitude = mpl.altitude() 
    return altitude  

def barometro(): 
    mpl = MPL3115A2(i2c, mode=MPL3115A2.PRESSURE)#modo altímetro 
    pressao = mpl.pressure() 
    temperatura = mpl.temperature() 
    return pressao 


#==============================================#
#============= Programa Principal =============#
#==============================================#

#-- Instancia objeto I2C com os pinos SCL e SDA definidos
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

#-- A lista "dispositivos" recebe um array de dispositivos encontrados
dispositivos = localizaDispI2C()

#----------------------------------------------------#
#   Loop Principal                                   #
#----------------------------------------------------#

#dispositivos = [0x9, 0x38]

try:
    #-- Caso tenha sido encontrado algum dispositivo...
    if len(dispositivos) > 0:
        i = 0
        taxaCO2 = CCS811(i2c)     # Instancia os objetos utilizados para Co2

        #-- Loop infinito caso exista algum dispositivo...
        while (True):

            #-- Varre todos os dispositivos da rede e "pega" o 
            #   que eles estão escrevendo no intervalo de 1 segundo
            for i in dispositivos:

                #----------------------------------------------------#
                #   Bloco de tratamento do Anemômetro                #
                #----------------------------------------------------#
                if i == 0x9:

                    #-- Constantes para cálculo de velocidade do anemômetro
                    PPR            = 1
                    COMPR_HASTE    = 15
                    FATOR_CORRECAO = 3.001

                    #-- Instancia os objetos utilizados no anemômetro
                    anemometro = Anemometro(COMPR_HASTE, PPR, FATOR_CORRECAO);

                    anemometro.velocidade(i2c, i)

                    #-- Gera a saída pelo terminal para conferência
                    #print("Direção do vento...........:", anemometro.__direcaoVento)
                    print("Deslocamento da roda.......:{:7.2f}cm".format(anemometro.__deslocamentoCm))
                    print("Velocidade do vento........:{:7.2f}m/s".format(anemometro.__mPorSegundo))
                    print("Velocidade do vento........:{:7.2f}Km/h".format(anemometro.__kmPorHora))
                    print("_________________________________________")

                #----------------------------------------------------#
                #   Bloco de tratamento do Sistema de                #
                #   Leitura da Direção do Vento                      #
                #----------------------------------------------------#
                elif i == 0xA:
                    direcao_vento = RoTW(i2c, 10, 0)
                    direcao = direcao_vento.lerValor()
                    print("Direção do vento..........: ",direcao)
                    print("_________________________________________")

                #----------------------------------------------------#
                #   Bloco de tratamento do sensor AHT                #
                #   (temperatura e umidade)                          #
                #----------------------------------------------------#
                elif i == 0x38:
                    aht = AHT2x(i2c, crc=True)
                    print("Umidade...................: {:2.2f}%".format(aht.humidity))
                    print("Temperatura...............: {:2.2f}ºC".format(aht.temperature))
                    print("_________________________________________")

                #----------------------------------------------------#
                #   Bloco de tratamento do sensor MPL3115A2          #
                #   (pressão e altitude)                             #
                #----------------------------------------------------#
                elif (i == 0x60):
                    print("Pressão atmosférica.......: {:2.2f}pa".format(barometro()))
                    print("Altitude..................: {:2.2f}m ".format(altimetro()))
                    print("_________________________________________")

                #------------------------------------------------------------#
                #   Bloco de tratamento do sensor CCS811                     #
                #   Qualidade do ar - concentração de Co2                    #
                #------------------------------------------------------------#
                elif (i == 0x5a):
                    if taxaCO2.data_ready():
                        print(f"CO2........................: {taxaCO2.eCO2:.0f} ppm, tVOC: {taxaCO2.tVOC:.0f} ppb")

                sleep(1)

except OSError as Err:
    print("Erro:", Err, type(Err))
    print("Provável erro de comunicação com o dispositivo:",i)
