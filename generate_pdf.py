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
    
    # Naslov - koristi font koji podržava ćirilicu
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        spaceAfter=20,
        alignment=1,  # Center alignment
        fontName=font_name
    )
    
    # Naslov dokumenta - koristi latinične karaktere za naslove
    story.append(Paragraph("PRILOZI", title_style))
    story.append(Paragraph("Obrazac 1.", title_style))
    story.append(Spacer(1, 20))
    
    # Glavni naslov
    main_title = ParagraphStyle(
        'MainTitle',
        parent=styles['Heading1'],
        fontSize=14,
        spaceAfter=30,
        alignment=1,
        fontName=font_name
    )
    story.append(Paragraph("OBRAZAC ZA PRIKUPLJANJE POTPISA BIRACA KOJI PODRZAVAJU ELEKTORE", main_title))
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
    
    # Birač podaci - koristi ćirilične karaktere za sadržaj
    story.append(Paragraph("Ja, dole potpisan/a", data_style))
    story.append(Paragraph(f"Ime i prezime biraca: <b>{ime} {prezime}</b>", data_style))
    story.append(Paragraph(f"Ime jednog roditelja biraca: <b>{ime_roditelja or '________________'}</b>", data_style))
    story.append(Paragraph(f"Biracev jedinstveni maticni broj gradjana: <b>{jmbg}</b>", data_style))
    story.append(Paragraph(f"Datum i mesto rodjenja biraca: <b>{datum_rodjenja or '________________'} {mesto_rodjenja or '________________'}</b>", data_style))
    story.append(Paragraph(f"Mesto i adresa prebivalista biraca: <b>{adresa}</b>", data_style))
    
    if adresa_boravista:
        story.append(Paragraph(f"Mesto i adresa boravista biraca za interno raseljene: <b>{adresa_boravista}</b>", data_style))
    else:
        story.append(Paragraph("Mesto i adresa boravista biraca za interno raseljene: ________________", data_style))
    
    story.append(Paragraph(f"Opstina/grad: <b>{opstina}</b>", data_style))
    
    if broj_telefona:
        story.append(Paragraph(f"Telefon: <b>{broj_telefona}</b> (nije obavezno ali je pozeljno upisati)", data_style))
    else:
        story.append(Paragraph("Telefon: ________________ (nije obavezno ali je pozeljno upisati)", data_style))
    
    story.append(Spacer(1, 15))
    
    # Nacionalna manjina
    story.append(Paragraph(f"Izjavljujem da sam pripadnik nacionalne manjine <b>{nacionalna_manjina or '________________'}</b>", data_style))
    story.append(Paragraph(f"i predlazem da na elektorskoj skupstini nacionalne manjine ucestvuje <b>{nacionalna_manjina or '________________'}</b>", data_style))
    story.append(Spacer(1, 15))
    
    # Elektor podaci
    story.append(Paragraph("Ime i prezime elektora:", data_style))
    story.append(Paragraph(f"<b>{ime_elektora or '________________'} {prezime_elektora or '________________'}</b>", data_style))
    story.append(Paragraph(f"Elektorov jedinstveni maticni broj gradjana: <b>{jmbg_elektora or '________________'}</b>", data_style))
    story.append(Paragraph(f"Mesto i adresa prebivalista elektora: <b>{adresa_elektora or '________________'}</b>", data_style))
    
    if adresa_boravista_elektora:
        story.append(Paragraph(f"Mesto i adresa boravista elektora za interno raseljene: <b>{adresa_boravista_elektora}</b>", data_style))
    else:
        story.append(Paragraph("Mesto i adresa boravista elektora za interno raseljene: ________________", data_style))
    
    story.append(Paragraph(f"Opstina/grad: <b>{opstina_elektora or '________________'}</b>", data_style))
    story.append(Spacer(1, 20))
    
    # GDPR izjava
    story.append(Paragraph("Istovremeno sa potpisivanjem ovog obrasca obavesten sam o obradi podataka o licnosti i pristajem na obradu podataka u skladu sa zakonom.", data_style))
    story.append(Spacer(1, 15))
    
    # Datum i mesto potpisa
    story.append(Paragraph(f"U <b>{mesto_potpisa or '________________'}</b>, dana <b>{datum_potpisa or '________________'}</b>", data_style))
    story.append(Paragraph("(potpis)", data_style))
    story.append(Spacer(1, 20))
    
    # Potvrda
    story.append(Paragraph("Potvrdjuje se da je ovu izjavu svojerucno potpisao.", data_style))
    story.append(Paragraph(f"(ime i prezime): <b>{ime} {prezime}</b>", data_style))
    story.append(Paragraph("Identitet pripadnika nacionalne manjine utvrden je na osnovu uvida u licne isprave.", data_style))
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
    
    story.append(Paragraph("U skladu sa clanom 101. stav 2. Zakona o nacionalnim savetima nacionalnih manjina („Sluzbeni glasnik RS", br. 72/09, 20/14 – US, 55/14 i 47/18) naknada za overu se ne naplacuje.", napomena_style))
    story.append(Spacer(1, 15))
    
    # Mesto za overu
    story.append(Paragraph("Ov. br. ________________", data_style))
    story.append(Paragraph("U ________________ casova.", data_style))
    story.append(Paragraph("(mesto) (datum)", data_style))
    story.append(Paragraph("Nadlezni organ za overu", data_style))
    story.append(Paragraph("(mesto)", data_style))
    story.append(Paragraph("(potpis)", data_style))
    story.append(Paragraph("(ime i prezime)", data_style))
    story.append(Spacer(1, 20))
    
    # Napomena na kraju
    story.append(Paragraph("NAPOMENA: Biraci koji podrzavaju elektore i podrzani kandidati za elektore u postupku za sprovodjenje izbornih radnji koje su u vezi sa ovim obrascm mogu koristiti i modele odgovarajucih akata (Clan 102. stav 2. Zakona o nacionalnim savetima nacionalnih manjina („Sluzbeni glasnik RS", br. 72/09, 20/14 – US, 55/14 i 47/18)) postavljene na zvaničnoj internet strani Ministarstva drzavne uprave i lokalne samouprave.", napomena_style))
    
    # Generisanje PDF-a
    print("Generisanje PDF-a...")
    doc.build(story)
    print(f"PDF je uspešno kreiran: {filepath}")
    return filepath

if __name__ == "__main__":
    # Example usage
    generisi_pdf("Ime", "Prezime", "1234567890123", "Adresa", "Opstina", "Ime roditelja", "1990-01-01", "Beograd", 
                "", "Slovacka", "Ime elektora", "Prezime elektora", "1234567890124", "Adresa elektora", 
                "Opstina elektora", "", "2024-01-01", "Beograd", "0123456789", "email@example.com") 