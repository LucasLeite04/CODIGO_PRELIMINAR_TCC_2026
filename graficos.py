#____________________________________________________________________
#____________________________________________________________________
#
# CÓDIGO 2 - GERA OS GRÁFICOS DE FUZZIFICAÇÃO DAS ENTRADAS E DEFUZZIFICAÇÃO DA SAÍDA
# graficos.py
#____________________________________________________________________
#____________________________________________________________________

#____________________________________________________________________
#
# BIBLIOTECAS
#____________________________________________________________________

# Path - MONTA O CAMINHO DA PASTA ONDE AS IMAGENS SERÃO SALVAS
from pathlib import Path

# matplotlib - DESENHA OS GRÁFICOS ("Agg" = SALVA DIRETO EM ARQUIVO, SEM ABRIR JANELA)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter      # troca o ponto por vírgula nos eixos

# numpy - PONTOS DO EIXO X DOS GRÁFICOS DE ENTRADA
import numpy as np

# SISTEMA FUZZY - O ARQUIVO PRECISA SE CHAMAR fuzzy_bomba.py E ESTAR NA MESMA PASTA
from fuzzy_bomba import (
    U_TEMP, U_PRES, U_CONT, Y, LIM_FAIXAS,
    CURVAS_SAIDA,
    pertinencia, limitar, fuzzificar, avaliar,
)

#____________________________________________________________________
#
# CONFIGURAÇÃO DOS GRÁFICOS - CORES, ESTILOS E LIMITES (GLOBAL)
#____________________________________________________________________

# UMA COR E UM ESTILO DE LINHA PARA CADA TERMO (CONTÍNUA, TRACEJADA, TRAÇO-PONTO)
# OS ESTILOS DIFERENTES PERMITEM DISTINGUIR OS TERMOS MESMO IMPRESSO EM PRETO E BRANCO
CORES = ["#2a78d6", "#1baf7a", "#eb6834"]
ESTILOS = ["-", "--", "-."]
COR_AGREGADO = "#4a3aa7"

# QUANTIDADE DE PONTOS DO EIXO X NOS GRÁFICOS DE ENTRADA
N_PONTOS = 801

#____________________________________________________________________
#
# BASE DOS GRÁFICOS - O QUE DESENHAR PARA CADA VARIÁVEL DE ENTRADA
#____________________________________________________________________

# (CHAVE DO VALOR NO RESULTADO DE avaliar, CHAVE DOS TERMOS, UNIVERSO, NOME DO EIXO X, NOME DO ARQUIVO)
# A CONTAMINAÇÃO USA A CHAVE "delta", POIS O VALOR FUZZIFICADO É O Δ E NÃO O CÓDIGO ISO
# OS TERMOS VÊM DO RESULTADO DE avaliar (resultado["termos"]), POIS DEPENDEM DAS REFERÊNCIAS DIGITADAS
ENTRADAS = [
    ("temperatura", "temperatura",  U_TEMP, "Temperatura do óleo [°C]",          "grafico_temperatura.png"),
    ("pressao",     "pressao",      U_PRES, "Pressão de saída [bar]",            "grafico_pressao.png"),
    ("delta",       "contaminacao", U_CONT, "Contaminação Δ [classes ISO 4406]", "grafico_contaminacao.png"),
]

ARQUIVO_SAIDA = "grafico_saida.png"

#____________________________________________________________________
#
# FUNÇÕES DE FORMATAÇÃO - VÍRGULA DECIMAL
#____________________________________________________________________

def br(valor, casas=2):

    return f"{valor:.{casas}f}".replace(".", ",")     # br(0.6667) -> "0,67"

def eixo_y_com_virgula(ax):

    # "lambda v, pos: ..." é uma função de uma linha: recebe o valor v de cada marca do eixo
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: br(v, 1)))

#____________________________________________________________________
#
# FUNÇÃO DO GRÁFICO DE ENTRADA (FUNÇÕES DE PERTINÊNCIA + VALOR MEDIDO)
#____________________________________________________________________

def grafico_entrada(valor, termos, universo, nome_eixo):

    x = np.linspace(universo[0], universo[1], N_PONTOS)

    valor_limitado = limitar(valor, universo)       
    graus = fuzzificar(valor, termos, universo)     

    fig, ax = plt.subplots(figsize=(6, 3.4), dpi=150)    # (largura, altura) em polegadas

    # UMA CURVA POR TERMO - enumerate() devolve a posição (i) junto com o item
    for i, (nome, parametros) in enumerate(termos.items()):
        y = [pertinencia(ponto, parametros) for ponto in x]
        ax.plot(x, y, color=CORES[i], linestyle=ESTILOS[i], linewidth=2,
                label=f"{nome} ({br(graus[nome])})")
        if graus[nome] > 0:                          # marca onde a leitura corta a curva
            ax.plot(valor_limitado, graus[nome], "o", color=CORES[i], markersize=6)

    # LINHA VERTICAL NO VALOR MEDIDO
    ax.axvline(valor_limitado, color="black", linewidth=1.2)

    # ACABAMENTO
    ax.set_xlim(universo[0], universo[1])
    ax.set_ylim(0, 1.1)
    ax.set_xlabel(nome_eixo)
    ax.set_ylabel("Grau de pertinência μ")
    eixo_y_com_virgula(ax)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=3, frameon=False)
    fig.tight_layout()                               # ajusta as margens
    return fig

#____________________________________________________________________
#
# FUNÇÃO DO GRÁFICO DE SAÍDA (CONJUNTO AGREGADO + CENTROIDE)
#____________________________________________________________________

def grafico_saida(resultado):

    agregado = resultado["agregado"]
    indice = resultado["indice"]

    fig, ax = plt.subplots(figsize=(7, 3.4), dpi=150)

    # TERMOS DE SAÍDA EM LINHA FINA 
    for i, (nome, curva) in enumerate(CURVAS_SAIDA.items()):
        ax.plot(Y, curva, color=CORES[i], linestyle=ESTILOS[i], linewidth=1, alpha=0.6, label=nome)

    # CONJUNTO AGREGADO - A ÁREA PINTADA É O RESULTADO DA INFERÊNCIA
    ax.fill_between(Y, agregado, color=COR_AGREGADO, alpha=0.25)
    ax.plot(Y, agregado, color=COR_AGREGADO, linewidth=2, label="conjunto agregado")

    # CENTROIDE - O "CENTRO DE GRAVIDADE" DA ÁREA, QUE É O ÍNDICE FINAL
    # SE O CENTROIDE ESTIVER PERTO DA BORDA DIREITA, O TEXTO VAI PARA A ESQUERDA DA LINHA (NÃO SAI DO GRÁFICO)
    ax.axvline(indice, color="black", linewidth=1.5)
    if indice <= 75:
        ax.text(indice + 1.5, 1.03, f"centroide = {br(indice, 1)}", fontsize=9, ha="left")
    else:
        ax.text(indice - 1.5, 1.03, f"centroide = {br(indice, 1)}", fontsize=9, ha="right")

    # LIMITES DAS FAIXAS DE AÇÃO EM PONTILHADO
    for limite in LIM_FAIXAS:
        ax.axvline(limite, color="gray", linewidth=0.8, linestyle=":")

    # ACABAMENTO
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 1.15)
    ax.set_xlabel("Índice de criticidade")
    ax.set_ylabel("Grau de pertinência μ")
    eixo_y_com_virgula(ax)
    ax.grid(alpha=0.3)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=4, frameon=False)
    fig.tight_layout()
    return fig

#____________________________________________________________________
#
# FUNÇÃO PARA GERAR E SALVAR TODOS OS GRÁFICOS
#____________________________________________________________________

def gerar_graficos(resultado):

    figuras = {}                                     # dicionário: nome do arquivo -> figura

    for chave, chave_termos, universo, nome_eixo, arquivo in ENTRADAS:
        termos = resultado["termos"][chave_termos]
        figuras[arquivo] = grafico_entrada(resultado[chave], termos, universo, nome_eixo)

    figuras[ARQUIVO_SAIDA] = grafico_saida(resultado)
    return figuras

def salvar_graficos(figuras, pasta):

    for arquivo, fig in figuras.items():
        caminho = pasta / arquivo                    # a barra junta pasta e nome do arquivo
        fig.savefig(caminho)
        plt.close(fig)                               # libera a memória da figura
        print("Salvo:", caminho)

#____________________________________________________________________
#
# FUNÇÃO PRINCIPAL
#____________________________________________________________________

if __name__ == "__main__":

    pasta = Path(__file__).parent                    # pasta onde este arquivo está

    r = avaliar(temperatura=70.0, pressao=100.0, codigo_iso="17/15/12")

    figuras = gerar_graficos(r)
    salvar_graficos(figuras, pasta)

    print()
    print(f"Índice de criticidade: {br(r['indice'], 1)} -> {r['categoria']}")
    print(f"Ação: {r['acao']}")