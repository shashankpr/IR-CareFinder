from clinical_trials_crawler import ClinicalTrialsCrawler
import pytest


def test_process_before_download1():
    with pytest.raises(RuntimeError):
        with_results = ClinicalTrialsCrawler({'searchClinicalTrials': 'heart attack los angeles'})
        with_results._process_zip()


def test_process_before_download2():
    with pytest.raises(RuntimeError):
        no_results = ClinicalTrialsCrawler({'searchClinicalTrials': 'jason derulo'})
        no_results._process_zip()


def test_wrong_dict1():
    with pytest.raises(RuntimeError):
        with_results = ClinicalTrialsCrawler({})
        with_results.execute()


def test_wrong_dict2():
    with pytest.raises(RuntimeError):
        with_results = ClinicalTrialsCrawler({'search': 'heart attack los angeles'})
        with_results.execute()


def test_processing1():
    with_results = ClinicalTrialsCrawler({'searchClinicalTrials': 'heart attack los angeles'})
    with_results.execute()
    assert (with_results.get_amount_of_results() > 0)
    assert (with_results.get_amount_of_results() == with_results.get_downloaded())


def test_processing2():
    no_results = ClinicalTrialsCrawler({'searchClinicalTrials': 'jason derulo'})
    no_results.execute()
    assert (no_results.get_amount_of_results() == 0)
    assert (no_results.get_amount_of_results() == no_results.get_downloaded())

