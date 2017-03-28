from clinical_trials_crawler import ClinicalTrialsCrawler
import pytest


def test_realworld():
    with_results = ClinicalTrialsCrawler({'search': 'Roosevelt Hospital New York'})
    with_results.execute()
    with_results.print_count()
    assert (with_results.get_amount_of_results() > 0)
    assert (with_results.get_amount_of_results() == with_results.get_downloaded())



