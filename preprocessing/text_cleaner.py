import re
import nltk
from bs4 import BeautifulSoup
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer


FALLBACK_STOP_WORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from",
    "has", "he", "in", "is", "it", "its", "of", "on", "that", "the",
    "to", "was", "were", "will", "with", "this", "these", "those",
}


def _load_stop_words():
    try:
        nltk.data.find("corpora/stopwords")
        return set(stopwords.words("english"))
    except LookupError:
        return FALLBACK_STOP_WORDS


class _IdentityLemmatizer:
    def lemmatize(self, word):
        return word


def _load_lemmatizer():
    try:
        nltk.data.find("corpora/wordnet")
        return WordNetLemmatizer()
    except LookupError:
        return _IdentityLemmatizer()


stop_words = _load_stop_words()
lemmatizer = _load_lemmatizer()


def advanced_clean_text(text):

    text = text.lower()

    text = BeautifulSoup(
        text,
        "html.parser"
    ).get_text()

    text = re.sub(
        r"http\S+",
        "",
        text
    )

    text = re.sub(
        r"[^a-zA-Z\s]",
        " ",
        text
    )

    text = re.sub(
        r"\s+",
        " ",
        text
    ).strip()

    words = text.split()

    cleaned_words = []

    for word in words:

        if word not in stop_words:

            lemma_word = lemmatizer.lemmatize(word)

            cleaned_words.append(lemma_word)

    return " ".join(cleaned_words)
