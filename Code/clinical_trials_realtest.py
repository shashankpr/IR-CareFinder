from clinical_trials_crawler import ClinicalTrialsCrawler
import pytest


def pytest_generate_tests(metafunc):
    if "search_string" in metafunc.funcargnames:
        with open('list_of_hospitals.txt') as f:
            hospitals = f.readlines()
            metafunc.parametrize("search_string", hospitals)

def test_realworld(search_string):
    print search_string
    with_results = ClinicalTrialsCrawler({'search': search_string})
    with_results.execute()
    with_results.print_count()
    assert (with_results.get_amount_of_results() == with_results.get_downloaded())



