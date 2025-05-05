import streamlit as st

from sme_mode import run_sme_mode
from cmae_mode import run_cmae_mode
from converter_mode import run_converter_mode
from formulario_portage import run_formulario_portage
from desenvolvimento_motor_mode import run_desenvolvimento_motor_mode
from ia_mode import run_ia_mode
from ah_mode import run_ah_mode  # ✅ Novo modo AH/SD

def exibir_tela_inicial():
    # Estilo visual
    st.markdown(
        """
        <style>
        .modo-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 40px;
            margin-top: 30px;
        }
        .modo-item {
            display: flex;
            flex-direction: column;
            align-items: center;
            width: 220px;
        }
        .modo-item img {
            width: 180px;
            height: 180px;
            object-fit: cover;
            border: 5px solid #007BFF;
            border-radius: 20px;
            margin-bottom: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
        }
        .stButton>button {
            width: 220px;
            height: 50px;
            font-size: 18px;
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
    st.markdown("## Selecione o Modo de Visualização:")

    # Layout com logos + botões agrupados
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_sme.png")
        if st.button("📊 Modo SME - Avaliação de Cursos"):
            st.session_state["modo"] = "SME"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_cmae.png")
        if st.button("🎯 Modo CMAE - Avaliação Portage"):
            st.session_state["modo"] = "CMAE"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_converter.png")
        if st.button("📄 Conversor - Arquivos PDF"):
            st.session_state["modo"] = "CONVERSOR"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    col4, col5, col6 = st.columns(3)
    with col4:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_portage.png")
        if st.button("📝 Formulário Portage - Questionário"):
            st.session_state["modo"] = "PORTAGE"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col5:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_motor.png")
        if st.button("🧠 Desenvolvimento Motor - Em Desenvolvimento"):
            st.session_state["modo"] = "MOTOR"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    with col6:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_ia.png")
        if st.button("🤖 Modo IA - Em Breve"):
            st.session_state["modo"] = "IA"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Nova linha para o modo AH/SD
    col7, _, _ = st.columns(3)
    with col7:
        st.markdown('<div class="modo-item">', unsafe_allow_html=True)
        st.image("images/logo_ahsd.png")  # 📌 Adicione esta imagem na pasta images
        if st.button("🧠 Modo AH/SD – Triagem de Altas Habilidades"):
            st.session_state["modo"] = "AH"
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
        elif st.session_state["modo"] == "PORTAGE":
            run_formulario_portage()
        elif st.session_state["modo"] == "MOTOR":
            run_desenvolvimento_motor_mode()
        elif st.session_state["modo"] == "IA":
            run_ia_mode()
        elif st.session_state["modo"] == "AH":
            run_ah_mode()  # ✅ Executa o modo de análise AH/SD

exibir_tela_inicial()
