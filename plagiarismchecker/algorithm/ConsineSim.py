"""Cosine similarity between a query and a search-result snippet."""
import math
import re
from collections import Counter

WORD = re.compile(r'\w+')


def get_cosine(vec1, vec2):
    """Similarity in [0, 1] between word-count vectors.

    Only words present in both vectors count, each at its smaller frequency,
    so a short snippet that contains the whole query scores close to 1.
    """
    intersection = set(vec1) & set(vec2)
    match_words = {word: min(vec1[word], vec2[word]) for word in intersection}
    numerator = sum(vec1[word] * match_words[word] for word in intersection)
    sum1 = sum(count ** 2 for count in vec1.values())
    sum2 = sum(count ** 2 for count in match_words.values())
    denominator = math.sqrt(sum1) * math.sqrt(sum2)
    return float(numerator) / denominator if denominator else 0.0


def text_to_vector(text):
    return Counter(WORD.findall(text))


def cosineSim(text1, text2):
    return get_cosine(text_to_vector(text1.lower()), text_to_vector(text2.lower()))
