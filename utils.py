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