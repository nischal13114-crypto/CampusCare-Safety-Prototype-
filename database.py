import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

DB_PATH = Path(__file__).with_name("campuscare.db")

def connect():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("""CREATE TABLE IF NOT EXISTS incidents (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            incident_id TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            created_at TEXT NOT NULL,
            location TEXT DEFAULT '',
            contact TEXT DEFAULT '',
            missing_person TEXT DEFAULT '',
            status TEXT NOT NULL DEFAULT 'New',
            is_demo INTEGER NOT NULL DEFAULT 0
        )""")
        con.execute("""CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            phone TEXT NOT NULL,
            is_demo INTEGER NOT NULL DEFAULT 0
        )""")

def create_incident(category, description, occurred_at=None, location="", contact="", missing_person="", is_demo=0):
    occurred_at = occurred_at or datetime.now().isoformat(timespec="minutes")
    incident_id = "CC-" + datetime.now().strftime("%y%m%d") + "-" + uuid.uuid4().hex[:6].upper()
    with connect() as con:
        con.execute("""INSERT INTO incidents
        (incident_id,category,description,occurred_at,created_at,location,contact,missing_person,status,is_demo)
        VALUES (?,?,?,?,?,?,?,?,?,?)""",
        (incident_id, category, description, occurred_at, datetime.now().isoformat(timespec="seconds"),
         location, contact, missing_person, "New", int(is_demo)))
    return incident_id

def list_incidents(limit=None):
    with connect() as con:
        sql = "SELECT * FROM incidents ORDER BY created_at DESC"
        if limit:
            sql += " LIMIT ?"
            rows = con.execute(sql, (int(limit),)).fetchall()
        else:
            rows = con.execute(sql).fetchall()
    return [dict(r) for r in rows]

def count_incidents():
    with connect() as con:
        return con.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]

def update_incident_status(incident_id, status):
    if status not in {"New", "Reviewing", "Resolved"}:
        raise ValueError("Invalid incident status")
    with connect() as con:
        cur = con.execute("UPDATE incidents SET status=? WHERE incident_id=?", (status, incident_id))
        return cur.rowcount > 0

def list_contacts():
    with connect() as con:
        rows = con.execute("SELECT * FROM contacts ORDER BY category,name").fetchall()
    return [dict(r) for r in rows]

def add_contact(name, category, phone, is_demo=0):
    with connect() as con:
        cur = con.execute("INSERT INTO contacts(name,category,phone,is_demo) VALUES (?,?,?,?)",
                          (name, category, phone, int(is_demo)))
        return cur.lastrowid

def update_contact(contact_id, name, category, phone, is_demo=0):
    with connect() as con:
        cur = con.execute("UPDATE contacts SET name=?,category=?,phone=?,is_demo=? WHERE id=?",
                          (name, category, phone, int(is_demo), contact_id))
        return cur.rowcount > 0

def delete_contact(contact_id):
    with connect() as con:
        cur = con.execute("DELETE FROM contacts WHERE id=?", (contact_id,))
        return cur.rowcount > 0

def reset_demo_data():
    with connect() as con:
        con.execute("DELETE FROM incidents")
        con.execute("DELETE FROM contacts")
    _insert_demo_data()

def seed_demo_data():
    with connect() as con:
        count = con.execute("SELECT COUNT(*) FROM contacts").fetchone()[0]
    if count == 0:
        _insert_demo_data()
    with connect() as con:
        count = con.execute("SELECT COUNT(*) FROM incidents").fetchone()[0]
    if count == 0:
        now = datetime.now()
        samples = [
            ("Medical", "Student felt dizzy near the library; staff notified in demo scenario.", "Library entrance", "Reviewing"),
            ("Fire", "Practice report: smoke alarm activation in science block.", "Science block, floor 1", "New"),
            ("Unsafe Situation", "Practice report: a corridor light is not working.", "East corridor", "Resolved"),
        ]
        for idx, (cat, desc, loc, status) in enumerate(samples):
            iid = "DEMO-" + str(idx+1).zfill(3)
            when = (now - timedelta(hours=idx+2)).isoformat(timespec="seconds")
            with connect() as con:
                con.execute("""INSERT OR IGNORE INTO incidents
                (incident_id,category,description,occurred_at,created_at,location,contact,missing_person,status,is_demo)
                VALUES (?,?,?,?,?,?,?,?,?,1)""",
                (iid,cat,desc,when,when,loc,"","",status))

def _insert_demo_data():
    contacts = [
        ("India Emergency Services", "National Emergency", "112", 0),
        ("Demo Ambulance Desk", "Ambulance", "000-000-0101", 1),
        ("Demo Fire Desk", "Fire", "000-000-0102", 1),
        ("Demo Campus Security", "Campus Security", "000-000-0103", 1),
        ("Demo Student Support", "Student Support", "000-000-0104", 1),
    ]
    with connect() as con:
        con.executemany("INSERT INTO contacts(name,category,phone,is_demo) VALUES (?,?,?,?)", contacts)
