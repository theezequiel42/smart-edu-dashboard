import io
import os
import tempfile
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib.utils import simpleSplit

def gerar_relatorio_pdf(aluno, medias_blocos, media_geral, radar_bytes):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margem_x = 2 * cm

    y = height - 2 * cm
    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(margem_x, y, f"Relatório de Triagem - AH/SD")
    y -= 1.2 * cm
    pdf.setFont("Helvetica", 12)
    pdf.drawString(margem_x, y, f"Nome do Aluno: {aluno}")
    y -= 0.8 * cm
    pdf.drawString(margem_x, y, f"Média Geral: {media_geral:.2f} / 4.00")
    y -= 1 * cm

    for bloco, media in medias_blocos.items():
        interpretacao = (
            "Alta" if media >= 3 else
            "Média" if media >= 1.6 else
            "Baixa"
        )
        recomendacao = (
            "Oferecer aprofundamento e desafios." if interpretacao == "Alta" else
            "Estimular com atividades direcionadas e reforço positivo." if interpretacao == "Média" else
            "Observar atentamente e oferecer suporte em áreas-chave."
        )

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margem_x, y, f"Bloco: {bloco}")
        y -= 0.6 * cm
        pdf.setFont("Helvetica", 10)

        pdf.drawString(margem_x + 0.4 * cm, y, f"Média: {media:.2f} - {interpretacao}")
        y -= 0.5 * cm
        pdf.drawString(margem_x + 0.4 * cm, y, f"Recomendação: {recomendacao}")
        y -= 0.8 * cm

        if y < 5 * cm:
            pdf.showPage()
            y = height - 2 * cm

    # Inserção do gráfico
    pdf.showPage()
    radar_bytes.seek(0)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
        tmp_img.write(radar_bytes.read())
        tmp_img_path = tmp_img.name

    try:
        pdf.drawImage(tmp_img_path, 4 * cm, height / 2 - 5 * cm, width=12 * cm, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margem_x, height / 2, f"[Erro ao inserir gráfico: {e}]")

    try:
        os.remove(tmp_img_path)
    except:
        pass

    pdf.save()
    buf.seek(0)
    return buf


def gerar_relatorio_completo_unificado(aluno, perfil, df_completo, medias_blocos, media_geral, radar_bytes):
    buf = io.BytesIO()
    pdf = canvas.Canvas(buf, pagesize=A4)
    width, height = A4
    margem_x = 2 * cm
    largura_util = width - 2 * margem_x
    y = height - 2 * cm

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(margem_x, y, f"Relatório Completo - AH/SD")
    y -= 1.2 * cm
    pdf.setFont("Helvetica", 12)
    pdf.drawString(margem_x, y, f"Nome do Aluno: {aluno}")
    y -= 0.8 * cm
    pdf.drawString(margem_x, y, f"Perfil: {perfil}")
    y -= 1 * cm
    pdf.drawString(margem_x, y, f"Média Geral: {media_geral:.2f} / 4.00")
    y -= 1.2 * cm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem_x, y, "📌 Interpretação por Bloco e Recomendações:")
    y -= 0.8 * cm
    pdf.setFont("Helvetica", 10)

    for bloco, media in medias_blocos.items():
        interpretacao = (
            "Alta" if media >= 3 else
            "Média" if media >= 1.6 else
            "Baixa"
        )
        recomendacao = (
            "Oferecer aprofundamento e desafios." if interpretacao == "Alta" else
            "Estimular com atividades direcionadas e reforço positivo." if interpretacao == "Média" else
            "Observar atentamente e oferecer suporte em áreas-chave."
        )

        linhas = simpleSplit(f"Bloco: {bloco} | Média: {media:.2f} – {interpretacao}", "Helvetica", 10, largura_util)
        for linha in linhas:
            pdf.drawString(margem_x, y, linha)
            y -= 0.4 * cm

        linhas_rec = simpleSplit(f"Recomendação: {recomendacao}", "Helvetica", 10, largura_util)
        for linha in linhas_rec:
            pdf.drawString(margem_x + 0.4 * cm, y, linha)
            y -= 0.4 * cm

        y -= 0.4 * cm
        if y < 4 * cm:
            pdf.showPage()
            y = height - 2 * cm

    # Inserção do gráfico
    pdf.showPage()
    y = height - 2 * cm
    radar_bytes.seek(0)
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_img:
        tmp_img.write(radar_bytes.read())
        tmp_img_path = tmp_img.name

    try:
        pdf.drawImage(tmp_img_path, 4 * cm, height / 2 - 5 * cm, width=12 * cm, preserveAspectRatio=True, mask='auto')
    except Exception as e:
        pdf.setFont("Helvetica", 10)
        pdf.drawString(margem_x, height / 2, f"[Erro ao inserir gráfico: {e}]")

    try:
        os.remove(tmp_img_path)
    except:
        pass

    pdf.showPage()
    y = height - 2 * cm

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(margem_x, y, "📋 Todas as Respostas:")
    y -= 0.8 * cm
    pdf.setFont("Helvetica", 10)

    for bloco in df_completo["Bloco"].unique():
        bloco_df = df_completo[df_completo["Bloco"] == bloco]

        pdf.setFont("Helvetica-Bold", 11)
        pdf.drawString(margem_x, y, f"📚 Bloco: {bloco}")
        y -= 0.6 * cm
        pdf.setFont("Helvetica", 10)

        for _, linha in bloco_df.iterrows():
            pergunta = str(linha["Pergunta"])
            resposta = str(linha["Resposta"])
            texto = f"- {pergunta}: {resposta}"

            linhas = simpleSplit(texto, "Helvetica", 10, largura_util)
            for linha_txt in linhas:
                pdf.drawString(margem_x + 0.4 * cm, y, linha_txt)
                y -= 0.4 * cm
                if y < 3 * cm:
                    pdf.showPage()
                    y = height - 2 * cm
                    pdf.setFont("Helvetica", 10)

        y -= 0.6 * cm
        if y < 3 * cm:
            pdf.showPage()
            y = height - 2 * cm
            pdf.setFont("Helvetica", 10)

    pdf.save()
    buf.seek(0)
    return buf
