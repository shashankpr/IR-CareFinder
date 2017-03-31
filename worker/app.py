import logging
from rq import Queue
from redis import Redis
from tasks import task_crawl_foursquare, task_find_clinical_trials
import argparse
from pony.orm import *
import Models
from Models.Hospital import Hospital
import time

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Best CareFinder commandline interface.')

parser.add_argument('program', help='hostpital-url, foursquare-seeder')
parser.add_argument('--id', action='store', type=int)
q = Queue(connection=Redis())


args = parser.parse_args()
print args


def hospital_url():
    if not args.id:
        print 'Please provide an hospital id.'
        exit

    hospital_list = []
    if args.id == -1:
        with db_session:
            hospital_list = select(hospital.id for hospital in Hospital if hospital.url == '')[:]
    else:
        hospital_list = [args.id]

    from HospitalUrlTasks import HospitalUrlEnricher

    for hospital_id in hospital_list:
        task = HospitalUrlEnricher({'id': hospital_id})
        task.execute()
        time.sleep(1)


def foursquare_seeder():
    q = Queue(connection=Redis())

    metadata = {
        "targetSquare": {
            'NE': "40.797480, -73.858479",
            'SW': "40.645527, -74.144426",
        },
        "step": 0.05
    }

    q.enqueue(task_crawl_foursquare, metadata, ttl=-1)

def clinical_trials():
    if not args.id:
        print 'Please provide an hospital id.'
        return

    hospital_list = []
    if args.id == -1:
        with db_session:
            hospital_list = select(hospital.id for hospital in Hospital if hospital.url == '')[:]
    else:
        hospital_list = [args.id]

    for hospital_id in hospital_list:
        q.enqueue(task_find_clinical_trials, {'search': hospital_id}, ttl=-1)

programs = {
    'foursquare-seeder': foursquare_seeder,
    'hospital-url': hospital_url,
    'clinical-trial': clinical_trials,
}

if args.program in programs:
    Models.init_db()
    programs.get(args.program)()
else:
    print 'Function not found.'
