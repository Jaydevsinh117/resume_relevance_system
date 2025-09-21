import re
import string

# optional advanced libraries
try:
    import nltk
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer

    # ensure nltk data is available
    try:
        nltk.data.find("tokenizers/punkt")
    except LookupError:
        nltk.download("punkt", quiet=True)

    try:
        nltk.data.find("corpora/stopwords")
    except LookupError:
        nltk.download("stopwords", quiet=True)

    try:
        nltk.data.find("corpora/wordnet")
    except LookupError:
        nltk.download("wordnet", quiet=True)

    STOPWORDS = set(stopwords.words("english"))
    LEMMATIZER = WordNetLemmatizer()

except Exception:
    STOPWORDS = set()
    LEMMATIZER = None


# --------------------------
# basic clean text
# --------------------------
def clean_text(text: str) -> str:
    """Lowercase, remove punctuation, normalize whitespace, strip URLs."""
    text = text.lower()
    text = re.sub(r"http\S+", "", text)  # remove urls
    text = text.translate(str.maketrans("", "", string.punctuation))
    text = re.sub(r"\s+", " ", text).strip()
    return text


# --------------------------
# tokenize
# --------------------------
def tokenize(text: str, include_numbers=True) -> list:
    """Split text into tokens. Optionally include numbers."""
    if include_numbers:
        return re.findall(r"[a-zA-Z0-9]+", text.lower())
    return re.findall(r"[a-zA-Z]+", text.lower())


# --------------------------
# remove stopwords
# --------------------------
def remove_stopwords(tokens: list) -> list:
    if not STOPWORDS:
        return tokens  # fallback if nltk not available
    return [t for t in tokens if t not in STOPWORDS]


# --------------------------
# lemmatize
# --------------------------
def lemmatize(tokens: list) -> list:
    if not LEMMATIZER:
        return tokens
    return [LEMMATIZER.lemmatize(t) for t in tokens]


# --------------------------
# n-grams
# --------------------------
def generate_ngrams(tokens: list, n: int = 2) -> list:
    """Create n-grams from tokens (e.g., ['machine', 'learning'] -> ['machine_learning'])."""
    return ["_".join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)]


# --------------------------
# preprocess pipeline
# --------------------------
def preprocess(
    text: str,
    use_stopwords=True,
    use_lemmatize=True,
    include_numbers=True,
    ngrams: int = 0
) -> list:
    """
    Full pipeline: clean -> tokenize -> optional stopwords -> optional lemmatize -> optional ngrams

    Args:
        text (str): raw text
        use_stopwords (bool): remove common stopwords
        use_lemmatize (bool): reduce words to base form
        include_numbers (bool): keep numeric tokens
        ngrams (int): generate n-grams (0 = none, 2 = bigrams, 3 = trigrams, etc.)

    Returns:
        list of processed tokens
    """
    cleaned = clean_text(text)
    tokens = tokenize(cleaned, include_numbers=include_numbers)

    if use_stopwords:
        tokens = remove_stopwords(tokens)
    if use_lemmatize:
        tokens = lemmatize(tokens)
    if ngrams and ngrams > 1:
        tokens += generate_ngrams(tokens, ngrams)

    return tokens
