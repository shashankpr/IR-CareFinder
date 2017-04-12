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
        self._run_wget()
        self._upload_warc('{}.warc.gz'.format(self.parsed_url.netloc))


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


    def _upload_warc(self, filename):
        import webdav.client as wc

        client = wc.Client(settings['webdav'])

        client.upload_file(filename, 'warcs/{}'.format(filename))
