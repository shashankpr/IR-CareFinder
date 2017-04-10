from BaseTask import BaseTask
import subprocess
import urlparse
from elastic import elastic
import datetime
from settings import settings


class WgetDownloader(BaseTask):
    def __init__(self, metadata):
        super(WgetDownloader, self).__init__(metadata)
        url = metadata['url']
        self.parsed_url = urlparse.urlparse(url)

    def execute(self):
        self._exists_online()
        self._set_as_claimed()
        self._run_wget()
        self._upload_warc('{}.warc.gz'.format(self.parsed_url.netloc))
        self._set_as_done()

    def _exists_online(self):
        query = {
            "query": {
                "bool": {
                    "must": [
                        {
                            "term": {
                                "url.netloc.keyword": self.parsed_url.netloc
                            }
                        }
                    ]
                }
            }
        }

        res = elastic.search(index="wget-sites", body=query)

        return res['hits']['total'] > 0

    def _set_as_claimed(self):
        self._set_status('claimed')

    def _run_wget(self):
        ignore_extensions_list = ['doc', 'docx', 'gif', 'jpeg', 'jpg', 'mp3', 'pdf', 'png', 'ppt', 'pptx', 'txt', 'wmv',
                                  'xls', 'xlsx']
        follow_tags_list = ['a']

        command = [
            'wget',
            '{url}'.format(url=self.parsed_url.netloc),
            '--mirror',
            '--warc-file={}'.format(self.parsed_url.netloc),
            '--follow-tags={}'.format(','.join(follow_tags_list)),
            '--wait=1',
            '--random-wait',
            '-R {}'.format(','.join(ignore_extensions_list))
        ]

        print subprocess.call(command)

    def _set_as_done(self):
        self._set_status('done')

    def _set_status(self, status):
        data = {
            "url": self.parsed_url,
            "status": status,
            "timestamp": datetime.datetime.now()
        }

        elastic.index(index="wget-sites", doc_type='site', id=self.parsed_url.netloc, body=data)
        self.info('Saved into elastic')

    def _upload_warc(self, filename):
        import webdav.client as wc

        client = wc.Client(settings['webdav'])

        client.upload_file(filename, 'warcs/{}'.format(filename))
