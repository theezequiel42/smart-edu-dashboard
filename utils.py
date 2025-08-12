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
        
        
# =========================
# ========= EDM ===========
# =========================


# Domínios EDM na escala 0–3
EDM_DOMINIOS = ["fina", "global_", "equilibrio", "esquema", "espacial", "temporal"]

def parse_anos_meses_to_dec(txt):
    """Converte 'anos.meses' -> valor decimal (anos + meses/12)."""
    if pd.isna(txt) or str(txt).strip() == "":
        return np.nan
    s = str(txt).strip().replace(",", ".")
    if "." in s:
        a, m = s.split(".", 1)
        try:
            return float(a) + float(m) / 12.0
        except ValueError:
            return np.nan
    try:
        return float(s)
    except ValueError:
        return np.nan

def dec_to_anos_meses_str(valor):
    """Converte decimal (ex.: 6.33) para 'anos.meses' (ex.: '6.4')."""
    if pd.isna(valor):
        return ""
    anos = int(valor)
    meses = round((valor - anos) * 12)
    return f"{anos}.{meses}"

def idade_cronologica_dec(nasc, data_av):
    """Calcula idade cronológica em anos decimais com base em nascimento e data da avaliação."""
    try:
        if pd.isna(nasc) or pd.isna(data_av):
            return np.nan
        y1, m1, d1 = nasc.year, nasc.month, nasc.day
        y2, m2, d2 = data_av.year, data_av.month, data_av.day
        delta_meses = (y2 - y1) * 12 + (m2 - m1) - (1 if d2 < d1 else 0)
        if delta_meses < 0:
            return np.nan
        anos = delta_meses // 12
        meses = delta_meses % 12
        return anos + meses / 12.0
    except Exception:
        return np.nan

def classificar_qdm(qdm):
    """Classificação do QDM conforme EDM de Rosa Neto."""
    if pd.isna(qdm):
        return "Sem cálculo"
    if qdm >= 130:
        return "Muito superior"
    if qdm >= 120:
        return "Superior"
    if qdm >= 110:
        return "Normal alto"
    if qdm >= 90:
        return "Normal"
    if qdm >= 80:
        return "Normal baixo"
    if qdm >= 70:
        return "Inferior"
    return "Muito inferior"

def preprocess_edm(df, colmap):
    """Limpa, normaliza e cria colunas derivadas para o modo EDM."""
    # Renomeia colunas conforme mapa
    df = df.rename(columns=colmap)

    # Datas
    for c in ["ts", "nasc", "data_avaliacao"]:
        if c in df.columns:
            df[c] = pd.to_datetime(df[c], errors="coerce", dayfirst=True)

    # Domínios 0–3
    for c in EDM_DOMINIOS:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors="coerce").clip(0, 3)

    # Idade cronológica dec
    if "idade_cron_str" in df.columns:
        df["idade_cron_dec"] = df.apply(
            lambda r: parse_anos_meses_to_dec(r.get("idade_cron_str"))
            if pd.notna(r.get("idade_cron_str")) and str(r.get("idade_cron_str")).strip() != ""
            else idade_cronologica_dec(r.get("nasc"), r.get("data_avaliacao")),
            axis=1
        )
    else:
        df["idade_cron_dec"] = df.apply(lambda r: idade_cronologica_dec(r.get("nasc"), r.get("data_avaliacao")), axis=1)

    # Idade motora dec (opcional)
    if "idade_motora_str" in df.columns:
        df["idade_mot_dec"] = df["idade_motora_str"].apply(parse_anos_meses_to_dec)
    else:
        df["idade_mot_dec"] = np.nan

    # QDM
    df["QDM"] = (df["idade_mot_dec"] / df["idade_cron_dec"] * 100).where(
        (df["idade_mot_dec"] > 0) & (df["idade_cron_dec"] > 0)
    )
    df["classe_qdm"] = df["QDM"].apply(classificar_qdm)

    # Alertas
    df["alerta_qdm"] = np.where(
        df["QDM"] < 90, "⚠️ Atraso",
        np.where(df["QDM"].isna(), "ℹ️ Sem idade motora", "OK")
    )
    # Lista domínios críticos (≤1)
    def _criticos(row):
        crit = [rotulo for rotulo, chave in [
            ("Fina", "fina"),
            ("Global", "global_"),
            ("Equilíbrio", "equilibrio"),
            ("Esquema", "esquema"),
            ("Espacial", "espacial"),
            ("Temporal", "temporal"),
        ] if pd.to_numeric(row.get(chave), errors="coerce") <= 1]
        return ", ".join(crit)

    df["alerta_dominios"] = df.apply(_criticos, axis=1)
    return df

def radar_edm_matplotlib(row, escala=4.5):
    """Retorna fig matplotlib de radar para um aluno."""
    labels = ["Fina", "Global", "Equilíbrio", "Esquema", "Espacial", "Temporal"]
    vals = [
        pd.to_numeric(row.get("fina"), errors="coerce"),
        pd.to_numeric(row.get("global_"), errors="coerce"),
        pd.to_numeric(row.get("equilibrio"), errors="coerce"),
        pd.to_numeric(row.get("esquema"), errors="coerce"),
        pd.to_numeric(row.get("espacial"), errors="coerce"),
        pd.to_numeric(row.get("temporal"), errors="coerce"),
    ]
    vals = [0 if pd.isna(v) else float(v) for v in vals]
    vals_plot = vals + [vals[0]]

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]
    fig, ax = plt.subplots(figsize=(escala, escala * 0.85), subplot_kw=dict(polar=True))
    ax.plot(angles, vals_plot, linewidth=2, linestyle='solid', marker='o')
    ax.fill(angles, vals_plot, alpha=0.25)
    ax.set_yticks([0, 1, 2, 3])
    ax.set_yticklabels(['0', '1', '2', '3'], fontsize=8)
    ax.set_ylim(0, 3)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels + [labels[0]], fontsize=9)
    ax.set_title('Radar – Domínios EDM', size=13, pad=10)
    fig.tight_layout()
    return fig