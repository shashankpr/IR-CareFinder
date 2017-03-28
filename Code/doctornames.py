import requests
from bs4 import BeautifulSoup
import re


class DoctorNames:
    # Initi
    def __init__(self, metadata):
        self.metadata = metadata
        self.url = metadata.get('hospitalurl')
        self.results = []

    def execute(self):
        listing = requests.get(self.url)
        soup = BeautifulSoup(listing.content, 'html.parser')
        soup.prettify()
        results = soup.find_all('a', href=re.compile("physicians/find-a-physician/detail/"))


        for elements in results:
            name = elements.get_text().strip()
            name = name.split(",")[0]
            self.results.append(name)

        print self.results
