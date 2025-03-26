import streamlit as st

from sme_mode import run_sme_mode
from cmae_mode import run_cmae_mode
from converter_mode import run_converter_mode  # Novo modo

def exibir_tela_inicial():
    # Estilo visual
    st.markdown(
        """
        <style>
        .logo-container {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 50px;
            margin-top: 50px;
            flex-wrap: wrap;
        }
        .logo-container img {
            height: 200px;
            width: 200px;
            object-fit: cover;
            border: 5px solid #007BFF;
            border-radius: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: transform 0.3s, box-shadow 0.3s;
        }
        .logo-container img:hover {
            transform: scale(1.1);
            box-shadow: 0 6px 8px rgba(0, 0, 0, 0.5);
        }
        .button-container {
            display: flex;
            justify-content: center;
            gap: 50px;
            flex-wrap: wrap;
            margin-top: 20px;
        }
        .stButton>button {
            width: 220px;
            height: 60px;
            font-size: 20px;
            border-radius: 15px;
            background-color: #007BFF;
            color: white;
            border: none;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            transition: background-color 0.3s, transform 0.3s;
        }
        .stButton>button:hover {
            background-color: #0056b3;
            transform: scale(1.05);
        }
        </style>
        """,
        unsafe_allow_html=True
    )

    st.title("Smart Edu Dashboard")

    # Logos
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        st.image("images/logo_sme.png", use_container_width=True)
    with col2:
        st.image("images/logo_cmae.png", use_container_width=True)
    with col3:
        st.image("images/logo_converter.png", use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

    # Botões
    st.markdown('<div class="button-container">', unsafe_allow_html=True)
    col4, col5, col6 = st.columns([1, 1, 1])

    with col4:
        if st.button("📊 Acessar Modo SME"):
            st.session_state["modo"] = "SME"
            st.rerun()

    with col5:
        if st.button("🎯 Acessar Modo CMAE"):
            st.session_state["modo"] = "CMAE"
            st.rerun()

    with col6:
        if st.button("📄 Conversor de Arquivos"):
            st.session_state["modo"] = "CONVERSOR"
            st.rerun()

    st.markdown('</div>', unsafe_allow_html=True)

    # Executa o modo escolhido
    if "modo" in st.session_state:
        st.empty()  # limpa a tela inicial
        if st.session_state["modo"] == "SME":
            run_sme_mode()
        elif st.session_state["modo"] == "CMAE":
            run_cmae_mode()
        elif st.session_state["modo"] == "CONVERSOR":
            run_converter_mode()

exibir_tela_inicial()