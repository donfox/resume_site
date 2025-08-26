# ... (top unchanged)

def main():
    if len(sys.argv) != 2 or sys.argv[1] not in {"create", "drop", "reset"}:
        print("Usage: python scripts/dev_db.py [create|drop|reset]")
        sys.exit(1)

    if sys.argv[1] == "create":
        INSTANCE_DIR.mkdir(exist_ok=True)
        if not DB_PATH.exists():
            DB_PATH.touch()
            print(f"📂 Created {DB_PATH}")
        app = create_app()
        with app.app_context():
            db.create_all()
            print("✅ Tables created.")

    elif sys.argv[1] == "drop":
        if DB_PATH.exists():
            app = create_app()
            with app.app_context():
                db.drop_all()
                print("🗑️ Tables dropped.")
        else:
            print("⚠️ dev.db does not exist, nothing to drop.")

    elif sys.argv[1] == "reset":
        INSTANCE_DIR.mkdir(exist_ok=True)
        app = create_app()
        with app.app_context():
            if DB_PATH.exists():
                db.drop_all()
                print("🗑️ Tables dropped.")
            if not DB_PATH.exists():
                DB_PATH.touch()
                print(f"📂 Created {DB_PATH}")
            db.create_all()
            print("🔁 DB reset complete (tables recreated).")

if __name__ == "__main__":
    main()