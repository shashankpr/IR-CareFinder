import time


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
    import FoursquareCrawler
    crawler = FoursquareCrawler(metadata)
    crawler.execute()


def task_find_hospital_url(metadata):
    import HospitalUrlFinder

    finder = HospitalUrlFinder(metadata)
    finder.execute()
