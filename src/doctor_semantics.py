import logging
from bs4 import BeautifulSoup
import urllib2

logging.basicConfig(filename='graphdoc.log', filemode='w', level=logging.DEBUG)

url     =   "https://en.wikipedia.org/wiki/Specialty_(medicine)"
page    =   urllib2.urlopen(url)

def url_to_html(url):

    page_html = urllib2.urlopen(url)
    return page_html

def get_speciality(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    speciality_sec = soup.find('div', attrs={'id':'mw-content-text'})

    tables_sec = speciality_sec.find_all('table')
    spec_table = tables_sec[1]

    data = []
    specialities = {}
    for rows in spec_table.find_all('tr'):
        cols = rows.find_all('td')
        cols = [ele.text for ele in cols]

        data.append(cols)

    #print data

    relation1 = "subSpeciality"
    relation2 = "focusOn"
    relation3 = "groupBy"
    #print data
    spec_list = []
    code_list = []
    group_list = []
    subspec_list = []
    focus_list = []
    for items in data:

        #print len(items)
        for vals in items:
            text = vals.split(',')
            ref_text = text
            #print len(text[0])
            print ref_text
            for i in ref_text:
                print i.split()[0]

            # specialities[text[0]][relation1] = text[3]
            # specialities[text[0]][relation2] = text[4]
            # specialities[text[0]][relation3] = text[2]

        #print specialities

get_speciality(page)