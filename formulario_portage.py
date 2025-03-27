import streamlit as st
import datetime
import pandas as pd
from cmae_mode import calcular_idade, calcular_status_aluno, gerar_pdf, gerar_word, CATEGORIAS_VALIDAS
from perguntas_portage import PERGUNTAS_PORTAGE
import io


def run_formulario_portage():
    st.title("📝 Avaliação de Desenvolvimento - Formulário Interativo")

    nome = st.text_input("Nome da criança")
    data_nascimento = st.date_input("Data de nascimento da criança. (ANO-MÊS-DIA)")
    data_avaliacao = datetime.date.today()

    if not nome:
        st.warning("Por favor, preencha o nome da criança.")
        return

    # Calcular idade
    anos, meses, total_meses = calcular_idade(data_nascimento, data_avaliacao)
    st.write(f"**Idade atual:** {anos} anos e {meses} meses")

    # Determinar faixa etária
    faixa_etaria = min(total_meses // 12 + 1, 6)  # de 1 a 6
    st.write(f"**Faixa etária correspondente:** {faixa_etaria} ({(faixa_etaria-1)} a {faixa_etaria} anos)")

    categoria = st.selectbox("Selecione a categoria para avaliação", CATEGORIAS_VALIDAS)
    perguntas_categoria = PERGUNTAS_PORTAGE.get(categoria, {}).get(faixa_etaria, [])

    if not perguntas_categoria:
        st.warning("Nenhuma pergunta disponível para esta faixa etária e categoria.")
        return

    respostas = []
    st.subheader("Responda às questões:")
    for idx, pergunta in enumerate(perguntas_categoria, 1):
        resposta = st.radio(f"{idx:02d}. {pergunta}", ["Sim", "Às vezes", "Não"], key=f"resp_{idx}")
        respostas.append(resposta)

    if st.button("📊 Gerar Relatório"):
        # Montar DataFrame com os dados
        colunas = [f"{categoria} - {i+1:02d}" for i in range(len(respostas))]
        dados = {"Aluno": nome, "Data_Nascimento": data_nascimento, "Data_Avaliacao": data_avaliacao,
                 "Ano": anos, "Meses": meses, "Meses_Totais": total_meses, **dict(zip(colunas, respostas))}
        df = pd.DataFrame([dados])

        status_df = calcular_status_aluno(df, categoria, meses_faixa_etaria=12)
        if status_df is None:
            st.error("Erro ao calcular o status do aluno.")
            return

        st.subheader("📋 Resultado da Avaliação")
        st.dataframe(status_df)

        filtros = {
            "Nome do Aluno": nome,
            "Data de Nascimento": data_nascimento.strftime("%d/%m/%Y"),
            "Data da Avaliação": data_avaliacao.strftime("%d/%m/%Y"),
            "Idade": f"{anos} anos e {meses} meses",
            "Categoria Avaliada": categoria
        }

        # Gerar gráfico em branco (por ora)
        buffer_vazio = io.BytesIO()

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 Baixar Relatório em PDF",
                gerar_pdf(filtros, status_df, buffer_vazio),
                file_name=f"relatorio_{nome}_portage.pdf",
                mime="application/pdf"
            )

        with col2:
            st.download_button(
                "📥 Baixar Relatório em Word",
                gerar_word(filtros, status_df, buffer_vazio),
                file_name=f"relatorio_{nome}_portage.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
