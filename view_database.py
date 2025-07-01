import sqlite3

def view_database():
    try:
        # Povežite se sa bazom
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        
        # Proverite da li tabela postoji
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print("📋 Tabele u bazi:")
        for table in tables:
            print(f"  - {table[0]}")
        
        print("\n" + "="*50)
        
        # Prikažite sadržaj tabele 'podrska'
        cursor.execute("SELECT * FROM podrska")
        rows = cursor.fetchall()
        
        if rows:
            print(f"📊 Sadržaj tabele 'podrska' ({len(rows)} redova):")
            print("\nID | Ime | Prezime | JMBG | Adresa | Opština | Telefon | Email")
            print("-" * 80)
            
            for row in rows:
                print(f"{row[0]:2} | {row[1]:10} | {row[2]:10} | {row[3]:13} | {row[4]:15} | {row[5]:10} | {row[6]:10} | {row[7]}")
        else:
            print("📭 Baza je prazna - nema podataka")
        
        conn.close()
        
    except sqlite3.OperationalError as e:
        print(f"❌ Greška: {e}")
        print("💡 Baza možda ne postoji ili je prazna")
    except Exception as e:
        print(f"❌ Neočekivana greška: {e}")

if __name__ == "__main__":
    view_database() 