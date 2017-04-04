import time
import HospitalUrlTasks
import clinical_trials_crawler
from pony.orm import *
from Models import init_db
from Models import ClinicalTrial
from Models import Hospital

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


def task_duplicate_hospital(metadata):
    duplicate_filter = HospitalUrlTasks.HospitalDuplicateChecker(metadata)
    duplicate_filter.execute()


def task_find_hospital_url(metadata):
    finder = HospitalUrlTasks.HospitalUrlTasks(metadata)
    finder.execute()

def task_find_clinical_trials(metadata):
    """
    metadata format:
    
    {
        'query': '',
    }
    
    :param metadata: 
    :return: 
    """
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


