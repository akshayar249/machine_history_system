import sqlite3
from config import DB_PATH

def connect():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    c.execute('PRAGMA foreign_keys=ON')
    return c

def init_db():
    with connect() as c:
        c.executescript('''
        CREATE TABLE IF NOT EXISTS machines (
          id INTEGER PRIMARY KEY AUTOINCREMENT, customer_name TEXT, machine_model TEXT,
          machine_number TEXT, source_pdf TEXT NOT NULL,
          UNIQUE(source_pdf, machine_number));
        CREATE TABLE IF NOT EXISTS components (
          id INTEGER PRIMARY KEY AUTOINCREMENT, machine_id INTEGER NOT NULL,
          component_name TEXT, model TEXT, make TEXT, component_type TEXT,
          source_page INTEGER, confidence REAL DEFAULT 0, needs_review INTEGER DEFAULT 1,
          FOREIGN KEY(machine_id) REFERENCES machines(id) ON DELETE CASCADE);
        CREATE TABLE IF NOT EXISTS page_ocr (
          id INTEGER PRIMARY KEY AUTOINCREMENT, machine_id INTEGER NOT NULL,
          page_number INTEGER NOT NULL, ocr_text TEXT, page_image TEXT,
          FOREIGN KEY(machine_id) REFERENCES machines(id) ON DELETE CASCADE,
          UNIQUE(machine_id,page_number));
        ''')

def save_machine(customer, model, number, source):
    with connect() as c:
        row = c.execute('SELECT id FROM machines WHERE source_pdf=? AND machine_number=?',
                        (source, number or '')).fetchone()
        if row:
            mid = row['id']
            c.execute('UPDATE machines SET customer_name=?,machine_model=? WHERE id=?',
                      (customer, model, mid))
        else:
            cur = c.execute('INSERT INTO machines(customer_name,machine_model,machine_number,source_pdf) VALUES(?,?,?,?)',
                            (customer, model, number, source))
            mid = cur.lastrowid
    return mid

def save_page(mid, page, text, image):
    with connect() as c:
        c.execute('INSERT OR REPLACE INTO page_ocr(machine_id,page_number,ocr_text,page_image) VALUES(?,?,?,?)',
                  (mid, page, text, image))

def save_component(mid, name, model, make, typ, page):
    with connect() as c:
        c.execute('INSERT INTO components(machine_id,component_name,model,make,component_type,source_page,needs_review) VALUES(?,?,?,?,?,?,1)',
                  (mid, name, model, make, typ, page))
