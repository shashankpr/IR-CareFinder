from BaseTask import BaseTask
from settings import settings
from elastic import elastic, get_hospitals_by_normalized_name
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
                self.info('Low Google Knowledge Graph Result score ({})'.format(item['resultScore']))
        else:
            self.info('No Google Knowledge Graph Result')

    def _check_if_type_hospital(self, element):
        if 'Hospital' in element['result']['@type']:
            self.info('Hospital according to Google Knowledge Graph')
            self.metadata['is_hospital_google'] = True
        else:
            self.info('Not a hospital according to Google Knowledge Graph')
            self.metadata['is_hospital_google'] = False

    def _get_hospital_url(self, element):
        if 'url' in element['result']:
            self.info('Google Knowledge Graph found url {}'.format(element['result']['url']))
            self.metadata['url'] = element['result']['url']


class DuplicateChecker(BaseTask):
    def __init__(self, metadata):
        super(DuplicateChecker, self).__init__(metadata)

    def execute(self):
        # Set default value

        self.metadata['duplicate'] = False

        res = get_hospitals_by_normalized_name(self.metadata['name'])

        if len(res) >= 1:
            self.metadata['log'].append('Duplicate entry')
            self.metadata['duplicate'] = True


class StoreInElastic(BaseTask):
    def __init__(self, metadata):
        super(StoreInElastic, self).__init__(metadata)

    def execute(self):
        from elastic import elastic
        from helpers import normalize_hospital_name
        id = normalize_hospital_name(self.metadata['name'])

        res = elastic.index(index="hospital-index", doc_type='hospital', id=id, body=self.metadata)
        print(res['created'])


class WikipediaUrlEnricher(BaseTask):
    def __init__(self, metadata):
        super(WikipediaUrlEnricher, self).__init__(metadata)

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
