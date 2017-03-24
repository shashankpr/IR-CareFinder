from BaseTask import BaseTask
from pony.orm import *
from Models.Hospital import Hospital
from Models import init_db



class HospitalDuplicateChecker(BaseTask):

    def __init__(self, metadata):
        super(HospitalDuplicateChecker, self).__init__(metadata)

    def execute(self):

        init_db()
        name = self.metadata['name']
        normalized_name = Hospital.normalize(name)

        with db_session:
             existing_count = count(h for h in Hospital if h.slug == normalized_name)

             if existing_count == 0:
                 self.add_to_database()


    def add_to_database(self):
        with db_session:
            h = Hospital(
                name=self.metadata['name'],
                slug=Hospital.normalize(self.metadata['name']),
                url=self.metadata['url'])
            commit()


class HospitalUrlEnricher(BaseTask):

    def __init__(self, metadata):
        self.metadata = metadata

    def execute(self):
        pass
