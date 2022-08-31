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
import bh1750

#== Classes para configuração do ESP32 como servidor web
import network
import usocket as socket
import gc

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

gc.collect()
strBufTransmissao = ["0.0", "0.0", "N", "57", "22", "0.97", "716.4", "0.0", "0.0"]

html = """<!DOCTYPE html>
<html>
  <head>
    <title>NodeMCU LED</title>
    <meta charset="utf-8">
  </head>
  <body>
    <form>
      <p align="center">""" + str(strBufTransmissao) + """</p>
    </form>
  </body>
</html>
"""

estacao = network.WLAN(network.STA_IF)
estacao.active(True)
estacao.connect('WInt', 'E705D884')
while estacao.isconnected() == False:
  pass
print('Conexao realizada.')
print(estacao.ifconfig())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

#----------------------------------------------------#
#   Loop Principal                                   #
#----------------------------------------------------#

try:
    #-- Caso tenha sido encontrado algum dispositivo...
    if len(dispositivos) > 0:
        i = 0

        if False:
            taxaCO2 = CCS811(i2c)     # Instancia os objetos utilizados para Co2

        #-- Loop infinito caso exista algum dispositivo...
        while (True):

            conexao, endereco = s.accept()
            print("Conexao de %s" % str(endereco))
            requisicao = conexao.recv(1024)
            requisicao = str(requisicao)
            print("Conteudo = %s" % requisicao)

            conexao.send('HTTP/1.1 200 OK\n')
            conexao.send('Content-Type: text/html\n')
            conexao.send('Connection: close\n\n')

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
                    #print("Velocidade do vento........:{:7.2f}m/s".format(anemometro.__mPorSegundo))
                    #print("Velocidade do vento........:{:7.2f}Km/h".format(anemometro.__kmPorHora))
                    print("_________________________________________")
                    strBufTransmissao[0] = str(anemometro.__mPorSegundo)
                    strBufTransmissao[1] = str(anemometro.__kmPorHora)

                #----------------------------------------------------#
                #   Bloco de tratamento do Sistema de                #
                #   Leitura da Direção do Vento                      #
                #----------------------------------------------------#
                elif i == 0xA:
                    direcao_vento = RoTW(i2c, 10, 0)
                    direcao = direcao_vento.lerValor()
                    print("Direção do vento..........: ",direcao)
                    print("_________________________________________")
                    strBufTransmissao[2] = str(direcao)

                #----------------------------------------------------#
                #   Bloco de tratamento do sensor AHT                #
                #   (temperatura e umidade)                          #
                #----------------------------------------------------#
                elif i == 0x38:
                    aht = AHT2x(i2c, crc=True)
                    print("Umidade...................: {:2.2f}%".format(aht.humidity))
                    print("Temperatura...............: {:2.2f}ºC".format(aht.temperature))
                    print("_________________________________________")
                    strBufTransmissao[3] = str(aht.humidity)
                    strBufTransmissao[4] = str(aht.temperature)

                #----------------------------------------------------#
                #   Bloco de tratamento do sensor MPL3115A2          #
                #   (pressão e altitude)                             #
                #----------------------------------------------------#
                elif (i == 0x60):
                    print("Pressão atmosférica.......: {:2.2f}pa".format(barometro()))
                    print("Altitude..................: {:2.2f}m ".format(altimetro()))
                    print("_________________________________________")
                    strBufTransmissao[5] = str(barometro())
                    strBufTransmissao[6] = str(altimetro())

                #------------------------------------------------------------#
                #   Bloco de tratamento do sensor CCS811                     #
                #   Qualidade do ar - concentração de Co2                    #
                #------------------------------------------------------------#
                elif (i == 0x5a):
                    if taxaCO2.data_ready():
                        print(f"CO2........................: {taxaCO2.eCO2:.0f} ppm, tVOC: {taxaCO2.tVOC:.0f} ppb")
                        strBufTransmissao[7] = str(taxaCO2.eCO2);

                elif ((i == 0x23) or (i == 0x5C)):
                    captura = bh1750.BH1750(i2c);
                    mesure_lux = captura.leitura_lux(bh1750.MODE_CONTINU_HAUTE_RESOLUTION);
                    strBufTransmissao[8] = str(mesure_lux);

            sleep(1)

            html = """<!DOCTYPE html><html><head><title></title><meta charset="utf-8"></head><body><form><p align="center">""" + str(strBufTransmissao) + """</p></form></body></html>"""
            conexao.sendall(html)
            conexao.close()

except OSError as Err:
    print("Erro:", Err, type(Err))
    print("Provável erro de comunicação com o dispositivo:",i)

except KeyboardInterrupt:
  s.close()
  estacao.active(False)
