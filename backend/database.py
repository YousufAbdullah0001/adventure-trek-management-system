"""
database.py

Creates (if needed) and seeds the SQLite database using Python's built-in
sqlite3 module. No external database driver is required.
"""

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "adventure_trek.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    phone          TEXT,
    role           TEXT NOT NULL DEFAULT 'customer' CHECK (role IN ('customer', 'admin')),
    created_at     TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS destinations (
    destination_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT NOT NULL,
    region         TEXT,
    country        TEXT NOT NULL DEFAULT 'Bangladesh',
    description    TEXT
);

CREATE TABLE IF NOT EXISTS guides (
    guide_id          INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name         TEXT NOT NULL,
    phone             TEXT NOT NULL,
    experience_years  INTEGER NOT NULL CHECK (experience_years >= 0),
    languages         TEXT,
    status            TEXT DEFAULT 'available' CHECK (status IN ('available', 'busy', 'inactive'))
);

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_type  TEXT NOT NULL CHECK (vehicle_type IN ('bus', 'microbus', 'jeep', 'boat')),
    reg_number    TEXT NOT NULL UNIQUE,
    capacity      INTEGER NOT NULL CHECK (capacity > 0),
    status        TEXT DEFAULT 'available' CHECK (status IN ('available', 'in_use', 'maintenance'))
);

CREATE TABLE IF NOT EXISTS activities (
    activity_id  INTEGER PRIMARY KEY AUTOINCREMENT,
    name         TEXT NOT NULL,
    description  TEXT
);

CREATE TABLE IF NOT EXISTS trips (
    trip_id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title           TEXT NOT NULL,
    destination_id  INTEGER NOT NULL REFERENCES destinations(destination_id),
    guide_id        INTEGER REFERENCES guides(guide_id) ON DELETE SET NULL,
    vehicle_id      INTEGER REFERENCES vehicles(vehicle_id) ON DELETE SET NULL,
    start_date      TEXT NOT NULL,
    end_date        TEXT NOT NULL CHECK (end_date >= start_date),
    price           REAL NOT NULL CHECK (price >= 0),
    difficulty      TEXT NOT NULL CHECK (difficulty IN ('easy', 'moderate', 'hard')),
    max_seats       INTEGER NOT NULL CHECK (max_seats > 0),
    status          TEXT DEFAULT 'upcoming' CHECK (status IN ('upcoming', 'ongoing', 'completed', 'cancelled'))
);

CREATE TABLE IF NOT EXISTS trip_activities (
    trip_id      INTEGER NOT NULL REFERENCES trips(trip_id) ON DELETE CASCADE,
    activity_id  INTEGER NOT NULL REFERENCES activities(activity_id) ON DELETE CASCADE,
    PRIMARY KEY (trip_id, activity_id)
);

CREATE TABLE IF NOT EXISTS bookings (
    booking_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id         INTEGER NOT NULL REFERENCES users(user_id),
    trip_id         INTEGER NOT NULL REFERENCES trips(trip_id),
    seats           INTEGER NOT NULL CHECK (seats > 0),
    total_amount    REAL NOT NULL CHECK (total_amount >= 0),
    booking_status  TEXT DEFAULT 'pending' CHECK (booking_status IN ('pending', 'confirmed', 'cancelled')),
    booked_at       TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id      INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    amount          REAL NOT NULL CHECK (amount >= 0),
    method          TEXT NOT NULL CHECK (method IN ('bkash', 'nagad', 'card', 'cash')),
    payment_status  TEXT DEFAULT 'paid' CHECK (payment_status IN ('paid', 'failed', 'refunded')),
    paid_at         TEXT DEFAULT CURRENT_TIMESTAMP
);
"""


def get_connection():
    """Returns a new SQLite connection with rows accessible by column name."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db():
    """Creates the tables (if missing) and loads sample data once."""
    conn = get_connection()
    conn.executescript(SCHEMA)

    user_count = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]

    if user_count == 0:
        print("Empty database detected. Loading sample data...")
        seed(conn)
        print("Sample data loaded.")

    conn.close()


def seed(conn):
    cur = conn.cursor()

    cur.executemany(
        "INSERT INTO users (full_name, email, password_hash, phone, role) VALUES (?, ?, ?, ?, ?)",
        [
            ("Admin One", "admin@trek.com", "hash_admin", "01700000001", "admin"),
            ("Rahim Uddin", "rahim@mail.com", "hash1", "01711111111", "customer"),
            ("Karim Hasan", "karim@mail.com", "hash2", "01722222222", "customer"),
            ("Nusrat Jahan", "nusrat@mail.com", "hash3", "01733333333", "customer"),
            ("Mitu Akter", "mitu@mail.com", "hash4", "01744444444", "customer"),
            ("Shakil Rana", "shakil@mail.com", "hash5", "01755555555", "customer"),
            ("Farzana Haque", "farzana@mail.com", "hash6", "01766666666", "customer"),
        ],
    )

    cur.executemany(
        "INSERT INTO destinations (name, region, country, description) VALUES (?, ?, ?, ?)",
        [
            ("Sajek Valley", "Rangamati", "Bangladesh", "Hilltop clouds and tribal villages"),
            ("Bandarban Nilgiri", "Bandarban", "Bangladesh", "High altitude cloud view point"),
            ("Sundarbans", "Khulna", "Bangladesh", "Mangrove forest and wildlife"),
            ("Saint Martin", "Cox's Bazar", "Bangladesh", "Coral island"),
            ("Srimangal", "Sylhet", "Bangladesh", "Tea gardens and lush greenery"),
            ("Kuakata", "Patuakhali", "Bangladesh", "Sea beach with sunrise and sunset view"),
        ],
    )

    cur.executemany(
        "INSERT INTO guides (full_name, phone, experience_years, languages, status) VALUES (?, ?, ?, ?, ?)",
        [
            ("Jamal Chakma", "01811111111", 8, "Bangla, English", "available"),
            ("Sumon Marma", "01822222222", 5, "Bangla", "busy"),
            ("Tanvir Ahmed", "01833333333", 10, "Bangla, English, Hindi", "available"),
            ("Liton Barua", "01844444444", 4, "Bangla, English", "available"),
        ],
    )

    cur.executemany(
        "INSERT INTO vehicles (vehicle_type, reg_number, capacity, status) VALUES (?, ?, ?, ?)",
        [
            ("microbus", "DHAKA-METRO-11-1234", 12, "available"),
            ("bus", "DHAKA-METRO-14-5678", 40, "available"),
            ("jeep", "CTG-METRO-12-9999", 8, "in_use"),
            ("boat", "KHULNA-METRO-02-4321", 20, "available"),
        ],
    )

    cur.executemany(
        "INSERT INTO activities (name, description) VALUES (?, ?)",
        [
            ("Trekking", "Guided hill trekking"),
            ("Camping", "Overnight tent camping"),
            ("Boat Ride", "River or sea boat tour"),
            ("Bonfire", "Evening bonfire and music"),
            ("Tea Garden Walk", "Guided walk through tea estates"),
            ("Beach Walk", "Sunrise and sunset beach walk"),
        ],
    )

    cur.executemany(
        """INSERT INTO trips
           (title, destination_id, guide_id, vehicle_id, start_date, end_date, price, difficulty, max_seats, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        [
            ("Sajek Cloud Camping", 1, 1, 1, "2026-12-05", "2026-12-07", 6500.0, "easy", 12, "upcoming"),
            ("Nilgiri Sunrise Trek", 2, 2, 3, "2026-12-12", "2026-12-14", 8500.0, "moderate", 8, "upcoming"),
            ("Sundarbans Wildlife Expedition", 3, 3, 2, "2026-12-20", "2026-12-23", 12000.0, "moderate", 30, "upcoming"),
            ("Saint Martin Coral Tour", 4, 4, 4, "2026-12-27", "2026-12-30", 9500.0, "easy", 25, "upcoming"),
            ("Srimangal Tea Trail", 5, 1, 1, "2027-01-10", "2027-01-12", 5500.0, "easy", 15, "upcoming"),
            ("Kuakata Sunrise-Sunset Tour", 6, 4, 2, "2026-11-01", "2026-11-03", 7000.0, "easy", 20, "completed"),
        ],
    )

    cur.executemany(
        "INSERT INTO trip_activities (trip_id, activity_id) VALUES (?, ?)",
        [
            (1, 1), (1, 2), (1, 4),
            (2, 1), (2, 2),
            (3, 3), (3, 1),
            (4, 3), (4, 6),
            (5, 5), (5, 1),
            (6, 6), (6, 3),
        ],
    )

    cur.executemany(
        "INSERT INTO bookings (user_id, trip_id, seats, total_amount, booking_status) VALUES (?, ?, ?, ?, ?)",
        [
            (2, 1, 2, 13000.0, "confirmed"),
            (3, 2, 1, 8500.0, "confirmed"),
            (4, 3, 3, 36000.0, "pending"),
            (5, 4, 2, 19000.0, "confirmed"),
            (6, 5, 1, 5500.0, "pending"),
            (7, 6, 4, 28000.0, "confirmed"),
        ],
    )

    cur.executemany(
        "INSERT INTO payments (booking_id, amount, method, payment_status) VALUES (?, ?, ?, ?)",
        [
            (1, 13000.0, "bkash", "paid"),
            (2, 8500.0, "card", "paid"),
            (4, 19000.0, "nagad", "paid"),
            (6, 28000.0, "cash", "paid"),
        ],
    )

    conn.commit()
