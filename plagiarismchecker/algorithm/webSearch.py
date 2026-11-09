"""Google Custom Search JSON API client used by the web plagiarism check."""
import logging

import requests
from django.conf import settings

from plagiarismchecker.algorithm import ConsineSim

logger = logging.getLogger(__name__)

API_URL = 'https://www.googleapis.com/customsearch/v1'


class SearchNotConfigured(Exception):
    """GOOGLE_API_KEY / GOOGLE_CSE_ID are not set."""


def is_configured():
    return bool(settings.GOOGLE_API_KEY and settings.GOOGLE_CSE_ID)


def search(query, session=None):
    """Return the result items (dicts with 'link' and 'snippet') for one query."""
    if not is_configured():
        raise SearchNotConfigured('Set GOOGLE_API_KEY and GOOGLE_CSE_ID to enable web search.')
    http = session or requests
    response = http.get(API_URL, params={'key': settings.GOOGLE_API_KEY,
                                         'cx': settings.GOOGLE_CSE_ID, 'q': query}, timeout=10)
    response.raise_for_status()
    return response.json().get('items', [])


def searchWeb(text, output, c, session=None):
    """Search one query and fold the best match into ``output`` (hit counts per link)
    and ``c`` (average similarity per link). Returns (output, c, error_count)."""
    try:
        items = search(text, session=session)
    except SearchNotConfigured:
        raise
    except Exception as exc:  # network error, quota exceeded, bad response
        # Never log the request URL: it contains the API key.
        logger.warning('Custom Search request failed: %s', exc.__class__.__name__)
        return output, c, 1

    if not items:
        return output, c, 0

    max_sim = 0
    item_link = ''
    for item in items[:5]:
        sim = ConsineSim.cosineSim(text, item.get('snippet', ''))
        if sim > max_sim:
            max_sim = sim
            item_link = item.get('link', '')
        if item.get('link') in output:
            item_link = item['link']
            break

    if not item_link:
        return output, c, 0
    if item_link in output:
        output[item_link] += 1
        c[item_link] = (c[item_link] * (output[item_link] - 1) + max_sim) / output[item_link]
    else:
        output[item_link] = 1
        c[item_link] = max_sim
    return output, c, 0
