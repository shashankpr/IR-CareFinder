from clinical_trials import Trials
import zipfile
import os
import xmltodict
import logging
logging.basicConfig(level=logging.INFO)

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


class ClinicalTrialsCrawler:
    # Initialization of the crawler
    def __init__(self, metadata):
        self.metadata = metadata
        self.zip_string = 'Not run yet'
        self.downloaded = 0
        self.results = {}

        if self.metadata.has_key('searchClinicalTrials'):
            self.search_string = self.metadata.get('searchClinicalTrials')
        else:
            try:
                raise RuntimeError
            except RuntimeError:
                logging.error('No property searchClinicalTrials found!')
                raise

    # Extracts the relevant data from a xml dictionary.
    def _extract_data(self, xmldict):
        extracted = {}
        extracted['nct_id'] = xmldict['clinical_study']['id_info']['nct_id']
        extracted['title'] = xmldict['clinical_study']['brief_title']

        if xmldict['clinical_study'].has_key('condition_browse'):
            extracted['conditions_mesh'] = xmldict['clinical_study']['condition_browse']['mesh_term']

        if xmldict['clinical_study'].has_key('condition'):
            extracted['conditions'] = xmldict['clinical_study']['condition']

        if xmldict['clinical_study'].has_key('keyword'):
            extracted['keyword'] = xmldict['clinical_study']['keyword']

        return extracted

    # Downloads the zip with XML files of the search results.
    def _download_zip(self):
        t = Trials()
        result_string = t.download(self.search_string)
        self.zip_string = StringIO(result_string)

    # Processes the zip with XML files of the search results.
    def _process_zip(self):
        if zipfile.is_zipfile(self.zip_string):
            with zipfile.ZipFile(self.zip_string, "r") as zip_file:
                members = zip_file.namelist()
                self.downloaded = len(members)

                logging.info(('{} search results found for {}').format(self.downloaded, self.search_string))

                for m in members:
                    zip_file.extract(m)
                    with open(m) as fd:
                        doc = xmltodict.parse(fd.read())
                        nct_id = doc['clinical_study']['id_info']['nct_id']
                        self.results[nct_id] = self._extract_data(doc)
                    os.remove(m)

        elif self.zip_string == 'Not run yet':
            try:
                raise RuntimeError
            except RuntimeError:
                logging.error('download_zip has not been run yet for ' + self.search_string)
                raise

        else:
            logging.debug('No search results found for ' + self.search_string)

    # Executes the downloading and processing of a search result.
    def execute(self):
        self._download_zip()
        self._process_zip()

    # Returns the amount of results.
    def get_amount_of_results(self):
        return len(self.results)

    # Returns the amount of results.
    def get_downloaded(self):
        return self.downloaded
