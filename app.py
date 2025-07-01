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
    c.execute('''CREATE TABLE IF NOT EXISTS podrska (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ime TEXT,
        prezime TEXT,
        jmbg TEXT UNIQUE,
        adresa TEXT,
        opstina TEXT,
        broj_telefona TEXT,
        email TEXT
    )''')
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
        adresa = request.form['adresa']
        opstina = request.form['opstina']
        broj_telefona = request.form['broj_telefona']
        email = request.form['email']

        try:
            conn = sqlite3.connect('database.db')
            c = conn.cursor()
            c.execute("INSERT INTO podrska (ime, prezime, jmbg, adresa, opstina, broj_telefona, email) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (ime, prezime, jmbg, adresa, opstina, broj_telefona, email))
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
            print(f"Generisanje PDF-a za: {ime} {prezime}")
            
            filename = generisi_pdf(ime, prezime, jmbg, adresa, opstina)
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
        
        elif 'sacuvaj' in request.form:
            # Čuvanje izmenjenih podataka
            id_osobe = request.form.get('id')
            ime = request.form.get('ime')
            prezime = request.form.get('prezime')
            jmbg = request.form.get('jmbg')
            adresa = request.form.get('adresa')
            opstina = request.form.get('opstina')
            broj_telefona = request.form.get('broj_telefona')
            email = request.form.get('email')
            
            try:
                conn = sqlite3.connect('database.db')
                c = conn.cursor()
                c.execute("""
                    UPDATE podrska 
                    SET ime=?, prezime=?, jmbg=?, adresa=?, opstina=?, broj_telefona=?, email=?
                    WHERE id=?
                """, (ime, prezime, jmbg, adresa, opstina, broj_telefona, email, id_osobe))
                conn.commit()
                conn.close()
                flash('Podaci su uspešno ažurirani!', 'success')
                return redirect('/izmeni')
            except sqlite3.IntegrityError:
                flash('Osoba sa ovim JMBG-om već postoji!', 'error')
            except Exception as e:
                flash(f'Greška pri ažuriranju podataka: {str(e)}', 'error')
    
    return render_template('izmeni.html')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 