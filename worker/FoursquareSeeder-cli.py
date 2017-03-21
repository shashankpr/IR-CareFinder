import logging
from redis import Redis
from rq import Queue
from tasks import task_crawl_foursquare

logging.basicConfig(level=logging.INFO)

q = Queue(connection=Redis())


metadata = {
    "targetSquare": {
        'NE': "40.797480, -73.858479",
        'SW': "40.645527, -74.144426",
    },
    "step": 0.05
}

result = q.enqueue(task_crawl_foursquare, metadata, ttl=-1)


