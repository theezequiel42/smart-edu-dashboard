import io
import requests
import streamlit as st
import pandas as pd
import numpy as np

from utils import (
    EDM_DOMINIOS,
    preprocess_edm,
    radar_edm_matplotlib,
)

# Mapeamento do cabeçalho vindo do Google Forms -> nomes internos
EDM_COLMAP = {
    "Carimbo de data/hora": "ts",
    "Nome do aluno": "nome",
    "Data de nascimento": "nasc",
    "Data de Avaliação": "data_avaliacao",
    "Idade cronológica (anos.meses)  (Opcional: Será calculada depois)": "idade_cron_str",
    "Sexo": "sexo",
    "Escola": "escola",
    "Turma": "turma",
    "Pontuação – Motricidade Fina": "fina",
    "Pontuação – Motricidade Global": "global_",
    "Pontuação – Equilíbrio": "equilibrio",
    "Pontuação – Esquema Corporal": "esquema",
    "Pontuação – Organização Espacial": "espacial",
    "Pontuação – Organização Temporal": "temporal",
    "Idade motora (anos.meses) (Opcional: Será calculada depois)": "idade_motora_str",
    "Comentários ou observações (opcional)": "obs",
}

EXPECTED_COLS = [
    "Carimbo de data/hora",
    "Nome do aluno",
    "Data de nascimento",
    "Data de Avaliação",
    "Idade cronológica (anos.meses)  (Opcional: Será calculada depois)",
    "Sexo",
    "Escola",
    "Turma",
    "Pontuação – Motricidade Fina",
    "Pontuação – Motricidade Global",
    "Pontuação – Equilíbrio",
    "Pontuação – Esquema Corporal",
    "Pontuação – Organização Espacial",
    "Pontuação – Organização Temporal",
    "Idade motora (anos.meses) (Opcional: Será calculada depois)",
    "Comentários ou observações (opcional)",
]


@st.cache_data(ttl=300)
def _load_csv(csv_url: str = None, uploaded_file=None) -> pd.DataFrame:
    """
    Le CSV (URL ou upload) de forma robusta:
    - detecta delimitador automaticamente (sep=None, engine='python')
    - usa encoding 'utf-8-sig'
    - pula linhas ruins (on_bad_lines='skip')
    - fallback para sep=';'
    - se vierem colunas excedentes (vírgulas nas observações), funde-as em 'Comentários ou observações (opcional)'
    """
    raw: bytes | None = None

    # Fonte de bytes
    if uploaded_file is not None:
        raw = uploaded_file.read()
    elif csv_url:
        try:
            resp = requests.get(csv_url, timeout=20)
            resp.raise_for_status()
            raw = resp.content
        except Exception as e:
            # Fallback: tentar ler direto com pandas da URL
            try:
                df = pd.read_csv(csv_url, encoding="utf-8-sig", engine="python", sep=None, on_bad_lines="skip")
                df.columns = [str(c).strip() for c in df.columns]
                return _fix_excess_columns(df)
            except Exception as e2:
                st.error(f"Falha ao baixar/ler a URL CSV.\n1) {e}\n2) {e2}")
                return pd.DataFrame()
    else:
        return pd.DataFrame()

    # Primeira tentativa: autodetect
    try:
        df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", engine="python", sep=None, on_bad_lines="skip")
    except Exception:
        # Fallback: separador ';'
        try:
            df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", engine="python", sep=";", on_bad_lines="skip")
        except Exception as e:
            st.error(f"Não foi possível ler o CSV (mesmo com fallback ';'). Erro: {e}")
            return pd.DataFrame()

    df.columns = [str(c).strip() for c in df.columns]
    df = _fix_excess_columns(df)

    if df.empty:
        st.warning("CSV lido, porém sem dados após a limpeza.")
    else:
        # Checagem de colunas principais (as mais críticas)
        missing = [c for c in EXPECTED_COLS[:10] if c not in df.columns]
        if missing:
            st.warning(f"Atenção: colunas esperadas ausentes: {missing}")

    return df


def _fix_excess_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Se o CSV vier com colunas a mais (p.ex., vírgulas em observações sem aspas),
    concatena as colunas excedentes dentro de 'Comentários ou observações (opcional)'
    e mantém apenas as colunas esperadas que existirem.
    """
    # Garante col de observações
    if EXPECTED_COLS[-1] not in df.columns:
        df[EXPECTED_COLS[-1]] = ""

    # Se há mais colunas que o esperado, concatenar as excedentes em 'observações'
    if len(df.columns) > len(EXPECTED_COLS):
        # A partir da coluna de observações
        start_idx = len(EXPECTED_COLS) - 1
        extras = df.columns[start_idx:]
        if len(extras) > 1:
            df[EXPECTED_COLS[-1]] = df[extras].astype(str).apply(
                lambda r: " ".join([x for x in r if x and x.lower() != "nan"]).strip(), axis=1
            )
        # Manter apenas as esperadas que existirem
        keep = [c for c in EXPECTED_COLS if c in df.columns]
        # Garante a última (obs)
        if EXPECTED_COLS[-1] not in keep:
            keep.append(EXPECTED_COLS[-1])
        df = df[keep]

    return df


def _apply_filters(df: pd.DataFrame, escola, turma, sexo_opts, only_alert):
    dff = df.copy()
    if escola and escola != "Todas":
        dff = dff[dff["escola"] == escola]
    if turma and turma != "Todas":
        dff = dff[dff["turma"] == turma]
    if sexo_opts:
        dff = dff[dff["sexo"].isin(sexo_opts)]
    if only_alert:
        dff = dff[dff["alerta_qdm"].isin(["⚠️ Atraso", "ℹ️ Sem idade motora"])]
    return dff


def _agg_by_turma(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(columns=["escola", "turma", "total", "qdm_med", *[f"avg_{d}" for d in EDM_DOMINIOS]])
    agg = df.groupby(["escola", "turma"]).agg(
        total=("nome", "count"),
        qdm_med=("QDM", "mean"),
        **{f"avg_{d}": (d, "mean") for d in EDM_DOMINIOS}
    ).reset_index()
    return agg


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
    df_raw = _load_csv(csv_url, uploaded) if not recarregar else _load_csv.clear() or _load_csv(csv_url, uploaded)

    if df_raw.empty:
        st.warning("Não foi possível carregar os dados. Verifique a fonte informada.")
        return

    # ============== Pré-processamento (utils) ==============
    df = preprocess_edm(df_raw.copy(), EDM_COLMAP)

    # ============== Sidebar: Filtros ==============
    with st.sidebar:
        st.header("Filtros")
        escolas = ["Todas"] + sorted(df["escola"].dropna().unique().tolist())
        escola = st.selectbox("Escola", escolas)
        turmas_base = df[df["escola"].eq(escola)]["turma"].dropna().unique().tolist() if escola != "Todas" \
            else df["turma"].dropna().unique().tolist()
        turma = st.selectbox("Turma", ["Todas"] + sorted(turmas_base))
        sexo_opts = st.multiselect("Sexo", sorted(df["sexo"].dropna().unique().tolist()))
        only_alert = st.checkbox("Mostrar apenas alunos com alerta")

    dff = _apply_filters(df, escola, turma, sexo_opts, only_alert)

    # ============== Abas ==============
    tab1, tab2, tab3, tab4 = st.tabs(["Resumo", "Turmas/Escolas", "Aluno", "Dados"])

    # ---------- Resumo ----------
    with tab1:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Avaliados", len(dff))
        pct_alerta = (dff['alerta_qdm'].eq('⚠️ Atraso').mean()*100 if len(dff) > 0 else 0.0)
        c2.metric("% com alerta", f"{pct_alerta:.1f}%")
        c3.metric("QDM médio", f"{dff['QDM'].mean():.1f}" if dff['QDM'].notna().any() else "—")
        pct_id_mot = (dff['idade_mot_dec'].notna().mean()*100 if len(dff) > 0 else 0.0)
        c4.metric("Com idade motora", f"{pct_id_mot:.1f}%")

        st.subheader("Média por domínio")
        st.bar_chart(dff[EDM_DOMINIOS].mean().rename("Média por domínio"))

        st.subheader("Distribuição do QDM")
        if dff["QDM"].notna().any():
            import matplotlib.pyplot as plt
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
        alunos = sorted(dff["nome"].dropna().unique().tolist())
        aluno = st.selectbox("Selecione o aluno", alunos)
        if aluno:
            row = dff[dff["nome"] == aluno].iloc[0]
            c1, c2 = st.columns([1, 1])
            with c1:
                st.write(f"**Escola:** {row.escola}  \n**Turma:** {row.turma}  \n**Sexo:** {row.sexo}")
                st.write(f"**Nascimento:** {row.nasc.date() if pd.notna(row.nasc) else '—'}")
                st.write(f"**Data de Avaliação:** {row.data_avaliacao.date() if pd.notna(row.data_avaliacao) else '—'}")
                st.write(f"**Idade cronológica:** {row.idade_cron_dec:.2f} anos" if pd.notna(row.idade_cron_dec) else "—")
                st.write(f"**Idade motora:** {row.idade_mot_dec:.2f} anos" if pd.notna(row.idade_mot_dec) else "—")
                st.write(f"**QDM:** {row.QDM:.1f}  \n**Classificação:** {row.classe_qdm}")
                st.write(f"**Alertas (domínios ≤1):** {row.alerta_dominios or '—'}")
                if pd.notna(row.get("obs", np.nan)) and str(row.get("obs", "")).strip():
                    st.info(f"**Observações:** {row.obs}")
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
