import re
import nltk

resources = {
    "corpora/stopwords": "stopwords",
    "corpora/wordnet": "wordnet",
    "corpora/omw-1.4": "omw-1.4",
    "tokenizers/punkt": "punkt",
}

for resource_path, resource_name in resources.items():
    try:
        nltk.data.find(resource_path)
    except LookupError:
        nltk.download(resource_name)

from bs4 import BeautifulSoup

from nltk.corpus import stopwords

from nltk.stem import WordNetLemmatizer


stop_words = set(stopwords.words('english'))

lemmatizer = WordNetLemmatizer()


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