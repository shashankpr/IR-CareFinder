

class BaseTask:

    def __init__(self, metadata):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
