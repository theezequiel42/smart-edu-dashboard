import os
import platform
import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image
import fitz  # PyMuPDF
import tempfile
from pdf2docx import Converter
import ezdxf

def run_converter_mode():
    st.title("📄 Conversor de Arquivos PDF, Word e Imagem")

    opcao = st.sidebar.selectbox("Escolha uma funcionalidade:", [
        "Dividir PDF",
        "Imagens para PDF",
        "PDF para Imagens",
        "PDF para Word",
        "Mesclar PDF",
        "PDF para DXF (AutoCAD)"
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
                    
    elif opcao == "Mesclar PDF":
        st.header("📚 Mesclar Vários PDFs em um Único Arquivo")
        arquivos_pdf = st.file_uploader("Selecione dois ou mais arquivos PDF:", type=["pdf"], accept_multiple_files=True)
        if arquivos_pdf and len(arquivos_pdf) >= 2:
            if st.button("Mesclar PDFs"):
                with st.spinner("🔄 Mesclando arquivos PDF..."):
                    try:
                        writer = PdfWriter()

                        for arquivo in arquivos_pdf:
                            reader = PdfReader(arquivo)
                            for pagina in reader.pages:
                                writer.add_page(pagina)

                        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                        with open(output_path.name, "wb") as f:
                            writer.write(f)

                        st.success("✅ PDFs mesclados com sucesso!")
                        st.download_button(
                            "📥 Baixar PDF Mesclado",
                            data=open(output_path.name, "rb"),
                            file_name="PDF_Mesclado.pdf",
                            mime="application/pdf"
                        )
                    except Exception as e:
                        st.error(f"❌ Erro ao mesclar PDFs: {e}")
            else:
                st.info("📌 Selecione pelo menos dois arquivos PDF para mesclar.")
    
    elif opcao == "PDF para DXF (AutoCAD)":
        st.header("📐 PDF para DXF (AutoCAD)")

        aba = st.radio("Escolha o tipo de conversão:", [
            "Converter PDF em imagem vetorial para DXF",
            "Gerar Tabela de Snellen vetorial (.dxf)"
        ])

        if aba == "Converter PDF em imagem vetorial para DXF":
            pdf_file = st.file_uploader("📂 Selecione o arquivo PDF:", type=["pdf"])
            if pdf_file:
                if st.button("Converter para DXF (com imagem)"):
                    with st.spinner("🔄 Convertendo PDF para imagem vetorial e inserindo no DXF..."):
                        try:
                            import ezdxf
                            import fitz
                            import os
                            import tempfile

                            # Salvar PDF temporário
                            temp_pdf_path = os.path.join(tempfile.gettempdir(), f"{os.urandom(4).hex()}.pdf")
                            with open(temp_pdf_path, "wb") as f:
                                f.write(pdf_file.read())

                            # Extrair imagem da primeira página
                            doc = fitz.open(temp_pdf_path)
                            page = doc.load_page(0)
                            pix = page.get_pixmap(dpi=300)
                            img_path = os.path.join(tempfile.gettempdir(), f"snellen_{os.urandom(4).hex()}.png")
                            pix.save(img_path)

                            # Criar DXF com imagem
                            dxf_doc = ezdxf.new()
                            msp = dxf_doc.modelspace()
                            msp.add_image(img_path, insert=(0, 0), size_in_units=(420, 297))  # A3

                            output_dxf_path = os.path.join(tempfile.gettempdir(), f"saida_{os.urandom(4).hex()}.dxf")
                            dxf_doc.saveas(output_dxf_path)

                            st.success("✅ Conversão concluída com sucesso!")
                            with open(output_dxf_path, "rb") as f:
                                st.download_button("📥 Baixar DXF com imagem", data=f, file_name="pdf_com_imagem.dxf", mime="application/octet-stream")

                        except Exception as e:
                            st.error(f"❌ Erro ao converter para DXF: {e}")

        elif aba == "Gerar Tabela de Snellen vetorial (.dxf)":
            st.subheader("🔤 Gerador de Tabela Vetorial da Snellen")

            margem_esquerda = st.number_input("📏 Margem esquerda (mm)", value=10)
            margem_superior = st.number_input("📐 Margem superior (mm)", value=30)
            espaco_linhas = st.number_input("🔢 Espaçamento entre linhas (mm)", value=10)
            fonte = st.text_input("🖋️ Nome da fonte (padrão Arial)", value="Arial")

            if st.button("Gerar Tabela Vetorial"):
                with st.spinner("🛠️ Gerando tabela vetorial da Snellen..."):
                    try:
                        import ezdxf

                        tamanhos = [60, 45, 30, 24, 18, 12, 9, 6, 4, 3]
                        letras = [
                            "E",
                            "F P",
                            "T O Z",
                            "L P E D",
                            "P E C F D",
                            "E D F C Z P",
                            "F E L O P Z D",
                            "D E F P O T E C",
                            "L E F O D P C T",
                            "F D P L T C E O"
                        ]

                        largura_papel = 420
                        altura_papel = 297

                        doc = ezdxf.new()
                        msp = doc.modelspace()

                        y = altura_papel - margem_superior
                        for tamanho, linha in zip(tamanhos, letras):
                            largura_texto = tamanho * 0.6 * len(linha.replace(" ", ""))
                            x = (largura_papel - largura_texto) / 2

                            texto = msp.add_text(
                                linha,
                                dxfattribs={
                                    "height": tamanho,
                                    "style": "STANDARD"
                                }
                            )
                            if fonte:
                                texto.dxf.style = fonte
                            texto.set_pos((x, y), align="LEFT")
                            y -= tamanho + espaco_linhas

                        output_path = os.path.join(tempfile.gettempdir(), f"snellen_centralizado_{os.urandom(4).hex()}.dxf")
                        doc.saveas(output_path)

                        st.success("✅ Tabela vetorial gerada com sucesso!")
                        with open(output_path, "rb") as f:
                            st.download_button("📥 Baixar Tabela Vetorial", data=f, file_name="tabela_snellen_vetorial.dxf", mime="application/octet-stream")

                    except Exception as e:
                        st.error(f"❌ Erro ao gerar tabela vetorial: {e}")
