from pony import orm
from Models import db

from nltk.corpus import stopwords
from nltk.tokenize import wordpunct_tokenize
from slugify import slugify


class Hospital(db.Entity):
    name = orm.Required(str)
    slug = orm.Required(str)
    url = orm.Optional(str)
    # foursquare_id = orm.Optional(str)
    # contact_facebook = orm.Optional(str)
    # contact_twitter = orm.Optional(str)
    # contact_phone = orm.Optional(str)
    #
    # location_address = orm.Optional(str)
    # location_lat = orm.Optional(str)
    # location_lng = orm.Optional(str)



    @staticmethod
    def normalize(name):
        normalized_name = name.lower()
        stopword_list = stopwords.words('english')
        filtered_words = [word for word in wordpunct_tokenize(normalized_name) if word not in stopword_list]

        slug = slugify(' '.join(filtered_words))

        return slug



