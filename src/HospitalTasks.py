from BaseTask import BaseTask
from pony.orm import *
from Models.Hospital import Hospital
from Models import init_db
from settings import settings
import urllib
import logging
import json
import re

import wikipedia
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


class KnowledgeGraphValidator(BaseTask):
    def __init__(self, metadata):
        super(KnowledgeGraphValidator, self).__init__(metadata)

    def execute(self):
        query = self.metadata['name']
        self.api_call(query)

    def api_call(self, query):
        """Make an api all to google knowledge graph"""
        api_key = settings['knowledge_graph']['key']
        service_url = 'https://kgsearch.googleapis.com/v1/entities:search'

        params = {
            'query': query,
            'limit': 1,
            'indent': True,
            'key': api_key,
        }
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())

        if len(response['itemListElement']) > 0:
            item = response['itemListElement'][0]

            if item['resultScore'] > 100:
                self._check_if_type_hospital(item)
                self._get_hospital_url(item)
            else:
                self.metadata['log'].append('Low Google Knowledge Graph Result score ({})'.format(item['resultScore']))
        else:
            self.metadata['log'].append('No Google Knowledge Graph Result')

    def _check_if_type_hospital(self, element):
        if 'Hospital' in element['result']['@type']:
            self.metadata['log'].append('Hospital according to Google Knowledge Graph')
            logging.info("{} is a Hospital".format(element['result']['name']))
        else:
            self.metadata['log'].append('Not a hospital according to Google Knowledge Graph')
            self.metadata['is_hospital_according_to_google'] = False
            logging.info("{} is NOT a Hospital".format(element['result']['name']))

    def _get_hospital_url(self, element):
        if 'url' in element['result']:
            logging.info("Name: {}, URL: {}".format(element['result']['name'], element['result']['url']))
            self.metadata['log'].append('Google Knowledge Graph found url {}'.format(element['result']['url']))
            self.metadata['url'] = element['result']['url']


class DuplicateChecker(BaseTask):
    def __init__(self, metadata):
        super(DuplicateChecker, self).__init__(metadata)

    def execute(self):
        # Set default value
        self.metadata['duplicate'] = False

        init_db()

        name = self.metadata['name']
        normalized_name = Hospital.normalize(name)

        with db_session:
            existing_count = count(h for h in Hospital if h.slug == normalized_name)

            if existing_count >= 1:
                self.metadata['log'].append('Duplicate entry')
                self.metadata['duplicate'] = True


class StoreInDB(BaseTask):
    def __init__(self, metadata):
        super(DuplicateChecker, self).__init__(metadata)

    def execute(self):
        init_db()

        self.add_to_database()

    def add_to_database(self):
        with db_session:
            h = Hospital(
                name=self.metadata['name'],
                slug=Hospital.normalize(self.metadata['name']),
                url=self.metadata['url'],
                foursquare_id=self.metadata['id'],

                # contact_phone=self.metadata['contact']['phone'],
                # contact_twitter=self.metadata['contact']['twitter'],
                # contact_facebook=self.metadata['contact']['facebook'],
                #
                # location_address=self.metadata['location']['address'],
                # location_lat=self.metadata['location']['lat'],
                # location_lng=self.metadata['location']['lng'],
                raw_data=json.dumps(self.metadata),
                log=json.dump(self.metadata['log'])
            )
            commit()
            self.metadata['id'] = h.id


class WikipediaUrlEnricher(BaseTask):
    def __init__(self, metadata):

        self.metadata = metadata

    def execute(self):
        hospital = self.metadata
        wikipedia_page = self.search_wikipedia(hospital['name'])

        if wikipedia_page is not False:
            url = self.find_url_on_wikipedia_page(wikipedia_page.html())

            if url and len(url) > 0:
                hospital['log'].append('Wikipedia found url: {}'.format(url))
                hospital['url'] = url

    def search_wikipedia(self, name):
        logging.info("Checking {}".format(name))
        search_result = wikipedia.search(name)
        logging.info("Found %s pages on wikipedia" % len(search_result))

        if len(search_result) > 0:
            try:
                first_page = wikipedia.page(search_result[0])
                logging.info("Title of first page: %s" % first_page.title)

                return first_page
            except wikipedia.DisambiguationError:
                pass  # do nothing, just pretend nothing was found

        return False

    def find_url_on_wikipedia_page(self, page_html):
        soup = BeautifulSoup(page_html, 'html.parser')
        infobox = soup.find(class_='infobox')

        if infobox is not None:
            logging.debug("Found infobox")

            for element in infobox(text=re.compile(r'Website')):
                url_cell = element.parent.find_next_sibling('td')
                link_element = url_cell.a

                if link_element is not None:
                    logging.info('Found url: {}'.format(link_element['href']))
                    return link_element['href']

        else:
            logging.debug("No infobox found")
