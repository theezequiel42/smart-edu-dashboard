import streamlit as st
from datetime import datetime
import pandas as pd
from cmae_mode import calcular_idade, calcular_status_aluno, gerar_pdf, gerar_word
from utils import gerar_grafico_respostas 
from perguntas_portage import PERGUNTAS_PORTAGE
import io

def run_formulario_portage():
    st.title("📝 Avaliação - Escala Portage")

    nome = st.text_input("Nome da criança")
    data_nascimento = st.date_input("Data de nascimento (ANO-MES-DIA)")
    data_avaliacao = st.date_input("Data da avaliação (ANO-MES-DIA)",)
    unidade = st.text_input("Unidade Escolar")
    professor = st.text_input("Nome do Professor")

    ano, meses, meses_totais = calcular_idade(data_nascimento, data_avaliacao)
    faixa_etaria = None

    if meses_totais < 12:
        faixa_etaria = 1
    elif meses_totais < 24:
        faixa_etaria = 2
    elif meses_totais < 36:
        faixa_etaria = 3
    elif meses_totais < 48:
        faixa_etaria = 4
    elif meses_totais < 60:
        faixa_etaria = 5
    elif meses_totais < 84:
        faixa_etaria = 6

    st.markdown(f"**Idade na data da avaliação:** {ano} ano(s) e {meses} mes(es)  ")
    st.markdown(f"**Faixa etária:** {faixa_etaria} ({meses_totais} meses)")

    categoria = st.selectbox("Selecione a categoria", list(PERGUNTAS_PORTAGE.keys()))

    perguntas = PERGUNTAS_PORTAGE.get(categoria, {}).get(faixa_etaria, [])

    if not perguntas:
        st.warning("Nenhuma pergunta disponível para esta faixa etária e categoria.")
        return

    st.subheader("Responda as perguntas:")
    respostas = {}
    for i, pergunta in enumerate(perguntas, 1):
        resposta = st.radio(f"{i:02d}. {pergunta}", ["Sim", "Às vezes", "Não"], key=f"resp_{i}")
        respostas[pergunta] = resposta

    if st.button("📊 Gerar Resultado"):
        # Criar DataFrame de respostas simulando estrutura
        colunas = {f"{categoria} {i+1:02d}": respostas[pergunta] for i, pergunta in enumerate(perguntas)}

        df_simulado = {
            "Aluno": [nome],
            "Unidade": [unidade],
            "Data_Nascimento": [data_nascimento],
            "Data_Avaliacao": [data_avaliacao],
            "Professor": [professor],
            "Ano": [ano],
            "Meses": [meses],
            "Meses_Totais": [meses_totais],
            **{col: [valor] for col, valor in colunas.items()}
        }

        df = pd.DataFrame(df_simulado)

        status_alunos = calcular_status_aluno(df, categoria, meses_faixa_etaria=12)

        if status_alunos is not None and not status_alunos.empty:
            st.success("Resultado gerado com sucesso!")
            st.dataframe(status_alunos)

            largura = st.slider("Largura do gráfico", 4, 12, 6)
            altura = st.slider("Altura do gráfico", 3, 10, 4)

            # Usando o novo gráfico de respostas
            fig, ax = gerar_grafico_respostas(df, categoria_selecionada=categoria, largura=largura, altura=altura)

            if fig:
                st.pyplot(fig)

                buffer_grafico = io.BytesIO()
                fig.savefig(buffer_grafico, format="png")
                buffer_grafico.seek(0)

                filtros = {
                    "Nome do Aluno": nome,
                    "Unidade Escolar": unidade,
                    "Data da Avaliação": data_avaliacao.strftime("%d/%m/%Y"),
                    "Data de Nascimento": data_nascimento.strftime("%d/%m/%Y"),
                    "Idade": f"{ano} anos e {meses} meses",
                    "Professor": professor
                }

                st.download_button(
                    "📥 Baixar Relatório (PDF)",
                    gerar_pdf(filtros, status_alunos, buffer_grafico),
                    file_name="relatorio_portage.pdf",
                    mime="application/pdf"
                )

                st.download_button(
                    "📥 Baixar Relatório (Word)",
                    gerar_word(filtros, status_alunos, buffer_grafico),
                    file_name="relatorio_portage.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
