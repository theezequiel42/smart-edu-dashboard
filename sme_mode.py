import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from docx import Document
import io
import os
import openpyxl

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

def run_sme_mode():
    st.title("📊 Painel Interativo de Avaliação de Cursos (Modo SME)")

    # Estilização
    st.markdown("""
        <style>
            .main { background-color: #f0f2f6; }
            h1 { color: #2c3e50; text-align: center; }
        </style>
    """, unsafe_allow_html=True)

    # Cores fixas para respostas
    cores_fixas = {
        "Concordo plenamente": "#2E7D32",
        "Concordo": "#66BB6A",
        "Não sei": "#FFEB3B",
        "Discordo": "#FF7043",
        "Discordo plenamente": "#D32F2F",
        "Muito Satisfeito(a)": "#2E7D32",
        "Satisfeito(a)": "#66BB6A",
        "Regular": "#FFEB3B",
        "Insatisfeito(a)": "#FF7043",
    }

    # Upload do arquivo
    uploaded_file = st.file_uploader("📂 Envie a planilha de respostas", type=["xlsx"])

    if uploaded_file:
        df = pd.read_excel(uploaded_file, sheet_name=None)
        sheet_name = list(df.keys())[0]
        df = df[sheet_name]

        # Padronizar colunas
        df.columns = df.columns.str.strip().str.lower()

        # Converter datas para string
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].astype(str)

        # Renomear colunas para facilitar
        df.rename(columns={
            'selecione o curso': 'curso',
            'satisfação geral: como você avalia sua satisfação geral com o curso?': 'satisfação geral'
        }, inplace=True, errors='ignore')

        # Filtros na barra lateral
        st.sidebar.header("🎓 Filtros")
        cursos = df['curso'].unique()
        curso_selecionado = st.sidebar.selectbox("📌 Selecione o Curso", ["Todos"] + list(cursos))

        if st.sidebar.button("🔄 Recarregar Dados"):
            st.rerun()

        st.sidebar.header("📊 Estatísticas Gerais")
        numeric_columns = df.select_dtypes(include=['number'])
        if not numeric_columns.empty:
            st.sidebar.write(f"📊 Total de respostas: {len(df)}")
        else:
            st.sidebar.write("Nenhuma coluna numérica encontrada.")

        perguntas = [col for col in df.columns if col not in ['curso']]
        perguntas_selecionadas = st.sidebar.multiselect("📋 Selecione as perguntas", perguntas, default=perguntas if perguntas else [])

        tipo_grafico = st.sidebar.selectbox("📈 Escolha o gráfico", ["Barras", "Pizza", "Linha"])

        doc = Document()
        doc.add_heading(f"Relatório de Avaliação - {curso_selecionado}", level=1)

        if curso_selecionado != "Todos":
            df_filtrado = df[df['curso'] == curso_selecionado]
        else:
            df_filtrado = df

        if perguntas_selecionadas:
            for coluna in perguntas_selecionadas:
                st.subheader(f"📊 {coluna}")

                largura_grafico = st.slider(f"📏 Largura ({coluna})", min_value=3, max_value=12, value=6)
                altura_grafico = st.slider(f"📐 Altura ({coluna})", min_value=2, max_value=10, value=4)

                contagem = df_filtrado[coluna].value_counts()
                paleta = {x: cores_fixas.get(x, "#999999") for x in contagem.index}

                fig, ax = plt.subplots(figsize=(largura_grafico, altura_grafico))
                if tipo_grafico == "Barras":
                    sns.barplot(x=contagem.index, y=contagem.values, hue=contagem.index, palette=paleta, legend=False, ax=ax)
                    ax.set_xticks(range(len(contagem.index)))
                    ax.set_xticklabels([quebrar_rotulo(label) for label in contagem.index], ha='center')
                    for bar in ax.patches:
                        ax.annotate(f'{bar.get_height()}', (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                                    ha='center', va='center', size=10, xytext=(0, 8), textcoords='offset points')
                    ax.set_xlabel("")
                    ax.set_ylabel("Quantidade")
                elif tipo_grafico == "Pizza":
                    ax.pie(contagem.values, labels=contagem.index, colors=[paleta[x] for x in contagem.index], autopct='%1.1f%%', startangle=140)
                elif tipo_grafico == "Linha":
                    ax.plot(contagem.index, contagem.values, marker='o', color='#1E88E5')
                st.pyplot(fig, use_container_width=True)

                # Salvar no Word diretamente via BytesIO
                img_buffer = io.BytesIO()
                fig.savefig(img_buffer, format='png', bbox_inches='tight')
                doc.add_heading(coluna, level=2)
                doc.add_paragraph("Número de respostas por opção:")
                doc.add_picture(img_buffer, width=doc.sections[0].page_width * 0.8)

        # Exportação do relatório Word
        doc_buffer = io.BytesIO()
        doc.save(doc_buffer)
        doc_buffer.seek(0)
        st.sidebar.download_button("📥 Baixar relatório", doc_buffer.getvalue(), "Relatorio.docx", "application/vnd.openxmlformats-officedocument.wordprocessingml.document")

    else:
        st.info("🔍 Envie a planilha para iniciar a análise.")
