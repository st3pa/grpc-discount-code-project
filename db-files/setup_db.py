import sqlite3

def setup_database():
    conn = sqlite3.connect('db-files/discounts.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS discount_codes (
            id INTEGER PRIMARY KEY,
            code TEXT UNIQUE,
            used BOOLEAN
        )
    ''')
    conn.commit()
    conn.close()

if __name__ == '__main__':
    setup_database()
