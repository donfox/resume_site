
web: gunicorn wsgi:app -w 2 -k gthread --threads 8 --timeout 60 --graceful-timeout 30 -b 0.0.0.0:${PORT}
