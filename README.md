# Personal Website Flask App

A personal portfolio/resume web application built using Flask.  
It serves a homepage, résumé, references, and book reviews, with a resume download request form, request logging, and a Postgres-backed database (SQLite as a local dev fallback).

---

## 🚀 Features
- Homepage with custom content
- Résumé rendered from templates
- References and book reviews
- Resume download form (serves the PDF/DOCX directly; logs the request)
- Logging to file and stdout
- Postgres database for request tracking (SQLite in dev)
- Developer tooling (Makefile, ruff/black, tests)

---

## 🛠️ Tech Stack
- Python 3.11+
- Flask 3.x
- Flask-SQLAlchemy
- Postgres (production), SQLite (local dev fallback)
- Alembic / Flask-Migrate for schema migrations
- HTML/CSS + Jinja2 templates

---

## 📁 Project Structure
```
.
├── wsgi.py                  # App entry point (dev + production)
├── config.py               # App configuration
├── resume_site/            # Core app package
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # Application routes
│   ├── extensions.py       # Flask extensions setup
│   ├── utils.py            # Helper functions
│   └── templates/          # Jinja2 templates
├── static/                 # Static files (CSS, images, PDFs)
├── instance/dev.db         # SQLite dev database
├── logs/                   # Log files
├── scripts/dev_db.py       # Database create/drop/reset utility
├── backups/                # Timestamped DB backups
├── tests/                  # Pytest unit tests
├── pyproject.toml          # Packaging metadata
├── requirements.txt        # Runtime dependencies
├── Makefile                # Task runner (dev/prod commands)
└── README.md               # Project description
```

---

## 💻 Development Setup

### 1. Clone the repo
```bash
git clone <repo-url>
cd resume_site_project
```

### 2. Create and activate environment
```bash
conda create -n flask_env python=3.11
conda activate flask_env
```
(or `python -m venv venv && source venv/bin/activate`)

### 3. Install dependencies
```bash
# install project + dev tools in editable mode
make install
```

### 4. Initialize database
```bash
make db-create          # create dev.db if missing
make db-status          # check DB size & table count
make db-backup          # back up dev.db
make db-reset CONFIRM=YES   # backup + reset tables (requires explicit confirm)
make db-restore         # restore most recent backup
```

### 5. Run the app
```bash
make run
```

---

## 🗄️ Database Migrations
Schema changes are managed with Flask-Migrate/Alembic (files under `migrations/`).

```bash
flask --app resume_site db migrate -m "describe the change"   # generate a new migration
flask --app resume_site db upgrade                            # apply pending migrations
flask --app resume_site db downgrade                          # roll back one migration
```

In production, `render.yaml`'s build step runs `flask db upgrade` automatically on every deploy, so committed migrations are applied before the new app version starts.

---

## 🧪 Tests & Linting
```bash
make test       # run pytest
make lint       # check style (ruff)
make format     # autoformat (black + ruff --fix)
```

---

## 🛠️ Production (local test)
```bash
# Example using Gunicorn
gunicorn wsgi:app -w 2 -k gthread --threads 8   --timeout 60 --graceful-timeout 30 -b 0.0.0.0:8000
```

---

## 📬 Contact
This website is for personal use. For issues, please open a GitHub Issue or contact the maintainer directly.

---

## 📄 License
MIT License
