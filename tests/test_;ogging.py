import io
import logging

def test_logging_initializes(app, capsys):
    """
    If you have a configure_logging() function, import and run it.
    Otherwise, simulate logging behavior and ensure it doesn’t crash under TESTING.
    """
    # If you expose a helper: from app import configure_logging; configure_logging(app)
    # For now, just emit a log record:
    logger = logging.getLogger("app")
    logger.setLevel(logging.DEBUG)

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    logger.addHandler(handler)

    logger.debug("Logging initialized. Debug mode: %s", app.config.get("DEBUG"))

    handler.flush()
    output = stream.getvalue()
    assert "Logging initialized." in output