"""
app.py

Flask application for the Adventure Trek dashboard.

This page has NO JavaScript. Every number, table row and chart bar is
calculated here in Python, filled into the HTML template with Jinja2,
and sent to the browser already complete. Refreshing the page re-runs
these queries against the SQLite database.

On top of the read-only dashboard, this file also exposes a simple
"Manage Data" area (/manage/<entity>) with plain HTML forms to add,
edit and delete rows in any of the 9 tables — all through normal
GET/POST requests and page reloads, still with no JavaScript.
"""

import sqlite3
from datetime import date
from flask import Flask, render_template, request, redirect, url_for, flash
from database import get_connection, init_db

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-me"  # only used to show flash messages


@app.template_filter("money")
def money_filter(value):
    """Formats a number as ৳ with thousands separators, e.g. ৳21,500"""
    return "৳{:,.0f}".format(value)


# =======================================================================
# MANAGE DATA (CRUD) — configuration for all 9 tables
# =======================================================================
# Each entry describes one table: its primary key, the columns shown in
# the list view, and the form fields used to add/edit a row. Foreign-key
# fields (type "select_fk") have their dropdown options loaded from the
# referenced table at request time.

ENTITIES = {
    "destinations": {
        "label": "Destinations",
        "table": "destinations",
        "id_field": "destination_id",
        "columns": ["destination_id", "name", "region", "country", "description"],
        "fields": [
            {"name": "name", "label": "Name", "type": "text", "required": True},
            {"name": "region", "label": "Region", "type": "text"},
            {"name": "country", "label": "Country", "type": "text", "default": "Bangladesh"},
            {"name": "description", "label": "Description", "type": "textarea"},
        ],
    },
    "guides": {
        "label": "Guides",
        "table": "guides",
        "id_field": "guide_id",
        "columns": ["guide_id", "full_name", "phone", "experience_years", "languages", "status"],
        "fields": [
            {"name": "full_name", "label": "Full name", "type": "text", "required": True},
            {"name": "phone", "label": "Phone", "type": "text", "required": True},
            {"name": "experience_years", "label": "Experience (years)", "type": "number", "required": True},
            {"name": "languages", "label": "Languages", "type": "text"},
            {"name": "status", "label": "Status", "type": "select",
             "choices": ["available", "busy", "inactive"], "default": "available"},
        ],
    },
    "vehicles": {
        "label": "Vehicles",
        "table": "vehicles",
        "id_field": "vehicle_id",
        "columns": ["vehicle_id", "vehicle_type", "reg_number", "capacity", "status"],
        "fields": [
            {"name": "vehicle_type", "label": "Type", "type": "select",
             "choices": ["bus", "microbus", "jeep", "boat"], "required": True},
            {"name": "reg_number", "label": "Registration number", "type": "text", "required": True},
            {"name": "capacity", "label": "Capacity", "type": "number", "required": True},
            {"name": "status", "label": "Status", "type": "select",
             "choices": ["available", "in_use", "maintenance"], "default": "available"},
        ],
    },
    "activities": {
        "label": "Activities",
        "table": "activities",
        "id_field": "activity_id",
        "columns": ["activity_id", "name", "description"],
        "fields": [
            {"name": "name", "label": "Name", "type": "text", "required": True},
            {"name": "description", "label": "Description", "type": "textarea"},
        ],
    },
    "users": {
        "label": "Users",
        "table": "users",
        "id_field": "user_id",
        "columns": ["user_id", "full_name", "email", "phone", "role"],
        "fields": [
            {"name": "full_name", "label": "Full name", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "text", "required": True},
            {"name": "password_hash", "label": "Password", "type": "text", "required": True},
            {"name": "phone", "label": "Phone", "type": "text"},
            {"name": "role", "label": "Role", "type": "select",
             "choices": ["customer", "admin"], "default": "customer"},
        ],
    },
    "trips": {
        "label": "Trips",
        "table": "trips",
        "id_field": "trip_id",
        "columns": ["trip_id", "title", "destination_id", "guide_id", "vehicle_id",
                    "start_date", "end_date", "price", "difficulty", "max_seats", "status"],
        "fields": [
            {"name": "title", "label": "Title", "type": "text", "required": True},
            {"name": "destination_id", "label": "Destination", "type": "select_fk",
             "options_table": "destinations", "options_id": "destination_id",
             "options_label": "name", "required": True},
            {"name": "guide_id", "label": "Guide", "type": "select_fk",
             "options_table": "guides", "options_id": "guide_id",
             "options_label": "full_name", "nullable": True},
            {"name": "vehicle_id", "label": "Vehicle", "type": "select_fk",
             "options_table": "vehicles", "options_id": "vehicle_id",
             "options_label": "reg_number", "nullable": True},
            {"name": "start_date", "label": "Start date", "type": "date", "required": True},
            {"name": "end_date", "label": "End date", "type": "date", "required": True},
            {"name": "price", "label": "Price (BDT)", "type": "number", "required": True},
            {"name": "difficulty", "label": "Difficulty", "type": "select",
             "choices": ["easy", "moderate", "hard"], "default": "easy"},
            {"name": "max_seats", "label": "Max seats", "type": "number", "required": True},
            {"name": "status", "label": "Status", "type": "select",
             "choices": ["upcoming", "ongoing", "completed", "cancelled"], "default": "upcoming"},
        ],
    },
    "bookings": {
        "label": "Bookings",
        "table": "bookings",
        "id_field": "booking_id",
        "columns": ["booking_id", "user_id", "trip_id", "seats", "total_amount", "booking_status"],
        "fields": [
            {"name": "user_id", "label": "Customer", "type": "select_fk",
             "options_table": "users", "options_id": "user_id",
             "options_label": "full_name", "required": True},
            {"name": "trip_id", "label": "Trip", "type": "select_fk",
             "options_table": "trips", "options_id": "trip_id",
             "options_label": "title", "required": True},
            {"name": "seats", "label": "Seats", "type": "number", "required": True},
            {"name": "total_amount", "label": "Total amount (BDT)", "type": "number", "required": True},
            {"name": "booking_status", "label": "Status", "type": "select",
             "choices": ["pending", "confirmed", "cancelled"], "default": "pending"},
        ],
    },
    "payments": {
        "label": "Payments",
        "table": "payments",
        "id_field": "payment_id",
        "columns": ["payment_id", "booking_id", "amount", "method", "payment_status"],
        "fields": [
            {"name": "booking_id", "label": "Booking", "type": "select_fk",
             "options_table": "bookings", "options_id": "booking_id",
             "options_label": "booking_id", "options_label_prefix": "Booking #", "required": True},
            {"name": "amount", "label": "Amount (BDT)", "type": "number", "required": True},
            {"name": "method", "label": "Method", "type": "select",
             "choices": ["bkash", "nagad", "card", "cash"], "required": True},
            {"name": "payment_status", "label": "Status", "type": "select",
             "choices": ["paid", "failed", "refunded"], "default": "paid"},
        ],
    },
}


def load_fk_options(conn, field):
    """Returns a list of (id, label) tuples for a select_fk field's dropdown."""
    rows = conn.execute(
        f"SELECT {field['options_id']} AS id, {field['options_label']} AS label "
        f"FROM {field['options_table']} ORDER BY {field['options_id']}"
    ).fetchall()
    prefix = field.get("options_label_prefix", "")
    return [(row["id"], f"{prefix}{row['label']}") for row in rows]


def build_fields_for_form(conn, config, record=None):
    """Returns a deep-ish copy of the entity's fields, with select_fk options
    resolved and current values filled in (for editing) or defaults (for adding)."""
    fields = []
    for f in config["fields"]:
        field = dict(f)
        if field["type"] == "select_fk":
            field["options"] = load_fk_options(conn, field)
        if record is not None:
            field["value"] = record[field["name"]]
        else:
            field["value"] = field.get("default", "")
        fields.append(field)
    return fields


@app.route("/")
def dashboard():
    conn = get_connection()

    # --- Stat cards --------------------------------------------------
    total_users = conn.execute("SELECT COUNT(*) AS c FROM users").fetchone()["c"]
    total_trips = conn.execute("SELECT COUNT(*) AS c FROM trips").fetchone()["c"]
    total_bookings = conn.execute("SELECT COUNT(*) AS c FROM bookings").fetchone()["c"]
    total_revenue = conn.execute(
        "SELECT COALESCE(SUM(amount), 0) AS r FROM payments WHERE payment_status = 'paid'"
    ).fetchone()["r"]

    # --- Upcoming trips panel -----------------------------------------
    trip_rows = conn.execute(
        """
        SELECT
            t.trip_id    AS id,
            t.title      AS title,
            d.region     AS region,
            d.country    AS country,
            t.start_date AS start_date,
            t.end_date   AS end_date,
            t.price      AS price,
            t.max_seats  AS max_seats,
            COALESCE(SUM(CASE WHEN b.booking_status <> 'cancelled' THEN b.seats ELSE 0 END), 0) AS booked_seats
        FROM trips t
        JOIN destinations d ON d.destination_id = t.destination_id
        LEFT JOIN bookings b ON b.trip_id = t.trip_id
        WHERE t.status = 'upcoming'
        GROUP BY t.trip_id
        ORDER BY t.start_date ASC
        """
    ).fetchall()

    emojis = ["🏔️", "🌄", "🌳", "🏕️", "⛺", "🚣"]
    trips = []
    for i, row in enumerate(trip_rows):
        percent = min(100, round((row["booked_seats"] / row["max_seats"]) * 100))
        trips.append(
            {
                "emoji": emojis[i % len(emojis)],
                "title": row["title"],
                "region": row["region"],
                "country": row["country"],
                "date_range": format_date_range(row["start_date"], row["end_date"]),
                "price": row["price"],
                "booked_seats": row["booked_seats"],
                "max_seats": row["max_seats"],
                "percent": percent,
            }
        )

    # --- Revenue chart --------------------------------------------------
    revenue_rows = conn.execute(
        """
        SELECT
            t.trip_id AS id,
            t.title   AS title,
            COALESCE(SUM(CASE WHEN p.payment_status = 'paid' THEN p.amount ELSE 0 END), 0) AS revenue
        FROM trips t
        LEFT JOIN bookings b ON b.trip_id = t.trip_id
        LEFT JOIN payments p ON p.booking_id = b.booking_id
        GROUP BY t.trip_id
        ORDER BY t.trip_id ASC
        """
    ).fetchall()

    bar_colors = ["#398a5b", "#77b88c", "#b8d9c2"]
    max_revenue = max([row["revenue"] for row in revenue_rows] + [1])
    revenue_chart = []
    for i, row in enumerate(revenue_rows):
        height_pct = 1 if row["revenue"] == 0 else round((row["revenue"] / max_revenue) * 100)
        revenue_chart.append(
            {
                "short_title": row["title"].split(" ")[0],
                "revenue": row["revenue"],
                "height_pct": height_pct,
                "color": bar_colors[i % len(bar_colors)],
            }
        )

    # --- Recent bookings table ------------------------------------------
    bookings = conn.execute(
        """
        SELECT
            b.booking_id     AS id,
            u.full_name      AS customer,
            t.title          AS trip,
            b.seats          AS seats,
            b.total_amount   AS amount,
            b.booking_status AS status
        FROM bookings b
        JOIN users u ON u.user_id = b.user_id
        JOIN trips t ON t.trip_id = b.trip_id
        ORDER BY b.booking_id DESC
        LIMIT 10
        """
    ).fetchall()

    # --- Resource overview cards -----------------------------------------
    def count(table):
        return conn.execute(f"SELECT COUNT(*) AS c FROM {table}").fetchone()["c"]

    resources = {
        "destinations": count("destinations"),
        "guides": count("guides"),
        "vehicles": count("vehicles"),
        "activities": count("activities"),
        "users": count("users"),
        "payments": count("payments"),
    }

    conn.close()

    return render_template(
        "index.html",
        today=date.today().strftime("%B %d, %Y"),
        total_users=total_users,
        total_trips=total_trips,
        total_bookings=total_bookings,
        total_revenue=total_revenue,
        trips=trips,
        revenue_total=sum(r["revenue"] for r in revenue_chart),
        revenue_chart=revenue_chart,
        bookings=bookings,
        resources=resources,
        entities=ENTITIES,
    )


@app.route("/manage/<entity>")
def manage_list(entity):
    config = ENTITIES.get(entity)
    if not config:
        return "Unknown section", 404

    conn = get_connection()

    edit_id = request.args.get("edit")
    record = None
    if edit_id:
        record = conn.execute(
            f"SELECT * FROM {config['table']} WHERE {config['id_field']} = ?", (edit_id,)
        ).fetchone()

    rows = conn.execute(f"SELECT * FROM {config['table']} ORDER BY {config['id_field']} DESC").fetchall()
    fields = build_fields_for_form(conn, config, record)
    conn.close()

    return render_template(
        "manage.html",
        entity=entity,
        config=config,
        rows=rows,
        fields=fields,
        editing=record is not None,
        edit_id=edit_id,
        entities=ENTITIES,
    )


@app.route("/manage/<entity>/save", methods=["POST"])
def manage_save(entity):
    config = ENTITIES.get(entity)
    if not config:
        return "Unknown section", 404

    record_id = request.form.get("record_id")  # present only when editing
    columns = []
    values = []

    for field in config["fields"]:
        raw = request.form.get(field["name"], "").strip()

        if field["type"] == "select_fk" and field.get("nullable") and raw == "":
            value = None
        elif field["type"] == "number":
            value = raw if raw != "" else None
        else:
            value = raw if raw != "" else field.get("default")

        columns.append(field["name"])
        values.append(value)

    conn = get_connection()
    try:
        if record_id:
            set_clause = ", ".join(f"{c} = ?" for c in columns)
            conn.execute(
                f"UPDATE {config['table']} SET {set_clause} WHERE {config['id_field']} = ?",
                (*values, record_id),
            )
            flash(f"{config['label'][:-1]} updated successfully.", "success")
        else:
            placeholders = ", ".join("?" for _ in columns)
            conn.execute(
                f"INSERT INTO {config['table']} ({', '.join(columns)}) VALUES ({placeholders})",
                values,
            )
            flash(f"New {config['label'][:-1].lower()} added successfully.", "success")
        conn.commit()
    except sqlite3.IntegrityError as err:
        flash(f"Could not save: {err}", "error")
    finally:
        conn.close()

    return redirect(url_for("manage_list", entity=entity))


@app.route("/manage/<entity>/<int:record_id>/delete", methods=["POST"])
def manage_delete(entity, record_id):
    config = ENTITIES.get(entity)
    if not config:
        return "Unknown section", 404

    conn = get_connection()
    try:
        conn.execute(f"DELETE FROM {config['table']} WHERE {config['id_field']} = ?", (record_id,))
        conn.commit()
        flash(f"{config['label'][:-1]} deleted.", "success")
    except sqlite3.IntegrityError:
        flash(
            f"Could not delete this {config['label'][:-1].lower()} — "
            f"other records (like trips or bookings) still refer to it.",
            "error",
        )
    finally:
        conn.close()

    return redirect(url_for("manage_list", entity=entity))


def format_date_range(start_iso, end_iso):
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)
    return f"{start.strftime('%d %b')} – {end.strftime('%d %b, %Y')}"


if __name__ == "__main__":
    init_db()
    app.run(debug=True, port=5000)
