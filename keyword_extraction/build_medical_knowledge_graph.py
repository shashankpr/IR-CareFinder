import logging
from bs4 import BeautifulSoup
import urllib2

logging.basicConfig(level=logging.INFO)

url     =   "https://medlineplus.gov/healthtopics.html"
page    =   urllib2.urlopen(url)

def find_health_topics(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    disease_categories = soup.find('div', attrs={'id':'section_1'})

    for categories in disease_categories.find_all('li'):
        links = categories.a['href']
        category_name = categories.a.get_text()
        logging.info("Link: {} Names: {}".format(links, category_name))


    #print disease_categories


find_health_topics(page)