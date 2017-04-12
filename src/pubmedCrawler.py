# -*- coding: utf-8 -*-
from Bio import Entrez
from Bio import Medline
from bs4 import BeautifulSoup
import re

import requests


def search_pubmed(author='', max_count=100):
    """Search the pubmed database

    Args:
        max_count -- specifies how many results will be returned
        author -- name of doctor of interest

    Returns:
        records -- a list of dictionaries, each dictionary contains information about an article
    """
    term = author + '[author]'

    print('Getting {0} publications of {1}...'.format(max_count, term))
    Entrez.email = 'A.N.Other@example.com'
    h = Entrez.esearch(db='pubmed', retmax=max_count, term=term)
    result = Entrez.read(h)
    print('Total number of publications containing {0}: {1}'.format(term, result['Count']))
    ids = result['IdList']
    h = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
    records = Medline.parse(h)

    return records


def help_information(show_all=True, term=''):
    """Find corresponding abbreviations of features in the Medline format,
       so as to access information in the articles dictionary.


    Args:
        show_all: if true, show all features and their abbreviations
        term: feature of interest
    """
    if term != '':
        show_all = False

    r = requests.get('https://www.nlm.nih.gov/bsd/mms/medlineelements.html')
    table_block = BeautifulSoup(r.text, "lxml").find("table")

    info = table_block.find_all("a")
    for idx, item in enumerate(info):

        if item.string is None or item.string.strip() == '':
            continue

        if re.match('\([A-Z]+\)', str(item.string)) and show_all:
            print(str(info[idx - 1].string) + '--->' + str(item.string))

        if term in str.lower(item.string) and not show_all:
            print(str(item.string) + "--->" + str(info[idx + 1].string))
