import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

def carregar_dados(uploaded_file):
    """Carrega os dados do arquivo e calcula a idade do aluno na data da avaliação."""
    df = pd.read_excel(uploaded_file, engine="openpyxl")
    df.columns = df.columns.str.strip()

    df.rename(columns={
        "Unidade escolar de origem do encaminhamento": "Unidade",
        "Nome completo do aluno:": "Aluno",
        "Data da avaliação:": "Data_Avaliacao",
        "Data de Nascimento:": "Data_Nascimento"
    }, inplace=True, errors="ignore")

    df["Data_Nascimento"] = pd.to_datetime(df["Data_Nascimento"], errors="coerce")
    df["Data_Avaliacao"] = pd.to_datetime(df["Data_Avaliacao"], errors="coerce")

    df["Ano"], df["Meses"], df["Meses_Totais"] = zip(*df.apply(
        lambda row: calcular_idade(row["Data_Nascimento"], row["Data_Avaliacao"]), axis=1))

    return df

def calcular_idade(data_nascimento, data_avaliacao):
    """Calcula a idade do aluno na data da avaliação, em anos e meses, considerando arredondamento de até 2 dias."""
    if pd.isnull(data_nascimento) or pd.isnull(data_avaliacao):
        return None, None, None

    data_nascimento = pd.to_datetime(data_nascimento, errors="coerce")
    data_avaliacao = pd.to_datetime(data_avaliacao, errors="coerce")

    if pd.isnull(data_nascimento) or pd.isnull(data_avaliacao):
        return None, None, None

    # Calculando a idade exata
    idade_anos = data_avaliacao.year - data_nascimento.year
    idade_meses = data_avaliacao.month - data_nascimento.month

    if data_avaliacao.day < data_nascimento.day:
        idade_meses -= 1

    if idade_meses < 0:
        idade_anos -= 1
        idade_meses += 12

    # Calcula idade total em meses
    meses_totais = (idade_anos * 12) + idade_meses

    # Ajuste de arredondamento de até 2 dias
    diferenca_dias = (data_avaliacao - data_nascimento).days
    if 0 < diferenca_dias % 30 <= 2:
        meses_totais += 1
        idade_meses += 1

    return idade_anos, idade_meses, meses_totais

CORES_FIXAS_STATUS = {
    "Sem atraso ✅": "#2E7D32",
    "Alerta para atraso ⚠️": "#FFC107",
    "Possível Déficit 🚨": "#D32F2F"
}

CATEGORIAS_VALIDAS = ["Socialização", "Linguagem", "Cognição", "Auto cuidado", "Desenvolvimento Motor"]

def calcular_status_aluno(df, categoria, meses_faixa_etaria, pontuacao_esperada_manual=None):
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

def gerar_pdf(filtros, status_alunos, img_grafico):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=40, rightMargin=40, topMargin=40, bottomMargin=40)
    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("Centro Municipal de Atendimento Especializado – CMAE", styles["Title"]))
    elements.append(Spacer(1, 12))

    for chave, valor in filtros.items():
        elements.append(Paragraph(f"<b>{chave}:</b> {valor}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    for chave, valor in filtros.items():
        elements.append(Paragraph(f"<b>{chave}:</b> {valor}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    if not status_alunos.empty:
        elements.append(Paragraph("📊 Estatística(s) do(s) Aluno(s) - INVENTÁRIO PORTAGE", styles["Heading2"]))
        
        alunos_unicos = status_alunos["Aluno"].unique()
        for aluno in alunos_unicos:
            elements.append(Spacer(1, 6))
            elements.append(Paragraph(f"<b>Aluno:</b> {aluno}", styles["Normal"]))
            elements.append(Spacer(1, 6))

            dados_tabela = status_alunos[status_alunos["Aluno"] == aluno][["Categoria", "Pontuação Obtida", "Pontuação Esperada", "Status"]]
            tabela = Table([dados_tabela.columns.tolist()] + dados_tabela.values.tolist(), colWidths=[120, 110, 110, 120])
            tabela.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 1, colors.black),
            ]))

        
        elements.append(tabela)
        elements.append(Spacer(1, 12))

    if img_grafico:
        img_path = "grafico_temp.png"
        with open(img_path, "wb") as f:
            f.write(img_grafico.getvalue())

        elements.append(Image(img_path, width=400, height=300))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("O Inventário Portage Operacionalizado (IPO) vem sendo respondido pelos professores dos Centros de Educação Infantil, de maneira adaptada e parcial, como forma de levantar dados e acompanhar o desenvolvimento das crianças.", styles["Normal"]))
        elements.append(Paragraph("Para investigação mais aprofundada, sugere-se a aplicação do Inventário Dimensional de Avaliação do Desenvolvimento Infantil - IDADI.", styles["Normal"]))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph("____________________________", styles["Normal"]))
        elements.append(Paragraph("Vanusa Apolinário - Psicóloga CRP 12/09868", styles["Normal"])) 

    doc.build(elements)
    buffer.seek(0)
    return buffer

def run_cmae_mode():
    st.title("📊 Painel Interativo de Avaliação (Modo CMAE)")

    uploaded_file = st.file_uploader("📂 Envie a planilha de respostas", type=["xlsx"])
    
    if not uploaded_file:
        st.info("🔍 Envie a planilha para iniciar a análise.")
        return
    
    df = carregar_dados(uploaded_file)
    df["Unidade"] = df["Unidade"].astype(str).str.strip()

    st.sidebar.header("🎯 **Filtros**")
    unidades = ["Todas"] + sorted(df["Unidade"].dropna().unique().tolist())
    unidade_selecionada = st.sidebar.selectbox("🏫 **Unidade Escolar**", unidades)

    categorias = ["Todas"] + CATEGORIAS_VALIDAS
    categoria_selecionada = st.sidebar.selectbox("🧩 **Categoria**", categorias)

    aluno_lista = df["Aluno"].dropna().unique().tolist()
    aluno_lista.insert(0, "Todos")
    aluno_selecionado = st.sidebar.selectbox("👦 **Pesquise um aluno**", aluno_lista)

    tipo_grafico = st.sidebar.selectbox("📊 **Escolha o tipo de gráfico**", ["Barras", "Pizza", "Linha"])
    largura = st.sidebar.slider("📏 **Largura do Gráfico**", min_value=4, max_value=12, value=6, step=1)
    altura = st.sidebar.slider("📐 **Altura do Gráfico**", min_value=3, max_value=10, value=4, step=1)

    if st.sidebar.button("🔄 **Atualizar Dados**"):
        st.rerun()

    if unidade_selecionada != "Todas":
        df = df[df["Unidade"] == unidade_selecionada]
    if aluno_selecionado != "Todos":
        df = df[df["Aluno"] == aluno_selecionado]

    status_alunos = calcular_status_aluno(df, categoria_selecionada, 12)

    if status_alunos is not None and not status_alunos.empty:
        st.write(f"### 📊 Estatísticas para {aluno_selecionado} na Categoria: {categoria_selecionada}")
        st.dataframe(status_alunos)

        status_counts = status_alunos["Status"].value_counts()
        fig, ax = plt.subplots(figsize=(largura, altura))
        cores = [CORES_FIXAS_STATUS.get(status, "#000000") for status in status_counts.index]

        if tipo_grafico == "Barras":
            ax.bar(status_counts.index, status_counts.values, color=cores)
        elif tipo_grafico == "Pizza":
            ax.pie(status_counts.values, labels=status_counts.index, autopct='%1.1f%%', colors=cores)
            ax.axis("equal")
        elif tipo_grafico == "Linha":
            ax.plot(status_counts.index, status_counts.values, marker='o', linestyle='-')

        st.pyplot(fig)

        buffer_grafico = io.BytesIO()
        fig.savefig(buffer_grafico, format="png")
        buffer_grafico.seek(0)

        st.download_button("📥 Baixar Relatório Completo (PDF)", gerar_pdf({}, status_alunos, buffer_grafico), file_name="relatorio_CMAE.pdf", mime="application/pdf")
