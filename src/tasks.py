import time
import HospitalTasks
import clinical_trials_crawler
from queue import q
import logging


def queue_next_tasks(task_function, metadata):
    tasks = pipeline[task_function]

    for task in tasks:
        logging.info('Queue task {0} for {1}'.format(task_function.__name__, task.__name__))
        q.enqueue_call(func=task, args=(metadata,), at_front=True)

    time.sleep(5)


def task_crawl_foursquare(metadata):
    """
    metadata format:

    {
        'NE': '',
        'SW': '',
    }

    :param metadata:
    :return:

    """
    from FoursquareCrawler import FourSquareCrawler
    crawler = FourSquareCrawler(metadata)
    crawler.execute()


def task_hospital_validate_with_knowledge_graph(metadata):
    """Search for the hospital name in Google Knowledge Graph to check if it is a hospital and get a possible url"""
    from HospitalTasks import KnowledgeGraphValidator
    hospital_validator = KnowledgeGraphValidator(metadata)
    hospital_validator.execute()

    queue_next_tasks(task_hospital_validate_with_knowledge_graph, hospital_validator.metadata)


def task_hospital_duplicate_detector(metadata):
    """Check if the hospital name is already in the database
    
    The name is first normalized to make sure small differences don't influence this step.
    """
    duplicate_filter = HospitalTasks.DuplicateChecker(metadata)
    duplicate_filter.execute()

    if not duplicate_filter.metadata['duplicate']:
        queue_next_tasks(task_hospital_duplicate_detector, duplicate_filter.metadata)
    else:
        logging.info('{} is a duplicate'.format(metadata['name']))


def task_hospital_find_url_from_wikipedia(metadata):
    finder = HospitalTasks.WikipediaUrlEnricher(metadata)
    finder.execute()

    queue_next_tasks(task_hospital_find_url_from_wikipedia, finder.metadata)


def task_save_hospital(metadata):
    from HospitalTasks import StoreInDB
    saver = StoreInDB(metadata)
    saver.execute()

    queue_next_tasks(task_save_hospital, saver.metadata)


def task_find_clinical_trials(metadata):
    """
    metadata format:
    
    {
        'search': '',
    }
    
    :param metadata: 
    :return: 
    """

    crawler = clinical_trials_crawler.ClinicalTrialsCrawler(metadata)
    crawler.execute()


def task_crawl_pubmed(metadata):
    pass



""" This dictionary defines our pipeline

Each task should check the the value of pipeline['task_name'] to get a list of tasks to queue next. 
"""
pipeline = {
    task_crawl_foursquare: [task_hospital_duplicate_detector],
    task_hospital_duplicate_detector: [task_hospital_validate_with_knowledge_graph],
    task_hospital_validate_with_knowledge_graph: [task_hospital_find_url_from_wikipedia],
    task_hospital_find_url_from_wikipedia: [task_save_hospital],
    task_save_hospital: [task_crawl_pubmed, task_find_clinical_trials],
}