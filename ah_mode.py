import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io

def run_ah_mode():
    st.title("📊 Análise de Questionários - Altas Habilidades/Superdotação")

    arquivo = st.file_uploader("📂 Envie o arquivo de respostas (.csv)", type=["csv"])

    mapa_respostas = {"Nunca": 0, "Raramente": 1, "Às vezes": 2, "As vezes": 2, "Frequentemente": 3, "Sempre": 4}
    mapa_diagnostico = {
        "Sim": 4, "Não": 0,
        "Altas": 4, "Alta": 4,
        "Média": 2, "Médias": 2,
        "Baixa": 0, "Baixas": 0
    }

    blocos = {
        "Características Gerais": [
            "Você considera que este aluno/a tem habilidades especiais e se destaca dos demais?",
            "As notas ou conceitos deste(a) aluno(a) na sua disciplina são:",
            "As notas ou conceitos deste(a) aluno(a) na Escola são:",
            "Este(a) aluno(a) dá a parecer que está no \"mundo da lua\" nas aulas?",
            "É um(a) aluno(a) atento(a) e interessado(a) e um dos melhores da turma?",
        ],
        "Habilidade Acima da Média": [
            "Tem grande curiosidade sobre assuntos incomuns (diferentes dos que interressam aos seus colegas)?",
            "Sua memória  muito destacada, especialmente em assuntos que são de seu interesse?",
            "Tem informações sobre os temas que são de seu interesse?",
            "Normalmente aprende mais de uma história, um filme, etc. do que outras crianças de sua idade?",
            "Tenta entender coisas complicadas examinando-as parte por parte?",
            "Aprende rapidademnte coisas que lhe interressam e usa o que arendeu em outras áreas?",
            "Percebe rapidamente as relações entre as partes e o todo?",
            "Tem vocabulário muito extenso e rico para sua idade (considerando a variedade de palavras, precisão vocabular, a complexidade das palavras utilizadas e a construção dos argumentos",
            "Tenta descobrir o “como” e o “porquê” das coisas fazendo perguntas inteligentes?",
            "Suas notas ou conceitos na escola são melhores que os demais colegas da sua turma?",
            "Aprende mais rápido que seus colegas?",
            "Adapta-se facilmente a situações novas ou as modifica?"
        ],
        "Criatividade": [
            "Tem um pensamento abstrato muito desenvolvido?",
            "As ideias que propõe são vistas como diferentes ou esquisitas pelos demais?",
            "É muito curioso/a?",
            "Tem muitas ideias, soluções e respostas incomuns, diferentes e inteligentes?",
            "Gosta de arriscar para conseguir algo que quer?",
            "Gosta de enfrentar desafios?",
            "É muito imaginativo/a e inventivo/a?",
            "É sensível às coisas bonitas?",
            "É inconformista e não se importa em ser diferente?",
            "Sabe compreender ideias diferentes das suas?",
            "Fica chateado/a quando tem que repetir um exercício de algo que já sabe?",
            "Descobre novos e diferentes caminhos para solucionar problemas?",
            "É questionador/a quando algum adulto fala algo com o qual não concorda?",
            "Presta atenção, apenas quando o assunto lhe interessa?",
            "Seus cadernos são incompletos e desorganizados?",
            "Não gosta de cumprir regras?"
        ],
        "Comprometimento com a Tarefa": [
            "Dedica muito mais tempo e energia a algum tema ou atividade que gosta ou que lhe interessa?",
            "É muito exigente e crítico/a consigo mesmo/a, e nunca fica satisfeito/a com o que faz?",
            "Insiste em buscar soluções para os problemas?",
            "Tem sua própria organização?",
            "É muito seguro/a e, às vezes, teimoso/a, em suas convicções?",
            "Precisa de pouco ou nenhum estímulo para terminar um trabalho que lhe interessa?",
            "Deixa de fazer outras coisas para envolver-se numa atividade que lhe interessa?",
            "Sabe identificar as áreas de dificuldade que podem surgir em uma atividade?",
            "Sabe estabelecer prioridades com facilidade?",
            "Consegue prever as etapas e os detalhes para realizar uma atividade?",
            "É persistente nas atividades que lhe interessam e busca concluir as tarefas?",
            "É interessado/a e eficiente na organização de tarefas?",
            "Sabe distinguir as consequências e os efeitos de ações?"
        ],
        "Liderança": [
            "É autossuficiente?",
            "É escolhido/a pelos seus colegas e amigos para funções de líder (líder de turma, coordenador/a)?",
            "É cooperativo/a com os demais?",
            "Tende a organizar o grupo?",
            "Sabe se expressar bem e convence os outros com os seus argumentos?"
        ]
    }

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
            if bloco == "Características Gerais":
                respostas_numericas = respostas.map(mapa_diagnostico)
                for pergunta in perguntas_existentes:
                    original = df_aluno[pergunta].values[0]
                    st.markdown(f"**{pergunta}** → _{original}_")
            else:
                respostas_numericas = respostas.map(mapa_respostas)

            media = pd.to_numeric(respostas_numericas, errors="coerce").mean()
            if pd.notna(media):
                medias_blocos.append(media)
                st.markdown(f"**Pontuação média:** `{media:.2f} / 4.00`")
                st.progress(media / 4)
            else:
                st.warning("⚠️ Não foi possível calcular a média (valores ausentes ou inválidos).")

        # Campos descritivos
        campos_descritivos = [
            col for col in df.columns
            if any(kw in col.lower() for kw in ["atividades mais gosta", "áreas esse(a) aluno(a)", "interesse", "destaque"])
        ]
        respostas_desc = df_aluno[campos_descritivos].iloc[0]
        if not respostas_desc.empty:
            st.markdown("### 💬 Interesses e Áreas de Destaque")
            for col, val in respostas_desc.items():
                if pd.notna(val) and str(val).strip():
                    st.markdown(f"**{col}** → _{val}_")

        # Avaliação geral
        st.subheader("🧠 Avaliação Geral – Probabilidade de Altas Habilidades/Superdotação")
        if medias_blocos:
            media_geral = sum(medias_blocos) / len(medias_blocos)
            percentual = (media_geral / 4) * 100
            st.metric("Probabilidade estimada", f"{percentual:.1f}%")
            st.progress(percentual / 100)
        else:
            st.warning("⚠️ Não foi possível calcular a média geral – dados insuficientes.")

        # Gráfico radar
        st.subheader("📊 Radar das Pontuações por Bloco")
        escala = st.slider("📐 Escala visual do gráfico (quanto menor, mais compacto)", 3, 8, 5)

        labels = list(blocos.keys())
        valores = []

        for bloco in labels:
            perguntas_existentes = [p for p in blocos[bloco] if p in df.columns]
            respostas = df_aluno[perguntas_existentes].iloc[0]

            if bloco == "Características Gerais":
                respostas_numericas = respostas.map(mapa_diagnostico)
            else:
                respostas_numericas = respostas.map(mapa_respostas)

            media = pd.to_numeric(respostas_numericas, errors="coerce").mean()
            valores.append(media if pd.notna(media) else 0)

        num_blocos = len(labels)
        angles = np.linspace(0, 2 * np.pi, num_blocos, endpoint=False).tolist()
        valores += valores[:1]
        angles += angles[:1]
        labels += labels[:1]

        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            fig, ax = plt.subplots(figsize=(escala, escala * 0.8), subplot_kw=dict(polar=True))
            ax.plot(angles, valores, linewidth=2, linestyle='solid', marker='o')
            ax.fill(angles, valores, alpha=0.25)
            ax.set_yticks([0, 1, 2, 3, 4])
            ax.set_yticklabels(['0', '1', '2', '3', '4'], fontsize=8)
            ax.set_ylim(0, 4)
            ax.set_xticks(angles)
            ax.set_xticklabels(labels, fontsize=9)
            ax.set_title(f'Radar das Pontuações – {aluno}', size=13, pad=10)
            st.pyplot(fig)

            # Exportar imagem PNG
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
