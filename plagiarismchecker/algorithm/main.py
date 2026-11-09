"""Web plagiarism check: split text into word n-grams, search each, combine the matches."""
import logging
import re

import requests
from django.conf import settings

from plagiarismchecker.algorithm import webSearch
from plagiarismchecker.algorithm.stopwords import english_stopwords

logger = logging.getLogger(__name__)

SENTENCE_END = re.compile(r'[.!?]+')
NON_WORD = re.compile(r'\W+', re.UNICODE)


def getQueries(text, n):
    """Split ``text`` into search queries of up to ``n`` content words.

    Each sentence is stripped of stopwords and cut into consecutive chunks of
    ``n`` words; chunks (or short sentences) with 5 or fewer words are dropped
    because they are too generic to search.
    """
    stops = english_stopwords()
    queries = []
    for sentence in SENTENCE_END.split(text or ''):
        words = [w for w in NON_WORD.split(sentence) if w and w.lower() not in stops]
        for start in range(0, len(words), n):
            chunk = words[start:start + n]
            if len(chunk) > 4:
                queries.append(chunk)
    return queries


def findSimilarity(text, n=9, max_queries=None):
    """Return (total_percent, {link: percent}) for ``text``.

    Raises ``webSearch.SearchNotConfigured`` when API credentials are missing.
    """
    if not webSearch.is_configured():
        raise webSearch.SearchNotConfigured('Web search is not configured.')

    max_queries = max_queries or settings.MAX_SEARCH_QUERIES
    queries = [' '.join(q) for q in getQueries(text, n)][:max_queries]
    output, c = {}, {}
    successful = 0
    with requests.Session() as session:
        for query in queries:
            output, c, errors = webSearch.searchWeb(query, output, c, session=session)
            successful += 1 - errors
    if successful == 0:
        return 0.0, {}

    total_percent = 0.0
    output_links = {}
    prev_link = ''
    for link in output:
        percentage = (output[link] * c[link] * 100) / successful
        if percentage > 10:
            total_percent += percentage
            prev_link = link
            output_links[link] = percentage
        elif prev_link:
            total_percent += percentage
            output_links[prev_link] += percentage
        elif c[link] == 1:
            total_percent += percentage
    logger.info('Web check: %d queries, %d succeeded, %.1f%%', len(queries), successful, total_percent)
    return min(total_percent, 100.0), output_links
