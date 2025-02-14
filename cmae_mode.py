import streamlit as st

def run_cmae_mode():
    st.title("🎯 Modo CMAE - Centro de Atendimento Especializado")

    st.write("Este modo será desenvolvido para a visualização de dados da educação especial.")

  # Estilização da interface
    st.markdown("""
        <style>
            .main {
                background-color: #f0f2f6;
            }
            h1 {
                color: #2c3e50;
                text-align: center;
            }
            .sidebar-button {
                background-color: #2E7D32 !important;
                color: white !important;
                font-size: 16px !important;
                font-weight: bold !important;
                text-align: center;
                width: 100%;
                padding: 10px;
                border-radius: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Dicionário de cores fixas para opções de resposta
    cores_fixas = {
        "Concordo plenamente": "#2E7D32",  # Verde escuro
        "Concordo": "#66BB6A",  # Verde claro
        "Não sei": "#FFEB3B",  # Amarelo
        "Discordo": "#FF7043",  # Laranja
        "Discordo plenamente": "#D32F2F",  # Vermelho
        "Muito Satisfeito(a)": "#2E7D32",
        "Satisfeito(a)": "#66BB6A",
        "Regular": "#FFEB3B",
        "Insatisfeito(a)": "#FF7043",
        "Muito motivado(a)": "#2E7D32",
        "Motivado(a)": "#66BB6A",
        "Ansioso(a) ou inseguro(a)": "#FF7043",
        "Sem expectativas claras": "#D32F2F",
        "Interesse no tema do curso": "#1E88E5",  # Azul forte
        "Interesse nas horas para ampliação / Foi o que consegui me inscrever": "#42A5F5",  # Azul médio
        "Não tinha muito interesse mas dei uma oportunidade ao tema": "#90CAF9"  # Azul claro
    }

    # Layout inicial
    st.info("Em breve, funcionalidades específicas para o CMAE serão implementadas.")
