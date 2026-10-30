"""SQLite helpers: connection, schema and auto-seeding."""
import os
import sqlite3

from seed import run_seed

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "market.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    display_name  TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS symbols (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT UNIQUE NOT NULL,
    name   TEXT NOT NULL,
    sector TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS prices (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    symbol_id INTEGER NOT NULL REFERENCES symbols(id),
    date      TEXT NOT NULL,
    close     REAL NOT NULL,
    volume    REAL NOT NULL,
    UNIQUE(symbol_id, date)
);

CREATE TABLE IF NOT EXISTS news (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    headline  TEXT NOT NULL,
    summary   TEXT NOT NULL,
    source    TEXT NOT NULL,
    published TEXT NOT NULL,
    ticker    TEXT,              -- NULL means market-wide event
    sentiment INTEGER NOT NULL,  -- +1 positive / 0 neutral / -1 negative
    magnitude REAL NOT NULL,     -- engineered price impact in percent
    is_market INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS watchlist (
    user_id   INTEGER NOT NULL REFERENCES users(id),
    symbol_id INTEGER NOT NULL REFERENCES symbols(id),
    added_at  TEXT NOT NULL,
    UNIQUE(user_id, symbol_id)
);
"""


def get_conn():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = get_conn()
    try:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM symbols").fetchone()[0] == 0:
            run_seed(conn)
        conn.commit()
    finally:
        conn.close()


def q(sql, params=()):
    conn = get_conn()
    try:
        return conn.execute(sql, params).fetchall()
    finally:
        conn.close()


def q1(sql, params=()):
    rows = q(sql, params)
    return rows[0] if rows else None


def x(sql, params=()):
    conn = get_conn()
    try:
        cur = conn.execute(sql, params)
        conn.commit()
        return cur
    finally:
        conn.close()
