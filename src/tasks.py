import time
import HospitalTasks
import clinical_trials_crawler
from queue import q
import logging


def queue_next_tasks(task_function, metadata):
    if task_function not in pipeline:
        return

    tasks = pipeline[task_function]

    for task in tasks:
        logging.info('Queue task {0} for {1}'.format(task_function.__name__, task.__name__))
        q.enqueue_call(func=task, args=(metadata,), at_front=True)


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
        logging.info('{} is a duplicate, so discard.'.format(metadata['name']))


def task_hospital_find_url_from_wikipedia(metadata):
    finder = HospitalTasks.WikipediaUrlEnricher(metadata)
    finder.execute()

    queue_next_tasks(task_hospital_find_url_from_wikipedia, finder.metadata)


def task_wget_download_hospital(metadata):
    import WgetDownloader
    crawler = WgetDownloader.WgetDownloader(metadata)
    crawler.execute()

    queue_next_tasks(task_wget_download_hospital, crawler.metadata)


def known_by_google(metadata):
    return 'is_hospital_google' in metadata


def task_hospital_discard_irrelevant(metadata):
    if known_by_google(metadata):
        if not metadata['is_hospital_google']:
            logging.info('Not a hospital according to google, so discard.')
            return  # discard result

    queue_next_tasks(task_hospital_discard_irrelevant, metadata)


def task_save_hospital(metadata):
    from HospitalTasks import StoreInElastic
    saver = StoreInElastic(metadata)
    saver.execute()

    queue_next_tasks(task_save_hospital, saver.metadata)


def task_find_clinical_trials(metadata):
    crawler = clinical_trials_crawler.ClinicalTrialsCrawler(metadata)
    crawler.execute()
    
    init_db()
    for ct in crawler.results.itervalues():
        conditions = ', '.join(ct['condition'])

        if ct.has_key('conditions_mesh'):
            conditions_mesh = ', '.join(ct['conditions_mesh'])

        if ct.has_key('keyword'):
            keyword = ', '.join(ct['keyword'])

        with db_session:
            clinicaltrial = ClinicalTrial(
                id=ct['nct_id'],
                title=ct['title'],
                condition = conditions,
                conditions_mesh = conditions_mesh,
                keyword = keyword,
            )

            hospital = Hospital[crawler.metadata['query']]
            clinicaltrial.hospitals.add(hospital)
            hospital.clinical_trials.add(clinicaltrial)
            commit()


def task_crawl_pubmed(metadata):
    pass


""" This dictionary defines our pipeline

Each task should check the the value of pipeline['task_name'] to get a list of tasks to queue next. 
"""
pipeline = {
    task_crawl_foursquare:                          [task_hospital_duplicate_detector],

    task_hospital_duplicate_detector:               [task_hospital_validate_with_knowledge_graph],
    task_hospital_validate_with_knowledge_graph:    [task_hospital_find_url_from_wikipedia],
    task_hospital_find_url_from_wikipedia:          [task_hospital_discard_irrelevant],
    task_hospital_discard_irrelevant:               [task_save_hospital],

    task_save_hospital: [], #task_crawl_pubmed, task_find_clinical_trials
}
