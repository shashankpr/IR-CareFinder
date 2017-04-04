from pony import orm
from settings import settings

db = orm.Database()


def init_db():
    db.bind('mysql',
            host=settings['mysql']['host'],
            user=settings['mysql']['user'],
            passwd=settings['mysql']['pass'],
            db=settings['mysql']['db'])

    db.generate_mapping(create_tables=False)
