from BaseTask import BaseTask
from pony.orm import *
from Models.Hospital import Hospital
from Models import init_db
import logging
import json
import re

import wikipedia
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)

class HospitalDuplicateChecker(BaseTask):

    def __init__(self, metadata):
        super(HospitalDuplicateChecker, self).__init__(metadata)

    def execute(self):

        init_db()
        name = self.metadata['name']
        normalized_name = Hospital.normalize(name)

        with db_session:
             existing_count = count(h for h in Hospital if h.slug == normalized_name)

             if existing_count == 0:
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
                raw_data=json.dumps(self.metadata)
            )
            commit()


class HospitalUrlEnricher(BaseTask):

    def __init__(self, metadata):

        self.metadata = metadata

    def execute(self):
        with db_session:
            hospital = Hospital[self.metadata['id']];

            wikipedia_page = self.search_wikipedia(hospital.name)

            if wikipedia_page is not False:
                url = self.find_url_on_wikipedia_page(wikipedia_page.html())

                if url and len(url) > 0:
                    hospital.url = url
                    commit()

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
                pass # do nothing, just pretend nothing was found

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


