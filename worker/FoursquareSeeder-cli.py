

from redis import Redis
from rq import Queue

q = Queue(connection=Redis())


from tasks import task_crawl_foursquare

parameters = {
        'NE': '',
        'SW': '',
}

result = q.enqueue(task_crawl_foursquare, 'http://nvie.com')

