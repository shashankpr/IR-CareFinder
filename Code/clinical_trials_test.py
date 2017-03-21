from clinical_trials_crawler import clinical_trials_crawler
import pytest


def test_process_before_download1():
    with pytest.raises(RuntimeError):
        with_results = clinical_trials_crawler("heart attack los angeles")
        with_results._process_zip()


def test_process_before_download2():
    with pytest.raises(RuntimeError):
        no_results = clinical_trials_crawler("jason derulo")
        no_results._process_zip()


def test_download1():
    with_results = clinical_trials_crawler("heart attack los angeles")
    with_results._download_zip()


def test_download2():
    no_results = clinical_trials_crawler("jason derulo")
    no_results._download_zip()


def test_processing1():
    with_results = clinical_trials_crawler("heart attack los angeles")
    with_results.execute_search()
    assert (with_results.get_amount_of_results() > 0)


def test_processing2():
    no_results = clinical_trials_crawler("jason derulo")
    no_results.execute_search()
    assert (no_results.get_amount_of_results() == 0)
