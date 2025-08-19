# app_edm.py
# ------------------------------------------------------------
# Streamlit – Escala de Desenvolvimento Motor (EDM)
# Versão "tudo em um":
# - preprocess_edm embutido
# - radar_edm_matplotlib embutido
# - idade CRONOLÓGICA e idade MOTORA GERAL em MESES (+ exibição em ANOS.MESES)
# - IN/IP = idade motora geral - idade cronológica (positivo quando motora > cronológica)
# - ignora "colunas opcionais" nos avisos
# Dependências: streamlit, pandas, numpy, requests, matplotlib
# ------------------------------------------------------------

import io
import math
import requests
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt

# =========================
# Config / Constantes
# =========================

EDM_DOMINIOS = [
    "fina",        # Motricidade Fina
    "global_",     # Motricidade Global
    "equilibrio",  # Equilíbrio
    "esquema",     # Esquema Corporal
    "espacial",    # Organização Espacial
    "temporal",    # Organização Temporal
]

EDM_COLMAP = {
    "Carimbo de data/hora": "ts",
    "Nome do aluno": "nome",
    "Data de nascimento": "nasc",
    "Data de Avaliação": "data_avaliacao",
    "Idade cronológica (anos.meses)  (Opcional: Será calculada depois)": "idade_cron_str",  # OPCIONAL
    "Sexo": "sexo",
    "Escola": "escola",
    "Turma": "turma",
    "Pontuação – Motricidade Fina": "fina",
    "Pontuação – Motricidade Global": "global_",
    "Pontuação – Equilíbrio": "equilibrio",
    "Pontuação – Esquema Corporal": "esquema",
    "Pontuação – Organização Espacial": "espacial",
    "Pontuação – Organização Temporal": "temporal",
    "Idade motora (anos.meses) (Opcional: Será calculada depois)": "idade_motora_str",     # OPCIONAL
    "Comentários ou observações (opcional)": "obs",                                          # OPCIONAL
}

EXPECTED_COLS = [
    "Carimbo de data/hora",
    "Nome do aluno",
    "Data de nascimento",
    "Data de Avaliação",
    "Idade cronológica (anos.meses)  (Opcional: Será calculada depois)",  # OPCIONAL
    "Sexo",
    "Escola",
    "Turma",
    "Pontuação – Motricidade Fina",
    "Pontuação – Motricidade Global",
    "Pontuação – Equilíbrio",
    "Pontuação – Esquema Corporal",
    "Pontuação – Organização Espacial",
    "Pontuação – Organização Temporal",
    "Idade motora (anos.meses) (Opcional: Será calculada depois)",        # OPCIONAL
    "Comentários ou observações (opcional)",                               # OPCIONAL
]

# =========================
# Funções de utilidade
# =========================

def _parse_date(val):
    if pd.isna(val):
        return pd.NaT
    if isinstance(val, (pd.Timestamp, datetime, date)):
        return pd.to_datetime(val).date()
    s = str(val).strip()
    if not s:
        return pd.NaT
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%m/%d/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            pass
    try:
        return pd.to_datetime(s, dayfirst=True, errors="coerce").date()
    except Exception:
        return pd.NaT


def _anos_meses_str_para_meses(s):
    """
    Converte "anos.meses" em MESES (int).
    Aceita "7.6", "7,6", "7 6", "7-6", "7;6".
    Se detectar padrão NÃO-mensal (ex.: "7.25"), trata como ANOS DECIMAIS (round(anos*12)).
    """
    if pd.isna(s):
        return np.nan
    s = str(s).strip()
    if not s:
        return np.nan

    s_sep = s.replace(",", ".")
    for sep in (".", " ", ";", "-"):
        if sep in s_sep:
            partes = s_sep.split(sep)
            try:
                anos = int(float(partes[0]))
            except Exception:
                anos = None
            meses_txt = partes[1] if len(partes) > 1 else ""
            try:
                meses_val = int(float(meses_txt)) if meses_txt != "" else 0
            except Exception:
                meses_val = None

            if anos is not None and meses_val is not None and 0 <= meses_val <= 11:
                return anos * 12 + meses_val
            break

    try:
        anos_float = float(s.replace(",", "."))
        return int(round(anos_float * 12))
    except Exception:
        return np.nan


def _idade_meses_via_datas(nasc: date, ref: date):
    """
    Idade em MESES (int) com regra: se dias residuais >= 15, arredonda +1 mês.
    """
    if pd.isna(nasc) or pd.isna(ref):
        return np.nan
    if not isinstance(nasc, date) or not isinstance(ref, date):
        return np.nan
    if ref <= nasc:
        return np.nan

    months = (ref.year - nasc.year) * 12 + (ref.month - nasc.month)
    anchor = pd.Timestamp(nasc) + pd.DateOffset(months=months)
    residual_days = (pd.Timestamp(ref) - anchor).days
    if residual_days >= 15:
        months += 1
    return int(months)


def _meses_para_anos_meses_str(meses):
    """Converte MESES (int/float) em 'anos.meses' (ex.: 90 -> '7.6')."""
    if pd.isna(meses):
        return ""
    try:
        meses = int(round(float(meses)))
    except Exception:
        return ""
    anos = meses // 12
    mm = meses % 12
    return f"{anos}.{mm}"


def _signed_meses_para_anos_meses_str(meses_signed):
    """Converte MESES com sinal em string '+A.M' ou '-A.M'."""
    if pd.isna(meses_signed):
        return ""
    try:
        m = int(round(float(meses_signed)))
    except Exception:
        return ""
    sign = "-" if m < 0 else "+"
    m_abs = abs(m)
    anos = m_abs // 12
    mm = m_abs % 12
    return f"{sign}{anos}.{mm}"


def _classificacao_qdm(qdm: float):
    if pd.isna(qdm):
        return "—"
    if qdm >= 130:
        return "Muito Superior"
    if qdm >= 120:
        return "Superior"
    if qdm >= 110:
        return "Normal Alto"
    if qdm >= 90:
        return "Normal Médio"
    if qdm >= 80:
        return "Normal Baixo"
    if qdm >= 70:
        return "Inferior"
    return "Muito Inferior"


def _alerta_qdm(qdm: float, idade_mot_meses: float):
    if pd.isna(idade_mot_meses):
        return "ℹ️ Sem idade motora"
    if pd.isna(qdm):
        return "—"
    return "⚠️ Atraso" if qdm < 85 else "OK"


def _alerta_dominios(row):
    criticos = []
    for d in EDM_DOMINIOS:
        val = row.get(d, np.nan)
        try:
            if pd.notna(val) and float(val) <= 1.0:
                criticos.append(d)
        except Exception:
            pass
    return ", ".join(criticos)


def _is_optional_header(column_name: str) -> bool:
    return "opcional" in str(column_name).lower()


# =========================
# Pré-processamento principal
# =========================

def preprocess_edm(df_raw: pd.DataFrame, colmap: dict) -> pd.DataFrame:
    """
    - Renomeia colunas conforme colmap
    - Converte datas
    - Calcula IDADE CRONOLÓGICA em MESES (+ string anos.meses)
    - Calcula IDADE MOTORA GERAL (média dos DOMÍNIOS em anos ⇒ meses) + string anos.meses
      (fallback para 'idade_motora_str' se os domínios estiverem vazios na linha)
    - QDM com base na idade motora FINAL (geral ou informada)
    - IN/IP = idade motora geral - idade cronológica (meses), com string em anos.meses com sinal
    - Classificação e alertas
    """
    df = df_raw.copy()

    # 1) Renomear
    rename_map = {k: v for k, v in colmap.items() if k in df.columns}
    df = df.rename(columns=rename_map)

    # 2) Datas
    if "nasc" in df.columns:
        df["nasc"] = df["nasc"].apply(_parse_date)
    if "data_avaliacao" in df.columns:
        df["data_avaliacao"] = df["data_avaliacao"].apply(_parse_date)

    # 3) Idade CRONOLÓGICA (MESES via datas)
    df["idade_cron_meses"] = np.nan
    if "nasc" in df.columns and "data_avaliacao" in df.columns:
        df["idade_cron_meses"] = df.apply(
            lambda r: _idade_meses_via_datas(r.get("nasc", pd.NaT), r.get("data_avaliacao", pd.NaT)),
            axis=1
        )
    df["idade_cron_anos_meses_str"] = df["idade_cron_meses"].apply(_meses_para_anos_meses_str)

    # 4) Idade MOTORA informada (opcional) → meses
    if "idade_motora_str" in df.columns:
        df["idade_mot_meses_informada"] = df["idade_motora_str"].apply(_anos_meses_str_para_meses)
    else:
        df["idade_mot_meses_informada"] = np.nan

    # 5) Idade MOTORA GERAL a partir dos DOMÍNIOS (anos -> meses, média por linha)
    dom_meses_cols = []
    for d in EDM_DOMINIOS:
        if d in df.columns:
            col_m = f"{d}_meses"
            dom_meses_cols.append(col_m)
            df[col_m] = df[d].apply(_anos_meses_str_para_meses)

    if dom_meses_cols:
        df["idade_mot_meses_calc"] = df[dom_meses_cols].mean(axis=1, skipna=True)
        none_dom = df[dom_meses_cols].isna().all(axis=1)
        df.loc[none_dom, "idade_mot_meses_calc"] = np.nan
    else:
        df["idade_mot_meses_calc"] = np.nan

    df["idade_mot_anos_meses_str_calc"] = df["idade_mot_meses_calc"].apply(_meses_para_anos_meses_str)

    # 6) Escolha FINAL para idade motora (preferir GERAL calculada; senão, informada)
    df["idade_mot_meses_final"] = np.where(
        df["idade_mot_meses_calc"].notna(),
        df["idade_mot_meses_calc"],
        df["idade_mot_meses_informada"]
    )
    df["idade_mot_anos_meses_str_final"] = df["idade_mot_meses_final"].apply(_meses_para_anos_meses_str)

    # 7) QDM usando a idade motora FINAL
    df["QDM"] = np.where(
        (df["idade_cron_meses"].notna()) & (df["idade_mot_meses_final"].notna()) & (df["idade_cron_meses"] > 0),
        (df["idade_mot_meses_final"] / df["idade_cron_meses"]) * 100.0,
        np.nan
    )

    # 8) IN/IP = motora (geral) - cronológica
    df["in_ip_meses"] = df["idade_mot_meses_final"] - df["idade_cron_meses"]
    df.loc[df["idade_mot_meses_final"].isna() | df["idade_cron_meses"].isna(), "in_ip_meses"] = np.nan
    df["in_ip_anos_meses_str"] = df["in_ip_meses"].apply(_signed_meses_para_anos_meses_str)

    # 9) Classificação e alertas
    df["classe_qdm"] = df["QDM"].apply(_classificacao_qdm)
    df["alerta_qdm"] = df.apply(
        lambda r: _alerta_qdm(r.get("QDM", np.nan), r.get("idade_mot_meses_final", np.nan)),
        axis=1
    )
    df["alerta_dominios"] = df.apply(_alerta_dominios, axis=1)

    # 10) Normalizações simples
    for c in ("escola", "turma", "sexo", "nome"):
        if c in df.columns:
            df[c] = df[c].astype(str).str.strip()

    sort_cols = [c for c in ("escola", "turma", "nome") if c in df.columns]
    if sort_cols:
        df = df.sort_values(sort_cols, kind="stable").reset_index(drop=True)

    return df


# =========================
# Radar
# =========================

def radar_edm_matplotlib(row):
    labels = ["Fina", "Global", "Equilíbrio", "Esquema", "Espacial", "Temporal"]
    values = [float(row.get(d, np.nan)) if pd.notna(row.get(d, np.nan)) else 0.0 for d in EDM_DOMINIOS]
    values += values[:1]
    angles = np.linspace(0, 2 * math.pi, len(labels), endpoint=False).tolist()
    angles += angles[:1]

    fig, ax = plt.subplots(subplot_kw={"projection": "polar"}, figsize=(5.5, 5))
    ax.set_theta_offset(math.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)

    rmax = max([v for v in values if pd.notna(v)] + [3.0])
    rmax = max(rmax, 3.0)
    ax.set_rlabel_position(0)
    ax.set_ylim(0, rmax)

    ax.plot(angles, values, linewidth=2)
    ax.fill(angles, values, alpha=0.15)
    ax.set_title("Perfil por Domínio (Radar EDM)")
    fig.tight_layout()
    return fig


# =========================
# Leitura robusta do CSV
# =========================

@st.cache_data(ttl=300)
def _load_csv(csv_url: str = None, uploaded_file=None) -> pd.DataFrame:
    raw: bytes | None = None
    if uploaded_file is not None:
        raw = uploaded_file.read()
    elif csv_url:
        try:
            resp = requests.get(csv_url, timeout=20)
            resp.raise_for_status()
            raw = resp.content
        except Exception as e:
            try:
                df = pd.read_csv(csv_url, encoding="utf-8-sig", engine="python", sep=None, on_bad_lines="skip")
                df.columns = [str(c).strip() for c in df.columns]
                return _fix_excess_columns(df)
            except Exception as e2:
                st.error(f"Falha ao baixar/ler a URL CSV.\n1) {e}\n2) {e2}")
                return pd.DataFrame()
    else:
        return pd.DataFrame()

    try:
        df = pd.read_csv(io.BytesIO(raw), encoding="utf-8-sig", engine="python", sep=None, on_bad_lines="skip")
    except Exception:
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
        primeiras = EXPECTED_COLS[:10]
        missing = [c for c in primeiras if (c not in df.columns) and (not _is_optional_header(c))]
        if missing:
            st.warning(f"Atenção: colunas esperadas ausentes: {missing}")

    return df


def _fix_excess_columns(df: pd.DataFrame) -> pd.DataFrame:
    if EXPECTED_COLS[-1] not in df.columns:
        df[EXPECTED_COLS[-1]] = ""
    if len(df.columns) > len(EXPECTED_COLS):
        start_idx = len(EXPECTED_COLS) - 1
        extras = df.columns[start_idx:]
        if len(extras) > 1:
            df[EXPECTED_COLS[-1]] = df[extras].astype(str).apply(
                lambda r: " ".join([x for x in r if x and x.lower() != "nan"]).strip(), axis=1
            )
        keep = [c for c in EXPECTED_COLS if c in df.columns]
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
        return pd.DataFrame(columns=[
            "escola", "turma", "total", "qdm_med", "in_ip_med", *[f"avg_{d}" for d in EDM_DOMINIOS]
        ])
    agg = df.groupby(["escola", "turma"], dropna=False).agg(
        total=("nome", "count"),
        qdm_med=("QDM", "mean"),
        in_ip_med=("in_ip_meses", "mean"),
        **{f"avg_{d}": (d, "mean") for d in EDM_DOMINIOS}
    ).reset_index()
    return agg


# =========================
# App principal
# =========================

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


# Ponto de entrada
if __name__ == "__main__":
    run_desenvolvimento_motor_mode()
