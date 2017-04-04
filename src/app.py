import logging
from tasks import *
from HospitalTasks import *
import argparse
from queue import q
from pony.orm import *
import Models
from Models.Hospital import Hospital
import time
import json

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Best CareFinder commandline interface.')

parser.add_argument('program', help='hostpital-url, foursquare-seeder')
parser.add_argument('--id', action='store', type=int)
parser.add_argument('--task', action='store', type=bool)

args = parser.parse_args()

def get_hospital_as_list():
    if not args.id:
        print('Please provide an hospital id.')
        exit()

    with db_session:
        if args.id == -1:
            hospital_list = select(hospital.raw_data for hospital in Hospital)[:]
        else:
            hospital_list = select(hospital.raw_data for hospital in Hospital if hospital.id == args.id)[:]
    return hospital_list


def hospital_commandline_function(task_function, executor_function):
    hospitals = get_hospital_as_list()

    for metadata_json in hospitals:
        metadata = json.loads(metadata_json)
        if args.task:
            task_function(metadata)
        else:
            executor = executor_function(metadata)
            executor.execute()

        time.sleep(1)


def hospital_wikipedia():
    hospital_commandline_function(task_hospital_find_url_from_wikipedia, WikipediaUrlEnricher)


def hospital_google_graph():
    hospital_commandline_function(task_hospital_validate_with_knowledge_graph, KnowledgeGraphValidator)



def foursquare_seeder():
    metadata = {
        "targetSquare": {
            'NE': "40.797480, -73.858479",
            # 'SW': "40.645527, -74.144426",
            'SW': "40.787480, -74.0",
        },
        "step": 0.05
    }

    q.enqueue(task_crawl_foursquare, metadata, ttl=-1)

def clinical_trials(    ):
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
    'hospital-wikipedia': hospital_wikipedia,
    'hospital-google': hospital_google_graph,
    'clinical-trial': clinical_trials,
}

if args.program in programs:
    Models.init_db()
    programs.get(args.program)()
else:
    print 'Function not found.'
    for key in programs.keys():
        print '  {}'.format(key)
