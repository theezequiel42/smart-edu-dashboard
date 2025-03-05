import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from utils import carregar_dados, calcular_idade
from docx import Document

# 🔹 Cores fixas para os status
CORES_FIXAS_STATUS = {
    "Sem atraso ✅": "#2E7D32",  
    "Alerta para atraso ⚠️": "#FFC107",  
    "Possível Déficit 🚨": "#D32F2F"
}

# 🔹 Lista de categorias conhecidas
CATEGORIAS_VALIDAS = ["Socialização", "Linguagem", "Cognição", "Auto cuidado", "Desenvolvimento Motor"]

def calcular_status_aluno(df, categoria, meses_faixa_etaria, pontuacao_esperada_manual=None):
    """Calcula o status do aluno para uma ou várias categorias."""
    
    # 🔹 Garante que 'categoria' seja sempre uma lista
    categorias = CATEGORIAS_VALIDAS if categoria == "Todas" else [categoria]
    
    df_resultado = []

    for _, row in df.iterrows():
        for categoria in categorias:
            colunas_categoria = [col for col in df.columns if col.startswith(categoria)]
            total_perguntas = len(colunas_categoria)

            if total_perguntas == 0:
                continue  

            pontos_obtidos = sum([
                1 if row[col] == "Sim" else 0.5 if row[col] == "Às vezes" else 0
                for col in colunas_categoria
            ])

            idade_meses = row["Meses"]
            if pd.isna(idade_meses):
                idade_meses = 0  

            if pd.isna(meses_faixa_etaria) or meses_faixa_etaria == 0:
                pontuacao_esperada = 0  
            else:
                pontuacao_esperada = (idade_meses * total_perguntas) / meses_faixa_etaria

            if pontuacao_esperada_manual is not None:
                pontuacao_esperada = pontuacao_esperada_manual

            if pontos_obtidos >= pontuacao_esperada:
                status = "Sem atraso ✅"
            elif pontos_obtidos >= (pontuacao_esperada - 2):
                status = "Alerta para atraso ⚠️"
            else:
                status = "Possível Déficit 🚨"

            df_resultado.append({
                "Aluno": row["Aluno"],
                "Categoria": categoria,
                "Pontuação Obtida": pontos_obtidos,
                "Pontuação Esperada": round(pontuacao_esperada, 2),
                "Status": status
            })

    df_resultado = pd.DataFrame(df_resultado)
    return df_resultado if not df_resultado.empty else None


def run_cmae_mode():
    """ Executa a interface do Modo CMAE no Streamlit. """
    st.title("📊 Painel Interativo de Avaliação (Modo CMAE)")
    
    uploaded_file = st.file_uploader("📂 Envie o arquivo da planilha de respostas", type=["xlsx"])
    
    if not uploaded_file:
        st.info("🔍 Por favor, envie a planilha para iniciar a análise.")
        return
    
    df = carregar_dados(uploaded_file)

    if "Unidade" not in df.columns or "Aluno" not in df.columns or "Meses_Totais" not in df.columns:
        st.error("🚨 Arquivo com colunas inesperadas. Verifique o formato.")
        return
    
    df["Unidade"] = df["Unidade"].astype(str).str.strip()
    
    st.sidebar.header("🎯 **Filtros**")
    
    unidades = ["Todas"] + sorted(df["Unidade"].dropna().unique().tolist())
    unidade_selecionada = st.sidebar.selectbox("🏫 **Unidade Escolar**", unidades).strip()

    df_filtrado = df.copy()
    if unidade_selecionada != "Todas":
        df_filtrado = df_filtrado[df_filtrado["Unidade"] == unidade_selecionada]

    if df_filtrado.empty:
        st.warning("⚠️ Nenhum dado encontrado para os filtros selecionados.")
        return

    categorias = ["Todas"] + CATEGORIAS_VALIDAS
    categoria_selecionada = st.sidebar.selectbox("🧩 **Categoria**", categorias)

    aluno_lista = df_filtrado["Aluno"].dropna().unique().tolist()
    aluno_lista.insert(0, "Todos")  
    aluno_selecionado = st.sidebar.selectbox("👦 **Pesquise um aluno**", aluno_lista)

    if st.sidebar.button("🔄 **Atualizar Dados**"):
        st.rerun()

    if aluno_selecionado != "Todos":
        df_filtrado = df_filtrado[df_filtrado["Aluno"] == aluno_selecionado]

    status_alunos = calcular_status_aluno(df_filtrado, categoria_selecionada, 12)

    if not status_alunos.empty:
        st.write(f"### 📊 Estatísticas para {aluno_selecionado if aluno_selecionado != 'Todos' else 'Todos os alunos'} na Categoria: {categoria_selecionada}")
        st.dataframe(status_alunos)
    else:
        st.warning("⚠️ Nenhuma informação disponível para esta categoria.")

    # 🔹 Configuração dos gráficos
    st.sidebar.header("📊 **Configuração dos Gráficos**")
    tipo_grafico = st.sidebar.selectbox("📊 **Escolha o tipo de gráfico**", ["Barras", "Pizza", "Linha"])
    largura = st.sidebar.slider("📏 **Largura do Gráfico**", min_value=4, max_value=12, value=6, step=1)
    altura = st.sidebar.slider("📐 **Altura do Gráfico**", min_value=3, max_value=10, value=4, step=1)

    # 🔹 Exibição do gráfico de distribuição de status dos alunos
    if not status_alunos.empty:
        st.subheader("📊 Distribuição de Status dos Alunos")
        status_counts = status_alunos["Status"].value_counts()

        fig, ax = plt.subplots(figsize=(largura, altura))

        cores = [CORES_FIXAS_STATUS.get(status, "#000000") for status in status_counts.index]

        if tipo_grafico == "Barras":
            ax.bar(status_counts.index, status_counts.values, color=cores)
            ax.set_ylabel("Quantidade de Alunos")

        elif tipo_grafico == "Pizza":
            ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=cores)
            ax.axis("equal")

        elif tipo_grafico == "Linha":
            ax.plot(status_counts.index, status_counts.values, marker='o', linestyle='-', color=cores[0])
            ax.set_ylabel("Quantidade de Alunos")

        plt.xticks(rotation=30, ha="right")
        st.pyplot(fig)

        buffer = io.BytesIO()
        fig.savefig(buffer, format="png")
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar Gráfico de Status",
            data=buffer,
            file_name="grafico_status_alunos.png",
            mime="image/png"
        )

    else:
        st.warning("⚠️ Nenhum dado de status disponível.")
