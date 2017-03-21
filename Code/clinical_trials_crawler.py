from clinical_trials import Trials
import zipfile
import os

try:
    from cStringIO import StringIO
except:
    from StringIO import StringIO


class clinical_trials_crawler:
    def __init__(self, search):
        self.search_string = search
        self.zip_string = 'Not run yet'
        self.results = -1

    def _download_zip(self):
        t = Trials()
        result_string = t.download(self.search_string)
        self.zip_string = StringIO(result_string)

    def _process_zip(self):
        if zipfile.is_zipfile(self.zip_string):
            with zipfile.ZipFile(self.zip_string, "r") as zip_file:
                members = zip_file.namelist()
                self.results = len(members)
                print('{} search results found for {}').format(len(members), self.search_string)
                for m in members:
                    zip_file.extract(m)
                    os.remove(m)

        elif self.zip_string == 'Not run yet':
            try:
                raise (RuntimeError)
            except RuntimeError:
                print('Error: download_zip has not been run yet for ' + self.search_string)
                raise

        else:
            self.results = 0;
            print('No search results found for ' + self.search_string)

    def execute_search(self):
        self._download_zip()
        self._process_zip()

    def get_amount_of_results(self):
        return self.results
