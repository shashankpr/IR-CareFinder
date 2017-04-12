from slugify import slugify
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


def normalize_hospital_name(name):
    """Normalizes a given hospital name.
        1. Converts all words to lower case.
        2. Removes all stopwords.

    Args:
        name -- Name to be normalized.

    Returns:
        slug -- The normalized hospital name.
    """
    normalized_name = name.lower()

    stopword_list = stopwords.words('english')
    filtered_words = [word for word in wordpunct_tokenize(normalized_name) if word not in stopword_list]

    slug = slugify(' '.join(filtered_words))

    return slug

