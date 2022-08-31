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
    def __init__(self, __comprimentoHaste):
        self.__tempoInicial = time.time()

        self.__ultimoTempo = 0
        self.__comprimentoHaste = __comprimentoHaste

        self.__deslocamentoCm = 0.0
        self.__mPorSegundo    = 0.0
        self.__kmPorHora      = 0.0

    #---------------- MÉTODOS -----------------#

    #-- Método: deslocamento(difPulsos, raio, PPR)
    #-- retorna o deslocamento da concha do anemômetro, em centímetros.
    #   difPulsos: representa a quantidade de pulsos do encoder.
    #   raio: representa o cumprimento da haste da concha do anemômetro, em centímetros.
    #   PPR: representa a quantidade de pulsos por revolução que possui o encoder.
    @staticmethod
    def deslocamento(difPulsos, raio, PPR):
        return (2 * math.pi * raio * difPulsos / PPR)

    #-- Método: metroPorSegundo(difTempo, deslocamentoCm)
    #-- retorna o deslocamento em metros por segundo (m/s)
    #   difTempo: diferença entre a leitura anterior e a atual, em segundos.
    #   __deslocamentoCm: representa o deslocamento medido em centímetros.
    @staticmethod
    def metroPorSegundo(difTempo, deslocamentoCm, FATOR_CORRECAO):
        difTempoH = difTempo
        return ((deslocamentoCm / 100.0 / difTempoH) * FATOR_CORRECAO)

    #-- Método: quilometroPorHora(difTempo, deslocamentoCm)
    #-- retorna o deslocamento em KM por hora (KM/h)
    #   difTempo: diferença entre a leitura anterior e a atual, em segundos.
    #   __deslocamentoCm: representa o deslocamento medido em centímetros.
    @staticmethod
    def quilometroPorHora(difTempo, deslocamentoCm, FATOR_CORRECAO):
        deslocamentoKm = (deslocamentoCm / 100000.0)
        difTempoH = (difTempo / 3600.0)
        return ((deslocamentoKm / difTempoH) * FATOR_CORRECAO)

#-- Função localiza dispositivos, e retorna a quantidade
#   encontrada
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

#-- Constantes para cálculo de velocidade do anemômetro
PPR = 1               # Define qtd. de pulsos por revolução dos sensores
COMPR_HASTE = 15      # Define qtd. de pulsos por revolução dos sensores
FATOR_CORRECAO = 1.3  # Fator de correção a ser definido após calibração

#==============================================#
#============= Programa Principal =============#
#==============================================#

#-- Instancia os objetos utilizados no anemômetro
anemometro = Anemometro(14);

#-- Instancia objeto I2C com os pinos SCL e SDA definidos
i2c = I2C(0, scl=Pin(22), sda=Pin(21))

#-- A lista "dispositivos" possui um array de dispositivos encontrados
dispositivos = localizaDispI2C()

#-- Variáveis globais do programa
b = ""                # Buffer de dados recebido do dispositivo

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
    if len(dispositivos) > 0:
        i = 0

        #-- Loop infinito caso exista algum dispositivo...
        while (True):

            #-- Varre todos os dispositivos da rede e "pega" o 
            #   que eles estão escrevendo no intervalo de 1 segundo
            for i in dispositivos: 
                buffer = i2c.readfrom(i, 15)             # lê 18 bytes do periférico endereçado como "i"

                for j in buffer:
                    b = b + chr(j)

                #-- Verifica direção do vento
                direcaoVento = b[9]

                pulsosAtual = convCharToInt(b, 10, 14)
                print(b);
                b = ""

                #-- Inicializa o temporizador para cálculo de velocidade
                tempoAtual = time.time()

                #-- Computa diferença de tempo entre os eventos
                difTempo = (tempoAtual - tempoAnterior)

                #-- O encoder gera quatro leituras para cada mudança
                difPulsos = ((pulsosAtual))

                #-- Atualiza varíaveis de controle de pulso e tempo
                pulsosAnterior = (pulsosAtual)
                tempoAnterior = (tempoAtual)

                #-- Realiza todos os cálculos de velocidade
                if (difTempo > 0):
                    anemometro.__deslocamentoCm = anemometro.deslocamento(difPulsos, anemometro.__comprimentoHaste, PPR)
                    anemometro.__mPorSegundo    = anemometro.metroPorSegundo(difTempo, anemometro.__deslocamentoCm, FATOR_CORRECAO)
                    anemometro.__kmPorHora      = anemometro.quilometroPorHora(difTempo, anemometro.__deslocamentoCm, FATOR_CORRECAO)

                    #-- Gera a saída pelo terminal para conferência
                    print("Direção do vento...........:", direcaoVento)
                    print("Deslocamento em pulsos.....:", difPulsos)
                    print("Deslocamento em centímetros:", anemometro.__deslocamentoCm)
                    print("Metros por segundo.........:", anemometro.__mPorSegundo)
                    print("KM por hora................:", anemometro.__kmPorHora)
                    print("_________________________________________")

                time.sleep(1)

except OSError as Err:
    print("Erro:", Err, type(Err))
    print("Provável erro de comunicação com o dispositivo:",i)
