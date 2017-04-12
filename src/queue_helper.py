from rq import Queue
from redis import Redis
from settings import settings

# Object that connects to the task queue
q = Queue(connection=Redis(host=settings['redis']['host'], port=settings['redis']['port'], password=settings['redis']['password']))
