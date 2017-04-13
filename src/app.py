import logging

from tasks import *
from HospitalWorkers import *
from ClinicalTrialWorker import *
import argparse
from queue_helper import q
from elastic import get_all_hospitals, get_hospitals_by_normalized_name

import time

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Best CareFinder commandline interface.')

parser.add_argument('program', help='hostpital-url, foursquare-seeder')
parser.add_argument('--id', action='store', type=str)
parser.add_argument('--task', action='store', type=bool)

args = parser.parse_args()


def get_hospital_as_list():
    if not args.id:
        print('Please provide an hospital id.')
        exit()

    if args.id == 'all':
        results = get_all_hospitals()
    else:
        results = get_hospitals_by_normalized_name(args.id)

    return results


def hospital_commandline_function(task_function, executor_function):
    hospitals = get_hospital_as_list()

    for metadata in hospitals:
        print metadata['name']
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


def hospital_match_keywords():
    hospitals = get_hospital_as_list()

    for hospital in hospitals:
        q.enqueue(task_clinicaltrials_graph_keywords, hospital)


def hospital_smart_names():
    hospitals = get_hospital_as_list()

    for hospital in hospitals:
        q.enqueue(task_hospital_extract_names_smart, hospital)

def wget_download():
    results = get_all_hospitals()
    urls = [h['url'] for h in results]
    urls_unique = list(set(urls))

    for url in urls_unique:
        q.enqueue(task_wget_download_hospital, {'url': url}, ttl=-1,
                  timeout=86400)  # timeout of 24 hours to grab whole site


def foursquare_seeder():
    metadata = {
        "targetSquare": {
            'NE': "40.797480, -73.858479",
            'SW': "40.645527, -74.144426",
            # 'SW': "40.787480, -74.0",
        },
        "step": 0.05
    }

    q.enqueue(task_crawl_foursquare, metadata, ttl=-1)


def clinical_trials():
    hospitals = get_hospital_as_list()

    for hospital in hospitals:
        q.enqueue(task_find_clinical_trials, hospital)

def pubmed_all():
    hospitals = get_hospital_as_list()

    for hospital in hospitals:
        q.enqueue(task_pubmed_crawler, hospital)

programs = {
    'foursquare-seeder': foursquare_seeder,
    'hospital-wikipedia': hospital_wikipedia,
    'hospital-google': hospital_google_graph,
    'hospital-names': hospital_smart_names,
    'clinical-trials': clinical_trials,
    'pubmed-all': pubmed_all,
    'wget-all': wget_download,

    'match-keywords': hospital_match_keywords,
}

if args.program in programs:
    programs.get(args.program)()
else:
    print 'Function not found.'
    for key in programs.keys():
        print '  {}'.format(key)
