import time
import HospitalUrlTasks
import clinical_trials_crawler

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
        'search': '',
    }
    
    :param metadata: 
    :return: 
    """
    crawler = clinical_trials_crawler.ClinicalTrialsCrawler(metadata)
    crawler.execute()


