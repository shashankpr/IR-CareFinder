from slugify import slugify
from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize


def normalize_hospital_name(name):
    normalized_name = name.lower()

    stopword_list = stopwords.words('english')
    filtered_words = [word for word in wordpunct_tokenize(normalized_name) if word not in stopword_list]

    slug = slugify(' '.join(filtered_words))

    return slug

