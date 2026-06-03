#!/usr/bin/env python3
"""
Advance Arena Full Stack
- Python standard library only
- SQLite database
- Login/signup, online account saving, admin panel, item database, goals, calendar, rewards
Run: python server.py
Open: http://localhost:8000
"""
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from pathlib import Path
import sqlite3, json, secrets, hashlib, hmac, os, mimetypes, datetime, re

BASE_DIR = Path(__file__).resolve().parent
PUBLIC_DIR = BASE_DIR / "public"
DB_PATH = BASE_DIR / "advance_arena.db"
SESSION_DAYS = 30

MECHS = [
    ("Paragon","Mech","Common","A-Coins",None),("Lancer","Mech","Common","A-Coins",None),
    ("Juggernaut","Mech","Uncommon","A-Coins",None),("M.D.","Mech","Uncommon","A-Coins",None),("Puma","Mech","Uncommon","A-Coins",None),("Slingshot","Mech","Uncommon","A-Coins",None),
    ("Guardian","Mech","Rare","A-Coins",None),("Shadow","Mech","Rare","A-Coins",None),("Ares","Mech","Rare","A-Coins",None),("Arachnos","Mech","Rare","A-Coins",None),("Stalker","Mech","Rare","A-Coins",None),("Tengu","Mech","Rare","A-Coins",None),
    ("Panther","Mech","Epic","A-Coins",None),("Killshot","Mech","Epic","A-Coins",None),("Zephyr","Mech","Epic","A-Coins",None),("Cheetah","Mech","Epic","A-Coins",None),("Aegis","Mech","Epic","A-Coins",None),("Orion","Mech","Epic","A-Coins",None),("Redeemer","Mech","Epic","A-Coins",None),("Sentinel","Mech","Epic","A-Coins",None),
    ("Brickhouse","Mech","Legendary","A-Coins",None),("Redox","Mech","Legendary","A-Coins",None),("Surge","Mech","Legendary","A-Coins",None),("Gatecrasher","Mech","Legendary","A-Coins",None),("Bastion","Mech","Legendary","A-Coins",None),("Onyx","Mech","Legendary","A-Coins",None),("Eclipse","Mech","Legendary","A-Coins",None),("Scorpius","Mech","Legendary","A-Coins",None),("Nomad","Mech","Legendary","A-Coins",None),("Hemlock","Mech","Legendary","A-Coins",None),("Vortex","Mech","Legendary","A-Coins",None),("Seeker","Mech","Legendary","A-Coins",None),("Solis","Mech","Legendary","A-Coins",None),("Lacewing","Mech","Legendary","A-Coins",None),("Blockhorn","Mech","Legendary","A-Coins",None),("Mimicker","Mech","Legendary","A-Coins",None),("Deathwalker","Mech","Legendary","A-Coins",None),("Outlaw","Mech","Legendary","A-Coins",None),("Salvor","Mech","Legendary","A-Coins",None),("Dreadnought","Mech","Legendary","A-Coins",None),("Parasite","Mech","Legendary","A-Coins",None),("Volti","Mech","Legendary","A-Coins",None),("Silverthorn","Mech","Legendary","A-Coins",None),("Blizzfrost","Mech","Legendary","A-Coins",None),("Citadel","Mech","Legendary","A-Coins",None)
]
WEAPONS = [
    ("Autocannon","Weapon","Common","Credits",None),("Thermal Lance","Weapon","Common","Credits",None),("Shotgun","Weapon","Common","Credits",None),("RPG","Weapon","Common","Credits",None),("Javelin Rack","Weapon","Common","Credits",None),
    ("Carbine","Weapon","Legendary","A-Coins",None),("Disruptor","Weapon","Legendary","A-Coins",None),("Particle Beam","Weapon","Legendary","A-Coins",None),("Repeater","Weapon","Legendary","A-Coins",None),("Railgun","Weapon","Legendary","A-Coins",None),("Viper","Weapon","Legendary","A-Coins",None),("Storm Rack","Weapon","Legendary","A-Coins",None),("Graviton Beam","Weapon","Legendary","A-Coins",None),("Howler","Weapon","Legendary","A-Coins",None),("EM Rifle","Weapon","Legendary","A-Coins",None),("Overdriver","Weapon","Legendary","A-Coins",None),("Blast RPG","Weapon","Epic","A-Coins",None),("Revoker","Weapon","Legendary","A-Coins",None),("Tetra Rifle","Weapon","Legendary","A-Coins",None),("Disc Launcher","Weapon","Legendary","A-Coins",None),("Savant","Weapon","Legendary","A-Coins",None),("Strike Rocket","Weapon","Legendary","A-Coins",None),("Pod Gun","Weapon","Legendary","A-Coins",None),("Minigun","Weapon","Legendary","A-Coins",None),("Chain Gun","Weapon","Legendary","A-Coins",None),("Hellfire","Weapon","Legendary","A-Coins",None)
]


# Costs below are seeded from the public Gear Hub cost table.
# Some new gear is marked as "$" on the wiki, so those items are stored as In-App Purchase with no numeric default_cost.
GEAR_HUB_COSTS = [
    # Mechs
    ("Paragon","Mech","Common","Credits",0),("Lancer","Mech","Common","Credits",400),
    ("Puma","Mech","Uncommon","A-Coins",45),("Slingshot","Mech","Uncommon","Credits",4700),("Juggernaut","Mech","Uncommon","A-Coins",45),("M.D.","Mech","Uncommon","Credits",4700),
    ("Guardian","Mech","Rare","A-Coins",420),("Shadow","Mech","Rare","A-Coins",420),("Ares","Mech","Rare","Credits",42200),
    ("Stalker","Mech","Rare","A-Coins",420),("Tengu","Mech","Rare","A-Coins",420),("Arachnos","Mech","Rare","Credits",42200),
    ("Aegis","Mech","Epic","A-Coins",1865),("Cheetah","Mech","Epic","A-Coins",1305),("Redeemer","Mech","Epic","A-Coins",1865),("Zephyr","Mech","Epic","Credits",186600),
    ("Killshot","Mech","Epic","A-Coins",1865),("Orion","Mech","Epic","A-Coins",1865),("Panther","Mech","Epic","A-Coins",2425),("Sentinel","Mech","Epic","Credits",130600),
    ("Brickhouse","Mech","Legendary","Credits",937500),("Eclipse","Mech","Legendary","A-Coins",9375),("Redox","Mech","Legendary","A-Coins",9375),("Scorpius","Mech","Legendary","A-Coins",9375),("Surge","Mech","Legendary","A-Coins",9375),
    ("Bastion","Mech","Legendary","A-Coins",9375),("Gatecrasher","Mech","Legendary","A-Coins",9375),("Hemlock","Mech","Legendary","Credits",937500),("Lacewing","Mech","Legendary","A-Coins",9375),("Nomad","Mech","Legendary","A-Coins",9375),("Onyx","Mech","Legendary","A-Coins",9375),("Solis","Mech","Legendary","Credits",937500),("Vortex","Mech","Legendary","A-Coins",9375),
    ("Blockhorn","Mech","Legendary","A-Coins",9375),("Mimicker","Mech","Legendary","Credits",937500),("Seeker","Mech","Legendary","A-Coins",9375),("Silverthorn","Mech","Legendary","A-Coins",9375),
    ("Blizzfrost","Mech","Legendary","In-App Purchase",None),("Citadel","Mech","Legendary","In-App Purchase",None),("Deathwalker","Mech","Legendary","In-App Purchase",None),("Dreadnought","Mech","Legendary","In-App Purchase",None),("Outlaw","Mech","Legendary","In-App Purchase",None),("Parasite","Mech","Legendary","In-App Purchase",None),("Salvor","Mech","Legendary","In-App Purchase",None),("Volti","Mech","Legendary","In-App Purchase",None),

    # Common / early weapons and variants
    ("Autocannon 2","Weapon","Common","Credits",50),("Autocannon 4","Weapon","Common","Credits",0),
    ("RPG 2","Weapon","Common","Credits",50),("RPG 4","Weapon","Common","Credits",100),("RPG 6","Weapon","Common","Credits",150),
    ("Thermal Lance 2","Weapon","Common","Credits",50),("Thermal Lance 4","Weapon","Common","Credits",100),("Thermal Lance 6","Weapon","Common","Credits",150),
    ("Plasma Cannon 2","Weapon","Uncommon","A-Coins",30),("Plasma Cannon 4","Weapon","Uncommon","Credits",3450),("Plasma Cannon 6","Weapon","Uncommon","Credits",3600),
    ("Shotgun 2","Weapon","Uncommon","Credits",3150),("Shotgun 4","Weapon","Uncommon","Credits",3450),("Shotgun 8","Weapon","Uncommon","A-Coins",35),
    ("Longarm 8","Weapon","Uncommon","Credits",3700),("Longarm 10","Weapon","Uncommon","Credits",3800),("Longarm 12","Weapon","Uncommon","A-Coins",40),
    ("Gauss Rifle 4","Weapon","Rare","A-Coins",205),("Gauss Rifle 6","Weapon","Rare","A-Coins",220),("Gauss Rifle 10","Weapon","Rare","A-Coins",235),
    ("Javelin Rack 4","Weapon","Rare","Credits",20300),("Javelin Rack 6","Weapon","Rare","A-Coins",220),("Javelin Rack 8","Weapon","Rare","A-Coins",230),("Javelin Rack 12","Weapon","Rare","A-Coins",245),("Javelin Rack 16","Weapon","Rare","A-Coins",255),
    ("Pulse Cannon 4","Weapon","Rare","A-Coins",205),("Pulse Cannon 6","Weapon","Rare","Credits",21850),("Pulse Cannon 8","Weapon","Rare","Credits",22850),
    ("Rocket Mortar 8","Weapon","Rare","A-Coins",230),("Rocket Mortar 10","Weapon","Rare","Credits",23700),("Rocket Mortar 12","Weapon","Rare","A-Coins",245),
    ("Fragment Gun 6","Weapon","Rare","Credits",21850),("Fragment Gun 8","Weapon","Rare","Credits",22850),("Fragment Gun 10","Weapon","Rare","A-Coins",235),("Fragment Gun 12","Weapon","Rare","Credits",24400),("Fragment Gun 14","Weapon","Rare","A-Coins",250),

    # Epic weapons
    ("Arc Torrent 6","Weapon","Epic","Credits",77250),("Arc Torrent 10","Weapon","Epic","A-Coins",870),("Arc Torrent 12","Weapon","Epic","A-Coins",910),
    ("Cryo Launcher 6","Weapon","Epic","Credits",66550),("Cryo Launcher 8","Weapon","Epic","A-Coins",705),("Cryo Launcher 10","Weapon","Epic","Credits",73450),("Cryo Launcher 12","Weapon","Epic","A-Coins",760),("Cryo Launcher 16","Weapon","Epic","Credits",79950),
    ("Ember Gun 6","Weapon","Epic","Credits",87900),("Ember Gun 8","Weapon","Epic","Credits",95000),("Ember Gun 10","Weapon","Epic","A-Coins",1005),("Ember Gun 12","Weapon","Epic","A-Coins",1055),("Ember Gun 16","Weapon","Epic","A-Coins",1130),
    ("Fusion Cannon 6","Weapon","Epic","A-Coins",665),("Fusion Cannon 8","Weapon","Epic","A-Coins",705),("Fusion Cannon 10","Weapon","Epic","Credits",73450),("Fusion Cannon 12","Weapon","Epic","A-Coins",760),("Fusion Cannon 16","Weapon","Epic","Credits",79950),
    ("Helix Rack 6","Weapon","Epic","A-Coins",880),("Helix Rack 8","Weapon","Epic","Credits",95000),("Helix Rack 10","Weapon","Epic","A-Coins",1005),("Helix Rack 12","Weapon","Epic","A-Coins",1055),("Helix Rack 16","Weapon","Epic","Credits",112800),
    ("Missile Rack 6","Weapon","Epic","Credits",77250),("Missile Rack 8","Weapon","Epic","A-Coins",825),("Missile Rack 12","Weapon","Epic","A-Coins",910),("Missile Rack 16","Weapon","Epic","A-Coins",965),
    ("Nade Launcher 6","Weapon","Epic","A-Coins",770),("Nade Launcher 8","Weapon","Epic","A-Coins",825),("Nade Launcher 10","Weapon","Epic","Credits",87100),("Nade Launcher 12","Weapon","Epic","A-Coins",910),("Nade Launcher 16","Weapon","Epic","A-Coins",965),
    ("Quantum Gun 6","Weapon","Epic","Credits",77250),("Quantum Gun 8","Weapon","Epic","Credits",82700),("Quantum Gun 10","Weapon","Epic","Credits",87100),("Quantum Gun 12","Weapon","Epic","A-Coins",910),("Quantum Gun 16","Weapon","Epic","A-Coins",965),
    ("Stasis Beam 8","Weapon","Epic","Credits",70400),("Stasis Beam 12","Weapon","Epic","A-Coins",760),("Stasis Beam 16","Weapon","Epic","Credits",79950),
    ("Voltaic RPG 8","Weapon","Epic","Credits",70400),("Voltaic RPG 14","Weapon","Epic","Credits",78050),("Voltaic RPG 16","Weapon","Epic","A-Coins",800),
    ("Fuse Mortar 8","Weapon","Epic","A-Coins",825),("Fuse Mortar 10","Weapon","Epic","Credits",87000),("Fuse Mortar 12","Weapon","Epic","A-Coins",910),

    # Legendary weapon variants listed in Gear Hub table
    ("Berserker 6","Weapon","Legendary","Credits",600000),("Berserker 8","Weapon","Legendary","A-Coins",8275),("Berserker 10","Weapon","Legendary","Credits",712500),("Berserker 12","Weapon","Legendary","A-Coins",7500),("Berserker 16","Weapon","Legendary","Credits",827500),
    ("Blast RPG 6","Weapon","Legendary","A-Coins",6000),("Blast RPG 8","Weapon","Legendary","Credits",700000),("Blast RPG 10","Weapon","Legendary","A-Coins",7125),("Blast RPG 12","Weapon","Legendary","A-Coins",7500),("Blast RPG 16","Weapon","Legendary","Credits",827500),
    ("Carbine 8","Weapon","Legendary","A-Coins",8275),("Carbine 10","Weapon","Legendary","A-Coins",7125),("Carbine 12","Weapon","Legendary","A-Coins",7500),
    ("Chain Gun 6","Weapon","Legendary","Credits",750000),("Chain Gun 8","Weapon","Legendary","A-Coins",8275),("Chain Gun 10","Weapon","Legendary","Credits",712500),("Chain Gun 12","Weapon","Legendary","A-Coins",7500),("Chain Gun 16","Weapon","Legendary","A-Coins",8275),
    ("Disc Launcher 8","Weapon","Legendary","Credits",826750),("Disc Launcher 12","Weapon","Legendary","A-Coins",7500),("Disc Launcher 16","Weapon","Legendary","A-Coins",8275),
    ("Disruptor 6","Weapon","Legendary","Credits",755000),("Disruptor 8","Weapon","Legendary","A-Coins",8275),("Disruptor 10","Weapon","Legendary","A-Coins",7125),("Disruptor 12","Weapon","Legendary","Credits",755000),("Disruptor 16","Weapon","Legendary","Credits",826750),
    ("Dreadshot 6","Weapon","Legendary","Credits",700000),("Dreadshot 8","Weapon","Legendary","Credits",800000),("Dreadshot 10","Weapon","Legendary","A-Coins",7125),("Dreadshot 12","Weapon","Legendary","A-Coins",7500),("Dreadshot 16","Weapon","Legendary","A-Coins",8275),
    ("EM Rifle 6","Weapon","Legendary","A-Coins",7500),("EM Rifle 8","Weapon","Legendary","A-Coins",8275),("EM Rifle 10","Weapon","Legendary","A-Coins",7125),("EM Rifle 12","Weapon","Legendary","A-Coins",7500),("EM Rifle 16","Weapon","Legendary","A-Coins",8275),
    ("Gemini 6","Weapon","Legendary","Credits",600000),("Gemini 8","Weapon","Legendary","A-Coins",8275),("Gemini 10","Weapon","Legendary","Credits",712500),("Gemini 12","Weapon","Legendary","A-Coins",7500),("Gemini 16","Weapon","Legendary","A-Coins",8275),
    ("Graviton Beam 10","Weapon","Legendary","Credits",711500),("Graviton Beam 12","Weapon","Legendary","A-Coins",7500),("Graviton Beam 16","Weapon","Legendary","A-Coins",8275),
    ("Hellfire 6","Weapon","Legendary","Credits",600000),("Hellfire 8","Weapon","Legendary","A-Coins",8275),("Hellfire 10","Weapon","Legendary","Credits",700000),("Hellfire 12","Weapon","Legendary","A-Coins",7500),("Hellfire 16","Weapon","Legendary","A-Coins",8275),
    ("Hornet 6","Weapon","Legendary","Credits",600000),("Hornet 8","Weapon","Legendary","A-Coins",8000),("Hornet 10","Weapon","Legendary","Credits",700000),("Hornet 12","Weapon","Legendary","Credits",750000),("Hornet 16","Weapon","Legendary","A-Coins",8275),
    ("Howler 6","Weapon","Legendary","A-Coins",6000),("Howler 8","Weapon","Legendary","Credits",827500),("Howler 10","Weapon","Legendary","A-Coins",6750),("Howler 12","Weapon","Legendary","A-Coins",7500),("Howler 16","Weapon","Legendary","Credits",827500),
    ("Minigun 6","Weapon","Legendary","A-Coins",7500),("Minigun 8","Weapon","Legendary","A-Coins",8275),("Minigun 10","Weapon","Legendary","A-Coins",7125),("Minigun 12","Weapon","Legendary","A-Coins",7500),("Minigun 16","Weapon","Legendary","A-Coins",8275),
    ("Oracle 6","Weapon","Legendary","Credits",600000),("Oracle 8","Weapon","Legendary","A-Coins",8000),("Oracle 10","Weapon","Legendary","Credits",700000),("Oracle 12","Weapon","Legendary","Credits",750000),("Oracle 16","Weapon","Legendary","A-Coins",8275),
    ("Overdriver 6","Weapon","Legendary","A-Coins",6000),("Overdriver 8","Weapon","Legendary","Credits",827500),("Overdriver 10","Weapon","Legendary","Credits",712500),("Overdriver 12","Weapon","Legendary","A-Coins",7500),("Overdriver 16","Weapon","Legendary","A-Coins",8275),
    ("Particle Beam 6","Weapon","Legendary","Credits",600000),("Particle Beam 8","Weapon","Legendary","A-Coins",8275),("Particle Beam 10","Weapon","Legendary","Credits",712500),("Particle Beam 12","Weapon","Legendary","A-Coins",7500),("Particle Beam 16","Weapon","Legendary","A-Coins",8275),
    ("Pod Gun 6","Weapon","Legendary","A-Coins",6250),("Pod Gun 8","Weapon","Legendary","Credits",827500),("Pod Gun 10","Weapon","Legendary","Credits",712500),("Pod Gun 12","Weapon","Legendary","A-Coins",7500),("Pod Gun 16","Weapon","Legendary","A-Coins",8275),
    ("Railgun 8","Weapon","Legendary","Credits",827500),("Railgun 12","Weapon","Legendary","A-Coins",7500),("Railgun 16","Weapon","Legendary","A-Coins",8275),
    ("Reaver 6","Weapon","Legendary","A-Coins",6000),("Reaver 8","Weapon","Legendary","Credits",650000),("Reaver 10","Weapon","Legendary","Credits",700000),("Reaver 12","Weapon","Legendary","A-Coins",7000),("Reaver 16","Weapon","Legendary","Credits",800000),
    ("Repeater 6","Weapon","Legendary","Credits",712500),("Repeater 8","Weapon","Legendary","A-Coins",8275),("Repeater 10","Weapon","Legendary","Credits",675000),("Repeater 12","Weapon","Legendary","A-Coins",7500),("Repeater 16","Weapon","Legendary","A-Coins",8275),
    ("Revoker 6","Weapon","Legendary","Credits",600000),("Revoker 8","Weapon","Legendary","A-Coins",7000),("Revoker 10","Weapon","Legendary","Credits",700000),("Revoker 12","Weapon","Legendary","A-Coins",8275),("Revoker 16","Weapon","Legendary","A-Coins",8275),
    ("Savant 6","Weapon","Legendary","Credits",600000),("Savant 8","Weapon","Legendary","A-Coins",8275),("Savant 10","Weapon","Legendary","A-Coins",7125),("Savant 12","Weapon","Legendary","A-Coins",7500),("Savant 16","Weapon","Legendary","Credits",827500),
    ("Storm Rack 6","Weapon","Legendary","Credits",675000),("Storm Rack 8","Weapon","Legendary","A-Coins",8275),("Storm Rack 10","Weapon","Legendary","Credits",712500),("Storm Rack 12","Weapon","Legendary","A-Coins",7500),("Storm Rack 16","Weapon","Legendary","Credits",827500),
    ("Strike Rocket 6","Weapon","Legendary","Credits",600000),("Strike Rocket 8","Weapon","Legendary","Credits",750000),("Strike Rocket 10","Weapon","Legendary","Credits",675000),("Strike Rocket 12","Weapon","Legendary","A-Coins",7500),("Strike Rocket 16","Weapon","Legendary","A-Coins",8275),
    ("Tetra Rifle 6","Weapon","Legendary","Credits",600000),("Tetra Rifle 8","Weapon","Legendary","Credits",800000),("Tetra Rifle 10","Weapon","Legendary","Credits",700000),("Tetra Rifle 12","Weapon","Legendary","A-Coins",7500),("Tetra Rifle 16","Weapon","Legendary","A-Coins",8275),
    ("Viper 6","Weapon","Legendary","Credits",600000),("Viper 8","Weapon","Legendary","Credits",827500),("Viper 10","Weapon","Legendary","A-Coins",7125),("Viper 12","Weapon","Legendary","A-Coins",7500),("Viper 16","Weapon","Legendary","A-Coins",8275),
    ("Burrow Beam","Weapon","Legendary","In-App Purchase",None),("Charge Rocket","Weapon","Legendary","In-App Purchase",None),("Compound Beam","Weapon","Legendary","In-App Purchase",None),("Continuum","Weapon","Legendary","In-App Purchase",None),("Quasher","Weapon","Legendary","In-App Purchase",None),("Suppressor","Weapon","Legendary","In-App Purchase",None),
]

def now_iso():
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(16)
    dk = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 120000)
    return f"{salt}${dk.hex()}"

def verify_password(password, stored):
    try:
        salt, _ = stored.split('$',1)
        return hmac.compare_digest(hash_password(password, salt), stored)
    except Exception:
        return False

def init_db():
    con = db(); cur = con.cursor()
    cur.executescript('''
    CREATE TABLE IF NOT EXISTS users (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      username TEXT UNIQUE NOT NULL,
      email TEXT UNIQUE NOT NULL,
      password_hash TEXT NOT NULL,
      is_admin INTEGER DEFAULT 0,
      created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS sessions (
      token TEXT PRIMARY KEY,
      user_id INTEGER NOT NULL,
      expires_at TEXT NOT NULL,
      created_at TEXT NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS items (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      name TEXT NOT NULL,
      category TEXT NOT NULL,
      rarity TEXT,
      currency TEXT,
      default_cost INTEGER,
      source TEXT,
      updated_at TEXT NOT NULL,
      UNIQUE(name, category)
    );
    CREATE TABLE IF NOT EXISTS goals (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      item_id INTEGER,
      item_name TEXT NOT NULL,
      category TEXT NOT NULL,
      goal_type TEXT NOT NULL,
      priority TEXT DEFAULT 'Medium',
      currency TEXT NOT NULL,
      target INTEGER NOT NULL,
      current INTEGER NOT NULL DEFAULT 0,
      deadline TEXT,
      completed INTEGER DEFAULT 0,
      status TEXT DEFAULT 'active',
      created_at TEXT NOT NULL,
      updated_at TEXT NOT NULL,
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE,
      FOREIGN KEY(item_id) REFERENCES items(id) ON DELETE SET NULL
    );
    CREATE TABLE IF NOT EXISTS progress_history (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      goal_id INTEGER NOT NULL,
      amount INTEGER NOT NULL,
      note TEXT,
      created_at TEXT NOT NULL,
      FOREIGN KEY(goal_id) REFERENCES goals(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS rewards (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id INTEGER NOT NULL,
      date TEXT NOT NULL,
      login_claimed INTEGER DEFAULT 0,
      ads_watched INTEGER DEFAULT 0,
      events_played INTEGER DEFAULT 0,
      tournament_done INTEGER DEFAULT 0,
      updated_at TEXT NOT NULL,
      UNIQUE(user_id, date),
      FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    ''')
    # admin
    cur.execute("SELECT id FROM users WHERE username='admin'")
    if not cur.fetchone():
        cur.execute("INSERT INTO users(username,email,password_hash,is_admin,created_at) VALUES(?,?,?,?,?)",(
            'admin','admin@advancearena.local',hash_password('admin123'),1,now_iso()))
    source = 'Seeded from Mech Arena wiki lists; costs can be edited by admin.'
    for row in MECHS + WEAPONS:
        cur.execute("INSERT OR IGNORE INTO items(name,category,rarity,currency,default_cost,source,updated_at) VALUES(?,?,?,?,?,?,?)", (*row, source, now_iso()))

    gear_source = 'Seeded from Mech Arena Wiki Gear Hub cost table; costs can change in-game and can be edited by admin.'
    for name, category, rarity, currency, default_cost in GEAR_HUB_COSTS:
        cur.execute('''INSERT INTO items(name,category,rarity,currency,default_cost,source,updated_at)
                       VALUES(?,?,?,?,?,?,?)
                       ON CONFLICT(name,category) DO UPDATE SET
                         rarity=excluded.rarity,
                         currency=excluded.currency,
                         default_cost=excluded.default_cost,
                         source=excluded.source,
                         updated_at=excluded.updated_at''',
                    (name, category, rarity, currency, default_cost, gear_source, now_iso()))
    con.commit(); con.close()

def rowdict(row):
    return dict(row) if row else None

def rowsdict(rows):
    return [dict(r) for r in rows]

class Handler(BaseHTTPRequestHandler):
    server_version = "AdvanceArena/1.0"

    def end_headers(self):
        self.send_header('X-Content-Type-Options','nosniff')
        super().end_headers()

    def log_message(self, fmt, *args):
        print("%s - - [%s] %s" % (self.address_string(), self.log_date_time_string(), fmt%args))

    def read_json(self):
        length = int(self.headers.get('Content-Length','0'))
        if length == 0: return {}
        raw = self.rfile.read(length).decode('utf-8')
        try: return json.loads(raw)
        except Exception: raise ValueError('Invalid JSON')

    def send_json(self, obj, status=200, cookie=None):
        body = json.dumps(obj, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type','application/json; charset=utf-8')
        self.send_header('Content-Length',str(len(body)))
        if cookie: self.send_header('Set-Cookie', cookie)
        self.end_headers(); self.wfile.write(body)

    def cookie_token(self):
        cookie = self.headers.get('Cookie','')
        for part in cookie.split(';'):
            if part.strip().startswith('aa_session='):
                return part.strip().split('=',1)[1]
        return None

    def current_user(self):
        token = self.cookie_token()
        if not token: return None
        con = db(); cur = con.cursor()
        cur.execute('''SELECT u.id,u.username,u.email,u.is_admin FROM sessions s
                       JOIN users u ON u.id=s.user_id
                       WHERE s.token=? AND s.expires_at > ?''', (token, now_iso()))
        user = rowdict(cur.fetchone()); con.close(); return user

    def require_user(self):
        user = self.current_user()
        if not user:
            self.send_json({'error':'Login required'},401); return None
        return user

    def require_admin(self):
        user = self.require_user()
        if not user: return None
        if not user.get('is_admin'):
            self.send_json({'error':'Admin access required'},403); return None
        return user

    def do_GET(self):
        try:
            parsed = urlparse(self.path)
            path = parsed.path
            qs = parse_qs(parsed.query)
            if path.startswith('/api/'):
                return self.route_get(path, qs)
            return self.serve_static(path)
        except Exception as e:
            self.send_json({'error':str(e)},500)

    def do_POST(self):
        try:
            return self.route_post(urlparse(self.path).path, self.read_json())
        except ValueError as e:
            self.send_json({'error':str(e)},400)
        except Exception as e:
            self.send_json({'error':str(e)},500)

    def do_PUT(self):
        try:
            return self.route_put(urlparse(self.path).path, self.read_json())
        except ValueError as e:
            self.send_json({'error':str(e)},400)
        except Exception as e:
            self.send_json({'error':str(e)},500)

    def do_DELETE(self):
        try:
            return self.route_delete(urlparse(self.path).path)
        except Exception as e:
            self.send_json({'error':str(e)},500)

    def serve_static(self, path):
        if path == '/': path = '/index.html'
        safe = os.path.normpath(path).lstrip(os.sep)
        file_path = PUBLIC_DIR / safe
        if not file_path.exists() or not file_path.is_file():
            file_path = PUBLIC_DIR / 'index.html'
        data = file_path.read_bytes()
        ctype = mimetypes.guess_type(str(file_path))[0] or 'application/octet-stream'
        self.send_response(200)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(data)))
        self.end_headers(); self.wfile.write(data)

    def route_get(self,path,qs):
        user = None if path in ['/api/me','/api/items'] else self.require_user()
        con = db(); cur = con.cursor()
        if path == '/api/me':
            u = self.current_user(); return self.send_json({'user':u})
        if path == '/api/items':
            category = qs.get('category',[None])[0]
            if category:
                cur.execute('SELECT * FROM items WHERE category=? ORDER BY category, rarity, name',(category,))
            else:
                cur.execute('SELECT * FROM items ORDER BY category, rarity, name')
            rows = rowsdict(cur.fetchall()); con.close(); return self.send_json({'items':rows})
        if not user: return
        if path == '/api/goals':
            cur.execute('SELECT * FROM goals WHERE user_id=? ORDER BY completed ASC, CASE priority WHEN "Main Goal" THEN 0 WHEN "High" THEN 1 WHEN "Medium" THEN 2 ELSE 3 END, deadline ASC', (user['id'],))
            goals = rowsdict(cur.fetchall())
            for g in goals:
                cur.execute('SELECT amount,note,created_at FROM progress_history WHERE goal_id=? ORDER BY id DESC LIMIT 8',(g['id'],))
                g['history'] = rowsdict(cur.fetchall())
            con.close(); return self.send_json({'goals':goals})
        if path == '/api/analytics':
            cur.execute('SELECT * FROM goals WHERE user_id=?',(user['id'],)); goals=rowsdict(cur.fetchall())
            active=[g for g in goals if not g['completed']]
            completed=[g for g in goals if g['completed']]
            total_needed=sum(max(0,int(g['target'])-int(g['current'])) for g in active)
            closest=min(active, key=lambda g:max(0,int(g['target'])-int(g['current'])), default=None)
            hardest=max(active, key=lambda g:daily_need(g), default=None)
            con.close(); return self.send_json({'totalGoals':len(goals),'activeGoals':len(active),'completedGoals':len(completed),'totalNeeded':total_needed,'closestGoal':closest,'hardestGoal':hardest})
        if path == '/api/rewards':
            date = qs.get('date',[datetime.date.today().isoformat()])[0]
            cur.execute('SELECT * FROM rewards WHERE user_id=? AND date=?',(user['id'],date)); r=rowdict(cur.fetchone())
            con.close(); return self.send_json({'reward':r or {'date':date,'login_claimed':0,'ads_watched':0,'events_played':0,'tournament_done':0}})
        if path == '/api/admin/users':
            if not self.require_admin(): con.close(); return
            cur.execute('SELECT id,username,email,is_admin,created_at FROM users ORDER BY id DESC'); rows=rowsdict(cur.fetchall()); con.close(); return self.send_json({'users':rows})
        con.close(); self.send_json({'error':'Not found'},404)

    def route_post(self,path,data):
        con = db(); cur = con.cursor()
        if path == '/api/signup':
            username=(data.get('username') or '').strip()
            email=(data.get('email') or '').strip().lower()
            password=data.get('password') or ''
            if not re.match(r'^[A-Za-z0-9_]{3,20}$', username): return self.send_json({'error':'Username must be 3-20 letters/numbers/underscore'},400)
            if '@' not in email or len(password)<6: return self.send_json({'error':'Use valid email and password minimum 6 characters'},400)
            try:
                cur.execute('INSERT INTO users(username,email,password_hash,is_admin,created_at) VALUES(?,?,?,?,?)',(username,email,hash_password(password),0,now_iso()))
                con.commit()
            except sqlite3.IntegrityError:
                return self.send_json({'error':'Username or email already exists'},409)
            return self.login_response(cur.lastrowid, con)
        if path == '/api/login':
            username=(data.get('username') or '').strip()
            password=data.get('password') or ''
            cur.execute('SELECT * FROM users WHERE username=? OR email=?',(username,username.lower()))
            u=cur.fetchone()
            if not u or not verify_password(password,u['password_hash']):
                return self.send_json({'error':'Wrong username or password'},401)
            return self.login_response(u['id'], con)
        if path == '/api/logout':
            token = self.cookie_token()
            if token: cur.execute('DELETE FROM sessions WHERE token=?',(token,)); con.commit()
            return self.send_json({'ok':True}, cookie='aa_session=; Path=/; Max-Age=0; SameSite=Lax')
        user = self.require_user()
        if not user: con.close(); return
        if path == '/api/goals':
            item_id=data.get('item_id') or None
            item_name=(data.get('item_name') or data.get('name') or 'Custom Goal').strip()
            vals=(user['id'],item_id,item_name,data.get('category','Custom'),data.get('goal_type','Unlock Goal'),data.get('priority','Medium'),data.get('currency','A-Coins'),int(data.get('target') or 0),int(data.get('current') or 0),data.get('deadline') or None,now_iso(),now_iso())
            if vals[7] <= 0: return self.send_json({'error':'Target amount is required'},400)
            cur.execute('''INSERT INTO goals(user_id,item_id,item_name,category,goal_type,priority,currency,target,current,deadline,created_at,updated_at)
                           VALUES(?,?,?,?,?,?,?,?,?,?,?,?)''', vals)
            goal_id=cur.lastrowid
            cur.execute('INSERT INTO progress_history(goal_id,amount,note,created_at) VALUES(?,?,?,?)',(goal_id,vals[8],'Goal created',now_iso()))
            con.commit(); con.close(); return self.send_json({'ok':True,'id':goal_id})
        if path == '/api/items':
            if not self.require_admin(): con.close(); return
            cur.execute('INSERT INTO items(name,category,rarity,currency,default_cost,source,updated_at) VALUES(?,?,?,?,?,?,?)',(
                data.get('name','Custom Item').strip(),data.get('category','Mech'),data.get('rarity','Unknown'),data.get('currency','A-Coins'),data.get('default_cost'),data.get('source','Admin entry'),now_iso()))
            con.commit(); con.close(); return self.send_json({'ok':True,'id':cur.lastrowid})
        con.close(); self.send_json({'error':'Not found'},404)

    def login_response(self,user_id,con):
        token=secrets.token_urlsafe(32)
        expires=(datetime.datetime.utcnow()+datetime.timedelta(days=SESSION_DAYS)).replace(microsecond=0).isoformat()+"Z"
        cur=con.cursor(); cur.execute('INSERT INTO sessions(token,user_id,expires_at,created_at) VALUES(?,?,?,?)',(token,user_id,expires,now_iso())); con.commit()
        cur.execute('SELECT id,username,email,is_admin FROM users WHERE id=?',(user_id,)); user=rowdict(cur.fetchone()); con.close()
        return self.send_json({'ok':True,'user':user}, cookie=f'aa_session={token}; Path=/; Max-Age={SESSION_DAYS*86400}; HttpOnly; SameSite=Lax')

    def route_put(self,path,data):
        user = self.require_user()
        if not user: return
        con=db(); cur=con.cursor()
        if path.startswith('/api/goals/'):
            goal_id=int(path.split('/')[-1])
            cur.execute('SELECT * FROM goals WHERE id=? AND user_id=?',(goal_id,user['id'])); old=rowdict(cur.fetchone())
            if not old: con.close(); return self.send_json({'error':'Goal not found'},404)
            fields=[]; vals=[]
            for k in ['item_id','item_name','category','goal_type','priority','currency','target','current','deadline','completed','status']:
                if k in data:
                    fields.append(f'{k}=?'); vals.append(data[k])
            fields.append('updated_at=?'); vals.append(now_iso()); vals += [goal_id,user['id']]
            cur.execute(f'UPDATE goals SET {", ".join(fields)} WHERE id=? AND user_id=?', vals)
            if 'current' in data and int(data['current']) != int(old['current']):
                cur.execute('INSERT INTO progress_history(goal_id,amount,note,created_at) VALUES(?,?,?,?)',(goal_id,int(data['current']),'Progress updated',now_iso()))
            if data.get('completed') in [1, True, '1', 'true']:
                cur.execute('INSERT INTO progress_history(goal_id,amount,note,created_at) VALUES(?,?,?,?)',(goal_id,int(data.get('current') or old['current']),'Mission completed',now_iso()))
            con.commit(); con.close(); return self.send_json({'ok':True})
        if path == '/api/rewards':
            d=data.get('date') or datetime.date.today().isoformat()
            vals=(user['id'],d,int(bool(data.get('login_claimed'))),int(bool(data.get('ads_watched'))),int(bool(data.get('events_played'))),int(bool(data.get('tournament_done'))),now_iso())
            cur.execute('''INSERT INTO rewards(user_id,date,login_claimed,ads_watched,events_played,tournament_done,updated_at)
                           VALUES(?,?,?,?,?,?,?)
                           ON CONFLICT(user_id,date) DO UPDATE SET login_claimed=excluded.login_claimed, ads_watched=excluded.ads_watched,
                           events_played=excluded.events_played, tournament_done=excluded.tournament_done, updated_at=excluded.updated_at''', vals)
            con.commit(); con.close(); return self.send_json({'ok':True})
        if path.startswith('/api/items/'):
            if not self.require_admin(): con.close(); return
            item_id=int(path.split('/')[-1])
            cur.execute('UPDATE items SET name=?,category=?,rarity=?,currency=?,default_cost=?,source=?,updated_at=? WHERE id=?',(
                data.get('name'),data.get('category'),data.get('rarity'),data.get('currency'),data.get('default_cost'),data.get('source','Admin edited'),now_iso(),item_id))
            con.commit(); con.close(); return self.send_json({'ok':True})
        con.close(); self.send_json({'error':'Not found'},404)

    def route_delete(self,path):
        user = self.require_user()
        if not user: return
        con=db(); cur=con.cursor()
        if path.startswith('/api/goals/'):
            goal_id=int(path.split('/')[-1]); cur.execute('DELETE FROM goals WHERE id=? AND user_id=?',(goal_id,user['id'])); con.commit(); con.close(); return self.send_json({'ok':True})
        if path.startswith('/api/items/'):
            if not self.require_admin(): con.close(); return
            item_id=int(path.split('/')[-1]); cur.execute('DELETE FROM items WHERE id=?',(item_id,)); con.commit(); con.close(); return self.send_json({'ok':True})
        con.close(); self.send_json({'error':'Not found'},404)

def daily_need(goal):
    try:
        target=int(goal['target']); current=int(goal['current']); remain=max(0,target-current)
        d=goal.get('deadline')
        if not d: return remain
        days=(datetime.date.fromisoformat(d)-datetime.date.today()).days
        return remain / max(1, days)
    except Exception:
        return 0

if __name__ == '__main__':
    init_db()

    # Render gives your app a PORT environment variable.
    # The server must listen on 0.0.0.0, not localhost, otherwise Render cannot open it.
    host = '0.0.0.0'
    port = int(os.environ.get('PORT', 8000))

    print(f'Advance Arena running on http://{host}:{port}')
    print('Default admin: username admin / password admin123')

    ThreadingHTTPServer((host, port), Handler).serve_forever()
