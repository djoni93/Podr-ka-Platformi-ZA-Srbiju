from flask import Flask, render_template, request, redirect, flash, send_file
import sqlite3
from generate_pdf import generisi_pdf
import os
import time

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Kreiranje baze ako ne postoji
def init_db():
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    
    # Kreiraj tabelu ako ne postoji
    c.execute('''CREATE TABLE IF NOT EXISTS podrska (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ime TEXT,
        prezime TEXT,
        jmbg TEXT UNIQUE,
        adresa TEXT,
        opstina TEXT,
        broj_telefona TEXT,
        email TEXT,
        ime_roditelja TEXT,
        datum_rodjenja TEXT,
        mesto_rodjenja TEXT,
        adresa_boravista TEXT,
        nacionalna_manjina TEXT,
        ime_elektora TEXT,
        prezime_elektora TEXT,
        jmbg_elektora TEXT,
        adresa_elektora TEXT,
        opstina_elektora TEXT,
        adresa_boravista_elektora TEXT,
        datum_potpisa TEXT,
        mesto_potpisa TEXT
    )''')
    
    # Proveri da li postoje nove kolone i dodaj ih ako ne postoje
    c.execute("PRAGMA table_info(podrska)")
    columns = [column[1] for column in c.fetchall()]
    
    # Lista novih kolona koje treba dodati
    new_columns = [
        ('ime_roditelja', 'TEXT'),
        ('datum_rodjenja', 'TEXT'),
        ('mesto_rodjenja', 'TEXT'),
        ('adresa_boravista', 'TEXT'),
        ('nacionalna_manjina', 'TEXT'),
        ('ime_elektora', 'TEXT'),
        ('prezime_elektora', 'TEXT'),
        ('jmbg_elektora', 'TEXT'),
        ('adresa_elektora', 'TEXT'),
        ('opstina_elektora', 'TEXT'),
        ('adresa_boravista_elektora', 'TEXT'),
        ('datum_potpisa', 'TEXT'),
        ('mesto_potpisa', 'TEXT')
    ]
    
    # Dodaj nove kolone ako ne postoje
    for column_name, column_type in new_columns:
        if column_name not in columns:
            try:
                c.execute(f"ALTER TABLE podrska ADD COLUMN {column_name} {column_type}")
                print(f"Dodata nova kolona: {column_name}")
            except Exception as e:
                print(f"Greška pri dodavanju kolone {column_name}: {e}")
    
    conn.commit()
    conn.close()

# Funkcija za čišćenje starih PDF fajlova
def cleanup_old_pdfs():
    temp_dir = os.path.join(os.getcwd(), 'temp_pdfs')
    if os.path.exists(temp_dir):
        current_time = time.time()
        for filename in os.listdir(temp_dir):
            filepath = os.path.join(temp_dir, filename)
            # Obriši fajlove starije od 1 sata
            if os.path.isfile(filepath) and current_time - os.path.getmtime(filepath) > 3600:
                try:
                    os.remove(filepath)
                    print(f"Obrisan stari fajl: {filename}")
                except Exception as e:
                    print(f"Greška pri brisanju {filename}: {e}")

init_db()

@app.route('/', methods=['GET', 'POST'])
def forma():
    if request.method == 'POST':
        ime = request.form['ime']
        prezime = request.form['prezime']
        jmbg = request.form['jmbg']
        ime_roditelja = request.form['ime_roditelja']
        datum_rodjenja = request.form['datum_rodjenja']
        mesto_rodjenja = request.form['mesto_rodjenja']
        adresa = request.form['adresa']
        adresa_boravista = request.form.get('adresa_boravista', '')
        opstina = request.form['opstina']
        broj_telefona = request.form.get('broj_telefona', '')
        email = request.form.get('email', '')
        nacionalna_manjina = request.form['nacionalna_manjina']
        ime_elektora = request.form['ime_elektora']
        prezime_elektora = request.form['prezime_elektora']
        jmbg_elektora = request.form['jmbg_elektora']
        adresa_elektora = request.form['adresa_elektora']
        opstina_elektora = request.form['opstina_elektora']
        adresa_boravista_elektora = request.form.get('adresa_boravista_elektora', '')
        datum_potpisa = request.form['datum_potpisa']
        mesto_potpisa = request.form['mesto_potpisa']

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("""INSERT INTO podrska (
                ime, prezime, jmbg, ime_roditelja, datum_rodjenja, mesto_rodjenja, 
                adresa, adresa_boravista, opstina, broj_telefona, email, nacionalna_manjina,
                ime_elektora, prezime_elektora, jmbg_elektora, adresa_elektora, opstina_elektora,
                adresa_boravista_elektora, datum_potpisa, mesto_potpisa
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                      (ime, prezime, jmbg, ime_roditelja, datum_rodjenja, mesto_rodjenja,
                       adresa, adresa_boravista, opstina, broj_telefona, email, nacionalna_manjina,
                       ime_elektora, prezime_elektora, jmbg_elektora, adresa_elektora, opstina_elektora,
                       adresa_boravista_elektora, datum_potpisa, mesto_potpisa))
            conn.commit()
            conn.close()
            flash('Podaci su uspešno sačuvani u bazu!', 'success')
        except sqlite3.IntegrityError:
            flash('Osoba sa ovim JMBG-om već postoji u bazi!', 'error')
        except Exception as e:
            flash(f'Greška pri čuvanju podataka: {str(e)}', 'error')

        return redirect('/')

    return render_template('form.html')

@app.route('/pretraga', methods=['GET', 'POST'])
def pretraga():
    if request.method == 'POST':
        jmbg = request.form.get('jmbg', '').strip()
        
        if not jmbg:
            flash('Molimo unesite JMBG za pretragu!', 'error')
            return render_template('pretraga.html')
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM podrska WHERE jmbg = ?", (jmbg,))
        osoba = c.fetchone()
        conn.close()
        
        if osoba:
            flash(f'Pronađena osoba: {osoba[1]} {osoba[2]}', 'success')
            return render_template('pretraga.html', osoba=osoba)
        else:
            flash('Osoba sa ovim JMBG-om nije pronađena!', 'error')
            return render_template('pretraga.html')
    
    return render_template('pretraga.html')

@app.route('/generisi_pdf/<jmbg>')
def generisi_pdf_za_jmbg(jmbg):
    try:
        # Očisti stare fajlove
        cleanup_old_pdfs()
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM podrska WHERE jmbg = ?", (jmbg,))
        osoba = c.fetchone()
        conn.close()
        
        if osoba:
            ime, prezime, jmbg, adresa, opstina = osoba[1], osoba[2], osoba[3], osoba[4], osoba[5]
            ime_roditelja, datum_rodjenja, mesto_rodjenja = osoba[8], osoba[9], osoba[10]
            adresa_boravista, nacionalna_manjina = osoba[11], osoba[12]
            ime_elektora, prezime_elektora, jmbg_elektora = osoba[13], osoba[14], osoba[15]
            adresa_elektora, opstina_elektora, adresa_boravista_elektora = osoba[16], osoba[17], osoba[18]
            datum_potpisa, mesto_potpisa = osoba[19], osoba[20]
            broj_telefona, email = osoba[6], osoba[7]
            
            print(f"Generisanje PDF-a za: {ime} {prezime}")
            
            filename = generisi_pdf(ime, prezime, jmbg, adresa, opstina, ime_roditelja, datum_rodjenja, mesto_rodjenja,
                                  adresa_boravista, nacionalna_manjina, ime_elektora, prezime_elektora, jmbg_elektora,
                                  adresa_elektora, opstina_elektora, adresa_boravista_elektora, datum_potpisa, mesto_potpisa,
                                  broj_telefona, email)
            print(f"PDF fajl kreiran: {filename}")
            
            # Proveri da li fajl postoji
            if os.path.exists(filename):
                print(f"Fajl postoji, šaljem korisniku: {filename}")
                try:
                    # Pošalji PDF fajl korisniku za download
                    safe_ime = "".join(c for c in ime if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    safe_prezime = "".join(c for c in prezime if c.isalnum() or c in (' ', '-', '_')).rstrip()
                    download_name = f"formular_{safe_ime}_{safe_prezime}.pdf"
                    
                    response = send_file(
                        filename,
                        as_attachment=True,
                        download_name=download_name,
                        mimetype='application/pdf'
                    )
                    
                    # Postavi callback za brisanje fajla nakon slanja
                    @response.call_on_close
                    def cleanup():
                        try:
                            if os.path.exists(filename):
                                os.remove(filename)
                                print(f"Obrisan privremeni fajl: {filename}")
                        except Exception as e:
                            print(f"Greška pri brisanju {filename}: {e}")
                    
                    return response
                except Exception as e:
                    print(f"Greška pri slanju PDF-a: {str(e)}")
                    flash(f'Greška pri slanju PDF-a: {str(e)}', 'error')
                    return redirect('/pretraga')
            else:
                print(f"Fajl ne postoji: {filename}")
                flash('Greška pri generisanju PDF-a - fajl nije kreiran!', 'error')
        else:
            print(f"Osoba nije pronađena za JMBG: {jmbg}")
            flash('Osoba nije pronađena!', 'error')
        
    except Exception as e:
        print(f"Greška u PDF generisanju: {str(e)}")
        flash(f'Greška pri generisanju PDF-a: {str(e)}', 'error')
    
    return redirect('/pretraga')

@app.route('/izmeni', methods=['GET', 'POST'])
def izmeni_podatke():
    if request.method == 'POST':
        if 'pretrazi' in request.form:
            # Pretraga osobe
            jmbg = request.form.get('jmbg', '').strip()
            
            if not jmbg:
                flash('Molimo unesite JMBG za pretragu!', 'error')
                return render_template('izmeni.html')
            
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("SELECT * FROM podrska WHERE jmbg = ?", (jmbg,))
            osoba = c.fetchone()
            conn.close()
            
            if osoba:
                flash(f'Pronađena osoba: {osoba[1]} {osoba[2]}', 'success')
                return render_template('izmeni.html', osoba=osoba, edit_mode=True)
            else:
                flash('Osoba sa ovim JMBG-om nije pronađena!', 'error')
                return render_template('izmeni.html')
    
        elif 'sacuvaj' in request.form:
            # Čuvanje izmenjenih podataka
            id_osobe = request.form.get('id')
            ime = request.form.get('ime')
            prezime = request.form.get('prezime')
            jmbg = request.form.get('jmbg')
            ime_roditelja = request.form.get('ime_roditelja')
            datum_rodjenja = request.form.get('datum_rodjenja')
            mesto_rodjenja = request.form.get('mesto_rodjenja')
            adresa = request.form.get('adresa')
            adresa_boravista = request.form.get('adresa_boravista', '')
            opstina = request.form.get('opstina')
            broj_telefona = request.form.get('broj_telefona', '')
            email = request.form.get('email', '')
            nacionalna_manjina = request.form.get('nacionalna_manjina')
            ime_elektora = request.form.get('ime_elektora')
            prezime_elektora = request.form.get('prezime_elektora')
            jmbg_elektora = request.form.get('jmbg_elektora')
            adresa_elektora = request.form.get('adresa_elektora')
            opstina_elektora = request.form.get('opstina_elektora')
            adresa_boravista_elektora = request.form.get('adresa_boravista_elektora', '')
            datum_potpisa = request.form.get('datum_potpisa')
            mesto_potpisa = request.form.get('mesto_potpisa')
            
            try:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("""
                    UPDATE podrska 
                    SET ime=?, prezime=?, jmbg=?, ime_roditelja=?, datum_rodjenja=?, mesto_rodjenja=?,
                        adresa=?, adresa_boravista=?, opstina=?, broj_telefona=?, email=?, nacionalna_manjina=?,
                        ime_elektora=?, prezime_elektora=?, jmbg_elektora=?, adresa_elektora=?, opstina_elektora=?,
                        adresa_boravista_elektora=?, datum_potpisa=?, mesto_potpisa=?
                    WHERE id=?
                """, (ime, prezime, jmbg, ime_roditelja, datum_rodjenja, mesto_rodjenja,
                      adresa, adresa_boravista, opstina, broj_telefona, email, nacionalna_manjina,
                      ime_elektora, prezime_elektora, jmbg_elektora, adresa_elektora, opstina_elektora,
                      adresa_boravista_elektora, datum_potpisa, mesto_potpisa, id_osobe))
                conn.commit()
                conn.close()
                flash('Podaci su uspešno ažurirani!', 'success')
                return redirect('/izmeni')
            except sqlite3.IntegrityError:
                flash('Osoba sa ovim JMBG-om već postoji!', 'error')
            except Exception as e:
                flash(f'Greška pri ažuriranju podataka: {str(e)}', 'error')
    
    # Ako je GET request sa JMBG parametrom, automatski pretraži
    if request.method == 'GET' and request.args.get('jmbg'):
        jmbg = request.args.get('jmbg').strip()
        
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        c.execute("SELECT * FROM podrska WHERE jmbg = ?", (jmbg,))
        osoba = c.fetchone()
        conn.close()
        
        if osoba:
            flash(f'Pronađena osoba: {osoba[1]} {osoba[2]}', 'success')
            return render_template('izmeni.html', osoba=osoba, edit_mode=True)
        else:
            flash('Osoba sa ovim JMBG-om nije pronađena!', 'error')
    
    return render_template('izmeni.html')

@app.route('/obrisi/<jmbg>')
def obrisi_podatke(jmbg):
    try:
        conn = sqlite3.connect('database.db')
        c = conn.cursor()
        
        # Prvo proveri da li osoba postoji
        c.execute("SELECT ime, prezime FROM podrska WHERE jmbg = ?", (jmbg,))
        osoba = c.fetchone()
        
        if osoba:
            ime, prezime = osoba[0], osoba[1]
            # Obriši osobu iz baze
            c.execute("DELETE FROM podrska WHERE jmbg = ?", (jmbg,))
            conn.commit()
            conn.close()
            flash(f'Podaci za {ime} {prezime} su uspešno obrisani iz baze!', 'success')
        else:
            conn.close()
            flash('Osoba sa ovim JMBG-om nije pronađena!', 'error')
            
    except Exception as e:
        flash(f'Greška pri brisanju podataka: {str(e)}', 'error')
    
    return redirect('/pretraga')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 