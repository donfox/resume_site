# --------------------------
# Makefile for dev/prod tasks
# --------------------------

PYTHON := python3
APP := app.py
GUNICORN_CMD := gunicorn wsgi:app -w 2 -k gthread --threads 8 --timeout 60 --graceful-timeout 30 -b 0.0.0.0:${PORT:-8000}

# Default target
help:
	@echo ""
	@echo "Available commands:"
	@echo "  make run       - Run Flask development server"
	@echo "  make prod      - Run Gunicorn production server (local test)"
	@echo "  make secret    - Generate a strong random SECRET_KEY"
	@echo "  make db        - Create dev DB tables (via scripts/dev_db.py)"
	@echo "  make db-drop   - Drop dev DB tables"
	@echo "  make clean     - Remove __pycache__ and .pyc files"
	@echo ""

# Run Flask development server
run:
	@echo "🚀 Starting Flask dev server..."
	@FLASK_DEBUG=True FLASK_ENV=development $(PYTHON) $(APP)

# Run Gunicorn production server (local test)
prod:
	@echo "🚀 Starting Gunicorn production server..."
	@$(GUNICORN_CMD)

# Generate a new SECRET_KEY
secret:
	@$(PYTHON) -c "import secrets; print(secrets.token_hex(32))"

# Dev DB: create/drop tables
db:
	@$(PYTHON) scripts/dev_db.py create

db-drop:
	@$(PYTHON) scripts/dev_db.py drop

# Clean caches
clean:
	@echo "🧹 Cleaning..."
	@find . -type d -name "__pycache__" -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

reset-db:
	@$(PYTHON) scripts/dev_db.py reset