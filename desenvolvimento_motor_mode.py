# desenvolvimento_motor_mode.py
# ------------------------------------------------------------
# Encapsula a UI do Modo EDM em uma função chamável pelo main.py
# ------------------------------------------------------------
from datetime import date

import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

from utils import (
    EDM_DOMINIOS,
    EDM_COLMAP,
    preprocess_edm,
    radar_edm_matplotlib,
    _load_csv,
    _apply_filters,
    _agg_by_turma,
)


def run_desenvolvimento_motor_mode():
    st.title("Modo EDM – Escala de Desenvolvimento Motor")

    # ============== Sidebar: Fonte de dados ==============
    with st.sidebar:
        st.header("Dados")
        fonte = st.radio("Fonte", ["URL CSV (Google Sheets publicado)", "Upload CSV"])
        csv_url = None
        uploaded = None
        if fonte == "URL CSV (Google Sheets publicado)":
            csv_url = st.text_input(
                "URL CSV",
                placeholder="https://docs.google.com/spreadsheets/d/.../pub?output=csv",
                help="Use o CSV publicado da planilha do Forms."
            )
        else:
            uploaded = st.file_uploader("Envie o CSV exportado do Forms", type=["csv"])
        recarregar = st.button("Recarregar")

    if not csv_url and uploaded is None:
        st.info("Informe a fonte de dados (URL CSV ou Upload) para iniciar a análise.")
        return

    # ============== Carregamento robusto ==============
    df_raw = _load_csv(csv_url, uploaded) if not recarregar else (_load_csv.clear() or _load_csv(csv_url, uploaded))
    if df_raw.empty:
        st.warning("Não foi possível carregar os dados. Verifique a fonte informada.")
        return

    # ============== Pré-processamento ==============
    df = preprocess_edm(df_raw.copy(), EDM_COLMAP)

    # ============== Sidebar: Filtros ==============
    with st.sidebar:
        st.header("Filtros")
        escolas = ["Todas"] + sorted(df["escola"].dropna().unique().tolist()) if "escola" in df.columns else ["Todas"]
        escola = st.selectbox("Escola", escolas)
        base = df[df["escola"].eq(escola)] if escola != "Todas" else df

        turmas_list = sorted(base["turma"].dropna().unique().tolist()) if "turma" in df.columns else []
        turma = st.selectbox("Turma", ["Todas"] + turmas_list)

        sexos_list = sorted(df["sexo"].dropna().unique().tolist()) if "sexo" in df.columns else []
        sexo_opts = st.multiselect("Sexo", sexos_list)
        only_alert = st.checkbox("Mostrar apenas alunos com alerta")

    dff = _apply_filters(df, escola, turma, sexo_opts, only_alert)

    # ============== Abas ==============
    tab1, tab2, tab3, tab4 = st.tabs(["Resumo", "Turmas/Escolas", "Aluno", "Dados"])

    # ---------- Resumo ----------
    with tab1:
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Avaliados", len(dff))
        pct_alerta = (dff['alerta_qdm'].eq('⚠️ Atraso').mean()*100 if len(dff) > 0 else 0.0)
        c2.metric("% com alerta", f"{pct_alerta:.1f}%")
        c3.metric("QDM médio", f"{dff['QDM'].mean():.1f}" if 'QDM' in dff and dff['QDM'].notna().any() else "—")
        pct_id_mot = (dff['idade_mot_meses_final'].notna().mean()*100 if len(dff) > 0 else 0.0)
        c4.metric("Com idade motora", f"{pct_id_mot:.1f}%")

        inip_med = dff['in_ip_meses'].mean() if 'in_ip_meses' in dff and dff['in_ip_meses'].notna().any() else np.nan
        c5.metric("IN/IP médio", f"{inip_med:+.0f} meses" if pd.notna(inip_med) else "—")

        st.subheader("Média por domínio")
        if all(col in dff.columns for col in EDM_DOMINIOS):
            st.bar_chart(dff[EDM_DOMINIOS].mean().rename("Média por domínio"))
        else:
            st.info("Sem colunas de domínios suficientes para o gráfico.")

        st.subheader("Distribuição do QDM")
        if "QDM" in dff.columns and dff["QDM"].notna().any():
            fig, ax = plt.subplots(figsize=(6, 3.2))
            ax.hist(dff["QDM"].dropna(), bins=10)
            ax.set_xlabel("QDM")
            ax.set_ylabel("Frequência")
            ax.set_title("Histograma de QDM")
            st.pyplot(fig)
        else:
            st.info("Sem QDM calculado (idade motora ausente).")

    # ---------- Turmas/Escolas ----------
    with tab2:
        st.subheader("Agregados por Turma")
        st.dataframe(_agg_by_turma(dff), use_container_width=True)

    # ---------- Aluno ----------
    with tab3:
        st.subheader("Perfil do aluno")
        if "nome" not in dff.columns or dff.empty:
            st.info("Sem alunos para exibir.")
        else:
            alunos = sorted(dff["nome"].dropna().unique().tolist())
            aluno = st.selectbox("Selecione o aluno", alunos)
            if aluno:
                row = dff[dff["nome"] == aluno].iloc[0]
                c1, c2 = st.columns([1, 1])
                with c1:
                    def _fmt_date(x):
                        return x if isinstance(x, date) else (x.date() if pd.notna(x) and hasattr(x, "date") else "—")
                    st.write(f"**Escola:** {row.get('escola','—')}  \n**Turma:** {row.get('turma','—')}  \n**Sexo:** {row.get('sexo','—')}")
                    st.write(f"**Nascimento:** {_fmt_date(row.get('nasc', pd.NaT))}")
                    st.write(f"**Data de Avaliação:** {_fmt_date(row.get('data_avaliacao', pd.NaT))}")

                    # Idades
                    icm = row.get('idade_cron_meses', np.nan)
                    icm_str = row.get('idade_cron_anos_meses_str', "")
                    st.write(f"**Idade cronológica:** {int(icm)} meses ({icm_str} a)" if pd.notna(icm) else "—")

                    imm_final = row.get('idade_mot_meses_final', np.nan)
                    imm_final_str = row.get('idade_mot_anos_meses_str_final', "")
                    st.write(f"**Idade motora (geral):** {int(round(imm_final))} meses ({imm_final_str} a)" if pd.notna(imm_final) else "—")

                    # IN/IP
                    inip = row.get('in_ip_meses', np.nan)
                    inip_str = row.get('in_ip_anos_meses_str', "")
                    if pd.notna(inip):
                        st.write(f"**IN/IP:** {int(round(inip)):+d} meses ({inip_str} a)")
                    else:
                        st.write("**IN/IP:** —")

                    st.write(f"**QDM:** {row.get('QDM', np.nan):.1f}  \n**Classificação:** {row.get('classe_qdm','—')}")
                    st.write(f"**Alertas (domínios ≤1):** {row.get('alerta_dominios') or '—'}")
                    obs = row.get("obs", "")
                    if pd.notna(obs) and str(obs).strip():
                        st.info(f"**Observações:** {obs}")
                with c2:
                    fig = radar_edm_matplotlib(row)
                    st.pyplot(fig, use_container_width=True)

    # ---------- Dados ----------
    with tab4:
        st.download_button(
            "Baixar CSV (filtro atual)",
            data=dff.to_csv(index=False).encode("utf-8"),
            file_name="edm_filtrado.csv",
            mime="text/csv"
        )
        st.dataframe(dff, use_container_width=True)
