from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
import os
import tempfile
from datetime import datetime

def generisi_pdf(ime, prezime, jmbg, adresa, opstina, ime_roditelja, datum_rodjenja, mesto_rodjenja, 
                adresa_boravista, nacionalna_manjina, ime_elektora, prezime_elektora, jmbg_elektora,
                adresa_elektora, opstina_elektora, adresa_boravista_elektora, datum_potpisa, mesto_potpisa,
                broj_telefona, email):
    # Generisanje imena fajla - ukloni specijalne karaktere
    safe_ime = "".join(c for c in ime if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_prezime = "".join(c for c in prezime if c.isalnum() or c in (' ', '-', '_')).rstrip()
    filename = f"obrazac_podrska_{safe_ime}_{safe_prezime}.pdf"
    
    # Kreiranje privremenog direktorijuma za PDF fajlove
    temp_dir = os.path.join(os.getcwd(), 'temp_pdfs')
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    # Puna putanja do fajla
    filepath = os.path.join(temp_dir, filename)
    
    # Kreiranje PDF dokumenta
    doc = SimpleDocTemplate(filepath, pagesize=A4, topMargin=2*cm, bottomMargin=2*cm, leftMargin=2*cm, rightMargin=2*cm)
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
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Center alignment
        fontName=font_name,
        fontName='Helvetica-Bold'
    )
    
    # Naslov dokumenta
    story.append(Paragraph("ПРИЛОЗИ", title_style))
    story.append(Paragraph("Образац 1.", title_style))
    story.append(Spacer(1, 20))
    
    # Glavni naslov
    main_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=30,
        alignment=1,
        fontName='Helvetica-Bold'
    )
    story.append(Paragraph("ОБРАЗАЦ ЗА ПРИКУПЉАЊЕ ПОТПИСА БИРАЧА КОЈИ ПОДРЖАВАЈУ ЕЛЕКТОРЕ", main_title))
    story.append(Spacer(1, 20))
    
    # Podaci o biraču
    data_style = ParagraphStyle(
        'DataStyle',
        parent=styles['Normal'],
        fontSize=11,
        spaceAfter=8,
        fontName=font_name,
        leading=14
    )
    
    # Birač podaci
    story.append(Paragraph("Ја, доле потписани/а", data_style))
    story.append(Paragraph(f"Име и презиме бирача: <b>{ime} {prezime}</b>", data_style))
    story.append(Paragraph(f"Име једног родитеља бирача: <b>{ime_roditelja or '________________'}</b>", data_style))
    story.append(Paragraph(f"Бирачев јединствени матични број грађана: <b>{jmbg}</b>", data_style))
    story.append(Paragraph(f"Датум и место рођења бирача: <b>{datum_rodjenja or '________________'} {mesto_rodjenja or '________________'}</b>", data_style))
    story.append(Paragraph(f"Место и адреса пребивалишта бирача: <b>{adresa}</b>", data_style))
    
    if adresa_boravista:
        story.append(Paragraph(f"Место и адреса боравишта бирача за интерно расељене: <b>{adresa_boravista}</b>", data_style))
    else:
        story.append(Paragraph("Место и адреса боравишта бирача за интерно расељене: ________________", data_style))
    
    story.append(Paragraph(f"Општина/град: <b>{opstina}</b>", data_style))
    
    if broj_telefona:
        story.append(Paragraph(f"Телефон: <b>{broj_telefona}</b> (није обавезно али је пожељно уписати)", data_style))
    else:
        story.append(Paragraph("Телефон: ________________ (није обавезно али је пожељно уписати)", data_style))
    
    story.append(Spacer(1, 15))
    
    # Nacionalna manjina
    story.append(Paragraph(f"Изјављујем да сам припадник националне мањине <b>{nacionalna_manjina or '________________'}</b>", data_style))
    story.append(Paragraph(f"и предлажем да на електорској скупштини националне мањине учествује <b>{nacionalna_manjina or '________________'}</b>", data_style))
    story.append(Spacer(1, 15))
    
    # Elektor podaci
    story.append(Paragraph("Име и презиме електора:", data_style))
    story.append(Paragraph(f"<b>{ime_elektora or '________________'} {prezime_elektora or '________________'}</b>", data_style))
    story.append(Paragraph(f"Електоров јединствени матични број грађана: <b>{jmbg_elektora or '________________'}</b>", data_style))
    story.append(Paragraph(f"Место и адреса пребивалишта електора: <b>{adresa_elektora or '________________'}</b>", data_style))
    
    if adresa_boravista_elektora:
        story.append(Paragraph(f"Место и адреса боравишта електора за интерно расељене: <b>{adresa_boravista_elektora}</b>", data_style))
    else:
        story.append(Paragraph("Место и адреса боравишта електора за интерно расељене: ________________", data_style))
    
    story.append(Paragraph(f"Општина/град: <b>{opstina_elektora or '________________'}</b>", data_style))
    story.append(Spacer(1, 20))
    
    # GDPR izjava
    story.append(Paragraph("Истовремено са потписивањем овог обрасца обавештен сам о обради података о личности и пристајем на обраду података у складу са законом.", data_style))
    story.append(Spacer(1, 15))
    
    # Datum i mesto potpisa
    story.append(Paragraph(f"У <b>{mesto_potpisa or '________________'}</b>, дана <b>{datum_potpisa or '________________'}</b>", data_style))
    story.append(Paragraph("(потпис)", data_style))
    story.append(Spacer(1, 20))
    
    # Potvrda
    story.append(Paragraph("Потврђује се да је ову изјаву својеручно потписао.", data_style))
    story.append(Paragraph(f"(име и презиме): <b>{ime} {prezime}</b>", data_style))
    story.append(Paragraph("Идентитет припадника националне мањине утврђен је на основу увида у личне исправе.", data_style))
    story.append(Spacer(1, 15))
    
    # Napomena
    napomena_style = ParagraphStyle(
        'NapomenaStyle',
        parent=styles['Normal'],
        fontSize=9,
        spaceAfter=10,
        fontName=font_name,
        leading=12
    )
    
    story.append(Paragraph("У складу са чланом 101. став 2. Закона о националним саветима националних мањина („Службени гласник РС", бр. 72/09, 20/14 – УС, 55/14 и 47/18) накнада за оверу се не наплаћује.", napomena_style))
    story.append(Spacer(1, 15))
    
    # Mesto za overu
    story.append(Paragraph("Ов. бр. ________________", data_style))
    story.append(Paragraph("У ________________ часова.", data_style))
    story.append(Paragraph("(место) (датум)", data_style))
    story.append(Paragraph("Надлежни орган за оверу", data_style))
    story.append(Paragraph("(место)", data_style))
    story.append(Paragraph("(потпис)", data_style))
    story.append(Paragraph("(име и презиме)", data_style))
    story.append(Spacer(1, 20))
    
    # Napomena na kraju
    story.append(Paragraph("НАПОМЕНА: Бирачи који подржавају електоре и подржани кандидати за електоре у поступку за спровођење изборних радњи које су у вези са овим обрасцем могу користити и моделе одговарајућих аката (Члан 102. став 2. Закона о националним саветима националних мањина („Службени гласник РС", бр. 72/09, 20/14 – УС, 55/14 и 47/18)) постављене на званичној интернет страни Министарства државне управе и локалне самоуправе.", napomena_style))
    
    # Generisanje PDF-a
    print("Generisanje PDF-a...")
    doc.build(story)
    print(f"PDF je uspešno kreiran: {filepath}")
    return filepath

if __name__ == "__main__":
    # Example usage
    generisi_pdf("Име", "Презиме", "1234567890123", "Адреса", "Општина", "Име родитеља", "1990-01-01", "Београд", 
                "", "Словачка", "Име електора", "Презиме електора", "1234567890124", "Адреса електора", 
                "Општина електора", "", "2024-01-01", "Београд", "0123456789", "email@example.com") 