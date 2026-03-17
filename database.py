import sqlite3
import os

DB_DIR = os.path.join(os.path.dirname(__file__), 'data')
DB_PATH = os.path.join(DB_DIR, 'app.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    if not os.path.exists(DB_DIR):
        os.makedirs(DB_DIR)
        
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_name TEXT NOT NULL,
            api_key TEXT,
            default_location_id INTEGER
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alias TEXT NOT NULL,
            city_name TEXT NOT NULL,
            is_default BOOLEAN NOT NULL CHECK (is_default IN (0, 1))
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS special_tags (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT,
            custom_message TEXT NOT NULL
        )
    ''')
    
    # Insert default data if empty
    cursor.execute('SELECT COUNT(*) FROM user_settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO user_settings (user_name, api_key) VALUES (?, ?)', ("Yasemin", "4fe0104e079aaab4cc0eeb611e31f3d2"))
        
    cursor.execute('SELECT COUNT(*) FROM locations')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO locations (alias, city_name, is_default) VALUES (?, ?, ?)', ("Konya - Okul", "Meram, TR", 1))
        cursor.execute('INSERT INTO locations (alias, city_name, is_default) VALUES (?, ?, ?)', ("İstanbul - Ev", "Sultangazi, TR", 0))

    conn.commit()
    conn.close()

if __name__ == '__main__':
    init_db()
    print("Database initialized successfully.")
