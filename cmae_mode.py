import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import datetime
from docx import Document

def calcular_idade(data_nascimento, data_avaliacao):
    """Calcula a idade do aluno na data da avaliação."""
    if pd.isnull(data_nascimento) or pd.isnull(data_avaliacao):
        return None, None
    
    data_nascimento = pd.to_datetime(data_nascimento, errors="coerce")
    data_avaliacao = pd.to_datetime(data_avaliacao, errors="coerce")

    if pd.isnull(data_nascimento) or pd.isnull(data_avaliacao):
        return None, None

    idade_anos = data_avaliacao.year - data_nascimento.year
    idade_meses = data_avaliacao.month - data_nascimento.month

    if data_avaliacao.day < data_nascimento.day:
        idade_meses -= 1

    if idade_meses < 0:
        idade_anos -= 1
        idade_meses += 12

    return idade_anos, idade_meses

def carregar_dados(uploaded_file):
    """Carrega os dados do arquivo e calcula a idade do aluno."""
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df.columns = df.columns.str.strip()

    # Renomear colunas para facilitar manipulação
    df.rename(columns={
        "Unidade escolar de origem do encaminhamento": "Unidade",
        "Nome completo do aluno:": "Aluno",
        "Data da avaliação:": "Data_Avaliacao",
        "Data de Nascimento:": "Data_Nascimento"
    }, inplace=True, errors="ignore")

    # Converter datas para datetime
    df["Data_Nascimento"] = pd.to_datetime(df["Data_Nascimento"], errors="coerce")
    df["Data_Avaliacao"] = pd.to_datetime(df["Data_Avaliacao"], errors="coerce")

    # Calcular idade exata do aluno na data da avaliação
    df["Ano"], df["Meses"] = zip(*df.apply(lambda row: calcular_idade(row["Data_Nascimento"], row["Data_Avaliacao"]), axis=1))

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
    colunas_esperadas = ["Unidade", "Aluno", "Ano", "Meses"]
    for col in colunas_esperadas:
        if col not in df.columns:
            st.error(f"🚨 A coluna '{col}' não foi encontrada no arquivo. Verifique o formato.")
            return

    # Definir idade mínima e máxima dos dados disponíveis
    idade_anos_min = int(df["Ano"].min()) if not df["Ano"].isnull().all() else 0
    idade_anos_max = int(df["Ano"].max()) if not df["Ano"].isnull().all() else 10
    idade_meses_min = int(df["Meses"].min()) if not df["Meses"].isnull().all() else 0
    idade_meses_max = int(df["Meses"].max()) if not df["Meses"].isnull().all() else 11

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

    # 📌 Campo de pesquisa com autocomplete (Usando selectbox com opção de digitação)
    aluno_lista = df["Aluno"].dropna().unique().tolist()
    aluno_lista.insert(0, "Todos")  # Adiciona opção para exibir todos os alunos

    aluno_selecionado = st.sidebar.selectbox("👦 **Pesquise um aluno**", aluno_lista)

    # 🔄 Botão para recarregar
    if st.sidebar.button("🔄 **Atualizar Dados**"):
        st.rerun()

    # 🔹 Filtrando os dados
    df_filtrado = df[
        ((df["Ano"] > idade_ano_min) | ((df["Ano"] == idade_ano_min) & (df["Meses"] >= idade_mes_min))) &
        ((df["Ano"] < idade_ano_max) | ((df["Ano"] == idade_ano_max) & (df["Meses"] <= idade_mes_max)))
    ]
    
    if unidade_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Unidade"] == unidade_selecionada]

    if aluno_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Aluno"] == aluno_selecionado]

    if aluno_selecionado != "Todos":
        st.write(f"### 📄 Informações do Aluno: {aluno_selecionado}")
        st.write(df_filtrado)

    # 📂 Criar os relatórios Word e Excel
    doc = Document()
    doc.add_heading(f"📊 Relatório de Avaliação - {aluno_selecionado}", level=1)
    
    excel_buffer = io.BytesIO()
    with pd.ExcelWriter(excel_buffer, engine='openpyxl') as writer:
        df_filtrado.to_excel(writer, index=False, sheet_name="Avaliações")
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
    
    # 🔹 Criando gráficos com cores fixas
    cores_fixas = {
        "Sim": "#2E7D32",
        "Não": "#D32F2F",
        "Parcialmente": "#FFEB3B",
        "Não sei": "#999999"
    }

    if categoria_selecionada and not df_filtrado.empty:
        for coluna in df_filtrado.columns:
            if coluna.startswith(categoria_selecionada):
                st.subheader(f"📊 {coluna}")
                
                contagem = df_filtrado[coluna].value_counts()

                fig, ax = plt.subplots(figsize=(6, 4))

                if not contagem.empty:
                    cores = [cores_fixas.get(resp, "#1E88E5") for resp in contagem.index]
                    ax.bar(contagem.index, contagem.values, color=cores)

                    for i, v in enumerate(contagem.values):
                        ax.text(i, v + 0.5, str(v), ha="center", fontsize=10)

                    st.pyplot(fig)
