import io
import math
from datetime import datetime, date

import requests
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sqlite3
import unicodedata

CATEGORIAS_VALIDAS = ["Socialização", "Linguagem", "Cognição", "Auto cuidado", "Desenvolvimento Motor"]

def gerar_grafico_respostas(df, categoria_selecionada="Todas", largura=6, altura=4):
    fig, ax = plt.subplots(figsize=(largura, altura))

    categorias = CATEGORIAS_VALIDAS if categoria_selecionada == "Todas" else [categoria_selecionada]
    contagem_respostas = {"Sim": 0, "Às vezes": 0, "Não": 0}

    for categoria in categorias:
        colunas_categoria = [col for col in df.columns if col.startswith(categoria)]
        for col in colunas_categoria:
            respostas = df[col].dropna().astype(str).str.strip()
            contagem_respostas["Sim"] += (respostas == "Sim").sum()
            contagem_respostas["Às vezes"] += (respostas == "Às vezes").sum()
            contagem_respostas["Não"] += (respostas == "Não").sum()

    cores = ["#2E7D32", "#FFC107", "#D32F2F"]
    ax.bar(contagem_respostas.keys(), contagem_respostas.values(), color=cores)
    ax.set_title(f"Contagem de Respostas - {categoria_selecionada}")
    ax.set_ylabel("Quantidade")
    return fig, ax


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

def analisar_todos_os_alunos():
    st.subheader("📊 Análise Geral de Todos os Alunos")
    conn = sqlite3.connect("respostas_ahsd.db")
    c = conn.cursor()

    c.execute("SELECT aluno, bloco, resposta FROM respostas")
    dados = c.fetchall()
    conn.close()

    if not dados:
        st.info("Ainda não há respostas registradas.")
        return

    df = pd.DataFrame(dados, columns=["Aluno", "Bloco", "Resposta"])
    
    # Remove o bloco "Descritivo" da análise
    df = df[df["Bloco"] != "Descritivo"]


    mapa_respostas = {"Nunca": 0, "Raramente": 1, "Às vezes": 2, "As vezes": 2, "Frequentemente": 3, "Sempre": 4}
    mapa_diagnostico = {"Sim": 4, "Não": 0, "Altas": 4, "Alta": 4, "Média": 2, "Medias": 2, "Médias": 2, "Baixa": 0, "Baixas": 0}

    df["RespostaNum"] = df["Resposta"].apply(lambda x: unicodedata.normalize("NFKD", str(x).strip()).encode("ASCII", "ignore").decode("utf-8"))
    df["RespostaNum"] = df["RespostaNum"].map(mapa_respostas).fillna(df["RespostaNum"].map(mapa_diagnostico))
    df["RespostaNum"] = pd.to_numeric(df["RespostaNum"], errors="coerce")

    # Média por bloco (geral)
    st.subheader("📚 Média Geral por Bloco")
    media_blocos = df.groupby("Bloco")["RespostaNum"].mean().round(2)
    st.bar_chart(media_blocos)

    # Média geral por aluno
    st.subheader("🏅 Ranking de Alunos por Média Geral")
    ranking = df.groupby("Aluno")["RespostaNum"].mean().sort_values(ascending=False).round(2)
    st.dataframe(ranking.reset_index().rename(columns={"RespostaNum": "Média Geral"}), use_container_width=True)

    # Radar da média por bloco (todos os alunos)
    st.subheader("📈 Radar da Média Geral por Bloco")
    if len(media_blocos) > 1:
        labels = list(media_blocos.index)
        valores = list(media_blocos.values)
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
            ax.set_title('Radar – Média Geral por Bloco', size=13, pad=10)
            st.pyplot(fig)
    else:
        st.info("Não há dados suficientes para exibir o gráfico radar.")
        
        
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
# Radar (matplotlib)
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
                st.error(f"Falha ao baixar/ler a URL CSV.\\n1) {e}\\n2) {e2}")
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
