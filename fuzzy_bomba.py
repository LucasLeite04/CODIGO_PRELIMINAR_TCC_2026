#____________________________________________________________________
#____________________________________________________________________
#
# CÓDIGO 1 - APLICAÇÃO DA LÓGICA FUZZY
# fuzzy_bomba.py
#____________________________________________________________________
#____________________________________________________________________

#____________________________________________________________________
#
# BIBLIOTECAS
#____________________________________________________________________

# numpy - UNIVERSO DE SAÍDA, OPERAÇÕES DE MÍNIMO E MÁXIMO E CENTROIDE
import numpy as np

#____________________________________________________________________
#
# BASE DE CONHECIMENTO - UNIVERSOS DE CADA VARIÁVEL DE ENTRADA E SAÍDA (GLOBAL)
#____________________________________________________________________

# VARIÁVEIS DE ENTRADA: (mínimo, máximo)
U_TEMP = (20.0, 100.0)      # °C
U_PRES = (0.0, 300.0)       # bar
U_CONT = (-4.0, 4.0)        # Δ, em classes ISO 4406

# VARIÁVEL DE SAÍDA: UNIVERSO DE 0 A 100 COM 1001 PONTOS (PASSO DE 0,1)
Y = np.linspace(0.0, 100.0, 1001)

# LIMITES FIXOS DO FABRICANTE DA BOMBA (NÃO MUDAM COM OS ENSAIOS)
LIM_TEMP = 80.0                 # °C - temperatura máxima do fluido com vedação NBR
LIM_PRES = (210.0, 250.0)       # bar - (conexão roscada, pressão contínua máxima)
LIM_CONT = (20, 18, 15)         # ISO 4406 - limpeza mínima do óleo

# REFERÊNCIAS DA BANCADA: VALORES PRELIMINARES, SUBSTITUÍDOS PELOS RESULTADOS
# DOS ENSAIOS DE REFERÊNCIA (CENÁRIO C1)
# NO DASHBOARD O USUÁRIO PODE DIGITAR OUTRAS REFERÊNCIAS;
# ESTES SÃO OS VALORES INICIAIS
T_REF = 50.0                    # °C - temperatura de regime da bancada
P_REF = 100.0                   # bar - pressão média da bancada

# FAIXAS ACEITAS PARA AS REFERÊNCIAS: (mínimo, máximo)
# A REFERÊNCIA PRECISA FICAR ABAIXO DO LIMITE DO FABRICANTE PARA O TERMO "ACEITÁVEL" EXISTIR
U_TREF = (U_TEMP[0], LIM_TEMP - 5.0)    # 20 a 75 °C
U_PREF = (10.0, LIM_PRES[0])            # 10 a 210 bar

#____________________________________________________________________
#
# BASE DE CONHECIMENTO - FAIXAS E VALORES DE CADA VARIÁVEL LINGUÍSTICA DE ENTRADA E SAÍDA
#____________________________________________________________________


# TEMPERATURA: O LADO DE BAIXO VEM DA REFERÊNCIA (T_REF) E O LADO DE CIMA DO LIMITE DO FABRICANTE (LIM_TEMP)
# t_meio É O PONTO MÉDIO ENTRE OS DOIS, ONDE O TERMO "ACEITÁVEL" É MÁXIMO
# COM T_REF = 50 E LIM_TEMP = 80 FICA (20, 20, 50, 65), (50, 65, 80) E (65, 80, 100, 100)
def termos_temperatura(t_ref):

    t_meio = (t_ref + LIM_TEMP) / 2
    return {
        "normal":    (U_TEMP[0], U_TEMP[0], t_ref, t_meio),     # trapézio (ombro à esquerda)
        "aceitável": (t_ref, t_meio, LIM_TEMP),                 # triângulo
        "alta":      (t_meio, LIM_TEMP, U_TEMP[1], U_TEMP[1]),  # trapézio (ombro à direita)
    }

TEMPERATURA = termos_temperatura(T_REF)     # termos com a referência padrão

CONTAMINACAO = {
    "limpo":       (-4, -4, -2, 0),
    "aceitável":   (-2, 0, 1),
    "contaminado": (0, 1, 4, 4),
}

# PRESSÃO: O LADO DE BAIXO VEM DA REFERÊNCIA (0,75*P_REF E 0,95*P_REF) E O LADO DE CIMA DOS LIMITES DO FABRICANTE (210 E 250 BAR)
# COM P_REF = 100 FICA (0, 0, 75, 95), (75, 95, 210, 250) E (210, 250, 300, 300)
def termos_pressao(p_ref):

    return {
        "baixa":     (U_PRES[0], U_PRES[0], 0.75 * p_ref, 0.95 * p_ref),
        "aceitável": (0.75 * p_ref, 0.95 * p_ref, LIM_PRES[0], LIM_PRES[1]),
        "alta":      (LIM_PRES[0], LIM_PRES[1], U_PRES[1], U_PRES[1]),
    }

PRESSAO = termos_pressao(P_REF)             # termos com a referência padrão

SAIDA = {
    "baixa": (0, 0, 25, 50),
    "média": (25, 50, 75),
    "alta":  (50, 75, 100, 100),
}

# LIMITES DAS FAIXAS DE AÇÃO (CRUZAMENTO DOS TERMOS VIZINHOS DA SAÍDA)
LIM_FAIXAS = (37.5, 62.5)

#____________________________________________________________________
#
# BASE DE REGRAS - REGRAS E AÇÕES DEFINIDAS PARA O SISTEMA
#____________________________________________________________________

REGRAS = [
    ("R1",  "normal",    "aceitável", "limpo",       "baixa", "sem sintoma"),
    ("R2",  "normal",    "baixa",     "limpo",       "média", "C4"),
    ("R3",  "normal",    "alta",      "limpo",       "alta",  "C1"),
    ("R4",  "aceitável", "aceitável", "limpo",       "baixa", "C4"),
    ("R5",  "aceitável", "baixa",     "limpo",       "alta",  "C3"),
    ("R6",  "aceitável", "alta",      "limpo",       "alta",  "C1"),
    ("R7",  "alta",      "aceitável", "limpo",       "alta",  "C1"),
    ("R8",  "alta",      "baixa",     "limpo",       "alta",  "C1"),
    ("R9",  "alta",      "alta",      "limpo",       "alta",  "C1"),
    ("R10", "normal",    "aceitável", "aceitável",   "baixa", "sem sintoma"),
    ("R11", "normal",    "baixa",     "aceitável",   "alta",  "C4 e C5"),
    ("R12", "normal",    "alta",      "aceitável",   "alta",  "C1"),
    ("R13", "aceitável", "aceitável", "aceitável",   "média", "C4 e C5"),
    ("R14", "aceitável", "baixa",     "aceitável",   "alta",  "C3"),
    ("R15", "aceitável", "alta",      "aceitável",   "alta",  "C1"),
    ("R16", "alta",      "aceitável", "aceitável",   "alta",  "C1"),
    ("R17", "alta",      "baixa",     "aceitável",   "alta",  "C1"),
    ("R18", "alta",      "alta",      "aceitável",   "alta",  "C1"),
    ("R19", "normal",    "aceitável", "contaminado", "média", "C2"),
    ("R20", "normal",    "baixa",     "contaminado", "alta",  "C2"),
    ("R21", "normal",    "alta",      "contaminado", "alta",  "C1"),
    ("R22", "aceitável", "aceitável", "contaminado", "alta",  "C2"),
    ("R23", "aceitável", "baixa",     "contaminado", "alta",  "C2 e C3"),
    ("R24", "aceitável", "alta",      "contaminado", "alta",  "C1"),
    ("R25", "alta",      "aceitável", "contaminado", "alta",  "C1"),
    ("R26", "alta",      "baixa",     "contaminado", "alta",  "C1"),
    ("R27", "alta",      "alta",      "contaminado", "alta",  "C1"),
]

ACOES = {
    "baixa": ("tolerável",   "Operação normal: manter o monitoramento."),
    "média": ("indesejável", "Programar manutenção: inspeção da bomba e da sucção, troca ou filtragem do óleo."),
    "alta":  ("crítico",     "Intervenção imediata: interromper a operação e investigar a causa."),
}

#____________________________________________________________________
#
# FUNÇÕES PARA VERIFICAR SE AS VARIÁVEIS LIDAS ESTÃO NO FORMATO CORRETO
# CADA FUNÇÃO DEVOLVE O VALOR JÁ CONVERTIDO EM NÚMERO, OU INTERROMPE COM UMA
# MENSAGEM DE ERRO (raise ValueError) QUE O DASHBOARD E O TERMINAL MOSTRAM
#____________________________________________________________________

# EXEMPLOS MOSTRADOS NAS MENSAGENS DE ERRO
EX_TEMP = "70"
EX_PRES = "100"
EX_ISO = "18/16/13"

# VERIFICAÇÃO DE UM NÚMERO (USADA PELA TEMPERATURA E PELA PRESSÃO)
def verificar_numero(valor, nome, universo, unidade, exemplo):

    texto = str(valor).strip().replace(",", ".")    # str() aceita texto ou número; aceita "70,5" e "70.5"

    if texto == "":                                 # campo vazio
        raise ValueError(f"Digite a {nome}. Exemplo: {exemplo} {unidade}.")

    try:
        numero = float(texto)                       # tenta converter o texto em número
    except ValueError:                              # não deu: tem letra ou símbolo
        raise ValueError(f"A {nome} deve ser um número. Exemplo: {exemplo} {unidade}.")

    minimo, maximo = universo
    if not (minimo <= numero <= maximo):            # fora do universo da variável
        raise ValueError(f"A {nome} deve estar entre {minimo:g} e {maximo:g} {unidade}. "
                         f"Valor digitado: {valor}.")
    return numero

# VERIFICAÇÃO DA TEMPERATURA
def verificacao_temp(valor):

    return verificar_numero(valor, "temperatura", U_TEMP, "°C", EX_TEMP)

# VERIFICAÇÃO DA PRESSÃO
def verificacao_pres(valor):

    return verificar_numero(valor, "pressão", U_PRES, "bar", EX_PRES)

# VERIFICAÇÃO DA TEMPERATURA DE REFERÊNCIA
def verificacao_tref(valor):

    return verificar_numero(valor, "temperatura de referência", U_TREF, "°C", f"{T_REF:g}")

# VERIFICAÇÃO DA PRESSÃO DE REFERÊNCIA
def verificacao_pres_ref(valor):

    return verificar_numero(valor, "pressão de referência", U_PREF, "bar", f"{P_REF:g}")

# VERIFICAÇÃO DA CONTAMINAÇÃO
def ler_codigo_iso(texto):

    partes = str(texto).replace(" ", "").split("/")   # "17/15/12" -> ["17", "15", "12"]

    if len(partes) != 3:
        raise ValueError(f"Informe os três números do código ISO 4406 separados por barra. Exemplo: {EX_ISO}.")

    numeros = []

    for parte in partes:
        if not parte.isdigit():                       # só aceita algarismos
            raise ValueError(f"O código ISO 4406 deve ter só números inteiros. Exemplo: {EX_ISO}.")
        numeros.append(int(parte))                    # int() converte texto em número inteiro

    for n in numeros:
        if n < 0 or n > 30:
            raise ValueError(f"Cada número do código ISO 4406 deve estar entre 0 e 30. Exemplo: {EX_ISO}.")

    r4, r6, r14 = numeros
    if not (r4 >= r6 >= r14):                         # partículas maiores nunca são mais numerosas que as menores
        raise ValueError("No código ISO 4406, o 1º número (≥4 µm) deve ser maior ou igual ao 2º (≥6 µm), "
                         f"e o 2º maior ou igual ao 3º (≥14 µm). Exemplo: {EX_ISO}.")
    return numeros


def delta_contaminacao(numeros):

    r4, r6, r14 = numeros
    return max(r4 - LIM_CONT[0], r6 - LIM_CONT[1], r14 - LIM_CONT[2])

# VERIFICAÇÃO DAS VARIÁVEIS E DAS REFERÊNCIAS (CHAMADA PELA FUNÇÃO PRINCIPAL)
def verificar_variavel(temperatura, pressao, codigo_iso, t_ref, p_ref):

    t = verificacao_temp(temperatura)
    p = verificacao_pres(pressao)
    codigo = ler_codigo_iso(codigo_iso)
    tr = verificacao_tref(t_ref)
    pr = verificacao_pres_ref(p_ref)
    return t, p, codigo, tr, pr

#____________________________________________________________________
#
# FUNÇÃO DE PERTINÊNCIA (TRIANGULAR E TRAPEZOIDAL)
#____________________________________________________________________

def trapezoidal(x, a, b, c, d):

    if x < a or x > d:          # fora do trapézio
        return 0.0
    if b <= x <= c:             # no topo
        return 1.0
    if x < b:                   # na subida (só chega aqui se a < b)
        return (x - a) / (b - a)
    return (d - x) / (d - c)    # na descida

def triangular(x, a, b, c):
    
    return trapezoidal(x, a, b, b, c)

def pertinencia(x, parametros):

    if len(parametros) == 3:
        return triangular(x, *parametros)
    return trapezoidal(x, *parametros)

#____________________________________________________________________
#
# FUNÇÃO DE FUZZIFICAÇÃO
#____________________________________________________________________

def limitar(x, universo):

    minimo, maximo = universo           # "desempacota" a tupla em duas variáveis
    
    return min(max(x, minimo), maximo)

def fuzzificar(x, termos, universo):

    x = limitar(x, universo)
    
    graus = {}                                  # dicionário vazio
    
    for nome, parametros in termos.items():     # percorre cada par termo -> parâmetros
        graus[nome] = pertinencia(x, parametros)
    return graus

#____________________________________________________________________
#
# FUNÇÃO DE INFERÊNCIA
#____________________________________________________________________

CURVAS_SAIDA = {}

for nome, parametros in SAIDA.items():
    CURVAS_SAIDA[nome] = np.array([pertinencia(y, parametros) for y in Y])

def inferir(graus_t, graus_p, graus_c):

    agregado = np.zeros(len(Y))     # começa com 1001 zeros
    
    ativadas = []
    
    for nome, t, p, c, saida, criterio in REGRAS:
        
        w = min(graus_t[t], graus_p[p], graus_c[c])
        
        if w > 0:                   # só as regras ativadas contribuem
            ativadas.append({"regra": nome, "temperatura": t, "pressao": p,
                             "contaminacao": c, "criticidade": saida,
                             "criterio": criterio, "w": w})
            cortada = np.minimum(w, CURVAS_SAIDA[saida])   # corta a curva em w
            agregado = np.maximum(agregado, cortada)       # une pelo máximo
    return agregado, ativadas

#____________________________________________________________________
#
# FUNÇÃO DE DEFUZZIFICAÇÃO
#____________________________________________________________________

def centroide(agregado):

    # A ÁREA NUNCA É ZERO: HÁ UMA REGRA PARA CADA COMBINAÇÃO DE TERMOS E OS
    # GRAUS DE CADA ENTRADA SOMAM 1, ENTÃO PELO MENOS UMA REGRA É ATIVADA
    area = np.sum(agregado)

    return float(np.sum(Y * agregado) / area)

#____________________________________________________________________
#
# FUNÇÃO DE CLASSIFICAÇÃO
#____________________________________________________________________

def classificar(indice):

    if indice < LIM_FAIXAS[0]:
        return "baixa"
    elif indice <= LIM_FAIXAS[1]:
        return "média"
    else:
        return "alta"

#____________________________________________________________________
#
# FUNÇÃO PRINCIPAL
#____________________________________________________________________

# t_ref=T_REF e p_ref=P_REF SÃO VALORES PADRÃO: SE QUEM CHAMAR NÃO INFORMAR AS REFERÊNCIAS, USA OS VALORES DA BASE
def avaliar(temperatura, pressao, codigo_iso, t_ref=T_REF, p_ref=P_REF):

    # Verificação: converte as entradas em número e confere se estão corretas.
    # Se algo estiver errado, o raise interrompe aqui e a mensagem vai para quem chamou avaliar()
    temperatura, pressao, codigo, t_ref, p_ref = verificar_variavel(temperatura, pressao, codigo_iso, t_ref, p_ref)

    # Contaminação: números -> Δ
    delta = delta_contaminacao(codigo)

    # Termos de temperatura e pressão montados com as referências informadas
    termos_t = termos_temperatura(t_ref)
    termos_p = termos_pressao(p_ref)

    # Etapa de fuzzificação
    graus_t = fuzzificar(temperatura, termos_t, U_TEMP)
    graus_p = fuzzificar(pressao, termos_p, U_PRES)
    graus_c = fuzzificar(delta, CONTAMINACAO, U_CONT)

    # Etapas de inferência
    agregado, ativadas = inferir(graus_t, graus_p, graus_c)

    # Etapa de defuzzificação e ação
    indice = centroide(agregado)
    termo = classificar(indice)
    categoria, acao = ACOES[termo]

    return {
        "temperatura": temperatura, "pressao": pressao, "t_ref": t_ref, "p_ref": p_ref,
        "codigo_iso": f"{codigo[0]}/{codigo[1]}/{codigo[2]}", "delta": delta,
        "termos": {"temperatura": termos_t, "pressao": termos_p, "contaminacao": CONTAMINACAO},
        "graus": {"temperatura": graus_t, "pressao": graus_p, "contaminacao": graus_c},
        "ativadas": ativadas,
        "agregado": agregado,
        "indice": indice,
        "termo": termo,
        "categoria": categoria,
        "acao": acao,
    }

#____________________________________________________________________
#
# TESTE PELO TERMINAL
#____________________________________________________________________

# Só roda quando o arquivo é executado direto (botão ▷).
# Se outro arquivo importar este, o bloco é ignorado.
if __name__ == "__main__":

    print("=" * 60)
    print("TESTE DO SISTEMA FUZZY - digite os valores e tecle Enter")
    print("(para sair sem terminar, aperte Ctrl+C)")
    print("=" * 60)

    # "while True" REPETE O BLOCO ATÉ ENCONTRAR UM "break"
    # SE ALGUM VALOR ESTIVER ERRADO, MOSTRA A MENSAGEM E PEDE OS TRÊS VALORES DE NOVO
    while True:

        try:
            # input() devolve TEXTO; a conversão em número e a verificação são feitas dentro de avaliar()
            temperatura = input("Temperatura do óleo (°C): ")
            pressao     = input("Pressão de saída (bar): ")
            codigo_iso  = input("Contaminação - código ISO 4406 (ex.: 18/16/13): ")

            r = avaliar(temperatura, pressao, codigo_iso)

        except ValueError as erro:          # valor digitado errado: volta para o início do while
            print("\nERRO:", erro)
            print("Digite os valores novamente.\n")

        else:                               # só roda se NÃO houve erro
            break                           # sai do while e segue para os resultados

    # RESULTADOS (FORA DO while: SÓ CHEGA AQUI COM VALORES CORRETOS)
    print("\n--- ENTRADAS ---")
    print(f"temperatura : {r['temperatura']} °C")
    print(f"pressao     : {r['pressao']} bar")
    print(f"t_ref       : {r['t_ref']} °C")
    print(f"p_ref       : {r['p_ref']} bar")
    print(f"codigo_iso  : {r['codigo_iso']}")
    print(f"delta       : {r['delta']} classe(s)")

    print("\n--- FUZZIFICAÇÃO (graus de pertinência) ---")
    for variavel, graus in r["graus"].items():
        texto = " | ".join(f"{termo}: {grau:.3f}" for termo, grau in graus.items())
        print(f"{variavel:13s} {texto}")

    print("\n--- INFERÊNCIA (regras ativadas) ---")
    for a in r["ativadas"]:
        print(f"{a['regra']:4s} SE T={a['temperatura']}, P={a['pressao']}, "
              f"C={a['contaminacao']} ENTÃO {a['criticidade']} "
              f"(w = {a['w']:.3f}, critério: {a['criterio']})")

    print("\n--- AGREGADO ---")
    print(f"{len(r['agregado'])} pontos | altura máxima = {r['agregado'].max():.3f}")

    print("\n--- DEFUZZIFICAÇÃO E AÇÃO ---")
    print(f"indice      : {r['indice']:.1f}")
    print(f"termo       : {r['termo']}")
    print(f"categoria   : {r['categoria']}")
    print(f"acao        : {r['acao']}")
