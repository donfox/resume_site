# Personal Website Flask App

A personal portfolio/resume web application built using Flask. It serves a homepage, resume, references, book list, and supports logging and request form submissions.

---

## 🚀 Features
- Homepage with custom content
- Resume rendered from templates
- Email request submission form
- References and book list pages
- Templating with Jinja2
- Logging to file
- SQLite database for request tracking

---

## 🛠️ Tech Stack
- Python 3.11+
- Flask 3.x
- Flask-Mail
- Flask-SQLAlchemy
- SQLite
- HTML/CSS + Jinja2 templates

---

## 💻 Development Environment
- Editor: Sublime Text 4
- Python Environment: Miniconda virtual environment

---

## 📁 Project Structure
```
.
├── app.py                  # Entry point
├── config.py               # App configuration
├── personal_website/       # Core app package
│   ├── __init__.py
│   ├── models.py           # SQLAlchemy models
│   ├── routes.py           # Application routes
│   ├── extensions.py       # Flask extensions setup
│   ├── utils.py            # Helper functions
│   └── templates/          # Jinja2 templates
├── static/                 # Static files (CSS, images, PDFs)
├── instance/site.db        # SQLite database
├── logs/app.log            # Log output
├── tests/                  # Pytest unit tests
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Dev/test dependencies
└── README.md               # Project description
```

---

## 🧪 Running Locally

### 1. Clone the repo
```bash
git clone <repo-url>
cd personal_website
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 4. Set environment variables (optional)
```bash
export FLASK_APP=app.py
export FLASK_ENV=development
```

### 5. Run the app
```bash
flask run
```

---

## ✅ Tests
```bash
pytest tests/
```

---

## 📬 Contact
This website is for personal use. For issues, please open a GitHub Issue or contact the maintainer directly.

---

## 📄 License
MIT License
