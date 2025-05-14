import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import unicodedata

CATEGORIAS_VALIDAS = ["Socialização", "Linguagem", "Cognição", "Auto cuidado", "Desenvolvimento Motor"]

def gerar_grafico_respostas(df, categoria_selecionada="Todas", largura=6, altura=4):
    fig, ax = plt.subplots(figsize=(largura, altura))

    categorias = CATEGORIAS_VALIDAS if categoria_selecionada == "Todas" else [categoria_selecionada]
    contagem_respostas = {"Sim": 0, "Às vezes": 0, "Não": 0}

    for categoria in categorias:
        colunas_categoria = [col for col in df.columns if col.startswith(categoria)]
        for col in colunas_categoria:
            respostas = df[col].dropna().astype(str).str.strip()
            contagem_respostas["Sim"] += (respostas == "Sim").sum()
            contagem_respostas["Às vezes"] += (respostas == "Às vezes").sum()
            contagem_respostas["Não"] += (respostas == "Não").sum()

    cores = ["#2E7D32", "#FFC107", "#D32F2F"]
    ax.bar(contagem_respostas.keys(), contagem_respostas.values(), color=cores)
    ax.set_title(f"Contagem de Respostas - {categoria_selecionada}")
    ax.set_ylabel("Quantidade")
    return fig, ax


def quebrar_rotulo(texto, limite=15):
    """ Quebra rótulos longos sem dividir palavras no meio. """
    palavras = texto.split()
    resultado = []
    linha_atual = ""
    
    for palavra in palavras:
        if len(linha_atual) + len(palavra) + 1 <= limite:
            linha_atual += " " + palavra if linha_atual else palavra
        else:
            resultado.append(linha_atual)
            linha_atual = palavra
    resultado.append(linha_atual)
    
    return "\n".join(resultado)

def analisar_todos_os_alunos():
    st.subheader("📊 Análise Geral de Todos os Alunos")
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()

    c.execute("SELECT aluno, bloco, resposta FROM respostas")
    dados = c.fetchall()
    conn.close()

    if not dados:
        st.info("Ainda não há respostas registradas.")
        return

    df = pd.DataFrame(dados, columns=["Aluno", "Bloco", "Resposta"])
    
    # Remove o bloco "Descritivo" da análise
    df = df[df["Bloco"] != "Descritivo"]


    mapa_respostas = {"Nunca": 0, "Raramente": 1, "Às vezes": 2, "As vezes": 2, "Frequentemente": 3, "Sempre": 4}
    mapa_diagnostico = {"Sim": 4, "Não": 0, "Altas": 4, "Alta": 4, "Média": 2, "Medias": 2, "Médias": 2, "Baixa": 0, "Baixas": 0}

    df["RespostaNum"] = df["Resposta"].apply(lambda x: unicodedata.normalize("NFKD", str(x).strip()).encode("ASCII", "ignore").decode("utf-8"))
    df["RespostaNum"] = df["RespostaNum"].map(mapa_respostas).fillna(df["RespostaNum"].map(mapa_diagnostico))
    df["RespostaNum"] = pd.to_numeric(df["RespostaNum"], errors="coerce")

    # Média por bloco (geral)
    st.subheader("📚 Média Geral por Bloco")
    media_blocos = df.groupby("Bloco")["RespostaNum"].mean().round(2)
    st.bar_chart(media_blocos)

    # Média geral por aluno
    st.subheader("🏅 Ranking de Alunos por Média Geral")
    ranking = df.groupby("Aluno")["RespostaNum"].mean().sort_values(ascending=False).round(2)
    st.dataframe(ranking.reset_index().rename(columns={"RespostaNum": "Média Geral"}), use_container_width=True)

    # Radar da média por bloco (todos os alunos)
    st.subheader("📈 Radar da Média Geral por Bloco")
    if len(media_blocos) > 1:
        labels = list(media_blocos.index)
        valores = list(media_blocos.values)
        labels_plot = labels + [labels[0]]
        valores_plot = valores + [valores[0]]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        escala = st.slider("📐 Escala visual do gráfico", 3, 8, 5)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            fig, ax = plt.subplots(figsize=(escala, escala * 0.8), subplot_kw=dict(polar=True))
            ax.plot(angles, valores_plot, linewidth=2, linestyle='solid', marker='o')
            ax.fill(angles, valores_plot, alpha=0.25)
            ax.set_yticks([0, 1, 2, 3, 4])
            ax.set_yticklabels(['0', '1', '2', '3', '4'], fontsize=8)
            ax.set_ylim(0, 4)
            ax.set_xticks(angles)
            ax.set_xticklabels(labels_plot, fontsize=9)
            ax.set_title('Radar – Média Geral por Bloco', size=13, pad=10)
            st.pyplot(fig)
    else:
        st.info("Não há dados suficientes para exibir o gráfico radar.")
