

data = [
    {
        "name": "Bellevue Hospital Center",
        "url": "www.nychealthandhospitals.org",
    },
    {
        "name": "New York Presbyterian Hospital Weill Cornell Medical Center",
        "url": "nyp.org",
    },
    {
        "name": "Mount Sinai Beth Israel",
        "url": "www.mountsinai.org",
    }
]

# Search wikipedia
import wikipedia
import logging
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

def search_wikipedia(name):

    search_result = wikipedia.search(name)
    logging.info("Found %s pages on wikipedia" % len(search_result))

    first_page = wikipedia.page(search_result[0])
    logging.info("Title of first page: %s" % first_page.title)

    return first_page

def find_url_on_wikipedia_page(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    infobox = soup.find(class_='infobox')
    found_urls = []

    if type(infobox):
        logging.debug("Found infobox")

        for row in infobox.find_all('tr'):

            url = row.find(class_='url')
            if url:
                href = url.a['href']
                logging.info('Found URL %s' % href)
                found_urls.append(href)
    else:
        logging.debug("No infobox found")

    return found_urls


wikipedia_page = search_wikipedia('Mount Sinai Beth Israel')

find_url_on_wikipedia_page(wikipedia_page.html())


for hospital in data:
    page = search_wikipedia(hospital['name'])
    hospital['found_urls'] = find_url_on_wikipedia_page(page.html())

for hospital in data:
    logging.info("Hospital: {} urls: {}".format(hospital['name'], hospital['found_urls']))