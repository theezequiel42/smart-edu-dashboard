
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