# Podrška Partija - Sistem za upravljanje zahtevima za podršku

Jednostavan Flask aplikacija za upravljanje zahtevima za podršku sa mogućnošću generisanja PDF izveštaja.

## Struktura projekta

```
podrska-partija/
│
├── app.py                ← Flask aplikacija
├── forms.html            ← HTML forma (standalone)
├── generate_pdf.py       ← PDF generacija
├── database.db           ← SQLite baza (automatski se pravi)
├── requirements.txt      ← Spisak biblioteka
├── README.md             ← Ova datoteka
└── templates/
    ├── form.html         ← HTML za prikaz forme (Flask template)
    └── zahtevi.html      ← HTML za prikaz svih zahteva
```

## Instalacija

1. **Klonirajte ili preuzmite projekat**

2. **Instalirajte potrebne biblioteke:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Pokrenite aplikaciju:**
   ```bash
   python app.py
   ```

4. **Otvorite browser i idite na:**
   ```
   http://localhost:5000
   ```

## Funkcionalnosti

### 1. Forma za podršku
- Unos imena i prezimena
- Email adresa
- Broj telefona (opciono)
- Opis problema
- Izbor prioriteta (Nizak, Srednji, Visok, Kritičan)

### 2. Pregled zahteva
- Prikaz svih poslatih zahteva
- Sortiranje po datumu kreiranja
- Bojno kodiranje prioriteta
- Statistika zahteva

### 3. PDF izveštaji
- Generisanje izveštaja svih zahteva
- Generisanje pojedinačnih zahteva
- Profesionalni format sa tabelama

## Korišćenje

### Pokretanje aplikacije
```bash
python app.py
```

### Generisanje PDF izveštaja
```python
# Generisanje izveštaja svih zahteva
python generate_pdf.py

# Ili iz Python-a:
from generate_pdf import generate_pdf_report, generate_single_request_pdf

# Generisanje izveštaja svih zahteva
generate_pdf_report("moj_izvestaj.pdf")

# Generisanje pojedinačnog zahteva
generate_single_request_pdf(1, "zahtev_1.pdf")
```

## Baza podataka

Aplikacija automatski kreira SQLite bazu `database.db` sa sledećom strukturom:

```sql
CREATE TABLE podrska_zahtevi (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ime TEXT NOT NULL,
    email TEXT NOT NULL,
    telefon TEXT,
    opis_problema TEXT NOT NULL,
    prioritet TEXT NOT NULL,
    datum_kreiranja TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## Rutiranje

- `/` - Glavna strana sa formom
- `/submit` - POST endpoint za slanje forme
- `/zahtevi` - Pregled svih zahteva

## Konfiguracija

U `app.py` možete promeniti:
- `app.secret_key` - za sigurnost sesija
- Port na kojem se pokreće aplikacija
- Debug mode

## Zavisnosti

- **Flask** - Web framework
- **reportlab** - PDF generacija
- **Werkzeug** - WSGI utility library

## Napomene

- Baza podataka se automatski kreira pri prvom pokretanju
- PDF fajlovi se čuvaju u root direktorijumu
- Aplikacija je konfigurisana za development mode
- Za produkciju promenite `debug=True` u `debug=False`

## Podrška

Za pitanja ili probleme, molimo vas da otvorite issue u GitHub repozitorijumu. 