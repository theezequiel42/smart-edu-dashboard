# Smart Edu Dashboard - Ferramenta de Análise de Avaliação Educacional Interativa

O Smart Edu Dashboard é um aplicativo da web baseado em Streamlit que permite que profissionais educacionais analisem e visualizem dados de avaliação de alunos por meio de dois modos especializados: SME (Análise de Pesquisa) e CMAE (Avaliação de Desenvolvimento do Aluno). O aplicativo fornece visualização de dados interativa, relatórios personalizáveis ​​e ferramentas de análise abrangentes para instituições educacionais.

O aplicativo oferece recursos robustos para análise de dados, incluindo:
- Filtragem dinâmica de dados de avaliação por unidade escolar, categoria e aluno individual
- Várias opções de visualização, incluindo gráficos de barras, gráficos de pizza e gráficos de linhas
- Geração automatizada de relatórios em formatos PDF e Word
- Cálculo em tempo real de métricas de desenvolvimento do aluno
- Painel interativo com estatísticas resumidas e distribuição de status

## Estrutura do Repositório
```
.
├── main.py # Ponto de entrada do aplicativo e inicialização da IU
├── sme_mode.py # Implementação do modo de análise de pesquisa
├── cmae_mode.py # Implementação do modo de análise de avaliação do aluno
├── requirements.txt # Dependências do pacote Python
└── auxiliar.txt # Instruções de configuração e implantação
```

## Instruções de uso
### Pré-requisitos
- Python 3.x
- gerenciador de pacotes pip

### Instalação
```bash
# Instale as dependências necessárias
python -m pip install -r requirements.txt

# Execute o aplicativo
python -m streamlit run main.py
```

### Início rápido
1. Inicie o aplicativo usando o comando acima
2. Selecione o modo SME ou CMAE na tela inicial
3. Carregue um arquivo Excel contendo os dados da avaliação
4. Use os filtros da barra lateral para personalizar sua análise
5. Gere e baixe relatórios com base nos dados visualizados

### Exemplos mais detalhados

**Uso do modo SME:**
```python
# Carregue o arquivo Excel de dados da pesquisa
# Selecione o curso no menu suspenso
# Escolha as perguntas para analisar
# Selecione o tipo de visualização (Barra/Pizza/Linha)
# Baixe o relatório do Word com análise
```

**Uso do modo CMAE:**
```python
# Carregue o arquivo Excel de avaliação do aluno
# Filtre por unidade escolar
# Selecione a categoria (Socialização/Linguagem/Cognição/etc.)
# Escolha o aluno no menu suspenso
# Visualize a distribuição de status
# Baixe o relatório em PDF
```

### Solução de problemas

**Problemas comuns:**

1. Erros de upload de arquivo
- Problema: "Não foi possível carregar o arquivo Excel"
- Solução: Certifique-se de que o arquivo esteja no formato .xlsx
- Verifique as permissões do arquivo

2. Problemas de visualização
- Problema: Gráficos não são exibidos
- Solução: Verifique se os dados contêm respostas válidas
- Verifique se os nomes das colunas correspondem ao formato esperado

3. Erros de geração de relatórios
- Problema: falha na exportação de PDF/Word
- Solução: garanta espaço em disco suficiente
- Verifique as permissões de gravação no diretório de saída

## Fluxo de dados
O aplicativo processa dados de avaliação educacional por meio de um pipeline estruturado, do upload do arquivo à visualização e ao relatório.

```ascii
[Arquivo Excel] -> [Carregamento de dados] -> [Processamento/filtragem] -> [Análise] -> [Visualização] -> [Geração de relatórios]
```

Interações de componentes principais:
1. Carregamento de dados por meio do carregador de arquivos do Streamlit
2. Processamento do Pandas DataFrame para manipulação de dados
3. Matplotlib/Seaborn para geração de visualização
4. ReportLab/python-docx para criação de relatórios
5. Filtragem e recálculo de métricas em tempo real
6. Atualizações dinâmicas da IU com base nas seleções do usuário
7. Cálculo de status automatizado com base nos critérios de avaliação
8. Funcionalidade de exportação para relatórios gerados

# Smart Edu Dashboard - Interactive Educational Assessment Analysis Tool

Smart Edu Dashboard is a Streamlit-based web application that enables educational professionals to analyze and visualize student assessment data through two specialized modes: SME (Survey Analysis) and CMAE (Student Development Assessment). The application provides interactive data visualization, customizable reporting, and comprehensive analysis tools for educational institutions.

The application offers robust features for data analysis including:
- Dynamic filtering of assessment data by school unit, category, and individual student
- Multiple visualization options including bar charts, pie charts, and line graphs
- Automated report generation in PDF and Word formats
- Real-time calculation of student development metrics
- Interactive dashboard with summary statistics and status distribution

## Repository Structure
```
.
├── main.py                 # Application entry point and UI initialization
├── sme_mode.py            # Survey analysis mode implementation
├── cmae_mode.py           # Student assessment analysis mode implementation
├── requirements.txt       # Python package dependencies
└── auxiliar.txt          # Setup and deployment instructions
```

## Usage Instructions
### Prerequisites
- Python 3.x
- pip package manager

### Installation
```bash
# Install required dependencies
python -m pip install -r requirements.txt

# Run the application
python -m streamlit run main.py
```

### Quick Start
1. Launch the application using the command above
2. Select either SME or CMAE mode from the initial screen
3. Upload an Excel file containing the assessment data
4. Use the sidebar filters to customize your analysis
5. Generate and download reports based on the visualized data

### More Detailed Examples

**SME Mode Usage:**
```python
# Upload survey data Excel file
# Select course from dropdown
# Choose questions to analyze
# Select visualization type (Bar/Pie/Line)
# Download Word report with analysis
```

**CMAE Mode Usage:**
```python
# Upload student assessment Excel file
# Filter by school unit
# Select category (Socialization/Language/Cognition/etc.)
# Choose student from dropdown
# View status distribution
# Download PDF report
```

### Troubleshooting

**Common Issues:**

1. File Upload Errors
   - Problem: "Unable to load Excel file"
   - Solution: Ensure file is in .xlsx format
   - Check file permissions

2. Visualization Issues
   - Problem: Graphs not displaying
   - Solution: Verify data contains valid responses
   - Check column names match expected format

3. Report Generation Errors
   - Problem: PDF/Word export fails
   - Solution: Ensure sufficient disk space
   - Verify write permissions in output directory

## Data Flow
The application processes educational assessment data through a structured pipeline from file upload to visualization and reporting.

```ascii
[Excel File] -> [Data Loading] -> [Processing/Filtering] -> [Analysis] -> [Visualization] -> [Report Generation]
```

Key component interactions:
1. Data loading through Streamlit's file uploader
2. Pandas DataFrame processing for data manipulation
3. Matplotlib/Seaborn for visualization generation
4. ReportLab/python-docx for report creation
5. Real-time filtering and recalculation of metrics
6. Dynamic UI updates based on user selections
7. Automated status calculation based on assessment criteria
8. Export functionality for generated reports