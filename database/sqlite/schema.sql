/* ==================================================
   ADVENTURE TRIP & TREK MANAGEMENT SYSTEM
   SQLite version of the schema (used by backend/db.js)
   This file is for reference only — the backend creates
   these same tables automatically when it starts.
   ================================================== */

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    user_id        INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name      TEXT NOT NULL,
    email          TEXT NOT NULL UNIQUE,
    password_hash  TEXT NOT NULL,
    phone          TEXT,
    role           TEXT NOT NULL DEFAULT 'customer'
                   CHECK (role IN ('customer', 'admin')),
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
    status            TEXT DEFAULT 'available'
                      CHECK (status IN ('available', 'busy', 'inactive'))
);

CREATE TABLE IF NOT EXISTS vehicles (
    vehicle_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    vehicle_type  TEXT NOT NULL CHECK (vehicle_type IN ('bus', 'microbus', 'jeep', 'boat')),
    reg_number    TEXT NOT NULL UNIQUE,
    capacity      INTEGER NOT NULL CHECK (capacity > 0),
    status        TEXT DEFAULT 'available'
                  CHECK (status IN ('available', 'in_use', 'maintenance'))
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
    status          TEXT DEFAULT 'upcoming'
                    CHECK (status IN ('upcoming', 'ongoing', 'completed', 'cancelled'))
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
    booking_status  TEXT DEFAULT 'pending'
                    CHECK (booking_status IN ('pending', 'confirmed', 'cancelled')),
    booked_at       TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS payments (
    payment_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id      INTEGER NOT NULL REFERENCES bookings(booking_id) ON DELETE CASCADE,
    amount          REAL NOT NULL CHECK (amount >= 0),
    method          TEXT NOT NULL CHECK (method IN ('bkash', 'nagad', 'card', 'cash')),
    payment_status  TEXT DEFAULT 'paid'
                    CHECK (payment_status IN ('paid', 'failed', 'refunded')),
    paid_at         TEXT DEFAULT CURRENT_TIMESTAMP
);
