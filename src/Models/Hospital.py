from pony.orm import *
from Models import db

from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from slugify import slugify


class Hospital(db.Entity):
    id = PrimaryKey(int, auto=True)
    clinical_trials = Set('ClinicalTrial')
    # doctors = Set('Doctor')
    name = Required(LongStr)
    slug = Required(str)
    url = Optional(LongStr)
    foursquare_id = Optional(str)
    raw_data = Optional(LongStr)
    log = Optional(LongStr)

    @staticmethod
    def normalize(name):
        normalized_name = name.lower()
        stopword_list = stopwords.words('english')
        filtered_words = [word for word in wordpunct_tokenize(normalized_name) if word not in stopword_list]

        slug = slugify(' '.join(filtered_words))

        return slug
