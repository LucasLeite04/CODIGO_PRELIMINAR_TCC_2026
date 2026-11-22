#____________________________________________________________________
#____________________________________________________________________
#
# CÓDIGO 3 - GERA A PÁGINA WEB
# app.py
# https://criticidadebombahidraulica.streamlit.app/
#____________________________________________________________________
#____________________________________________________________________

#____________________________________________________________________
#
# BIBLIOTECAS
#____________________________________________________________________

# streamlit - TRANSFORMA ESTE ARQUIVO EM UMA PÁGINA WEB
import streamlit as st

# pandas - MONTA A TABELA DO HISTÓRICO E O ARQUIVO .csv PARA BAIXAR (JÁ VEM INSTALADO JUNTO COM O STREAMLIT)
import pandas as pd

# datetime - DATA E HORA DE CADA AVALIAÇÃO DO HISTÓRICO
from datetime import datetime, timezone, timedelta

# pyplot - SÓ PARA FECHAR AS FIGURAS DEPOIS DE MOSTRAR (LIBERA MEMÓRIA DO SERVIDOR)
import matplotlib.pyplot as plt

# SISTEMA FUZZY E GRÁFICOS
from fuzzy_bomba import (
    U_TEMP, U_PRES, U_TREF, U_PREF,
    T_REF, P_REF, LIM_TEMP, LIM_PRES, LIM_CONT,
    EX_TEMP, EX_PRES, EX_ISO, REGRAS,
    avaliar,
)
from graficos import gerar_graficos, br

#____________________________________________________________________
#
# CONFIGURAÇÃO DA PÁGINA 
#____________________________________________________________________

st.set_page_config(page_title="Criticidade da bomba", layout="wide")

#____________________________________________________________________
#
# VALORES INICIAIS E TEXTOS FIXOS
#____________________________________________________________________

# VALORES QUE JÁ APARECEM NAS CAIXAS 
TEMP_INICIAL = "50"         # °C
PRES_INICIAL = "100"        # bar
ISO_INICIAL = "18/14/12"    # código ISO 4406

# HORÁRIO DE BRASÍLIA (UTC-3) - O SERVIDOR DO STREAMLIT CLOUD FICA NOS EUA E USA OUTRO FUSO
FUSO_BR = timezone(timedelta(hours=-3))

def num(valor):

    return f"{valor:g}".replace(".", ",")      # :g tira casas desnecessárias: 57.5 -> "57,5" | 100.0 -> "100"

# FAIXAS DE VALORES ACEITAS NAS VARIÁVEIS DE ENTRADA
FAIXA_TEMP = f"{num(U_TEMP[0])} a {num(U_TEMP[1])} °C"
FAIXA_PRES = f"{num(U_PRES[0])} a {num(U_PRES[1])} bar"
FAIXA_TREF = f"{num(U_TREF[0])} a {num(U_TREF[1])} °C"
FAIXA_PREF = f"{num(U_PREF[0])} a {num(U_PREF[1])} bar"
TEXTO_LIM_CONT = f"{LIM_CONT[0]}/{LIM_CONT[1]}/{LIM_CONT[2]}"

#____________________________________________________________________
#
# MEMÓRIA DA PÁGINA (st.session_state)
# O STREAMLIT RODA O app.py INTEIRO DE NOVO A CADA CLIQUE. O QUE PRECISA SOBREVIVER
# DE UMA EXECUÇÃO PARA A OUTRA (O HISTÓRICO E O ÚLTIMO RESULTADO) FICA NO st.session_state
#____________________________________________________________________

if "historico" not in st.session_state:
    st.session_state["historico"] = []      # lista de avaliações: cada item vira uma linha da tabela

if "ultimo" not in st.session_state:
    st.session_state["ultimo"] = None       # resultado da última avaliação (None = nenhuma ainda)

#____________________________________________________________________
#
# FUNÇÕES DE APRESENTAÇÃO DOS RESULTADOS
#____________________________________________________________________

def mostrar_acao(r):

    texto = f"**Criticidade {r['termo']} ({r['categoria']})**  \n{r['acao']}"   # "  \n" quebra a linha

    if r["termo"] == "baixa":
        st.success(texto)       # caixa verde
    elif r["termo"] == "média":
        st.warning(texto)       # caixa amarela
    else:
        st.error(texto)         # caixa vermelha

def tabela_regras(ativadas):

    tabela = []                 # lista vazia: cada item vira uma linha da tabela

    for regra in ativadas:
        tabela.append({
            "Regra":        regra["regra"],
            "Temperatura":  regra["temperatura"],
            "Pressão":      regra["pressao"],
            "Contaminação": regra["contaminacao"],
            "Criticidade":  regra["criticidade"],
            "Critério":     regra["criterio"],
            "Ativação (w)": br(regra["w"]),
        })
    return tabela

def linha_historico(r):

    return {
        "Avaliação":        len(st.session_state["historico"]) + 1,
        "Horário":          datetime.now(FUSO_BR).strftime("%d/%m/%Y %H:%M:%S"),
        "Temperatura (°C)": r["temperatura"],
        "Pressão (bar)":    r["pressao"],
        "T_ref (°C)":       r["t_ref"],
        "p_ref (bar)":      r["p_ref"],
        "Código ISO 4406":  r["codigo_iso"],
        "Δ (classes)":      r["delta"],
        "Índice":           round(r["indice"], 1),
        "Criticidade":      r["termo"],
        "Ação":             r["acao"],
    }

def arquivo_historico(tabela):

    csv = tabela.copy()

    # ="18/16/13" FAZ O EXCEL TRATAR O CÓDIGO COMO TEXTO (SEM ISSO, UM CÓDIGO COMO 15/12/9 VIRA A DATA 15/12/2009)
    csv["Código ISO 4406"] = '="' + csv["Código ISO 4406"] + '"'

    # sep=";" E decimal="," É O PADRÃO DO EXCEL EM PORTUGUÊS | "utf-8-sig" FAZ O EXCEL LER OS ACENTOS E O °
    return csv.to_csv(sep=";", decimal=",", index=False).encode("utf-8-sig")

#____________________________________________________________________
#
# LATERAL - REFERÊNCIAS DA BANCADA E LIMITES DO FABRICANTE
#____________________________________________________________________

with st.sidebar:

    st.header("Configuração da bancada")

    # SEM min_value/max_value: QUEM CONFERE A FAIXA É O fuzzy_bomba.py, QUE MOSTRA A MENSAGEM DE ERRO
    t_ref = st.number_input(
        "Temperatura de referência T_ref (°C)",
        value=T_REF, step=0.5, format="%.1f",
        help=f"Temperatura de regime da bancada, obtida nos ensaios de referência (cenário C1). Faixa aceita: {FAIXA_TREF}.")

    p_ref = st.number_input(
        "Pressão de referência p_ref (bar)",
        value=P_REF, step=1.0, format="%.1f",
        help=f"Pressão média da bancada nos ensaios de referência (cenário C1). Faixa aceita: {FAIXA_PREF}.")

    st.subheader("Limites fixos do fabricante")
    st.markdown(
        f"- Temperatura máxima (vedação NBR): {num(LIM_TEMP)} °C\n"
        f"- Pressão: {num(LIM_PRES[0])} bar (conexão roscada) e {num(LIM_PRES[1])} bar (contínua máxima)\n"
        f"- Limpeza mínima do óleo: {TEXTO_LIM_CONT} (ISO 4406)")

#____________________________________________________________________
#
# CABEÇALHO
#____________________________________________________________________

st.title("Criticidade da bomba de engrenagens AZPF")
st.caption(f"Sistema fuzzy de Mamdani: 3 entradas, {len(REGRAS)} regras e defuzzificação pelo centroide.")

#____________________________________________________________________
#
# ENTRADAS - FORMULÁRIO
# st.form AGRUPA AS CAIXAS: OS VALORES SÓ SÃO ENVIADOS QUANDO O USUÁRIO CLICA NO BOTÃO
#____________________________________________________________________

with st.form("entradas"):

    col_t, col_p, col_c = st.columns(3)     # três colunas lado a lado

    # placeholder = TEXTO CINZA QUE APARECE COM A CAIXA VAZIA | help = DICA DO ÍCONE (?)
    with col_t:
        temperatura = st.text_input(
            "Temperatura do óleo (°C)",
            value=TEMP_INICIAL,
            placeholder=f"Ex.: {EX_TEMP}",
            help=f"Valores aceitos: {FAIXA_TEMP}. Pode usar vírgula, por exemplo 70,5.")

    with col_p:
        pressao = st.text_input(
            "Pressão de saída (bar)",
            value=PRES_INICIAL,
            placeholder=f"Ex.: {EX_PRES}",
            help=f"Valores aceitos: {FAIXA_PRES}. Pode usar vírgula, por exemplo 98,5.")

    with col_c:
        codigo_iso = st.text_input(
            "Contaminação: código ISO 4406",
            value=ISO_INICIAL,
            placeholder=f"Ex.: {EX_ISO}",
            help=f"Três números inteiros de 0 a 30 separados por barra, por exemplo {EX_ISO}.")

    # type="primary" DEIXA O BOTÃO NA COR PRINCIPAL DO STREAMLIT (VERMELHO)
    # clicou = True SÓ NA EXECUÇÃO LOGO DEPOIS DO CLIQUE
    clicou = st.form_submit_button("Avaliar criticidade", type="primary")

#____________________________________________________________________
#
# EXECUÇÃO - SÓ QUANDO O BOTÃO É CLICADO
#____________________________________________________________________

if clicou:

    # "try" TENTA RODAR; SE A VERIFICAÇÃO DO fuzzy_bomba.py ENCONTRAR ALGO ERRADO, O "except" MOSTRA O AVISO
    try:
        r = avaliar(temperatura, pressao, codigo_iso, t_ref, p_ref)

    except ValueError as erro:
        st.session_state["ultimo"] = None           # apaga o resultado anterior para não confundir
        st.error(f"**Valor inválido:** {erro}")     # a mensagem escrita no raise do fuzzy_bomba.py
        st.info(f"Valores aceitos: temperatura de {FAIXA_TEMP} · pressão de {FAIXA_PRES} · "
                f"código ISO com três números de 0 a 30, por exemplo {EX_ISO}.  \n"
                f"Referências (na lateral): T_ref de {FAIXA_TREF} · p_ref de {FAIXA_PREF}.")

    else:                                           # só roda se NÃO houve erro
        st.session_state["ultimo"] = r
        st.session_state["historico"].append(linha_historico(r))

#____________________________________________________________________
#
# RESULTADO - ÍNDICE, CRITICIDADE, RECOMENDAÇÃO E GRÁFICOS
# MOSTRA A ÚLTIMA AVALIAÇÃO GUARDADA (CONTINUA NA TELA MESMO QUANDO A PÁGINA RODA DE NOVO)
#____________________________________________________________________

r = st.session_state["ultimo"]

if r is None:
    if not clicou:
        st.info("Preencha os valores e clique em **Avaliar criticidade** para ver o resultado.")

else:
    figuras = gerar_graficos(r)     # dicionário: nome do arquivo -> figura (graficos.py)

    # 1. ÍNDICE, CRITICIDADE E RECOMENDAÇÃO
    st.subheader("Resultado")

    col_indice, col_acao = st.columns([1, 3])   # a coluna da direita tem o triplo da largura

    with col_indice:
        st.metric("Índice de criticidade (0 a 100)", br(r["indice"], 1))
    with col_acao:
        mostrar_acao(r)

    # 2. GRÁFICO DE SAÍDA
    st.subheader("Agregação e defuzzificação pelo centroide")
    st.pyplot(figuras["grafico_saida.png"])

    with st.expander("Ver as regras ativadas nesta avaliação"):
        st.dataframe(tabela_regras(r["ativadas"]), hide_index=True)

    # 3. GRÁFICOS DE FUZZIFICAÇÃO
    st.subheader("Fuzzificação das entradas")

    col_t, col_p, col_c = st.columns(3)

    with col_t:
        st.pyplot(figuras["grafico_temperatura.png"])
        st.caption(f"Temperatura de referência usada: {num(r['t_ref'])} °C")
    with col_p:
        st.pyplot(figuras["grafico_pressao.png"])
        st.caption(f"Pressão de referência usada: {num(r['p_ref'])} bar")
    with col_c:
        st.pyplot(figuras["grafico_contaminacao.png"])
        st.caption(f"Laudo {r['codigo_iso']}: Δ = {r['delta']} classe(s) em relação a {TEXTO_LIM_CONT}")

    # FECHA AS FIGURAS (CADA AVALIAÇÃO CRIA 4 FIGURAS NOVAS NO SERVIDOR)
    for fig in figuras.values():
        plt.close(fig)

#____________________________________________________________________
#
# HISTÓRICO - TODAS AS AVALIAÇÕES DESTA SESSÃO, COM DOWNLOAD
#____________________________________________________________________

st.subheader("Histórico das avaliações")

historico = st.session_state["historico"]

if len(historico) == 0:
    st.caption("Nenhuma avaliação feita ainda nesta sessão.")

else:
    tabela = pd.DataFrame(historico)         # lista de dicionários -> tabela
    st.dataframe(tabela, hide_index=True)

    st.download_button(
        "Baixar histórico (.csv)",
        data=arquivo_historico(tabela),
        file_name=f"historico_criticidade_{datetime.now(FUSO_BR):%Y-%m-%d_%Hh%M}.csv",
        mime="text/csv")

    st.caption("O histórico fica guardado só enquanto esta página estiver aberta. "
               "Baixe o arquivo antes de fechar ou recarregar a página.")
