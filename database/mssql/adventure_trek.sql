
/* ==================================================
   ADVENTURE TRIP & TREK MANAGEMENT SYSTEM
   MICROSOFT SQL SERVER - T-SQL
   9 TABLES + CONSTRAINTS + SAMPLE DATA
   ================================================== */

-- STEP 1: CREATE DATABASE
-- NOTE: Requires CREATE DATABASE permission.

USE master;
GO

IF DB_ID('adventure_trek') IS NULL
BEGIN
    CREATE DATABASE adventure_trek;
END;
GO

USE adventure_trek;
GO

/* ==================================================
   STEP 2: CREATE USERS TABLE
   ================================================== */

CREATE TABLE users (
    user_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    phone VARCHAR(20),

    role VARCHAR(20) NOT NULL
        CONSTRAINT DF_users_role DEFAULT 'customer',

    created_at DATETIME
        CONSTRAINT DF_users_created DEFAULT GETDATE(),

    CONSTRAINT CHK_users_role
        CHECK (role IN ('customer', 'admin'))
);
GO

/* ==================================================
   STEP 3: CREATE DESTINATIONS TABLE
   ================================================== */

CREATE TABLE destinations (
    destination_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    region VARCHAR(100),

    country VARCHAR(50) NOT NULL
        CONSTRAINT DF_dest_country DEFAULT 'Bangladesh',

    description VARCHAR(MAX)
);
GO

/* ==================================================
   STEP 4: CREATE GUIDES TABLE
   ================================================== */

CREATE TABLE guides (
    guide_id INT IDENTITY(1,1) PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    experience_years INT NOT NULL,
    languages VARCHAR(100),

    status VARCHAR(20)
        CONSTRAINT DF_guides_status DEFAULT 'available',

    CONSTRAINT CHK_guides_experience
        CHECK (experience_years >= 0),

    CONSTRAINT CHK_guides_status
        CHECK (status IN ('available', 'busy', 'inactive'))
);
GO

/* ==================================================
   STEP 5: CREATE VEHICLES TABLE
   ================================================== */

CREATE TABLE vehicles (
    vehicle_id INT IDENTITY(1,1) PRIMARY KEY,

    vehicle_type VARCHAR(20) NOT NULL,
    reg_number VARCHAR(30) NOT NULL UNIQUE,
    capacity INT NOT NULL,

    status VARCHAR(20)
        CONSTRAINT DF_vehicles_status DEFAULT 'available',

    CONSTRAINT CHK_vehicle_type
        CHECK (vehicle_type IN ('bus', 'microbus', 'jeep', 'boat')),

    CONSTRAINT CHK_vehicle_capacity
        CHECK (capacity > 0),

    CONSTRAINT CHK_vehicle_status
        CHECK (status IN ('available', 'in_use', 'maintenance'))
);
GO

/* ==================================================
   STEP 6: CREATE ACTIVITIES TABLE
   ================================================== */

CREATE TABLE activities (
    activity_id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(MAX)
);
GO

/* ==================================================
   STEP 7: CREATE TRIPS TABLE
   ================================================== */

CREATE TABLE trips (
    trip_id INT IDENTITY(1,1) PRIMARY KEY,
    title VARCHAR(150) NOT NULL,

    destination_id INT NOT NULL,
    guide_id INT NULL,
    vehicle_id INT NULL,

    start_date DATE NOT NULL,
    end_date DATE NOT NULL,

    price DECIMAL(10,2) NOT NULL,
    difficulty VARCHAR(20) NOT NULL,
    max_seats INT NOT NULL,

    status VARCHAR(20)
        CONSTRAINT DF_trips_status DEFAULT 'upcoming',

    CONSTRAINT CHK_trip_price
        CHECK (price >= 0),

    CONSTRAINT CHK_trip_seats
        CHECK (max_seats > 0),

    CONSTRAINT CHK_trip_dates
        CHECK (end_date >= start_date),

    CONSTRAINT CHK_trip_difficulty
        CHECK (difficulty IN ('easy', 'moderate', 'hard')),

    CONSTRAINT CHK_trip_status
        CHECK (status IN ('upcoming', 'ongoing', 'completed', 'cancelled')),

    CONSTRAINT FK_trips_destination
        FOREIGN KEY (destination_id)
        REFERENCES destinations(destination_id),

    CONSTRAINT FK_trips_guide
        FOREIGN KEY (guide_id)
        REFERENCES guides(guide_id)
        ON DELETE SET NULL,

    CONSTRAINT FK_trips_vehicle
        FOREIGN KEY (vehicle_id)
        REFERENCES vehicles(vehicle_id)
        ON DELETE SET NULL
);
GO

/* ==================================================
   STEP 8: CREATE TRIP ACTIVITIES TABLE
   MANY-TO-MANY RELATIONSHIP
   ================================================== */

CREATE TABLE trip_activities (
    trip_id INT NOT NULL,
    activity_id INT NOT NULL,

    CONSTRAINT PK_trip_activities
        PRIMARY KEY (trip_id, activity_id),

    CONSTRAINT FK_ta_trip
        FOREIGN KEY (trip_id)
        REFERENCES trips(trip_id)
        ON DELETE CASCADE,

    CONSTRAINT FK_ta_activity
        FOREIGN KEY (activity_id)
        REFERENCES activities(activity_id)
        ON DELETE CASCADE
);
GO

/* ==================================================
   STEP 9: CREATE BOOKINGS TABLE
   ================================================== */

CREATE TABLE bookings (
    booking_id INT IDENTITY(1,1) PRIMARY KEY,

    user_id INT NOT NULL,
    trip_id INT NOT NULL,

    seats INT NOT NULL,
    total_amount DECIMAL(10,2) NOT NULL,

    booking_status VARCHAR(20)
        CONSTRAINT DF_bookings_status DEFAULT 'pending',

    booked_at DATETIME
        CONSTRAINT DF_bookings_date DEFAULT GETDATE(),

    CONSTRAINT CHK_booking_seats
        CHECK (seats > 0),

    CONSTRAINT CHK_booking_amount
        CHECK (total_amount >= 0),

    CONSTRAINT CHK_booking_status
        CHECK (booking_status IN ('pending', 'confirmed', 'cancelled')),

    CONSTRAINT FK_bookings_user
        FOREIGN KEY (user_id)
        REFERENCES users(user_id),

    CONSTRAINT FK_bookings_trip
        FOREIGN KEY (trip_id)
        REFERENCES trips(trip_id)
);
GO

/* ==================================================
   STEP 10: CREATE PAYMENTS TABLE
   ================================================== */

CREATE TABLE payments (
    payment_id INT IDENTITY(1,1) PRIMARY KEY,

    booking_id INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    method VARCHAR(20) NOT NULL,

    payment_status VARCHAR(20)
        CONSTRAINT DF_payments_status DEFAULT 'paid',

    paid_at DATETIME
        CONSTRAINT DF_payments_date DEFAULT GETDATE(),

    CONSTRAINT CHK_payment_amount
        CHECK (amount >= 0),

    CONSTRAINT CHK_payment_method
        CHECK (method IN ('bkash', 'nagad', 'card', 'cash')),

    CONSTRAINT CHK_payment_status
        CHECK (payment_status IN ('paid', 'failed', 'refunded')),

    CONSTRAINT FK_payments_booking
        FOREIGN KEY (booking_id)
        REFERENCES bookings(booking_id)
        ON DELETE CASCADE
);
GO

PRINT 'ALL 9 TABLES CREATED SUCCESSFULLY';
GO

/* ==================================================
   STEP 11: INSERT SAMPLE USERS
   ================================================== */

INSERT INTO users
(full_name, email, password_hash, phone, role)
VALUES
('Admin One', 'admin@trek.com', 'hash_admin', '01700000001', 'admin'),
('Rahim Uddin', 'rahim@mail.com', 'hash1', '01711111111', 'customer'),
('Karim Hasan', 'karim@mail.com', 'hash2', '01722222222', 'customer'),
('Nusrat Jahan', 'nusrat@mail.com', 'hash3', '01733333333', 'customer');
GO

/* ==================================================
   STEP 12: INSERT DESTINATIONS
   ================================================== */

INSERT INTO destinations
(name, region, country, description)
VALUES
('Sajek Valley', 'Rangamati', 'Bangladesh',
 'Hilltop clouds and tribal villages'),

('Bandarban Nilgiri', 'Bandarban', 'Bangladesh',
 'High altitude cloud view point'),

('Sundarbans', 'Khulna', 'Bangladesh',
 'Mangrove forest and wildlife'),

('Saint Martin', 'Cox''s Bazar', 'Bangladesh',
 'Coral island');
GO

/* ==================================================
   STEP 13: INSERT GUIDES
   ================================================== */

INSERT INTO guides
(full_name, phone, experience_years, languages)
VALUES
('Jamal Chakma', '01811111111', 8, 'Bangla, English'),
('Sumon Marma', '01822222222', 5, 'Bangla'),
('Tanvir Ahmed', '01833333333', 10, 'Bangla, English, Hindi');
GO

/* ==================================================
   STEP 14: INSERT VEHICLES
   ================================================== */

INSERT INTO vehicles
(vehicle_type, reg_number, capacity)
VALUES
('microbus', 'DHAKA-METRO-11-1234', 12),
('bus', 'DHAKA-METRO-14-5678', 40),
('jeep', 'CTG-METRO-12-9999', 8);
GO

/* ==================================================
   STEP 15: INSERT ACTIVITIES
   ================================================== */

INSERT INTO activities (name, description)
VALUES
('Trekking', 'Guided hill trekking'),
('Camping', 'Overnight tent camping'),
('Boat Ride', 'River or sea boat tour'),
('Bonfire', 'Evening bonfire and music');
GO

/* ==================================================
   STEP 16: INSERT TRIPS
   ================================================== */

INSERT INTO trips
(title, destination_id, guide_id, vehicle_id,
 start_date, end_date, price, difficulty, max_seats)
VALUES
('Sajek Cloud Camping', 1, 1, 1,
 '2026-12-05', '2026-12-07', 6500.00, 'easy', 12),

('Nilgiri Sunrise Trek', 2, 2, 3,
 '2026-12-12', '2026-12-14', 8500.00, 'moderate', 8),

('Sundarbans Wildlife Expedition', 3, 3, 2,
 '2026-12-20', '2026-12-23', 12000.00, 'moderate', 30);
GO

/* ==================================================
   STEP 17: INSERT TRIP ACTIVITIES
   ================================================== */

INSERT INTO trip_activities (trip_id, activity_id)
VALUES
(1,1),(1,2),(1,4),
(2,1),(2,2),
(3,3),(3,1);
GO

/* ==================================================
   STEP 18: INSERT BOOKINGS
   ================================================== */

INSERT INTO bookings
(user_id, trip_id, seats, total_amount, booking_status)
VALUES
(2, 1, 2, 13000.00, 'confirmed'),
(3, 2, 1, 8500.00, 'confirmed'),
(4, 3, 3, 36000.00, 'pending');
GO

/* ==================================================
   STEP 19: INSERT PAYMENTS
   ================================================== */

INSERT INTO payments
(booking_id, amount, method, payment_status)
VALUES
(1, 13000.00, 'bkash', 'paid'),
(2, 8500.00, 'card', 'paid');
GO

PRINT 'SAMPLE DATA INSERTED SUCCESSFULLY';
GO

/* ==================================================
   STEP 20: VERIFY ALL 9 TABLES
   ================================================== */

SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
AND TABLE_SCHEMA = 'dbo'
ORDER BY TABLE_NAME;
GO

/* ==================================================
   STEP 21: CHECK SAMPLE DATA COUNTS
   ================================================== */

SELECT 'users' AS table_name, COUNT(*) AS total_records FROM users
UNION ALL
SELECT 'destinations', COUNT(*) FROM destinations
UNION ALL
SELECT 'guides', COUNT(*) FROM guides
UNION ALL
SELECT 'vehicles', COUNT(*) FROM vehicles
UNION ALL
SELECT 'activities', COUNT(*) FROM activities
UNION ALL
SELECT 'trips', COUNT(*) FROM trips
UNION ALL
SELECT 'trip_activities', COUNT(*) FROM trip_activities
UNION ALL
SELECT 'bookings', COUNT(*) FROM bookings
UNION ALL
SELECT 'payments', COUNT(*) FROM payments;
GO

/* ==================================================
   STEP 22: DASHBOARD STATISTICS
   ================================================== */

SELECT
    (SELECT COUNT(*) FROM users) AS total_users,

    (SELECT COUNT(*) FROM destinations) AS total_destinations,

    (SELECT COUNT(*) FROM trips) AS total_trips,

    (SELECT COUNT(*) FROM bookings) AS total_bookings,

    (SELECT COUNT(*) FROM payments
     WHERE payment_status = 'paid') AS paid_payments,

    (SELECT COALESCE(SUM(amount), 0)
     FROM payments
     WHERE payment_status = 'paid') AS total_revenue;
GO

/* ==================================================
   STEP 23: REMAINING SEATS
   ================================================== */

SELECT
    t.trip_id,
    t.title,
    t.max_seats,

    COALESCE(SUM(
        CASE
            WHEN b.booking_status <> 'cancelled'
            THEN b.seats
            ELSE 0
        END
    ), 0) AS booked_seats,

    t.max_seats - COALESCE(SUM(
        CASE
            WHEN b.booking_status <> 'cancelled'
            THEN b.seats
            ELSE 0
        END
    ), 0) AS seats_left

FROM trips t

LEFT JOIN bookings b
    ON t.trip_id = b.trip_id

GROUP BY t.trip_id, t.title, t.max_seats
ORDER BY t.trip_id;
GO

/* ==================================================
   STEP 24: REVENUE PER TRIP
   ================================================== */

SELECT
    t.trip_id,
    t.title,

    COALESCE(SUM(
        CASE
            WHEN p.payment_status = 'paid'
            THEN p.amount
            ELSE 0
        END
    ), 0) AS revenue

FROM trips t

LEFT JOIN bookings b
    ON t.trip_id = b.trip_id

LEFT JOIN payments p
    ON b.booking_id = p.booking_id

GROUP BY t.trip_id, t.title
ORDER BY t.trip_id;
GO

/* ==================================================
   STEP 25: COMPLETE BOOKING REPORT
   ================================================== */

SELECT
    b.booking_id,
    u.full_name AS customer_name,
    t.title AS trip_name,
    b.seats,
    b.total_amount,
    b.booking_status,
    p.method AS payment_method,
    p.amount AS paid_amount,
    p.payment_status

FROM bookings b

INNER JOIN users u
    ON b.user_id = u.user_id

INNER JOIN trips t
    ON b.trip_id = t.trip_id

LEFT JOIN payments p
    ON b.booking_id = p.booking_id

ORDER BY b.booking_id;
GO

/* ==================================================
   STEP 26: TRIP SEARCH
   ================================================== */

SELECT
    t.title,
    d.name AS destination,
    t.price,
    t.difficulty,
    t.start_date

FROM trips t

INNER JOIN destinations d
    ON t.destination_id = d.destination_id

WHERE t.price <= 9000
AND t.difficulty = 'moderate'
AND t.start_date >= '2026-12-01';
GO

/* ==================================================
   STEP 27: TRIP ACTIVITIES REPORT
   ================================================== */

SELECT
    t.title AS trip_name,
    a.name AS activity_name

FROM trip_activities ta

INNER JOIN trips t
    ON ta.trip_id = t.trip_id

INNER JOIN activities a
    ON ta.activity_id = a.activity_id

ORDER BY t.trip_id;
GO

PRINT '==========================================';
PRINT 'ADVENTURE TREK DATABASE READY';
PRINT '9 TABLES CREATED';
PRINT 'SAMPLE DATA INSERTED';
PRINT 'DASHBOARD QUERIES COMPLETED';
PRINT '==========================================';
GO
