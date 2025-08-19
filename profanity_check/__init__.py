import re

# Minimal local implementation to satisfy `profanity_free` guard imports
# and provide a basic profanity signal without external deps.

_DEFAULT_PROFANE_WORDS = {
    "fuck", "shit", "bitch", "bastard", "asshole", "dick", "cunt",
    "slut", "whore", "piss", "douche", "bollocks", "bloody", "crap",
}

_word_boundary_pattern = re.compile(r"\b({})\b".format("|".join(map(re.escape, _DEFAULT_PROFANE_WORDS))), re.IGNORECASE)


def _score_text(text: str) -> float:
    if not isinstance(text, str):
        return 0.0
    return 1.0 if _word_boundary_pattern.search(text or "") else 0.0


def predict(texts):
    if isinstance(texts, (list, tuple)):
        return [int(_score_text(t) >= 0.5) for t in texts]
    return [int(_score_text(texts) >= 0.5)]


def predict_prob(texts):
    if isinstance(texts, (list, tuple)):
        return [_score_text(t) for t in texts]
    return [_score_text(texts)]


