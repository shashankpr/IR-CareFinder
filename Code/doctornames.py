import requests
from bs4 import BeautifulSoup
import re


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

            result = re.match(r'(\D*)M\.?D\.?(\D*)', string)
            if result:
                name = result.group(1)
                self.results.append(name.strip())

        print self.results


if __name__ == '__main__':

    urls = [
        'http://www.barnabashealth.org/Jersey-City-Medical-Center/Our-Doctors/Search-Results.aspx?Name=a&L=6613726', # WORKS 10/10
        'https://www.mountsinai.org/find-a-doctor/result?pcp=false&searchby=byname&lastName=a', # Dynamic, with invalid results
        'http://www.kingsbrook.org/Physician-Directory.aspx'
    ]

    for url in urls:
        c = DoctorNames({'hospitalurl' : url})
        c.execute()


