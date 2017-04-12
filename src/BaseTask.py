import logging


class BaseTask(object):
    __queue = None

    def __init__(self, metadata):
        """Initializes a task.

        Args:
            metadata -- Input dictionary.
        """
        self.metadata = metadata

    def execute(self):
        """Executes BaseTask.
        Raises error as BaseTask is not allowed to be executed.
        """
        raise NotImplementedError

    def info(self, message):
        """Adds message to internal log.
        
        Args:
            message -- Info message.
        """
        self.metadata['log'].append(message)
        logging.info(message)
