from machine import Pin
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


#----------------------------------------------#
#-------------- classe Encoder ----------------#
#----------------------------------------------#
class Encoder:
    def __init__(self, canalA, canalB, PPR):
        self.canalA = Pin(canalA, Pin.IN, Pin.PULL_UP)
        self.canalB = Pin(canalB, Pin.IN, Pin.PULL_UP)
        self.PPR = PPR

        self.estadoCanalA = self.canalA.value()
        self.estadoCanalB = self.canalB.value()

        self.estadoAnterior = (self.estadoCanalA | self.estadoCanalB << 1)
        self.pos = [0, -1, 1, 0, 1, 0, 0, -1, -1, 0, 0, 1, 0, 1, -1, 0]

        self.pulsos = 0;

        self.estadoCanalA = 0
        self.estadoCanalB = 0
        self.estadoAtual = 0
        self.estadoAnterior = 0

    def computaMudanca(self):

        self.estadoCanalA = self.canalA.value()
        self.estadoCanalB = self.canalB.value()

        self.estadoAtual = (self.estadoCanalA | self.estadoCanalB << 1)

        if (self.estadoAtual != self.estadoAnterior):
            self.pulsos += self.pos[self.estadoAtual | (self.estadoAnterior << 2)]
            self.estadoAnterior = self.estadoAtual
        else:
            self.pulsos = 0

        return self.pulsos

#==============================================#
#============= Programa Principal =============#
#==============================================#

#-- Instancia os objetos utilizados no anemômetro
encoder    = Encoder(19, 21, 20)
anemometro = Anemometro(40);

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

while True:

    #-- Obtém a todo momento as variações do encoder
    pulsosAtual += encoder.computaMudanca()

    #-- Inicializa o temporizador para cálculo de velocidade
    tempoAtual = time.time()

    #-- Verifica se houve variação do encoder no intervalo
    if (pulsosAtual != pulsosAnterior):

        #-- Só atualiza as informações a cada segundo
        if ((tempoAnterior + 1) < tempoAtual):

            #-- Computa diferença de tempo entre os eventos
            difTempo = (tempoAtual - tempoAnterior)

            #-- O encoder gera quatro leituras para cada mudança
            difPulsos = ((pulsosAtual - pulsosAnterior) / 4)

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
            anemometro.deslocamentoCm = anemometro.deslocamento(difPulsos, anemometro.comprimentoHaste, encoder.PPR)
            anemometro.mPorSegundo    = anemometro.metroPorSegundo(difTempo, anemometro.deslocamentoCm)
            anemometro.kmPorHora      = anemometro.quilometroPorHora(difTempo, anemometro.deslocamentoCm)

            #-- Gera a saída pelo terminal para conferência
            print("Direção do vento...........:", direcaoVento)
            print("Deslocamento em pulsos.....:", difPulsos)
            print("Deslocamento em centímetros:", anemometro.deslocamentoCm)
            print("Metros por segundo.........:", anemometro.mPorSegundo)
            print("KM por hora................:", anemometro.kmPorHora)
            print("_________________________________________")

##======= FIM DO PROGRAMA PRINCIPAL ==========##