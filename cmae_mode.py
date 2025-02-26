import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
from docx import Document

def carregar_dados(uploaded_file):
    """ Carrega os dados do arquivo e faz ajustes necessários. """
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df.columns = df.columns.str.strip()

    # Renomear colunas para facilitar manipulação
    df.rename(columns={
        "Unidade escolar de origem do encaminhamento": "Unidade",
        "Idade da criança no dia da avaliação (em anos e meses):": "Idade",
        "Nome completo do aluno:": "Aluno"
    }, inplace=True, errors="ignore")

    # Extrair anos e meses da idade (formato esperado: 'X anos e Y meses')
    df["Ano"] = df["Idade"].str.extract(r"(\d+)").astype(float)  # Pega apenas os anos
    df["Meses"] = df["Idade"].str.extract(r"(\d+) meses").astype(float).fillna(0)  # Pega apenas os meses

    return df

def run_cmae_mode():
    """ Executa a interface do Modo CMAE no Streamlit. """
    st.title("📊 Painel Interativo de Avaliação (Modo CMAE)")
    
    uploaded_file = st.file_uploader("📂 Envie o arquivo da planilha de respostas", type=["xlsx"])
    
    if not uploaded_file:
        st.info("🔍 Por favor, envie a planilha para iniciar a análise.")
        return
    
    df = carregar_dados(uploaded_file)
    
    # 🔹 Verifica se as colunas esperadas estão presentes
    colunas_esperadas = ["Unidade", "Idade", "Aluno", "Ano", "Meses"]
    for col in colunas_esperadas:
        if col not in df.columns:
            st.error(f"🚨 A coluna '{col}' não foi encontrada no arquivo. Verifique o formato.")
            return

    # Definir idade mínima e máxima dos dados disponíveis
    idade_anos_min = int(df["Ano"].min()) if not df["Ano"].isnull().all() else 0
    idade_anos_max = int(df["Ano"].max()) if not df["Ano"].isnull().all() else 10
    idade_meses_min = int(df["Meses"].min()) if not df["Meses"].isnull().all() else 0
    idade_meses_max = int(df["Meses"].max()) if not df["Meses"].isnull().all() else 11

 # 🔹 Definir cores fixas para respostas
    cores_fixas = {
        "Sim": "#2E7D32",
        "Não": "#D32F2F",
        "Às vezes": "#FFEB3B",
        "Nunca": "#D32F2F",
        "Sempre": "#2E7D32",
        "Frequentemente": "#66BB6A",
        "Ocasionalmente": "#FFEB3B"
    }

    # 🔹 Filtros na barra lateral
    st.sidebar.header("🎯 **Filtros**")
    
    # 🏫 Filtro de Unidade Escolar com opção "Todas"
    unidades = ["Todas"] + sorted(df["Unidade"].dropna().unique().tolist())
    unidade_selecionada = st.sidebar.selectbox("🏫 **Unidade Escolar**", unidades)

    # 📅 Filtro por idade (Ano e Meses)
    st.sidebar.markdown("### 📅 **Idade Mínima**")
    idade_ano_min = st.sidebar.slider("Ano", min_value=idade_anos_min, max_value=idade_anos_max, value=idade_anos_min, step=1)
    idade_mes_min = st.sidebar.slider("Meses", min_value=0, max_value=11, value=idade_meses_min, step=1)

    st.sidebar.markdown("### 📅 **Idade Máxima**")
    idade_ano_max = st.sidebar.slider("Ano", min_value=idade_anos_min, max_value=idade_anos_max, value=idade_anos_max, step=1)
    idade_mes_max = st.sidebar.slider("Meses", min_value=0, max_value=11, value=idade_meses_max, step=1)

    # 🎯 Filtro por categoria de avaliação
    categorias = ["Socialização", "Linguagem", "Cognição", "Auto cuidado", "Desenvolvimento Motor"]
    categoria_selecionada = st.sidebar.selectbox("🧩 **Categoria**", categorias)

    # 📌 Filtro de aluno individual
    alunos_filtrados = df["Aluno"][
        (df["Ano"] > idade_ano_min) | ((df["Ano"] == idade_ano_min) & (df["Meses"] >= idade_mes_min)) &
        (df["Ano"] < idade_ano_max) | ((df["Ano"] == idade_ano_max) & (df["Meses"] <= idade_mes_max))
    ]
    aluno_selecionado = st.sidebar.selectbox("👦 **Selecionar Aluno**", ["Todos"] + sorted(alunos_filtrados.unique().tolist()))

    # 📈 Escolha do tipo de gráfico
    tipo_grafico = st.sidebar.selectbox("📊 **Tipo de Gráfico**", ["Barras", "Pizza", "Linha"])

    # 🔄 Botão para recarregar
    if st.sidebar.button("🔄 **Atualizar Dados**"):
        st.rerun()

    # 📂 Criar os relatórios Word e Excel
    doc = Document()
    doc.add_heading("📊 Relatório de Avaliação - CMAE", level=1)
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Avaliações")
    excel_buffer.seek(0)

    st.sidebar.markdown("### 📥 **Baixar Relatórios**")
    
    doc_buffer = io.BytesIO()
    doc.save(doc_buffer)
    doc_buffer.seek(0)
    
    st.sidebar.download_button(
        "📥 Baixar Relatório (Word)",
        data=doc_buffer.getvalue(),
        file_name="Relatorio_CMAE.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )

    st.sidebar.download_button(
        "📥 Baixar Dados Filtrados (Excel)",
        data=excel_buffer.getvalue(),
        file_name="Dados_Filtrados_CMAE.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

# 🔹 Criando gráficos
    if categoria_selecionada:
        for coluna in df.columns:
            if coluna.startswith(categoria_selecionada):
                st.subheader(f"📊 {coluna}")
                
                largura_grafico = st.slider(f"📏 **Largura do gráfico ({coluna})**", min_value=3, max_value=12, value=6)
                altura_grafico = st.slider(f"📐 **Altura do gráfico ({coluna})**", min_value=2, max_value=10, value=4)

                contagem = df[coluna].value_counts()

                fig, ax = plt.subplots(figsize=(largura_grafico, altura_grafico))

                if tipo_grafico == "Barras":
                    cores = [cores_fixas.get(opcao, "#999999") for opcao in contagem.index]
                    ax.bar(contagem.index, contagem.values, color=cores)
                    for i, v in enumerate(contagem.values):
                        ax.text(i, v + 0.5, str(v), ha="center", fontsize=10)

                elif tipo_grafico == "Pizza":
                    cores = [cores_fixas.get(opcao, "#999999") for opcao in contagem.index]
                    ax.pie(contagem.values, labels=contagem.index, colors=cores, autopct="%1.1f%%", startangle=140)

                elif tipo_grafico == "Linha":
                    ax.plot(contagem.index, contagem.values, marker="o", color="#1E88E5")

                st.pyplot(fig)

                # 📥 Download do gráfico
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format="png", bbox_inches="tight")
                img_buffer.seek(0)

                st.download_button(f"📥 Baixar gráfico - {coluna}", data=img_buffer, file_name=f"{coluna}.png", mime="image/png")

