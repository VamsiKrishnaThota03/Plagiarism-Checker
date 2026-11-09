"""English stopwords from NLTK, with a built-in fallback when the corpus is unavailable."""
import logging
from functools import lru_cache

logger = logging.getLogger(__name__)

# Subset of NLTK's English list, used only if the corpus can't be loaded or downloaded.
_FALLBACK = set("""
i me my myself we our ours ourselves you your yours yourself yourselves he him his himself she her
hers herself it its itself they them their theirs themselves what which who whom this that these
those am is are was were be been being have has had having do does did doing a an the and but if or
because as until while of at by for with about against between into through during before after
above below to from up down in out on off over under again further then once here there when where
why how all any both each few more most other some such no nor not only own same so than too very
s t can will just don should now d ll m o re ve y ain aren couldn didn doesn hadn hasn haven isn ma
mightn mustn needn shan shouldn wasn weren won wouldn
""".split())


@lru_cache(maxsize=1)
def english_stopwords():
    try:
        from nltk.corpus import stopwords
        try:
            return frozenset(stopwords.words('english'))
        except LookupError:
            import nltk
            if nltk.download('stopwords', quiet=True):
                return frozenset(stopwords.words('english'))
    except Exception:  # offline, read-only filesystem, ...
        logger.warning('NLTK stopwords unavailable; using built-in list', exc_info=True)
    return frozenset(_FALLBACK)
