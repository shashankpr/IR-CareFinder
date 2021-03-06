# coding=utf-8
import requests
from bs4 import BeautifulSoup
import re
import logging


# one instance for one hospital
class doc_craw:
    def __init__(self, ori_url, page_limit=5, thres=0.8):
        self.ori_url = ori_url
        self.page_limit = page_limit
        self.pattern_button1 = re.compile('\s*(?i)(find)?\s?(a)?\s?doctor\s*')
        self.pattern_button2 = re.compile('\s*(?i)(find)?\s?(a)?\s?physician(s)?\s*')
        self.pattern_MD = re.compile("(\W+)M\.?D\.?(\W*)")
        self.doc_links = {}  # doctor name: doctor url
        self.thres = thres  # judge whether it is a general search or a doctor name search
        self.base_soup = BeautifulSoup(requests.get(ori_url).text, 'lxml')
        self.button_soup = ''

    # the input url has to be the search result list
    # search for all M.D. in this website
    # and check whether there is a list containing the MDs
    # if so, count the total number of items in the list
    def check_list(self, url, page_count=0):
        logging.info('-> check_list({}, {})'.format(url, page_count))

        if page_count >= self.page_limit:
            return  # stop recursion

        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'lxml')

        # 1.add all the doctor name's link in this page to the list
        l_soup = soup.find_all(text=self.pattern_MD)
        logging.info('{} doctors found'.format(len(l_soup)))

        if len(l_soup) == 0:
            self.check_form(url)
            logging.info("check form")
            return
        for item in l_soup:
            logging.info(item)
            try:
                tmp_link = item.find_parent("a")['href']
            except:
                tmp_link = ''
            self.doc_links[item.strip()] = tmp_link

        # check whether it is a general search in the first page
        # now only works for lists.
        # for tables it won't work
        if page_count == 0:
            block = l_soup[0]
            for i in range(15):  # 9
                logging.info("-------------------------")
                block = block.parent
                tmp = str(block.find_next_sibling())

                if tmp is not None and l_soup[1] in tmp:
                    break
            logging.info(block.name + block.get('class', ''))

            next_block = block.find_next_sibling()

            next_count = 0
            while next_block is not None and next_block.get("class", '') == block.get('class', ''):
                logging.info(next_block.get('class'))
                next_count += 1
                next_block = next_block.find_next_sibling('div')

            logging.info("next->front")

            prev_block = block.find_previous_sibling('div')
            prev_count = 0
            while prev_block is not None and prev_block.get("class", '') == block.get('class', ''):
                logging.info(prev_block.get('class'))
                prev_count += 1
                prev_block = prev_block.find_previous_sibling('div')

            count = next_count + prev_count + 1
            logging.info("count", count)

            if len(l_soup) / count <= self.thres:
                # this page is generated by general search
                return

        # find the url to the next page
        ch_page = soup.find_all(text=["next", "Next", "»"])
        logging.info(len(ch_page))  # there might be multiple a tag with "next"
        if len(ch_page) == 0:
            return
        p_a_href = ''
        for item in ch_page:
            try:
                p_a_href = item.find_parent("a")['href']
            except:
                continue

            valid = re.compile("\S+" + "page")
            if valid.match(p_a_href):
                logging.info(p_a_href)
                p_a_href = self.complete_url(p_a_href)
        if p_a_href == '':
            return
        self.check_list(p_a_href, page_count + 1)

    def complete_url(self, url):
        logging.info('-> complete_url({})'.format(url))
        if "http" not in url:
            # incomplete url, need to be changed
            base_url = self.ori_url[:-1] if self.ori_url[-1] == '/' else self.ori_url
            return str(base_url) + str(url)
        else:
            return url

    # main page -> doctors page, through button
    def check_button(self):
        logging.info('-> check_button()')
        # double check
        a_result = self.base_soup.find_all(text=self.pattern_button1)  # call doctor
        a_result2 = self.base_soup.find_all(text=self.pattern_button2)  # call physician

        if len(a_result) > 0:
            a_result.extend(a_result2)
        else:
            a_result = a_result2

        logging.info('Results: {}'.format(len(a_result)))
        for item in a_result:
            logging.info('Loop iteration')
            try:
                # get the url and go to the doctors page
                doc_ref = item.find_parent("a")['href']
                self.button_soup=BeautifulSoup(requests.get(self.complete_url(doc_ref)).text,'lxml')
                self.check_list(self.complete_url(doc_ref))
                return  # currently only check the first button
            except:
                continue

        # if there is no such button on the main page, look for a search box
        self.check_form(self.ori_url)

    # look for search box, and check for its search results.
    def check_form(self, url, search_term=''):
        logging.info('-> check_form({}, {})'.format(url, search_term))
        r = requests.get(url)
        soup = BeautifulSoup(r.text, "lxml")
        forms = soup.find_all("input")
        for item in forms:
            tmp_pre = item.find_parent("form").get("action", '')
            tmp_mea = item.get('name', '')
            if tmp_mea == ['s', 'q', 'search']:
                try:
                    self.check_list(self.complete_url(tmp_pre) + "?" + tmp_mea + "=" + search_term)
                    return  # currently only check the first successful search
                except:
                    continue
            else:
                continue
        self.check_alpha()

    # look for doctors indexed by alphabet
    def check_alpha(self):
        logging.info("alpha")
        alpha_dict = {}
        alpha_list = [chr(i) for i in range(97, 123)]
        for ch in alpha_list:
            logging.info(ch)
            tmp = self.button_soup.find('a', text=re.compile('^(?i)' + 'a' + '$'))
            if tmp is not None:
                alpha_dict[ch] = tmp.get('href', '')

        for item in alpha_dict.values():
            self.check_list(self.complete_url(item))


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    c = doc_craw('http://www.tbh.org/')
    c.check_button()
    logging.info('Final results: {}'.format(len(c.doc_links)))
