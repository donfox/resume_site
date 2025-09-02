#!/usr/bin/env python3
"""Utility for creating, dropping, or resetting the dev database.

Usage:
    python scripts/dev_db.py create
    python scripts/dev_db.py drop
    python scripts/dev_db.py reset
"""

import argparse
import logging
from pathlib import Path

from resume_site import create_app, db

logger = logging.getLogger("dev_db")

def _ensure_logging():
    # If the root logger has no handlers (invoked outside Flask), set a sane default.
    if not logging.getLogger().handlers:
        logging.basicConfig(level=logging.INFO, format="%(asctime)s — %(name)s — %(levelname)s — %(message)s")

def _db_paths_from_app(app):
    """Return (instance_dir, sqlite_path_or_none) for visibility/logging."""
    instance_dir = Path(app.instance_path)
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    sqlite_path = None
    if uri.startswith("sqlite:///"):
        # sqlite:///relative_or_instance_path.db OR sqlite:////absolute_path.db
        raw = uri.replace("sqlite:///", "", 1)
        sqlite_path = Path(raw)
        if not sqlite_path.is_absolute():
            # If relative, resolve relative to instance path
            sqlite_path = instance_dir / sqlite_path
    return instance_dir, sqlite_path, uri

def create_db():
    app = create_app()
    with app.app_context():
        instance_dir, sqlite_path, uri = _db_paths_from_app(app)
        instance_dir.mkdir(parents=True, exist_ok=True)
        db.create_all()
        if sqlite_path:
            logger.info(f"✅ Database created: {sqlite_path} (URI={uri})")
        else:
            logger.info(f"✅ Database created (URI={uri})")

def drop_db():
    app = create_app()
    with app.app_context():
        instance_dir, sqlite_path, uri = _db_paths_from_app(app)
        # Drop all tables first (works for any backend)
        db.drop_all()
        # If sqlite file exists, remove it for a truly clean slate
        if sqlite_path and sqlite_path.exists():
            sqlite_path.unlink(missing_ok=True)
            logger.info(f"🗑️  Database dropped and file removed: {sqlite_path}")
        else:
            logger.info(f"🗑️  Database dropped (no file to remove). URI={uri}")

def reset_db():
    app = create_app()
    with app.app_context():
        instance_dir, sqlite_path, uri = _db_paths_from_app(app)
        instance_dir.mkdir(parents=True, exist_ok=True)
        db.drop_all()
        if sqlite_path and sqlite_path.exists():
            sqlite_path.unlink(missing_ok=True)
        db.create_all()
        if sqlite_path:
            logger.info(f"🔁 Database reset complete: {sqlite_path} (URI={uri})")
        else:
            logger.info(f"🔁 Database reset complete (URI={uri})")

def main():
    _ensure_logging()

    parser = argparse.ArgumentParser(description="Manage the development database.")
    parser.add_argument("action", choices=["create", "drop", "reset"], help="Action to perform.")
    args = parser.parse_args()

    if args.action == "create":
        create_db()
    elif args.action == "drop":
        drop_db()
    elif args.action == "reset":
        reset_db()

if __name__ == "__main__":
    main()

    