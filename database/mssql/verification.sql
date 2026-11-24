
USE adventure_trek;
GO

-- 1. Check all tables
SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
GO

-- 2. Check Primary Keys and Foreign Keys
SELECT
    TABLE_NAME,
    CONSTRAINT_NAME,
    CONSTRAINT_TYPE
FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
ORDER BY TABLE_NAME, CONSTRAINT_TYPE;
GO

-- 3. Check sample data in all tables
SELECT * FROM users;
SELECT * FROM destinations;
SELECT * FROM guides;
SELECT * FROM vehicles;
SELECT * FROM activities;
SELECT * FROM trips;
SELECT * FROM trip_activities;
SELECT * FROM bookings;
SELECT * FROM payments;
GO

-- 4. Search trips by budget, difficulty and date
SELECT
    t.title,
    d.name AS destination,
    t.price,
    t.difficulty,
    t.start_date
FROM trips t
JOIN destinations d
    ON t.destination_id = d.destination_id
WHERE t.price <= 9000
  AND t.difficulty = 'moderate'
  AND t.start_date >= '2026-12-01';
GO

-- 5. Remaining seats per trip
SELECT
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
GROUP BY t.trip_id, t.title, t.max_seats;
GO

-- 6. Total paid revenue
SELECT
    COALESCE(SUM(amount), 0) AS total_revenue
FROM payments
WHERE payment_status = 'paid';
GO

-- 7. Revenue per trip
SELECT
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
GROUP BY t.trip_id, t.title;
GO

-- 8. Trip and assigned activities
SELECT
    t.title AS trip_name,
    a.name AS activity_name
FROM trips t
JOIN trip_activities ta
    ON t.trip_id = ta.trip_id
JOIN activities a
    ON ta.activity_id = a.activity_id
ORDER BY t.trip_id;
GO

-- 9. Booking and payment report
SELECT
    b.booking_id,
    u.full_name AS customer,
    t.title AS trip,
    b.seats,
    b.total_amount,
    b.booking_status,
    p.method,
    p.amount AS paid_amount,
    p.payment_status
FROM bookings b
JOIN users u ON b.user_id = u.user_id
JOIN trips t ON b.trip_id = t.trip_id
LEFT JOIN payments p ON b.booking_id = p.booking_id
ORDER BY b.booking_id;
GO
