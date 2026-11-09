# Plagiarism Checker

A Django web app that estimates plagiarism. It compares text or documents against web search results, or compares two documents with each other, using cosine similarity.

![Plagiarism Checker banner](Modern%20Minimalist%20Simple%20Technology%20Facebook%20Cover.png)

![Python](https://img.shields.io/badge/Python-3.8%2B-3776AB?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-3.1-092E20?logo=django&logoColor=white)
![NLTK](https://img.shields.io/badge/NLP-NLTK-154F5B)
![Google Custom Search](https://img.shields.io/badge/API-Google_Custom_Search-4285F4?logo=google&logoColor=white)

## Overview

The app has two tools:

1. **Web plagiarism check**: the input text is split into sentences, stopwords are removed (NLTK), and the words are grouped into 9-word query chunks. Each chunk (up to 100) is searched with the Google Custom Search JSON API. The top 5 result snippets are scored with cosine similarity, and the best-matching links are combined into an overall plagiarism percentage with source links.
2. **Document comparison**: two texts are turned into word-frequency vectors over their combined vocabulary, and the app reports their cosine similarity as a percentage.

## Features

- Paste text, or upload a `.txt` or `.docx` file, and check it against the web.
- Get an overall match percentage and the matching source URLs.
- Compare two pasted texts, or two uploaded `.txt` / `.docx` files, side by side.
- Stopword filtering with the NLTK English stopword list.
- A `Procfile` for running under gunicorn on Heroku-style platforms.

PDF upload has partial code in `views.py`, but the text is not passed to the checker yet.

## Tech stack

- Python, Django 3.1
- NLTK (stopwords)
- python-docx, PyPDF2
- google-api-python-client (Custom Search JSON API)
- gunicorn (Procfile)
- SQLite (Django default; the app defines no models)

## Project structure

```
Plagiarism-Checker/
├── manage.py
├── Procfile                      # web: gunicorn Plagiarism_Checker.wsgi
├── requirements.txt
├── stopWordRemove.py             # helper that downloads NLTK corpora
├── Plagiarism_Checker/           # Django project (settings, urls, wsgi/asgi)
└── plagiarismchecker/            # Django app
    ├── algorithm/
    │   ├── main.py               # query building + web similarity scoring
    │   ├── webSearch.py          # Google Custom Search calls
    │   ├── ConsineSim.py         # cosine similarity of two strings
    │   └── fileSimilarity.py     # document-vs-document similarity
    ├── templates/pc/             # index.html, doc_compare.html
    ├── static/pc/                # CSS
    ├── url.py
    └── views.py
```

## Getting started

### Prerequisites

- Python 3.8 or later
- A Google API key with the Custom Search JSON API enabled, and a Programmable Search Engine ID (`cx`)

### Install

```bash
git clone https://github.com/VamsiKrishnaThota03/Plagiarism-Checker.git
cd Plagiarism-Checker
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
python -c "import nltk; nltk.download('stopwords')"
```

`requirements.txt` pins `wincertstore`, which only installs on Windows. Remove that line on macOS or Linux if `pip` fails.

### Configuration

These values are currently set in source files. Replace them with your own, ideally loaded from environment variables:

| Setting             | File                                       | Example placeholder           |
| ------------------- | ------------------------------------------ | ----------------------------- |
| `SECRET_KEY`        | `Plagiarism_Checker/settings.py`           | `<your-django-secret-key>`    |
| `DEBUG`             | `Plagiarism_Checker/settings.py`           | `False` in production         |
| `ALLOWED_HOSTS`     | `Plagiarism_Checker/settings.py`           | `localhost,127.0.0.1`         |
| `searchEngine_API`  | `plagiarismchecker/algorithm/webSearch.py` | `<your-google-api-key>`       |
| `searchEngine_Id`   | `plagiarismchecker/algorithm/webSearch.py` | `<your-search-engine-id>`     |

### Run

```bash
python manage.py migrate
python manage.py runserver        # http://127.0.0.1:8000
```

## Routes

| Method | Path                | Purpose                                              |
| ------ | ------------------- | ---------------------------------------------------- |
| GET    | `/`                 | Web plagiarism check page                            |
| POST   | `/test/`            | Check pasted text (`q`) against the web              |
| POST   | `/filetest/`        | Check an uploaded `.txt` / `.docx` (`docfile`)       |
| GET    | `/compare/`         | Document comparison page                             |
| POST   | `/twofiletest1/`    | Compare two pasted texts (`q1`, `q2`)                |
| POST   | `/twofilecompare1/` | Compare two uploaded files (`docfile1`, `docfile2`)  |
| GET    | `/admin/`           | Django admin                                         |
