# app.py

from flask import render_template
from resume_site import create_app

app = create_app()

@app.errorhandler(403)
def forbidden(error):
    app.logger.warning(f"403 Forbidden: {error}")
    return render_template("403.html"), 403


@app.errorhandler(404)
def page_not_found(error):
    app.logger.warning(f"404 Not Found: {error}")
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    app.logger.exception("Internal server error")
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)  # Set to app in production
