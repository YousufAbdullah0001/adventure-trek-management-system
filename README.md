# Adventure Trip & Trek Management System

A simple admin dashboard for managing adventure trips, destinations,
guides, vehicles, activities, bookings and payments — built with
**Python (Flask) and SQLite, no JavaScript at all**.

## How it's built (kept intentionally simple)

```
Browser  <----  Flask (Python)  <----  SQLite database
  just reads        app.py                adventure_trek.db
  plain HTML        database.py
  (no JS)           templates/index.html
```

- **No JavaScript anywhere.** The dashboard page has zero `<script>`
  tags. Every number, table row and chart bar is calculated in Python
  and already filled into the page before it reaches the browser.
- **Backend**: Flask (`backend/app.py`) reads from SQLite, runs a few
  SQL queries (stats, upcoming trips, revenue, bookings, resource
  counts), and passes the results into an HTML template
  (`backend/templates/index.html`) using Jinja2 — Flask's built-in
  templating engine. Refreshing the page re-runs the queries.
- **Database**: SQLite (`backend/adventure_trek.db`), created and
  seeded automatically the first time the app runs, using Python's
  built-in `sqlite3` module (no extra database driver needed). The
  original 9-table design (users, destinations, guides, vehicles,
  activities, trips, trip_activities, bookings, payments) is unchanged.
- The original SQL Server scripts are kept in `database/mssql/` for
  reference, and an equivalent SQLite schema is documented in
  `database/sqlite/schema.sql` (the same schema `database.py` creates
  automatically).

## Project structure

```
Adventure-Trek-Management/
├── backend/
│   ├── app.py              # Flask routes + all the data logic (dashboard + CRUD)
│   ├── database.py          # creates tables & seed data (SQLite)
│   ├── requirements.txt
│   ├── templates/
│   │   ├── index.html       # read-only dashboard, no JavaScript
│   │   └── manage.html       # generic add/edit/delete page, reused for all 9 tables
│   ├── static/
│   │   ├── style.css
│   │   └── manage.css        # styling for the Manage Data forms
│   └── adventure_trek.db    # created automatically on first run (not in git)
├── database/
│   ├── mssql/                # original SQL Server scripts (optional/reference)
│   │   ├── adventure_trek.sql
│   │   └── verification.sql
│   └── sqlite/
│       └── schema.sql        # same schema, SQLite flavor (for reading/reference)
└── README.md
```

## Running it locally

**Requirement:** Python 3.9 or newer. Check with `python3 --version`.

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Adventure-Trek-Management/backend

# 2. (Recommended) create a virtual environment
python3 -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

# 3. Install Flask (the only dependency)
pip install -r requirements.txt

# 4. Run the app (this also creates and seeds the database)
python3 app.py

# 5. Open the dashboard
# Visit http://127.0.0.1:5000 in your browser
```

That's it — no JavaScript build step, no Node, no separate API calls.
The first time you run it, `database.py` creates `adventure_trek.db`
next to it and fills it with sample data.

To start fresh, delete `backend/adventure_trek.db` and restart the app;
it will be recreated and reseeded automatically.

## Managing data (Add / Edit / Delete)

Besides the read-only dashboard at `/`, there's a **Manage Data** section
(linked from the sidebar) with a plain HTML page for each of the 9 tables:

- `/manage/destinations`, `/manage/guides`, `/manage/vehicles`,
  `/manage/activities`, `/manage/users`, `/manage/trips`,
  `/manage/bookings`, `/manage/payments`

Each page has:
- A form at the top to **add** a new row (or **edit** an existing one —
  click "Edit" on any row to load it into the form, "Save Changes" to
  update it)
- A table below listing every row, with **Edit** and **Delete** buttons

This still uses no JavaScript — every add/edit/delete is a normal HTML
form `POST` request, followed by a page reload that shows the updated
data straight from the database. Dropdowns for related data (e.g.
choosing a Destination when adding a Trip) are built from whatever
rows already exist in that table.

If you try to delete a row that other rows depend on (e.g. a
Destination that a Trip still points to), the database's foreign key
rules block it and the page shows a clear message instead of breaking.

## How the data flows (for understanding, not just running)

1. Browser requests `/`
2. `app.py`'s `dashboard()` function runs several SQL queries against
   `adventure_trek.db` (stats, upcoming trips, revenue per trip, recent
   bookings, resource counts)
3. The results are passed to `templates/index.html`
4. Jinja2 fills in the `{{ ... }}` placeholders and loops (`{% for %}`)
   with the real numbers
5. Flask sends back one complete, already-filled HTML page — nothing
   else needs to run in the browser

## Database design

- Primary keys, foreign keys and auto-increment columns
- `NOT NULL`, `UNIQUE`, `CHECK` and `DEFAULT` constraints
- `ON DELETE CASCADE` and `ON DELETE SET NULL` relationships
- A many-to-many relationship (`trip_activities` between `trips` and `activities`)

## Project scope

This is a learning / portfolio project: a small, easy-to-read example
of connecting a real database to a dashboard using a server-rendered
approach, so the whole flow (database → Python → HTML) stays simple
and easy to follow end-to-end, without needing to understand
JavaScript, APIs or fetch calls.

## License

MIT — feel free to use this for learning or as a starting point.
