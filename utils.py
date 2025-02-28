import pandas as pd

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


def calcular_status_aluno(df, categoria, meses_faixa_etaria, pontuacao_esperada_manual=None):
    """
    Calcula o status do aluno na categoria selecionada.
    Considera "Sim" = 1 ponto, "Às vezes" = 0.5 ponto e "Não" = 0 ponto.
    Permite ajuste manual da pontuação esperada.
    """
    df_resultado = []

    for _, row in df.iterrows():
        # Filtra as colunas pertencentes à categoria
        colunas_categoria = [col for col in df.columns if isinstance(col, str) and col.startswith(categoria)]
        total_perguntas = len(colunas_categoria)

        if total_perguntas == 0:
            continue

        # Contagem de respostas
        pontos_obtidos = sum([
            1 if row[col] == "Sim" else 0.5 if row[col] == "Às vezes" else 0
            for col in colunas_categoria
        ])

        # Cálculo correto da pontuação esperada
        pontuacao_esperada = (total_perguntas / meses_faixa_etaria) * row["Meses_Totais"]

        # Se o usuário alterou manualmente a pontuação esperada, usar o valor inserido
        if pontuacao_esperada_manual is not None:
            pontuacao_esperada = pontuacao_esperada_manual

        # Determinar o status com base nos critérios
        if pontos_obtidos >= pontuacao_esperada:
            status = "Sem atraso ✅"
        elif pontos_obtidos >= (pontuacao_esperada - 2):
            status = "Alerta para atraso ⚠️"
        else:
            status = "Déficit 🚨"

        df_resultado.append({
            "Aluno": row["Aluno"],
            "Pontuação Obtida": pontos_obtidos,
            "Pontuação Esperada": round(pontuacao_esperada, 2),
            "Status": status
        })

    return  pd.DataFrame(df_resultado) if df_resultado else None
