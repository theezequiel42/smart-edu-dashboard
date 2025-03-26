import os
import platform
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
import tempfile
from pdf2docx import Converter

def run_converter_mode():
    st.title("📄 Conversor de Arquivos PDF, Word e Imagem")

    opcao = st.sidebar.selectbox("Escolha uma funcionalidade:", [
        "Dividir PDF",
        "Imagens para PDF",
        "PDF para Imagens",
        "PDF para Word"
    ])

    if opcao == "Dividir PDF":
        st.header("✂️ Dividir PDF")
        pdf_file = st.file_uploader("Selecione o arquivo PDF:", type=["pdf"])
        if pdf_file:
            selecao = st.text_input("Digite as páginas (ex: 1,2,4-6):")
            if st.button("Dividir PDF"):
                with st.spinner("🔄 Dividindo PDF..."):
                    try:
                        input_pdf = PdfReader(pdf_file)
                        total_paginas = len(input_pdf.pages)

                        paginas_selecionadas = []
                        for parte in selecao.split(","):
                            if "-" in parte:
                                inicio, fim = map(int, parte.split("-"))
                                paginas_selecionadas.extend(range(inicio - 1, fim))
                            else:
                                paginas_selecionadas.append(int(parte) - 1)

                        paginas_selecionadas = sorted(set(paginas_selecionadas))
                        if any(p < 0 or p >= total_paginas for p in paginas_selecionadas):
                            st.error("❌ Seleção de páginas fora do intervalo válido.")
                            return

                        writer = PdfWriter()
                        for page_num in paginas_selecionadas:
                            writer.add_page(input_pdf.pages[page_num])

                        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        with open(output_path.name, "wb") as output_pdf:
                            writer.write(output_pdf)

                        st.success("✅ PDF gerado com sucesso!")
                        st.download_button("📥 Baixar PDF Selecionado", data=open(output_path.name, "rb"), file_name="PDF_Selecionado.pdf")

                    except Exception as e:
                        st.error(f"❌ Erro ao dividir PDF: {e}")

    elif opcao == "Imagens para PDF":
        st.header("🖼️ Converter Imagens em PDF")
        imagem_files = st.file_uploader("Selecione as imagens:", type=["png", "jpg", "jpeg"], accept_multiple_files=True)
        if imagem_files:
            if st.button("Converter para PDF"):
                with st.spinner("🔄 Convertendo imagens para PDF..."):
                    try:
                        pil_imagens = [Image.open(img).convert('RGB') for img in imagem_files]

                        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        pil_imagens[0].save(output_path.name, save_all=True, append_images=pil_imagens[1:])

                        st.success("✅ PDF criado com sucesso!")
                        st.download_button("📥 Baixar PDF", data=open(output_path.name, "rb"), file_name="imagens_convertidas.pdf")

                    except Exception as e:
                        st.error(f"❌ Erro ao converter imagens: {e}")

    elif opcao == "PDF para Imagens":
        st.header("📑 Converter PDF em Imagens")
        pdf_input = st.file_uploader("Selecione o arquivo PDF:", type=["pdf"])
        if pdf_input:
            if st.button("Converter para Imagens"):
                with st.spinner("🔄 Convertendo PDF para imagens..."):
                    try:
                        pdf_documento = fitz.open(stream=pdf_input.read(), filetype="pdf")

                        for i, pagina in enumerate(pdf_documento):
                            imagem = pagina.get_pixmap()
                            temp_path = os.path.join(tempfile.gettempdir(), f"pagina_{i+1}_{os.urandom(4).hex()}.png")
                            imagem.save(temp_path)

                            st.image(temp_path, caption=f"Página {i+1}", use_container_width=True)
                            with open(temp_path, "rb") as f:
                                st.download_button(
                                    f"📥 Baixar Página {i+1}",
                                    data=f,
                                    file_name=f"pagina_{i+1}.png",
                                    mime="image/png"
                                )

                        st.success("✅ Conversão completa!")

                    except Exception as e:
                        st.error(f"❌ Erro ao converter PDF para imagens: {e}")

    elif opcao == "PDF para Word":
        st.header("📝 Converter PDF em Word")
        pdf_file = st.file_uploader("Selecione o PDF:", type=["pdf"])
        if pdf_file and st.button("Converter para Word"):
            with st.spinner("🔄 Convertendo PDF para Word..."):
                try:
                    pdf_path = os.path.join(tempfile.gettempdir(), f"temp_pdf_{os.urandom(4).hex()}.pdf")
                    with open(pdf_path, "wb") as f:
                        f.write(pdf_file.read())

                    output_path = pdf_path.replace(".pdf", ".docx")
                    cv = Converter(pdf_path)
                    cv.convert(output_path, start=0, end=None)
                    cv.close()

                    st.success("✅ PDF convertido para Word com sucesso!")
                    with open(output_path, "rb") as f:
                        st.download_button("📥 Baixar Word (.docx)", data=f, file_name="convertido.docx")

                except Exception as e:
                    st.error(f"❌ Erro ao converter PDF para Word: {e}")
