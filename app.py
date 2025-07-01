from flask import Flask, render_template, request, redirect, flash
import sqlite3
from generate_pdf import generisi_pdf
import os

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
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * FROM podrska WHERE jmbg = ?", (jmbg,))
    osoba = c.fetchone()
    conn.close()
    
    if osoba:
        ime, prezime, jmbg, adresa, opstina = osoba[1], osoba[2], osoba[3], osoba[4], osoba[5]
        generisi_pdf(ime, prezime, jmbg, adresa, opstina)
        flash(f'PDF je generisan za {ime} {prezime}!', 'success')
    else:
        flash('Osoba nije pronađena!', 'error')
    
    return redirect('/pretraga')

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False) 