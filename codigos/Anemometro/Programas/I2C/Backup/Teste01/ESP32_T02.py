##########################################################
#==  ROTINA PARA LEITURA DE DADOS DE DISPOSITIVOS I2C  ==#
##########################################################

#-- importação de objetos de uso no programa
from machine import Pin, I2C
import time
import math

#==============================================#
#============ Definição de classes ============#
#==============================================#

#----------------------------------------------#
#------------ classe Anemometro ---------------#
#----------------------------------------------#
class Anemometro:

    #--------------- CONSTRUTOR ---------------#
    def __init__(self, comprimentoHaste):
        self.tempoInicial = time.time()

        self.ultimoTempo = 0
        self.comprimentoHaste = comprimentoHaste

        self.deslocamentoCm = 0.0
        self.mPorSegundo    = 0.0
        self.kmPorHora      = 0.0

    #---------------- MÉTODOS -----------------#

    #-- Método: deslocamento(difPulsos, raio, PPR)
    #-- retorna o deslocamento da concha do anemômetro, em centímetros.
    #   difPulsos: representa a quantidade de pulsos do encoder.
    #   raio: representa o cumprimento da haste da concha do anemômetro, em centímetros.
    #   PPR: representa a quantidade de pulsos por revolução que possui o encoder.
    @staticmethod
    def deslocamento(difPulsos, raio, PPR):
        return (2 * math.pi * raio * difPulsos / PPR)

    #-- Método: mPorSegundo(difTempo, deslocamentoCm)
    #-- retorna o deslocamento em metros por segundo (m/s)
    #   difTempo: diferença entre a leitura anterior e a atual, em segundos.
    #   deslocamentoCm: representa o deslocamento medido em centímetros.
    @staticmethod
    def metroPorSegundo(difTempo, deslocamentoCm):
        difTempoH = difTempo
        return (deslocamentoCm / 100.0 / difTempoH)

    #-- Método: kmPorHora(difTempo, deslocamentoCm)
    #-- retorna o deslocamento em KM por hora (KM/h)
    #   difTempo: diferença entre a leitura anterior e a atual, em segundos.
    #   deslocamentoCm: representa o deslocamento medido em centímetros.
    @staticmethod
    def quilometroPorHora(difTempo, deslocamentoCm):
        deslocamentoKm = (deslocamentoCm / 100000.0)
        difTempoH = (difTempo / 3600.0)
        return (deslocamentoKm / difTempoH)

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

def convCharToInt(a, inicio, fim):
    i = fim
    total = 0
    j = 1
    algarismo = 0
    while i > inicio:
        algarismo = int(a[i])
        total = total + (algarismo * j)
        j = j * 10
        i = i - 1
    return total

#==============================================#
#============= Programa Principal =============#
#==============================================#

#-- Instancia os objetos utilizados no anemômetro
anemometro = Anemometro(40);

#-- Instancia objeto I2C com os pinos SCL e SDA definidos
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

#-- A lista "devices" possui um array de dispositivos encontrados
devices = localizaDispI2C()

b = ""
pulsos = 0

#-- Variáveis para controle do intervalo entre movimentos
tempoAtual = time.time()
tempoAnterior = time.time()
difTempo = 0

#-- Variáveis para controle da qtd. de pulsos do intervalo
pulsosAtual = 0;
pulsosAnterior = 0;
difPulsos = 0

#-- Varíavel de controle da direção do vento
direcaoVento = 'N'

try:
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
                #print("Buffer:",b)                      # Imprime o buffer lido
                pulsosAtual = convCharToInt(b, 10, 14)
                #print("Pulsos:",pulsos)
                b = ""

                #-- Inicializa o temporizador para cálculo de velocidade
                tempoAtual = time.time()+1

                #-- Verifica se houve variação do encoder no intervalo
                #if (pulsosAtual != pulsosAnterior):

                #-- Só atualiza as informações a cada segundo
                #if ((tempoAnterior + 1) < tempoAtual):

                #-- Computa diferença de tempo entre os eventos
                difTempo = (tempoAtual - tempoAnterior)

                #-- O encoder gera quatro leituras para cada mudança
                difPulsos = ((pulsosAtual))

                #-- Verifica direção do vento
                if (difPulsos < 0):
                    difPulsos = (difPulsos * -1)
                    direcaoVento = 'S'
                else:
                    direcaoVento = 'N'

                #-- Atualiza varíaveis de controle de pulso e tempo
                pulsosAnterior = (pulsosAtual)
                tempoAnterior = (tempoAtual)

                #-- Realiza todos os cálculos de velocidade
                anemometro.deslocamentoCm = anemometro.deslocamento(difPulsos, anemometro.comprimentoHaste, 20)
                anemometro.mPorSegundo    = anemometro.metroPorSegundo(difTempo, anemometro.deslocamentoCm)
                anemometro.kmPorHora      = anemometro.quilometroPorHora(difTempo, anemometro.deslocamentoCm)

                #-- Gera a saída pelo terminal para conferência
                print("Direção do vento...........:", direcaoVento)
                print("Deslocamento em pulsos.....:", difPulsos)
                print("Deslocamento em centímetros:", anemometro.deslocamentoCm)
                print("Metros por segundo.........:", anemometro.mPorSegundo)
                print("KM por hora................:", anemometro.kmPorHora)
                print("_________________________________________")

                time.sleep(1)

except OSError:
    print("Provável erro de comunicação com o dispositivo:",i)
