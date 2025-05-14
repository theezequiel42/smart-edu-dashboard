import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import io
import sqlite3
from datetime import datetime
import unicodedata
from blocos_ahsd import blocos
from utils import analisar_todos_os_alunos

def normalizar_texto(texto):
    return unicodedata.normalize("NFKD", texto.strip()).encode("ASCII", "ignore").decode("utf-8")

def init_db():

    if st.checkbox("🎓 Gerenciar alunos cadastrados"):
        gerenciar_alunos()
        st.divider()

    
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()

    # Cria a tabela de respostas se não existir
    c.execute('''CREATE TABLE IF NOT EXISTS respostas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    aluno TEXT,
                    perfil TEXT,
                    pergunta TEXT,
                    resposta TEXT,
                    data_envio TEXT,
                    bloco TEXT
                )''')

    # Cria a tabela de alunos se não existir
    c.execute('''CREATE TABLE IF NOT EXISTS alunos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT UNIQUE
                )''')

    # Cria a tabela de profissionais se não existir
    c.execute('''CREATE TABLE IF NOT EXISTS profissionais (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome TEXT,
                    perfil TEXT,
                    disciplina TEXT,
                    UNIQUE(nome, perfil)
                )''')

    conn.commit()
    conn.close()

def salvar_respostas_lote(df, perfil):
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()

    for _, linha in df.iterrows():
        # Ignora se o nome do aluno estiver ausente ou vazio
        if pd.isna(linha.get('Nome do(a) Aluno(a)', linha.get('Nome'))):
            continue
        nome_aluno = str(linha.get('Nome do(a) Aluno(a)', linha.get('Nome'))).strip()

        # Cadastra aluno se ainda não existir
        c.execute("SELECT id FROM alunos WHERE nome = ?", (nome_aluno,))
        if not c.fetchone():
            c.execute("INSERT INTO alunos (nome) VALUES (?)", (nome_aluno,))

        nome_resp = ""
        disciplina = ""

        if perfil == "Professor":
            nome_resp = str(linha.get('Nome do(a) Professor(a)', '')).strip()
            disciplina = str(linha.get('Disciplina do professor', '')).strip()
        elif perfil == "Responsável":
            nome_resp = str(linha.get('Nome do(a) Responsável', '')).strip()
        elif perfil == "Artístico/Esportivo":
            nome_resp = str(linha.get('Nome do(a) Profissional', '')).strip()
            disciplina = str(linha.get('Área de atuação', '')).strip()

        if nome_resp:
            c.execute("SELECT id FROM profissionais WHERE nome = ? AND perfil = ?", (nome_resp, perfil))
            if not c.fetchone():
                c.execute("INSERT INTO profissionais (nome, perfil, disciplina) VALUES (?, ?, ?)", (nome_resp, perfil, disciplina))

        for bloco, perguntas in blocos.items():
            for pergunta in perguntas:
                if pergunta in df.columns:
                    resposta = str(linha[pergunta])
                    c.execute("""
                        INSERT INTO respostas (aluno, perfil, pergunta, resposta, data_envio, bloco)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (nome_aluno, perfil, pergunta, resposta, datetime.now().isoformat(), bloco))

    conn.commit()
    conn.close()

def gerenciar_profissionais():
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()

    st.subheader("👥 Profissionais Cadastrados")
    c.execute("SELECT id, nome, perfil, disciplina FROM profissionais ORDER BY perfil, nome")
    dados = c.fetchall()

    if dados:
        df = pd.DataFrame(dados, columns=["ID", "Nome", "Perfil", "Disciplina"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

        st.markdown("---")
        st.subheader("✏️ Editar ou Excluir Profissional")
        ids = df["ID"].tolist()
        nomes = df["Nome"].tolist()
        id_sel = st.selectbox("Selecione um profissional para editar ou excluir", ids, format_func=lambda i: nomes[ids.index(i)])

        if id_sel:
            prof = df[df["ID"] == id_sel].iloc[0]
            novo_nome = st.text_input("Nome", prof["Nome"])
            novo_perfil = st.selectbox("Perfil", ["Professor", "Responsável", "Artístico/Esportivo"], index=["Professor", "Responsável", "Artístico/Esportivo"].index(prof["Perfil"]))
            nova_disciplina = st.text_input("Disciplina", prof["Disciplina"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Salvar alterações"):
                    c.execute("""
                        UPDATE profissionais SET nome = ?, perfil = ?, disciplina = ? WHERE id = ?
                    """, (novo_nome.strip(), novo_perfil, nova_disciplina.strip(), id_sel))
                    conn.commit()
                    st.toast("Alterações salvas com sucesso!", icon="✅")
                    st.rerun()
            with col2:
                if st.button("🗑️ Excluir profissional"):
                    c.execute("DELETE FROM profissionais WHERE id = ?", (id_sel,))
                    conn.commit()
                    st.toast("Profissional excluído.", icon="⚠️")
                    st.experimental_rerun()

    else:
        st.info("Nenhum profissional cadastrado até o momento.")

    conn.close()
    st.subheader("👥 Profissionais Cadastrados")
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()
    c.execute("SELECT nome, perfil, disciplina FROM profissionais ORDER BY perfil, nome")
    dados = c.fetchall()
    conn.close()

    if dados:
        df = pd.DataFrame(dados, columns=["Nome", "Perfil", "Disciplina"])
        st.dataframe(df, use_container_width=True)
    else:
        st.info("Nenhum profissional cadastrado até o momento.")

def gerenciar_alunos():
    st.subheader("👩‍🎓 Alunos Cadastrados")
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()
    c.execute("SELECT id, nome FROM alunos ORDER BY nome")
    dados = c.fetchall()

    if dados:
        df = pd.DataFrame(dados, columns=["ID", "Nome"])
        st.dataframe(df.drop(columns=["ID"]), use_container_width=True)

        st.markdown("---")
        st.subheader("✏️ Editar ou Excluir Aluno")
        ids = df["ID"].tolist()
        nomes = df["Nome"].tolist()
        id_sel = st.selectbox("Selecione um aluno para editar ou excluir", ids, format_func=lambda i: nomes[ids.index(i)])

        if id_sel:
            aluno = df[df["ID"] == id_sel].iloc[0]
            novo_nome = st.text_input("Nome do Aluno", aluno["Nome"])

            col1, col2 = st.columns(2)
            with col1:
                if st.button("💾 Salvar alterações"):
                    c.execute("UPDATE alunos SET nome = ? WHERE id = ?", (novo_nome.strip(), id_sel))
                    conn.commit()
                    st.success("Alterações salvas com sucesso!")
                    st.experimental_rerun()
            with col2:
                if st.button("🗑️ Excluir aluno"):
                    c.execute("DELETE FROM alunos WHERE id = ?", (id_sel,))
                    conn.commit()
                    st.warning("Aluno excluído.")
                    st.experimental_rerun()
    else:
        st.info("Nenhum aluno cadastrado ainda.")

    conn.close()

def analisar_respostas_aluno():
    st.subheader("📊 Análise Detalhada por Aluno")
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()

    # Lista alunos
    c.execute("SELECT nome FROM alunos ORDER BY nome")
    nomes = [row[0] for row in c.fetchall()]

    if not nomes:
        st.info("Nenhum aluno cadastrado.")
        return

    aluno_sel = st.selectbox("👤 Selecione um aluno para análise", ["Todos"] + nomes)
    if aluno_sel == "Todos":
        analisar_todos_os_alunos()
        return

    # Seleciona o perfil desejado
    c.execute("SELECT DISTINCT perfil FROM respostas WHERE aluno = ?", (aluno_sel,))
    perfis_disponiveis = sorted([row[0] for row in c.fetchall()])
    perfil_sel = st.selectbox("👤 Filtrar por perfil", ["Todos"] + perfis_disponiveis)

    # Busca as respostas de acordo com o perfil selecionado
    if perfil_sel == "Todos":
        c.execute("SELECT bloco, pergunta, resposta, perfil FROM respostas WHERE aluno = ?", (aluno_sel,))
    else:
        c.execute("SELECT bloco, pergunta, resposta, perfil FROM respostas WHERE aluno = ? AND perfil = ?", (aluno_sel, perfil_sel))

    dados = c.fetchall()
    conn.close()

    if not dados:
        st.warning("Este aluno ainda não possui respostas registradas.")
        return

    df = pd.DataFrame(dados, columns=["Bloco", "Pergunta", "Resposta", "Perfil"])

    mapa_respostas = {"Nunca": 0, "Raramente": 1, "Às vezes": 2, "As vezes": 2, "Frequentemente": 3, "Sempre": 4}
    mapa_diagnostico = {"Sim": 4, "Não": 0, "Altas": 4, "Alta": 4, "Média": 2, "Medias": 2, "Médias": 2, "Baixa": 0, "Baixas": 0}

    medias_blocos = {}

    for bloco in df["Bloco"].unique():
        st.subheader(f"📚 Bloco: {bloco}")
        bloco_df = df[df["Bloco"] == bloco]

        if bloco == "Descritivo":
            for _, linha in bloco_df.drop_duplicates(subset=["Pergunta", "Resposta"]).iterrows():
                st.markdown(f"**{linha['Pergunta']}** → _{linha['Resposta']}_")
        else:
            respostas = bloco_df["Resposta"].apply(lambda x: unicodedata.normalize("NFKD", str(x).strip()).encode("ASCII", "ignore").decode("utf-8"))
            respostas_numericas = respostas.map(mapa_respostas).fillna(respostas.map(mapa_diagnostico))
            media = pd.to_numeric(respostas_numericas, errors="coerce").mean()
            if pd.notna(media):
                st.markdown(f"**Pontuação média:** `{media:.2f} / 4.00`")
                st.progress(media / 4)
                medias_blocos[bloco] = media
            else:
                st.toast("⚠️ Não foi possível calcular a média deste bloco.", icon="⚠️")

    if medias_blocos:
        st.subheader("🧠 Avaliação Geral")
        media_geral = sum(medias_blocos.values()) / len(medias_blocos)
        percentual = (media_geral / 4) * 100
        st.metric("Probabilidade estimada de Altas Habilidades/Superdotação", f"{percentual:.1f}%")
        st.progress(percentual / 100)

        st.divider()
        st.subheader("📈 Radar de Pontuação por Bloco")
        labels = list(medias_blocos.keys())
        valores = list(medias_blocos.values())
        labels_plot = labels + [labels[0]]
        valores_plot = valores + [valores[0]]
        angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False).tolist()
        angles += angles[:1]

        escala = st.slider("📐 Escala visual do gráfico", 3, 8, 5)
        col1, col2, col3 = st.columns([1, 6, 1])
        with col2:
            fig, ax = plt.subplots(figsize=(escala, escala * 0.8), subplot_kw=dict(polar=True))
            ax.plot(angles, valores_plot, linewidth=2, linestyle='solid', marker='o')
            ax.fill(angles, valores_plot, alpha=0.25)
            ax.set_yticks([0, 1, 2, 3, 4])
            ax.set_yticklabels(['0', '1', '2', '3', '4'], fontsize=8)
            ax.set_ylim(0, 4)
            ax.set_xticks(angles)
            ax.set_xticklabels(labels_plot, fontsize=9)
            ax.set_title(f'Radar – {aluno_sel}', size=13, pad=10)
            st.pyplot(fig)

        # Exporta o gráfico como imagem PNG
        buf = io.BytesIO()
        fig.savefig(buf, format="png", bbox_inches="tight")
        buf.seek(0)

        nome_limpo = aluno_sel.replace(" ", "_").lower()
        nome_arquivo = f"grafico_radar_{nome_limpo}.png"
        st.download_button(
            label="📥 Baixar gráfico como imagem (PNG)",
            data=buf,
            file_name=nome_arquivo,
            mime="image/png"
        )

def run_ah_mode():
    st.title("📤 Importação de Respostas - Altas Habilidades/Superdotação")

    if st.checkbox("📊 Acessar análise por aluno"):
        analisar_respostas_aluno()
        st.divider()

    init_db()

    perfil = st.selectbox("👥 Quem está respondendo?", ["Professor", "Responsável", "Artístico/Esportivo"])

    st.subheader("📁 Importar respostas de um arquivo")
    arquivo = st.file_uploader("Envie um arquivo CSV ou Excel contendo as respostas", type=["csv", "xlsx"])

    if arquivo:
        try:
            if arquivo.name.endswith(".csv"):
                df = pd.read_csv(arquivo)
            else:
                df = pd.read_excel(arquivo)

            col_nome_aluno = 'Nome do(a) Aluno(a)' if 'Nome do(a) Aluno(a)' in df.columns else 'Nome'
            if col_nome_aluno not in df.columns:
                st.error("❌ O arquivo deve conter uma coluna com o nome do aluno.")
                return

            salvar_respostas_lote(df, perfil)
            st.success("✅ Respostas importadas e associadas aos alunos e profissionais com sucesso!")

        except Exception as e:
            st.error(f"Erro ao processar o arquivo: {e}")
    else:
        st.info("Envie um arquivo com a coluna 'Nome do(a) Aluno(a)' ou 'Nome' e as perguntas como cabeçalhos.")
