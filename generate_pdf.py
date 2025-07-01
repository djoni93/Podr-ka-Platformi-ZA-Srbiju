from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
import tempfile

def generisi_pdf(ime, prezime, jmbg, adresa, opstina):
    try:
        # Generisanje imena fajla - ukloni specijalne karaktere
        safe_ime = "".join(c for c in ime if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_prezime = "".join(c for c in prezime if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"formular_{safe_ime}_{safe_prezime}.pdf"
        
        # Kreiranje privremenog direktorijuma za PDF fajlove
        temp_dir = os.path.join(os.getcwd(), 'temp_pdfs')
        print(f"Kreiranje direktorijuma: {temp_dir}")
        
        if not os.path.exists(temp_dir):
            os.makedirs(temp_dir)
            print(f"Direktorijum kreiran: {temp_dir}")
        else:
            print(f"Direktorijum već postoji: {temp_dir}")
        
        # Puna putanja do fajla
        filepath = os.path.join(temp_dir, filename)
        print(f"Puna putanja fajla: {filepath}")
        
        # Kreiranje PDF dokumenta
        doc = SimpleDocTemplate(filepath, pagesize=A4)
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
        print("Generisanje PDF-a...")
        doc.build(story)
        print(f"PDF je uspešno kreiran: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"Greška pri generisanju PDF-a: {str(e)}")
        raise e

if __name__ == "__main__":
    # Example usage
    generisi_pdf("Ime", "Prezime", "1234567890123", "Adresa", "Opstina") 