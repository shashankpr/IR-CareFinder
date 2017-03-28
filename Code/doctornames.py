import requests
from bs4 import BeautifulSoup


class DoctorNames:
    def __init__(self, metadata):
        self.metadata = metadata
        self.url = metadata.get('hospitalurl')
        self.results = []

    def execute(self):
        listing = requests.get(self.url)
        soup = BeautifulSoup(listing.content, 'html.parser')
        soup.prettify()

        for string in soup.stripped_strings:
            string = string.strip()
            if "D." in string:
                name = string
                name = name.split(",")[0]
                self.results.append(name)

        print self.results
