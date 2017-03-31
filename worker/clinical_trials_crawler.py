from clinical_trials import Trials
import zipfile
import os
import xmltodict

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


class ClinicalTrialsCrawler:
    # Initialization of the crawler
    def __init__(self, metadata):
        self.metadata = metadata
        self.search_string = self.metadata.get('search')
        self.zip_string = 'Not run yet'
        self.downloaded = 0
        self.results = {}
        self.count = 0
        self.countConditions = 0
        self.countConditionBrowse = 0
        self.countKeywords = 0


    # Extracts the relevant data from a xml dictionary.
    def _extract_data(self,xmldict):
        extracted = {}
        extracted['nct_id'] = xmldict['clinical_study']['id_info']['nct_id']
        extracted['title'] = xmldict['clinical_study']['brief_title']

        if xmldict['clinical_study'].has_key('location'):
            extracted['location'] = xmldict['clinical_study']['location']

        if xmldict['clinical_study'].has_key('sponsor'):
            extracted['sponsor'] = xmldict['clinical_study']['sponsors']

        if xmldict['clinical_study'].has_key('condition_browse'):
            extracted['conditions_mesh'] = xmldict['clinical_study']['condition_browse']['mesh_term']
            self.countConditionBrowse += 1

        if xmldict['clinical_study'].has_key('condition'):
            extracted['conditions'] = xmldict['clinical_study']['condition']
            self.countConditions += 1

        if xmldict['clinical_study'].has_key('keyword'):
            extracted['keyword'] = xmldict['clinical_study']['keyword']
            self.countKeywords += 1

        if xmldict['clinical_study'].has_key('condition_browse') or xmldict['clinical_study'].has_key('condition') or xmldict['clinical_study'].has_key('keyword'):
            self.count += 1

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

                print('{} search results found for {}').format(len(members), self.search_string)

                for m in members:
                    zip_file.extract(m)
                    with open(m) as fd:
                        doc = xmltodict.parse(fd.read())
                        nct_id = doc['clinical_study']['id_info']['nct_id']
                        self.results[nct_id] = self._extract_data(doc)
                    os.remove(m)

        elif self.zip_string == 'Not run yet':
            try:
                raise (RuntimeError)
            except RuntimeError:
                print('Error: download_zip has not been run yet for ' + self.search_string)
                raise

        else:
            print('No search results found for ' + self.search_string)

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

    # Returns the amount of results.
    def print_count(self):
        print self.count
        print('Conditions: {}').format(self.countConditions)
        print('Condition_browse: {}').format(self.countConditionBrowse)
        print('Keywords: {}').format(self.countKeywords)
