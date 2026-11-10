# syntax=docker/dockerfile:1

FROM python:3.12-slim AS runtime
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DJANGO_DEBUG=false \
    NLTK_DATA=/usr/share/nltk_data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Download the corpora at build time so the running container needs no network
# and no write access to a home directory.
RUN python -m nltk.downloader -d "$NLTK_DATA" stopwords punkt punkt_tab

COPY manage.py ./
COPY Plagiarism_Checker ./Plagiarism_Checker
COPY plagiarismchecker ./plagiarismchecker

RUN DJANGO_SECRET_KEY=build-time-only-not-used-at-runtime \
    DJANGO_DEBUG=true \
    python manage.py collectstatic --noinput

RUN useradd --create-home --shell /usr/sbin/nologin app && chown -R app:app /app
USER app

EXPOSE 8000

# Binds all interfaces inside the container; the published port is the security
# boundary (docker-compose.yml publishes to 127.0.0.1 only).
CMD ["gunicorn", "Plagiarism_Checker.wsgi:application", \
     "--bind", "0.0.0.0:8000", "--workers", "2", "--timeout", "180", \
     "--access-logfile", "-"]
