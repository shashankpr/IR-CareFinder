from BaseTask import BaseTask
import subprocess
import urlparse


class WgetDownloader(BaseTask):
    def __init__(self, metadata):
        super(WgetDownloader, self).__init__(metadata)

    def execute(self):
        self._run_wget()

    def _run_wget(self):
        url = self.metadata['url']
        parsed_url = urlparse.urlparse(url)

        ignore_extensions_list = ['gif', 'jpg', 'jpeg', 'png', 'pdf', 'pptx', 'ppt', 'xls', 'xlsx']
        follow_tags_list = ['a']

        command = [
            'wget',
            '{url}'.format(url=url),
            '--mirror',
            '--warc-file={}'.format(parsed_url.netloc),
            '--follow-tags={}'.format(','.join(follow_tags_list)),
            '--wait=1',
            '--random-wait',
            '-R {}'.format(','.join(ignore_extensions_list))
        ]

        print subprocess.call(command)

        pass

    def _upload_warc(self):
        pass
