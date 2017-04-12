# -*- coding: utf-8 -*-
from Bio import Entrez
from Bio import Medline
from BaseTask import BaseTask
import time
from elastic import elastic


class StorePublicationsInElastic(BaseTask):
    def __init__(self, metadata):
        super(StorePublicationsInElastic, self).__init__(metadata)

    def execute(self):

        if 'papers' not in self.metadata:
            return

        for paper in self.metadata['papers']:
            self.save_single(paper, self.metadata['normalized-name'])

    def save_single(self, paper, normalize_hospital_name):
        id = '{}-{}-{}'.format(normalize_hospital_name, paper['searched_name'], paper['pmid'])

        result = elastic.index(index="publication-index", doc_type='publication', id=id, body=paper)


class PubMedCrawler(BaseTask):
    def __init__(self, metadata):
        super(PubMedCrawler, self).__init__(metadata)
        Entrez.email = 'A.N.Other@example.com'

    def execute(self):

        if 'doctors' not in self.metadata:
            return

        names = self.metadata['doctors']

        papers = []
        for name in names:
            papers.extend(self.search_pubmed(name))

        self.metadata['papers'] = papers

    def search_pubmed(self, author, max_count=1000):
        """Search the pubmed database
    
        Args:
            max_count -- specifies how many results will be returned
            author -- name of doctor of interest
    
        Returns:
            records -- a list of dictionaries, each dictionary contains information about an article
        """
        name=author.split(' ')
        abbr_name=''
        for item in name[:-1]:
            abbr_name+=item[0].upper()
        author='\"'+name[-1]+' '+abbr_name+'\"'
        term = author + '[author]'

        self.info('Search publications of {0}...'.format(term))

        # Get list of id's
        handle = Entrez.esearch(db='pubmed', retmax=max_count, term=term)
        result = Entrez.read(handle)
        self.info('Total number of publications containing {0}: {1}'.format(term, result['Count']))
        ids = result['IdList']

        # Fetch actual metadata of the papers
        handle = Entrez.efetch(db='pubmed', id=ids, rettype='medline', retmode='text')
        records = Medline.parse(handle)

        # Sleep for 1 second to adhere to the requested waiting time between requests
        time.sleep(1)

        # Convert the Bio record generator into a list of dictionaries
        papers = []
        for record in records:
            if 'AB' in record and 'AU' in record and 'MH' in record and 'PMID' in record:
                paper = dict({'abstract': record['AB'],
                              'author': record['AU'],
                              'mesh-terms': record['MH'],
                              'pmid': record['PMID'],
                              'searched_name': author
                              })
                papers.append(paper)

        return papers
