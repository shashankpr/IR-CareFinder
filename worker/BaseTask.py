class BaseTask(object):
    __queue = None

    def __init__(self, metadata):
        self.metadata = metadata

    def execute(self):
        raise NotImplementedError

    @property
    def queue(self):
        if self.__queue is None:
            from redis import Redis
            from rq import Queue

            self.__queue = Queue(connection=Redis())

        return self.__queue
