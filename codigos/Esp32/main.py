
###################################################################
#==                                                             ==#
#==  Projeto....: Estação Meteorológica                         ==#
#==  Instituição: FATEC-JD - Sistemas Embarcados                ==#
#==  Data.......: Junho/2023                                    ==#
#==                                                             ==#
#==  Trabalho da disciplina Projeto Integrador II               ==#
#==                                                             ==#
#==  Mediante o conhecimento adquirido nas disciplinas Banco de ==# 
#==  dados, Programação para Sistemas Embarcados I,  Eletrônica ==#
#==  Digital II e Engenharia de Software I,  revisar  o projeto ==#
#==  Estação Meteorológica FATEC anterior e apresentar uma nova ==#                                                                                                       ==#
#==  proposta com base no microcontrolador ESP32,   sensores  e ==#
#==  barramento I2C.                                            ==#
#==                                                             ==#
###################################################################

#== Importação de classes gerais
from machine import Pin, I2C
from time import time, sleep

#== Classes específicas do projeto (sensores)
from anemometro import Anemometro   # Velocidade do vento
from mpl3115a2 import MPL3115A2     # Pressão e altitude
from aht import AHT2x               # Temperatura e umidade
from ccs811 import CCS811           # Nível de Co2 e VTOC
from RoTW import RoTW               # Rosa dos Ventos
import bh1750                       # Luminosidade

#== Classes para configuração do ESP32 como servidor WEB E mqtt
from umqtt.simple import MQTTClient
import usocket as socket
import network
import gc

#==============================================#
#=========== Bloco de Funções =================#
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

#==============================================#
#============= Programa Principal =============#
#==============================================#

#-- Instancia objeto I2C com os pinos SCL e SDA definidos CCS811
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

#-- A lista "dispositivos" recebe um array de dispositivos encontrados
dispositivos = localizaDispI2C()
transicao = ""

gc.collect()
strBufTransmissao = ["0.0", "0.0", "N", "57", "22", "0.97", "716.4", "0.0", "0.0"]

# Dicionario dos sensores e seus topicos mqtt 
dict_mqtt_topicos = {
    'anemometro_m_seg': 'estacao/anem/m',
    'anemometro_km_h': 'estacao/anem/km',
    'direcao_vento': 'estacao/direcao_vento',
    'umidade': 'estacao/umidade',
    'temperatura': 'estacao/temperatura',
    'pressao': 'estacao/pressao',
    'altitude': 'estacao/altitude',
    'nivel_co2': 'estacao/nivel_co2',
    'luminosidade': 'estacao/luminosidade',
    'pluviometro': 'estacao/pluviometro'}

dict_sensores = {}

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
print("Iniciando WiFi...")
estacao = network.WLAN(network.STA_IF)
estacao.active(True)
#estacao.connect('FatecJdi - Alunos', 'FatecJdi2023!')
#estacao.connect('Soares','Jomi11022016')
#estacao.connect('','felipe100')
estacao.connect('Ez','12345678')

while estacao.isconnected() == False:
    pass
print(estacao.ifconfig())
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)
servidor = 'test.mosquitto.org' 
cliente = MQTTClient('NodeMCU', servidor, 1883)
print('Conexao realizada.')

#==============================================#
#=============  Loop principal ================#
#==============================================#

try:
    #-- Caso tenha sido encontrado algum dispositivo...
    if len(dispositivos) > 0:
        i = 0
        taxaCO2 = CCS811(i2c)     # Instancia os objetos utilizados para CCS811

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
                print('entrou no for')
            #==============================================#
            #===== Bloco de tratamento do Anemômetro ======#
            #==============================================#

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
                    #print("_________________________________________")
                    dict_sensores['anem_m_seg'] = str(anemometro.__mPorSegundo)
                    dict_sensores['anem_km_h'] = str(anemometro.__kmPorHora)

            #==============================================#
            #======= Bloco de tratamento dos sensores  ====#
            #======= TCRT5000 e LM339                ======#
            #======= Rosa dos ventos               ========#
            #==============================================#

                elif i == 0xA:
                    direcao_vento = RoTW(i2c, 10, 0)
                    direcao = direcao_vento.lerValor()
                    if direcao != "":
                        transicao = direcao
                    print("Direção do vento..........: ",transicao)
#                     print("_________________________________________")
                    strBufTransmissao[2] = str(direcao)

            #==============================================#
            #======= Bloco de tratamento do sensor     ====#
            #======= AHT (umidade e temperatura)     ======#
            #==============================================#

                elif i == 0x38:
                    aht = AHT2x(i2c, crc=True)
                    print("Umidade...................: {:2.2f}%".format(aht.humidity))
                    print("Temperatura...............: {:2.2f}ºC".format(aht.temperature))
                    #print("_________________________________________")
                    strBufTransmissao[3] = str(aht.humidity)
                    strBufTransmissao[4] = str(aht.temperature)

            #==============================================#
            #======= Bloco de tratamento do sensor     ====#
            #======= MPL3115A2 (pressão e altitude)  ======#
            #==============================================#

                elif (i == 0x60):
                    mpl = MPL3115A2(i2c, mode=MPL3115A2.PRESSURE)   #modo pressão 
                    pressao = mpl.pressure()
                    #temperatura = mpl.temperature()
                    print("Pressão atmosférica.......: {:2.2f}pa".format(pressao))

                    mpl = MPL3115A2(i2c, mode=MPL3115A2.ALTITUDE)   #modo altímetro 
                    altitude = mpl.altitude() 
                    print("Altitude..................: {:2.2f}m ".format(altitude))
                    #print("_________________________________________")
                    strBufTransmissao[5] = str(pressao)
                    strBufTransmissao[6] = str(altitude)

            #==============================================#
            #======= Bloco de tratamento do sensor     ====#
            #======= CCS811 (CO2 e Gases voláteis)   ======#
            #==============================================#

                elif (i == 0x5a):
                    if taxaCO2.data_ready():
                        print(f"CO2........................: {taxaCO2.eCO2:.0f} ppm, tVOC: {taxaCO2.tVOC:.0f} ppb")
                        strBufTransmissao[7] = str(taxaCO2.eCO2);

            #==============================================#
            #======= Bloco de tratamento do sensor     ====#
            #======= BH1750 (Luminosidade)           ======#
            #==============================================#

                elif ((i == 0x23) or (i == 0x5C)):
                    captura = bh1750.BH1750(i2c)
                    mesure_lux = captura.leitura_lux(bh1750.MODE_CONTINU_HAUTE_RESOLUTION)
                    if (captura.detect()):
                        while True:
                            mesure_lux = captura.leitura_lux(bh1750.MODE_CONTINU_HAUTE_RESOLUTION)
                            if mesure_lux > 0:
                                print("Luminosidade..............: {} lux".format(mesure_lux))
                                print("_________________________________________")
                                break
                            sleep(0.2)
                    strBufTransmissao[8] = str(mesure_lux);
                    #print("Luminosidade: {}".format(mesure_lux))

            #==============================================#
            #======= Bloco de tratamento do sensor     ====#
            #======= LM393 (Precipitação pluviométrica)  ==#
            #==============================================#

#TODO: COLOCAR AQUI o HTML
            html = """<!DOCTYPE html><html><head><title></title><meta charset="utf-8"></head><body><form><p align="center">""" + str(strBufTransmissao) + """</p></form></body></html>"""
            conexao.sendall(html)
            conexao.close()
            
            print('Publicando no servidor MQTT') 
            
            cliente.connect()
        
            conteudo=[
                dict_sensores['anem_m_seg'],
                dict_sensores['anem_km_h'],   
            ]
        
            cliente.publish(dict_mqtt_topicos['anemometro_m_seg'].encode(), conteudo[0].encode())
            cliente.publish(dict_mqtt_topicos['anemometro_km_h'].encode(), conteudo[1].encode()) 

            cliente.disconnect() 

            print ('Envio realizado.') 

            gc.collect()
            sleep(3)
except OSError as Err:
    print("Erro:", Err, "\n", "Tipo do erro: ", type(Err))
    print("Provável erro de comunicação com o dispositivo:",i)

except KeyboardInterrupt:
  s.close()
  estacao.active(False)

