from queue import q
class BaseTask(object):
    __queue = None

    def __init__(self, metadata):
        self.metadata = metadata

    def execute(self):
        raise NotImplementedError

    @property
    def queue(self):
        return q
