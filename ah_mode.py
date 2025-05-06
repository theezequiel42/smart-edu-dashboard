import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import unicodedata
from blocos_ahsd import blocos

def run_ah_mode():
    st.title("📊 Análise de Questionários - Altas Habilidades/Superdotação")

    arquivo = st.file_uploader("📂 Envie o arquivo de respostas (.csv)", type=["csv"])

    mapa_respostas = {
        "Nunca": 0, "Raramente": 1, "As vezes": 2, "Frequentemente": 3, "Sempre": 4
    }
    mapa_diagnostico = {
        "Sim": 4, "Não": 0, "Altas": 4, "Alta": 4, "Média": 2, "Medias": 2, "Médias": 2,
        "Baixa": 0, "Baixas": 0
    }

    # Função para normalizar acentuação
    def normalizar_respostas(respostas):
        return respostas.astype(str).str.strip().apply(
            lambda x: unicodedata.normalize("NFKD", x).encode("ASCII", "ignore").decode("utf-8")
        )

    if arquivo is not None:
        df = pd.read_csv(arquivo, encoding="utf-8")
        col_nome = [col for col in df.columns if "nome do(a) aluno(a)" in col.lower()][0]

        st.success("✅ Arquivo carregado com sucesso!")
        aluno = st.selectbox("👤 Selecione um aluno", df[col_nome].unique())
        df_aluno = df[df[col_nome] == aluno]

        medias_blocos = []

        for bloco, perguntas in blocos.items():
            st.subheader(f"📚 Bloco: {bloco}")
            perguntas_existentes = [p for p in perguntas if p in df.columns]
            if not perguntas_existentes:
                st.warning("⚠️ Nenhuma pergunta deste bloco foi encontrada.")
                continue

            respostas = df_aluno[perguntas_existentes].iloc[0]

            if bloco == "Descritivo":
                respostas_numericas = normalizar_respostas(respostas).map(mapa_diagnostico)
                for pergunta in perguntas_existentes:
                    original = df_aluno[pergunta].values[0]
                    st.markdown(f"**{pergunta}** → _{original}_")
            else:
                respostas_numericas = normalizar_respostas(respostas).map(mapa_respostas)
                media = pd.to_numeric(respostas_numericas, errors="coerce").mean()
                if pd.notna(media):
                    medias_blocos.append(media)
                    st.markdown(f"**Pontuação média:** `{media:.2f} / 4.00`")
                    st.progress(media / 4)
                else:
                    st.warning("⚠️ Não foi possível calcular a média (valores ausentes ou inválidos).")

        # Avaliação geral
        st.subheader("🧠 Avaliação Geral – Probabilidade de Altas Habilidades/Superdotação")
        if medias_blocos:
            media_geral = sum(medias_blocos) / len(medias_blocos)
            percentual = (media_geral / 4) * 100
            st.metric("Probabilidade estimada", f"{percentual:.1f}%")
            st.progress(percentual / 100)
        else:
            st.warning("⚠️ Não foi possível calcular a média geral – dados insuficientes.")

        # 📊 Gráfico radar
        st.subheader("📊 Radar das Pontuações por Bloco")
        escala = st.slider("📐 Escala visual do gráfico (quanto menor, mais compacto)", 3, 8, 5)

        labels = [bloco for bloco in blocos if bloco != "Descritivo"]
        valores = []

        for bloco in labels:
            perguntas_existentes = [p for p in blocos[bloco] if p in df.columns]
            respostas = df_aluno[perguntas_existentes].iloc[0]
            respostas_numericas = normalizar_respostas(respostas).map(mapa_respostas)
            media = pd.to_numeric(respostas_numericas, errors="coerce").mean()
            valores.append(media if pd.notna(media) else 0)

        labels_plot = labels + [labels[0]]
        valores_plot = valores + [valores[0]]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

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
            ax.set_title(f'Radar das Pontuações – {aluno}', size=13, pad=10)
            st.pyplot(fig)

            buf = io.BytesIO()
            fig.savefig(buf, format="png", bbox_inches="tight")
            buf.seek(0)

            nome_limpo = aluno.replace(" ", "_").lower()
            nome_arquivo = f"grafico_radar_{nome_limpo}.png"
            st.download_button(
                label="📥 Baixar gráfico como imagem (PNG)",
                data=buf,
                file_name=nome_arquivo,
                mime="image/png"
            )

    else:
        st.info("Envie um arquivo .csv com as respostas estruturadas conforme o modelo.")
