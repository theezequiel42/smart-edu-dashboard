# Smart Edu Dashboard: Uma plataforma abrangente de análise de dados educacionais

O Smart Edu Dashboard é uma plataforma integrada de análise educacional que simplifica a análise de dados, o gerenciamento de avaliações e o processamento de documentos para instituições educacionais. A plataforma combina vários módulos especializados para fornecer aos educadores ferramentas poderosas para avaliação de alunos, rastreamento de desenvolvimento e tarefas administrativas.

O painel oferece seis modos operacionais distintos:
- Modo SME para análise de dados de pesquisa e geração de relatórios
- Modo CMAE para processamento de avaliações de desenvolvimento infantil usando o Inventário Portage Operacionalizado (IPO)
- Modo Converter para lidar com conversões de formato de documento
- Modo Portage Form para avaliações interativas de desenvolvimento infantil
- Modo Motor Development para rastreamento de habilidades motoras de alunos
- Modo AI para análise de dados educacionais e respostas automatizadas (em desenvolvimento)

## Estrutura do Repositório
```
.
├── main.py                         # Ponto de entrada do aplicativo e interface de seleção de modo
├── sme_mode.py                     # Módulo de análise e visualização de dados de pesquisa
├── cmae_mode.py                    # Módulo de processamento de avaliação do desenvolvimento infantil
├── converter_mode.py               # Utilitários de conversão de formato de arquivo
├── desenvolvimento_motor_mode.py   # Módulo de rastreamento do desenvolvimento motor
├── formulario_portage.py           # Implementação do formulário de avaliação do Portage
├── ia_mode.py                      # Módulo de análise educacional com tecnologia de IA
├── perguntas_portage.py            # Banco de dados de perguntas de avaliação do Portage
├── iniciar_dashboard.bat           # Arquivo em lote do Windows para iniciar o aplicativo
└── requirements.txt                # Dependências de pacote Python
```

## Uso Instruções
### Pré-requisitos
- Python 3.x
- Navegador da Web
- Conexão com a Internet para instalação do pacote

Pacotes Python necessários:
```
streamlit
pandas
matplotlib
seaborn
python-docx
openpyxl
reportlab
pdf2docx
PyPDF2
Pillow
PyMuPDF
```

### Instalação
1. Clone o repositório:
```bash
git clone https://github.com/theezequiel42/smart-edu-dashboard
cd smart-edu-dashboard
```

2. Instale os pacotes necessários:
```bash
pip install -r requirements.txt
```

### Início rápido
1. Inicie o aplicativo:
- No Windows: clique duas vezes em `iniciar_dashboard.bat`
- No Linux/MacOS:
```bash
streamlit run main.py
```

2. Selecione um modo operacional na interface do painel:
- Clique no ícone do modo desejado
- Siga as instruções específicas do modo

### Exemplos mais detalhados
1. Modo SME:
```python
# Carregar dados da pesquisa
# Selecionar opções de visualização
# Gerar e baixar relatórios
```

2. Modo CMAE:
```python
# Inserir dados de avaliação do aluno
# Processar avaliações de IPO
# Gerar relatórios em PDF
```

3. Modo Conversor:
```python
# Dividir arquivos PDF
# Converter imagens em PDF
# Converter PDF em Word
```

### Solução de problemas
Problemas comuns:
1. O aplicativo falha ao iniciar:
- Verifique a instalação do Python
- Verifique se todas as dependências estão instaladas
- Mensagem de erro: "Nenhum módulo encontrado"
Solução: Execute `pip install -r requirements.txt`

2. Erros de conversão de arquivo:
- Certifique-se de que as permissões do arquivo estejam corretas
- Verifique o formato do arquivo de entrada
- Mensagem de erro: "Permissão negada"
Solução: Execute com as permissões apropriadas

3. A geração do relatório falha:
- Verifique o espaço em disco disponível
- Verifique a gravação permissões no diretório de saída
- Mensagem de erro: "Não foi possível criar o arquivo"
Solução: Libere espaço em disco ou ajuste as permissões

## Fluxo de dados
O aplicativo processa dados educacionais por meio de módulos especializados, transformando a entrada bruta em insights e relatórios acionáveis.

```ascii
[Entrada]      ->  [Processamento] -> [Saída]
|                       |                |
v                       v                v
Relatórios           análise         arquivos
Visualizações       conversão          dados
Formulários         Avaliação      PDF/Word Docs
```

Interações de componentes:
1. O usuário insere dados por meio da interface da web
2. Os dados são processados ​​por módulos de modo específicos
3. Os resultados são armazenados na memória durante a sessão
4. As visualizações são geradas usando matplotlib/seaborn
5. Os relatórios são criados usando docx/reportlab
6. Os arquivos são convertidos usando bibliotecas especializadas
7. A saída é entregue por meio da interface streamlit




# Smart Edu Dashboard: A Comprehensive Educational Data Analysis Platform

Smart Edu Dashboard is an integrated educational analytics platform that streamlines data analysis, assessment management, and document processing for educational institutions. The platform combines multiple specialized modules to provide educators with powerful tools for student evaluation, development tracking, and administrative tasks.

The dashboard offers six distinct operational modes:
- SME Mode for survey data analysis and report generation
- CMAE Mode for processing child development assessments using the Inventário Portage Operacionalizado (IPO)
- Converter Mode for handling document format conversions
- Portage Form Mode for interactive child development assessments
- Motor Development Mode for student motor skills tracking
- AI Mode for educational data analysis and automated responses (in development)

## Repository Structure
```
.
├── main.py                         # Application entry point and mode selection interface
├── sme_mode.py                     # Survey data analysis and visualization module
├── cmae_mode.py                    # Child development assessment processing module
├── converter_mode.py               # File format conversion utilities
├── desenvolvimento_motor_mode.py   # Motor development tracking module
├── formulario_portage.py           # Portage assessment form implementation
├── ia_mode.py                      # AI-powered educational analysis module
├── perguntas_portage.py            # Portage assessment question database
├── iniciar_dashboard.bat           # Windows batch file for launching the application
└── requirements.txt                # Python package dependencies
```

## Usage Instructions
### Prerequisites
- Python 3.x
- Web browser
- Internet connection for package installation

Required Python packages:
```
streamlit
pandas
matplotlib
seaborn
python-docx
openpyxl
reportlab
pdf2docx
PyPDF2
Pillow
PyMuPDF
```

### Installation
1. Clone the repository:
```bash
git clone https://github.com/theezequiel42/smart-edu-dashboard
cd smart-edu-dashboard
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

### Quick Start
1. Launch the application:
   - On Windows: Double-click `iniciar_dashboard.bat`
   - On Linux/MacOS:
   ```bash
   streamlit run main.py
   ```

2. Select an operational mode from the dashboard interface:
   - Click on the desired mode icon
   - Follow the mode-specific instructions

### More Detailed Examples
1. SME Mode:
```python
# Upload survey data
# Select visualization options
# Generate and download reports
```

2. CMAE Mode:
```python
# Input student assessment data
# Process IPO evaluations
# Generate PDF reports
```

3. Converter Mode:
```python
# Split PDF files
# Convert images to PDF
# Convert PDF to Word
```

### Troubleshooting
Common Issues:
1. Application fails to start:
   - Verify Python installation
   - Check if all dependencies are installed
   - Error message: "No module found"
   Solution: Run `pip install -r requirements.txt`

2. File conversion errors:
   - Ensure file permissions are correct
   - Verify input file format
   - Error message: "Permission denied"
   Solution: Run with appropriate permissions

3. Report generation fails:
   - Check available disk space
   - Verify write permissions in output directory
   - Error message: "Could not create file"
   Solution: Free up disk space or adjust permissions

## Data Flow
The application processes educational data through specialized modules, transforming raw input into actionable insights and reports.

```ascii
[Input] -> [Processing] -> [Output]
 |            |             |
 v            v             v
Files     Analysis      Reports
Data    Conversion     Visualizations
Forms   Assessment    PDF/Word Docs
```

Component Interactions:
1. User inputs data through web interface
2. Data is processed by specific mode modules
3. Results are stored in memory during session
4. Visualizations are generated using matplotlib/seaborn
5. Reports are created using docx/reportlab
6. Files are converted using specialized libraries
7. Output is delivered through streamlit interface