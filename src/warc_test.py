from warcreader import WarcFile
from gzip import GzipFile
from bs4 import BeautifulSoup
import re
import probablepeople as pp


warc_filename = 'www.maimonidesmed.org.warc.gz'
old = {'doc', 'docx', 'gif', 'jpeg', 'jpg', 'mp3', 'pdf', 'png', 'ppt', 'pptx', 'txt', 'wmv', 'xls', 'xlsx'}
ext = set()


def name_dict_to_string(name_dict):
    result = ''

    fragments = []
    for fragment_type, fragment in name_dict.items():
        fragments.append(fragment)

    return ' '.join(fragments)


def valid_name(possible_name):

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

    except pp.RepeatedLabelError:
        return False, ''
        pass # Just ignore the name on errors


def extract_names(content):
    found_names = set()
    soup = BeautifulSoup(content, 'lxml')

    for string in soup.stripped_strings:
        result = re.match(doctor_name_regex, string)
        if result:
            name = result.group(1).strip()

            is_valid, constructed_name = valid_name(name)
            if is_valid:
                found_names.add(constructed_name)

    return found_names


doctor_name_regex = re.compile(r'(\D*)M\.?D\.?(\D*)')

results = set()
with GzipFile(warc_filename, mode='rb') as gzip_file:
    warc_file = WarcFile(gzip_file)
    for webpage in warc_file:

        if not webpage.content_type.startswith('text/html'):
            e = webpage.uri.split('.')[-1].lower()
            if e not in old:
                ext.add(e)

            print(webpage.content_type, webpage.uri.split('.')[-1], webpage.url)

        else:
            names_in_page = extract_names(webpage.payload)

            results |= names_in_page





                    # print name.strip()
#
# long_names = [a for a in results if len(a) > 25]
#
#
#
# for name in long_names:
#     parsed = pp.tag(name)
#     print parsed

