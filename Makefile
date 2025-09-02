# --------------------------
# Makefile for dev/prod tasks
# --------------------------

.PHONY: install dev db-create db-drop db-reset db-status db-backup db-restore run test lint format pre-commit
.DEFAULT_GOAL := help

PYTHON := python3

help:
	@echo ""
	@echo "Available commands:"
	@echo "  make install     - pip install -e .[dev]"
	@echo "  make dev         - install requirements + pre-commit hooks"
	@echo "  make run         - run Flask dev server"
	@echo "  make test        - run tests"
	@echo "  make lint        - ruff check"
	@echo "  make format      - black + ruff --fix"
	@echo "  make pre-commit  - run all pre-commit hooks"
	@echo "  make db-create   - create dev DB tables"
	@echo "  make db-drop     - DROP dev DB tables (requires CONFIRM=YES)"
	@echo "  make db-status   - show dev.db size and table count"
	@echo "  make db-backup   - copy dev.db to backups/ with timestamp"
	@echo "  make db-restore  - restore most recent backup to dev.db"
	@echo "  make db-reset    - backup + DROP/CREATE tables (requires CONFIRM=YES)"
	@echo ""

install:
	$(PYTHON) -m pip install -e .[dev]

dev:
	$(PYTHON) -m pip install -r requirements.txt || true
	pre-commit install || true

db-create:
	$(PYTHON) scripts/dev_db.py create

# Destructive; require CONFIRM=YES
db-drop:
	@if [ "$(CONFIRM)" != "YES" ]; then \
		echo "⚠️  This will DROP your dev.db tables."; \
		echo "    To proceed, run:"; \
		echo "      make db-drop CONFIRM=YES"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/dev_db.py drop
	@echo "✅ Tables dropped."

db-status:
	@echo "📦 Checking instance/dev.db..."
	@ls -lh instance/dev.db 2>/dev/null || { echo "❌ instance/dev.db not found"; exit 0; }
	@echo "📊 Table count:"
	@$(PYTHON) - <<'PYCODE'
import sqlite3, os
p = "instance/dev.db"
if os.path.exists(p):
    con = sqlite3.connect(p); cur = con.cursor()
    cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
    print("   tables:", cur.fetchone()[0])
    con.close()
PYCODE

db-backup:
	@echo "🗄️ Backing up instance/dev.db..."
	@[ -f instance/dev.db ] || { echo "❌ No dev.db to back up"; exit 1; }
	@mkdir -p backups
	@cp instance/dev.db backups/dev.db.$(shell date +%Y%m%d_%H%M%S)
	@echo "✅ Backup written to backups/"

# Always back up before resetting; also require CONFIRM=YES
db-reset: db-backup
	@if [ "$(CONFIRM)" != "YES" ]; then \
		echo "⚠️  This will DROP and recreate your dev.db tables."; \
		echo "    To proceed, run:"; \
		echo "      make db-reset CONFIRM=YES"; \
		exit 1; \
	fi
	@$(PYTHON) scripts/dev_db.py reset
	@echo "✅ Database has been reset (after backup)."

db-restore:
	@echo "♻️ Restoring latest backup to instance/dev.db..."
	@[ -d backups ] || { echo "❌ No backups directory"; exit 1; }
	@[ "$$(ls -A backups/dev.db.* 2>/dev/null)" ] || { echo "❌ No backups found"; exit 1; }
	@latest=$$(ls -t backups/dev.db.* | head -n1); \
	echo "Using $$latest"; \
	cp "$$latest" instance/dev.db
	@echo "✅ Restore complete."

run:
	flask --app resume_site run --debug

test:
	pytest -q

lint:
	ruff check .

format:
	black .
	ruff check . --fix

pre-commit:
	pre-commit run --all-files