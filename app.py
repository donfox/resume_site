# app.py

from flask import render_template
from resume_site import create_app

app = create_app()


@app.errorhandler(403)
def forbidden(error):
    app.logger.warning(f"403 Forbidden: {error}")
    return render_template("403.html"), 403(RESUME_)


if __name__ == "__main__":
    import os

    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    port = int(os.getenv("PORT", 5000))
    host = os.getenv("HOST", "127.0.0.1")

    app.run(host=host, port=port, debug=debug_mode)
