from queue_helper import q
import HospitalWorkers
import logging
import ClinicalTrialWorker


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
    from FoursquareWorker import FourSquareCrawler
    crawler = FourSquareCrawler(metadata)
    crawler.execute()


def task_hospital_validate_with_knowledge_graph(metadata):
    """Search for the hospital name in Google Knowledge Graph to check if it is a hospital and get a possible url"""
    from HospitalWorkers import KnowledgeGraphValidator
    hospital_validator = KnowledgeGraphValidator(metadata)
    hospital_validator.execute()

    queue_next_tasks(task_hospital_validate_with_knowledge_graph, hospital_validator.metadata)


def task_hospital_duplicate_detector(metadata):
    """Check if the hospital name is already in the database
    
    The name is first normalized to make sure small differences don't influence this step.
    """
    duplicate_filter = HospitalWorkers.DuplicateChecker(metadata)
    duplicate_filter.execute()

    if not duplicate_filter.metadata['duplicate']:
        queue_next_tasks(task_hospital_duplicate_detector, duplicate_filter.metadata)
    else:
        logging.info('{} is a duplicate, so discard.'.format(metadata['name']))


def task_hospital_remove_match_keywords(metadata):
    """ Remove Hospitals that have one of the selected keywords in their name
    
    This step mimics what could have been done with crowdsourcing. Thr crowdsourcing task would ask users to judge if a 
    name is really a hospital name, or something else such as animal hospital, cafetaria in the hospital, parking etc.
     
    The list of keywords here was found by manually looking in the results of foursquare and finding keywords that 
    appeared in non-hospital items. 
    """
    keywords = ['veterinary', 'animal', 'department', 'floor', 'cafe', 'mta', 'cafeteria', 'food', 'parking', 'room',
                'office']

    for keyword in keywords:
        if keyword in metadata['name'].lower():
            logging.info('Keyword {} found in {}'.format(keyword, metadata['name']))
            return

    queue_next_tasks(task_hospital_remove_match_keywords, metadata)


def task_hospital_find_url_from_wikipedia(metadata):
    finder = HospitalWorkers.WikipediaUrlEnricher(metadata)
    finder.execute()

    queue_next_tasks(task_hospital_find_url_from_wikipedia, finder.metadata)


def task_wget_download_hospital(metadata):
    import WgetDownloader
    crawler = WgetDownloader.WgetDownloader(metadata)
    crawler.execute()

    queue_next_tasks(task_wget_download_hospital, crawler.metadata)


def task_find_clinical_trials(hospital_data):
    crawler = ClinicalTrialWorker.ClinicalTrialsCrawler(hospital_data)
    crawler.execute()

    queue_next_tasks(task_find_clinical_trials, crawler.metadata)


def task_save_clinical_trials(hospital_data):
    saver = ClinicalTrialWorker.StoreCTInElastic(hospital_data)
    saver.execute()

    queue_next_tasks(task_save_clinical_trials, saver.metadata)


def known_by_google(metadata):
    return 'is_hospital_google' in metadata


def task_hospital_discard_irrelevant(metadata):
    if known_by_google(metadata):
        if not metadata['is_hospital_google']:
            logging.info('Not a hospital according to google, so discard.')
            return  # discard result

    queue_next_tasks(task_hospital_discard_irrelevant, metadata)


def task_save_hospital(metadata):
    from HospitalWorkers import StoreInElastic
    saver = StoreInElastic(metadata)
    saver.execute()

    queue_next_tasks(task_save_hospital, saver.metadata)


def task_crawl_pubmed(metadata):
    pass

def queue_next_tasks(task_function, metadata):
    """ Queue next tasks
    
    This function checks the `pipeline` dictionary for tasks that should be queued following `task_function`.
    """
    if task_function not in pipeline:
        return  # The calling task is not in the pipeline, so no next tasks can be executed

    tasks = pipeline[task_function]

    for task in tasks:
        logging.info('Queue task {0} for {1}'.format(task.__name__, task_function.__name__))

        # at_front=True gives a depth-first pipeline, as newly generated tasks are also executed first
        # timeout is set not to low because some tasks take quite a while to finish
        q.enqueue_call(func=task, args=(metadata,), at_front=True, timeout=60 * 15)


""" This dictionary defines our pipeline

Each task should call `queue_next_tasks` at the end of the function. This will check the `pipeline` dictionary for 
the next tasks that need to be queued. 
"""
pipeline = {
    task_crawl_foursquare:                          [task_hospital_duplicate_detector],  # Actually defined in the class

    task_hospital_duplicate_detector:               [task_hospital_remove_match_keywords],
    task_hospital_remove_match_keywords:            [task_hospital_validate_with_knowledge_graph],
    task_hospital_validate_with_knowledge_graph:    [task_hospital_find_url_from_wikipedia],
    task_hospital_find_url_from_wikipedia:          [task_hospital_discard_irrelevant],
    task_hospital_discard_irrelevant:               [task_save_hospital, task_crawl_pubmed, task_find_clinical_trials],

    task_find_clinical_trials:                      [task_save_hospital, task_save_clinical_trials],

    task_save_hospital:                             [],

}
