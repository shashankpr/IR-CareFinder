from clinical_trials_crawler import ClinicalTrialsCrawler
import pytest


# def test_process_before_download1():
#     with pytest.raises(RuntimeError):
#         with_results = ClinicalTrialsCrawler({'search': 'heart attack los angeles'})
#         with_results._process_zip()
#
#
# def test_process_before_download2():
#     with pytest.raises(RuntimeError):
#         no_results = ClinicalTrialsCrawler({'search': 'jason derulo'})
#         no_results._process_zip()
#
#
# def test_download1():
#     with_results = ClinicalTrialsCrawler({'search': 'heart attack los angeles'})
#     with_results._download_zip()
#
#
# def test_download2():
#     no_results = ClinicalTrialsCrawler({'search': 'jason derulo'})
#     no_results._download_zip()
#
#
# def test_processing1():
#     with_results = ClinicalTrialsCrawler({'search': 'heart attack los angeles'})
#     with_results.execute()
#     with_results.print_count()
#     assert (with_results.get_amount_of_results() > 0)
#     assert (with_results.get_amount_of_results() == with_results.get_downloaded())
#
#
# def test_processing2():
#     no_results = ClinicalTrialsCrawler({'search': 'jason derulo'})
#     no_results.execute()
#     no_results.get_amount_of_results()
#     assert (no_results.get_amount_of_results() == 0)
#     assert (no_results.get_amount_of_results() == no_results.get_downloaded())


# def test_massive():
#     new_york_results = ClinicalTrialsCrawler({'search': 'new york'})
#     new_york_results.execute()
#     new_york_results.get_amount_of_results()
#     assert (new_york_results.get_amount_of_results() > 0)
