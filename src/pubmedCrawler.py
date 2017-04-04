# -*- coding: utf-8 -*-
from Bio import Entrez
from Bio import Medline
from bs4 import BeautifulSoup
import re

import requests

#return a list of dictionaries
#each dictionary contain information about an article
#to extract attributes from the dictionary use help_information() for help
def search_pubmed(term,max_count,author=''):
    # can add constraints on the author's name
    term = term + '&' + author + '[author]' if author != '' else term

    print('Getting {0} publications containing {1}...'.format(max_count, term))
    Entrez.email = 'A.N.Other@example.com'
    h = Entrez.esearch(db='pubmed', retmax=max_count, term=term)
    result = Entrez.read(h)
    print('Total number of publications containing {0}: {1}'.format(term, result['Count']))
    ids = result['IdList']
    h = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
    records = Medline.parse(h)

    return records

#the keys of the dictionary is the abbreviation of the term,
#to find out which term correspond to which abbreviation, please
#use this help function
def help_information(show_all=True,term=''):
    # mode=input("please select from options below\nShow all abbr: 1\nSearch for an abbr ")
    if term!='':
        show_all=False

    r=requests.get('https://www.nlm.nih.gov/bsd/mms/medlineelements.html')
    table_block=BeautifulSoup(r.text,"lxml").find("table")

    info=table_block.find_all("a")
    for idx,item in enumerate(info):

        if item.string is None or item.string.strip()=='':
            continue

        if re.match('\([A-Z]+\)',str(item.string)) and show_all:
            print(str(info[idx-1].string) + '--->' + str(item.string))

        if term in str.lower(item.string) and not show_all:
            print(str(item.string)+"--->"+str(info[idx+1].string))
