from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os

def generisi_pdf(ime, prezime, jmbg, adresa, opstina):
    # Generisanje imena fajla
    filename = f"formular_{ime}_{prezime}.pdf"
    
    # Kreiranje PDF dokumenta
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    story = []
    
    # Registruj DejaVu font koji je dodat u projekat
    try:
        if os.path.exists("DejaVuSans.ttf"):
            pdfmetrics.registerFont(TTFont('DejaVu', 'DejaVuSans.ttf'))
            font_name = 'DejaVu'
            print("DejaVu font je uspešno učitan!")
        else:
            font_name = 'Helvetica'
            print("DejaVu font nije pronađen, koristim Helvetica")
    except Exception as e:
        font_name = 'Helvetica'
        print(f"Greška pri učitavanju fonta: {e}")
    
    # Naslov
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=1,  # Center alignment
        fontName=font_name
    )
    title = Paragraph("PODRŠKA LISTI", title_style)
    story.append(title)
    story.append(Spacer(1, 20))
    
    # Podaci
    normal_style = ParagraphStyle(
        'Normal',
        parent=styles['Normal'],
        fontSize=12,
        spaceAfter=10,
        fontName=font_name
    )
    
    story.append(Paragraph(f"<b>Ime i prezime:</b> {ime} {prezime}", normal_style))
    story.append(Paragraph(f"<b>JMBG:</b> {jmbg}", normal_style))
    story.append(Paragraph(f"<b>Adresa:</b> {adresa}", normal_style))
    story.append(Paragraph(f"<b>Opština:</b> {opstina}", normal_style))
    story.append(Spacer(1, 20))
    
    # Mesto za potpis
    story.append(Paragraph("<b>POTPIS: _______________________</b>", normal_style))
    
    # Generisanje PDF-a
    doc.build(story)
    print(f"PDF je kreiran: {filename}")
    return filename

if __name__ == "__main__":
    # Example usage
    generisi_pdf("Ime", "Prezime", "1234567890123", "Adresa", "Opstina") 