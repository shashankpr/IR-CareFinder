from clinical_trials import Trials
import zipfile
import os
import xmltodict
import logging
from elastic import elastic
from BaseTask import BaseTask

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO

logging.basicConfig(level=logging.INFO)


class ClinicalTrialsCrawler(BaseTask):
    def __init__(self, metadata):
        """Initializes a ClinicalTrialsCrawler instance.
        
        Args:
            metadata -- Input dictionary, should contain the Hospital name under key 'name'.
        """
        super(ClinicalTrialsCrawler, self).__init__(metadata)

        self.metadata = metadata
        self.zip_string = 'Not run yet'
        self.downloaded = 0
        self.results = []
        self.metadata['clinicaltrials'] = []
        self.search_string = self.metadata['name']

        logging.info('Start for {}'.format(metadata['name']))

    def _change_to_list(self, value):
        """Converts extracted data to a list if it is a single value.
        
        Args:
            value -- The value that requires checking
        """
        if type(value) is not list:
            value = [value]
        return value

    def _extract_data(self, xmldict):
        """Extracts the nct_id, title, conditions and keywords from a xml dictionary.
        
        Args:
            xmldict -- A downloaded XML file in dictionary form.
        
        Returns:
            extracted -- A dictionary containing the extracted data.
        """
        extracted = {}
        ctdict = xmldict['clinical_study']

        extracted['nct_id'] = ctdict['id_info']['nct_id']
        extracted['title'] = ctdict['brief_title']

        if ctdict.has_key('condition_browse'):
            extracted['conditions_mesh'] = self._change_to_list(ctdict['condition_browse']['mesh_term'])

        if ctdict.has_key('condition'):
            extracted['conditions'] = self._change_to_list(ctdict['condition'])

        if ctdict.has_key('keyword'):
            extracted['keywords'] = self._change_to_list(ctdict['keyword'])

        return extracted

    def _download_zip(self):
        """Downloads a zipfile containing the XML files of the search results from ClinicalTrials.
        """
        t = Trials()
        result_string = t.download(self.search_string)
        self.zip_string = StringIO(result_string)

    def _process_zip(self):
        """Processes the data in the zipfile downloaded by _download_zip.
        """
        if zipfile.is_zipfile(self.zip_string):
            # Check if the downloaded file is a valid zipfile.
            with zipfile.ZipFile(self.zip_string, "r") as zip_file:
                members = zip_file.namelist()
                self.downloaded = len(members)

                logging.info(('{} search results found for {}').format(self.downloaded, self.search_string))

                # Parse every XML file in the zipfile and add it to the results-list.
                for m in members:
                    zip_file.extract(m)
                    with open(m) as fd:
                        doc = xmltodict.parse(fd.read())
                        self.results.append(self._extract_data(doc))
                    os.remove(m)

            self.metadata['clinicaltrials'] = self.results

        # If there is no downloaded file, throw exception.
        elif self.zip_string == 'Not run yet':
            try:
                raise RuntimeError
            except RuntimeError:
                logging.error('download_zip has not been run yet for ' + self.search_string)
                raise

        # If there are no search results, no processing required.
        else:
            logging.info('No search results found for ' + self.search_string)

    def execute(self):
        """Executes the downloading and processing of a search result.
        """
        self._download_zip()
        self._process_zip()

    def get_downloaded(self):
        """Returns the amount of downloaded results.
        """
        return self.downloaded

    def get_amount_of_results(self):
        """Returns the amount of processed results.
        """
        return len(self.results)


class StoreCTInElastic(BaseTask):
    def __init__(self, metadata):
        """Initializes an instance to store ClinicalTrials into ElasticSearch.

        Args:
            metadata -- Input dictionary, should contain a list with the processed ClinicalTrials under key 'clinicaltrials'.
        """
        super(StoreCTInElastic, self).__init__(metadata)

    def execute(self):
        """Stores all processed ClinicalTrials into ElasticSearch.
        """
        for ct in self.metadata['clinicaltrials']:
            index_id = self.metadata['normalized-name'] + '-' + ct['nct_id']

            elastic.index(index="clinicaltrails-index", doc_type='clinicaltrial', id=index_id, body=ct)
