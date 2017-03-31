from HospitalUrlTasks import HospitalDuplicateChecker
from Models import init_db

data = {'url': '',
        'contact': {'phone': '', 'twitter': None, 'facebook': ''},
        'location': {
            'lat': 40.76772814802792,
            'lng': -73.90321519262554,
            'address': [u'98th Street (Madison Ave)', u'Manhattan, NY 10128', u'United States']},
        'id': u'4eb7dccc7ee5024d8005dac0',
        'name': u"Mt Sinai Hospital, Dr Harbison's office 10 Floor"}


init_db()

task = HospitalDuplicateChecker(metadata=data)

task.execute()
