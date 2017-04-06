from queue import q
import logging

class BaseTask(object):
    __queue = None

    def __init__(self, metadata):
        self.metadata = metadata

    def execute(self):
        raise NotImplementedError

    def info(self, message):
        self.metadata['log'].append(message)
        logging.info(message)

    @property
    def queue(self):
        return q
