import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
import io
import tempfile
import os

# Configuração da página
st.set_page_config(page_title="Análise de Cursos", layout="wide")

# Estilização da interface
st.markdown("""
    <style>
        .main {
            background-color: #f0f2f6;
        }
        h1 {
            color: #2c3e50;
            text-align: center;
        }
        .stSlider > div > div {
            background: #2980b9 !important;
        }
    </style>
""", unsafe_allow_html=True)

# Título do painel
st.title("📊 Painel Interativo de Avaliação de Cursos")

# Upload do arquivo
uploaded_file = st.file_uploader("📂 Envie o arquivo da planilha de respostas", type=["xlsx"])

if uploaded_file:
    # Carregar os dados da planilha
    df = pd.read_excel(uploaded_file, sheet_name=None)  # Carregar todas as abas
    sheet_name = list(df.keys())[0]  # Pegar a primeira aba disponível
    df = df[sheet_name]

    # Padronizar nomes das colunas
    df.columns = df.columns.str.strip()  # Remove espaços extras
    df.columns = df.columns.str.lower()  # Converte para minúsculas

    # Exibir colunas disponíveis para depuração
    st.write("Colunas disponíveis na planilha:", df.columns.tolist())

    # Renomeando colunas para facilitar
    df.rename(columns={
        'selecione o curso': 'curso',
        'satisfação geral: como você avalia sua satisfação geral com o curso?': 'satisfação geral',
        'conteúdo do curso [o curso foi relevante para suas atividades profissionais ou interesses]': 'o curso foi relevante para suas atividades profissionais ou interesses',
        'habilidade e didática do instrutor [o instrutor foi um palestrante/demonstrador eficiente]': 'o instrutor foi um palestrante/demonstrador eficiente'
    }, inplace=True, errors='ignore')

    # Barra lateral para filtros
    st.sidebar.header("🎓 Filtros")
    cursos = df['curso'].unique()
    curso_selecionado = st.sidebar.selectbox("📌 Selecione o Curso", cursos)

    # Filtrando os dados pelo curso selecionado
    df_filtrado = df[df['curso'] == curso_selecionado]

    # Exibindo os dados filtrados
    st.subheader(f"📄 Respostas para o curso: {curso_selecionado}")
    st.dataframe(df_filtrado, use_container_width=True)

    # Sliders para ajustar tamanho dos gráficos
    largura_grafico = st.sidebar.slider("📏 Ajuste a largura dos gráficos", min_value=3, max_value=12, value=6)
    altura_grafico = st.sidebar.slider("📐 Ajuste a altura dos gráficos", min_value=2, max_value=10, value=4)

    # Obter todas as perguntas específicas (excluindo colunas irrelevantes como 'curso')
    perguntas = [col for col in df_filtrado.columns if col not in ['curso']]
    perguntas_selecionadas = st.sidebar.multiselect("📋 Selecione as perguntas para visualizar", perguntas, default=perguntas if perguntas else [])

    if perguntas_selecionadas:
        # Criar um documento Word/ODT
        doc = Document()
        doc.add_heading(f"Relatório de Avaliação - {curso_selecionado}", level=1)

        for coluna in perguntas_selecionadas:
            st.subheader(f"📊 {coluna}")
            contagem = df_filtrado[coluna].value_counts()
            fig, ax = plt.subplots(figsize=(largura_grafico, altura_grafico))
            sns.barplot(x=contagem.index, y=contagem.values, hue=contagem.index, palette="coolwarm", ax=ax, legend=False)
            ax.set_ylabel("Número de Respostas")
            ax.set_xlabel("Opções")
            ax.set_title(coluna, fontsize=10, fontweight='bold')
            st.pyplot(fig, use_container_width=True)

            # Criar um arquivo temporário para a imagem
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
                tmp_file_path = tmp_file.name  # Salvar caminho do arquivo
                fig.savefig(tmp_file_path, format='png', bbox_inches='tight')

            # Adicionar gráfico ao documento
            doc.add_heading(coluna, level=2)
            doc.add_paragraph("Número de respostas para cada opção:")
            doc.add_picture(tmp_file_path, width=doc.sections[0].page_width * 0.8)
            os.remove(tmp_file_path)  # Remover arquivo temporário após uso

        # Botão para exportar Word
        doc_buffer = io.BytesIO()
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        st.download_button("📥 Baixar relatório em Word", data=doc_buffer.getvalue(), file_name=f"Relatorio_{curso_selecionado}.docx", mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
else:
    st.info("🔍 Por favor, envie a planilha para iniciar a análise.")
