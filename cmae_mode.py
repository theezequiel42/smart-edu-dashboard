import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
import os
import datetime
from utils import carregar_dados, calcular_status_aluno, calcular_idade
from docx import Document

carregar_dados
calcular_status_aluno
calcular_idade


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

    if st.sidebar.button("🔄 **Atualizar Dados**"):
        st.rerun()

    # Campo de entrada para pontuação esperada manual
    pontuacao_manual = st.sidebar.number_input("✍️ **Pontuação Esperada Manual**", min_value= 5.0, step=0.1)

    # 🔹 Filtrando os dados
    df_filtrado = df.copy()
    if unidade_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Unidade"] == unidade_selecionada]

    if aluno_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Aluno"] == aluno_selecionado]

        st.write(f"### 📄 Informações do Aluno: {aluno_selecionado}")
        st.write(df_filtrado)

        status_df = calcular_status_aluno(df_filtrado, categoria_selecionada, 12)
        st.write("### 📊 Status Automático do Aluno na Categoria Selecionada")
        st.write(status_df)

        contagem_respostas = {
            "Sim": sum(df_filtrado.filter(like=categoria_selecionada).apply(lambda x: (x == "Sim").sum())),
            "Não": sum(df_filtrado.filter(like=categoria_selecionada).apply(lambda x: (x == "Não").sum())),
            "Às vezes": sum(df_filtrado.filter(like=categoria_selecionada).apply(lambda x: (x == "Às vezes").sum()))
        }

        fig, ax = plt.subplots(figsize=(6, 4))
        ax.bar(contagem_respostas.keys(), contagem_respostas.values(), color=["#2E7D32", "#D32F2F", "#FFEB3B"])
        for i, v in enumerate(contagem_respostas.values()):
            ax.text(i, v + 0.5, str(v), ha="center", fontsize=10)
        st.pyplot(fig)

    doc = Document()
    doc.add_heading(f"📊 Relatório de Avaliação - {aluno_selecionado}", level=1)

     # 🔹 Cálculo automático do status do aluno selecionado
    if aluno_selecionado != "Todos":
        df_aluno = df[df["Aluno"] == aluno_selecionado]
        status_aluno = calcular_status_aluno(df_aluno, categoria_selecionada, meses_faixa_etaria=12)

        st.write(f"### 📄 Informações do Aluno: {aluno_selecionado}")
        st.write(df_aluno)

    
    # 📊 Exibir status do aluno
    status_aluno_atualizado = calcular_status_aluno(df_filtrado, categoria_selecionada, 12, pontuacao_esperada_manual=pontuacao_manual)

    if status_aluno_atualizado is None:
        st.warning("⚠️ Nenhuma informação disponível para esta categoria.")
    else:
        for _, row in status_aluno_atualizado.iterrows():
            st.write(f"📌 **{row['Aluno']}**: {row['Status']} "
                     f"(Obtido: {row['Pontuação Obtida']} / Esperado: {row['Pontuação Esperada']})")


    # 📂 Criar relatórios
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
