from BaseTask import BaseTask
import urlparse
from settings import settings
import os.path
import shutil
import re
from warcreader import WarcFile
from gzip import GzipFile
from bs4 import BeautifulSoup
import probablepeople as pp
import logging


class ExtensiveSearchNameExtractor(BaseTask):
    def __init__(self, metadata):
        super(ExtensiveSearchNameExtractor, self).__init__(metadata)

    def execute(self):

        if self._archive_in_central_storage():
            self.info('Archive {} in central storage, create local copy.'.format(self._archive_name()))

            self._make_local_copy()

        else:
            self.info('Download website {}'.format(self._archive_name()))
            self.download_whole_website()

        if os.path.isfile(self._archive_local_path()):
            names = self.extract_names()
            self.metadata['doctors'] = list(names)

        self._remove_local_copy()

    def extract_names(self):
        name_extractor = FindNamesInWarc(self._archive_local_path())
        return name_extractor.extract_all_names()

    def download_whole_website(self):
        # use wget downloader
        # This part was done manually in parallel with development
        pass

    def _make_local_copy(self):
        if not os.path.isfile(self._archive_local_path()):  # file does not exist locally
            shutil.copy2(self._archive_storage_path(), self._archive_local_path())

    def _remove_local_copy(self):
        if os.path.isfile(self._archive_local_path()):
            self.info('Clean up local copy')
            os.remove(self._archive_local_path())

    def _archive_name(self):
        parsed_url = urlparse.urlparse(self.metadata['url'])

        return parsed_url.netloc + '.warc.gz'

    def _archive_storage_path(self):
        archive_name = self._archive_name()
        return os.path.join(settings['warc']['path'], archive_name)

    def _archive_in_central_storage(self):
        if os.path.isfile(self._archive_storage_path()):
            return True

        return False

    def _archive_local_path(self):
        return self._archive_name()


class FindNamesInWarc:
    """Find all doctor names in a warc file"""
    doctor_name_regex = re.compile(r'(\D*)M\.?D\.?(\D*)')

    def __init__(self, warc_file):
        self.warc_file_name = warc_file

    def _name_dict_to_string(self, name_dict):
        """ Convert the dictionary with name parts to a string."""
        fragments = []
        for fragment_type, fragment in name_dict.items():
            fragments.append(fragment)

        return ' '.join(fragments)

    def _valid_name(self, possible_name):
        """ Check with probable people if possible_name is a valid person name"""
        try:
            parsed_name = pp.tag(possible_name)

            if parsed_name[1] != 'Person':
                return False, ''

            name_dict = parsed_name[0]

            if not ('GivenName' in name_dict and 'Surname' in name_dict):
                return False, ''

            fragments = []
            for fragment_type, fragment in name_dict.items():
                fragments.append(fragment.capitalize())

            return True, ' '.join(fragments)

        except (pp.RepeatedLabelError, UnicodeEncodeError):
            return False, ''
            pass  # Just ignore the name on errors

    def extract_names_from_content(self, content):
        """Extract the doctor names from page content."""
        found_names = set()
        soup = BeautifulSoup(content, 'lxml')

        for string in soup.stripped_strings:
            result = re.match(self.doctor_name_regex, string)
            if result:
                name = result.group(1).strip()

                is_valid, constructed_name = self._valid_name(name)
                if is_valid:
                    found_names.add(constructed_name)

        return found_names

    def extract_all_names(self):
        """Find all doctor names on the pages in a warc.gz file."""

        results = set()
        with GzipFile(self.warc_file_name, mode='rb') as gzip_file:
            warc_file = WarcFile(gzip_file)
            for webpage in warc_file:

                if webpage.content_type.startswith('text/html'):  # only do text/html mimetype files
                    names_in_page = self.extract_names_from_content(webpage.payload)

                    results |= names_in_page
        logging.info('Found {} names.'.format(len(results)))
        return results
