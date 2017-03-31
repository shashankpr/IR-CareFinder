from rq import Queue
from redis import Redis
from settings import settings


q = Queue(connection=Redis(host=settings['redis']['host'], port=settings['redis']['port'], password=settings['redis']['auth']))
