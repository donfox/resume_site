# Personal Website Flask App

A personal portfolio/resume web application built using Flask.  
It serves a homepage, résumé, references, and book reviews, with support for email form submissions, request logging, and a SQLite-backed database.

---

## 🚀 Features
- Homepage with custom content
- Résumé rendered from templates
- References and book reviews
- Email request submission form (Flask-Mail)
- Logging to file and stdout
- SQLite database for request tracking
- Developer tooling (Makefile, pre-commit hooks, tests)

---

## 🛠️ Tech Stack
- Python 3.11+
- Flask 3.x
- Flask-Mail
- Flask-SQLAlchemy
- SQLite
- HTML/CSS + Jinja2 templates

---

## 📁 Project Structure
```
.
├── app.py                  # Dev entry point
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
├── pyproject.toml          # Packaging & dependencies
├── requirements.txt        # Runtime dependencies
├── Makefile                # Task runner (dev/prod commands)yes
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

## 🧪 Tests & Linting
```bash
make test       # run pytest
make lint       # check style (ruff)
make format     # autoformat (black + ruff --fix)
make pre-commit # run all pre-commit hooks
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
