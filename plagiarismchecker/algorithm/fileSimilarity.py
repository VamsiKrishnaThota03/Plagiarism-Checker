"""Document-vs-document similarity: cosine similarity of term-frequency vectors."""
import math
import re
from collections import Counter

from .stopwords import english_stopwords

_NON_WORD = re.compile(r'[^\w]+')


def tokenize(text):
    """Lower-case words with punctuation removed and stopwords dropped."""
    stops = english_stopwords()
    return [w for w in _NON_WORD.sub(' ', (text or '').lower()).split() if w not in stops]


def findFileSimilarity(inputQuery, database):
    """Return the similarity of two texts as a percentage (0-100).

    Returns 0.0 when either text has no meaningful words.
    """
    query_tf = Counter(tokenize(inputQuery))
    database_tf = Counter(tokenize(database))
    if not query_tf or not database_tf:
        return 0.0

    dot = sum(count * database_tf[word] for word, count in query_tf.items())
    query_norm = math.sqrt(sum(c * c for c in query_tf.values()))
    database_norm = math.sqrt(sum(c * c for c in database_tf.values()))
    return dot / (query_norm * database_norm) * 100
