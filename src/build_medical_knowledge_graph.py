import logging
from bs4 import BeautifulSoup
import urllib2

logging.basicConfig(filename='graph.log', filemode='w', level=logging.DEBUG)

url     =   "https://medlineplus.gov/healthtopics.html"
page    =   urllib2.urlopen(url)

def url_to_html(url):

    page_html = urllib2.urlopen(url)
    return page_html

def find_health_topics(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    disease_categories = soup.find('div', attrs={'id':'section_1'})

    disease_type   = []

    for categories in disease_categories.find_all('li'):
        links           = categories.a['href']
        category_name   = categories.a.get_text()

        disease_type.append((category_name, links))

    #logging.info("Disease Category Info : {}".format(disease_type))
    print "Found Illness Categories ... "

    return disease_type


def find_specifics(url):

    page_html           =       url_to_html(url)
    soup                =       BeautifulSoup(page_html, 'html.parser')
    specifics_box       =       soup.find('div', attrs={'id':'section42'})
    specifics_list      =       []

    print "Finding Specific Topics ... "

    try:
        related_topics_on_main_page     =   specifics_box.find_all('li')

        for topics in related_topics_on_main_page:
            names_from_specific_sec = topics.a.get_text()
            #print names_from_specific_sec
            #logging.info("Specifics-Names: {}".format(names_from_specific_sec))
            specifics_list.append(names_from_specific_sec)

    except AttributeError:
        logging.debug("No 'Specifics' related topic")

    return specifics_list


def find_med_encylo(url):

    page_html   =   url_to_html(url)
    soup        =   BeautifulSoup(page_html, 'html.parser')
    encyclopedia_section    =   soup.find(id='encyclopedia-box')

    encyclopedia_list   =   []

    print "Finding Encyclopedia Topics ... "

    try:
        encyclo_list    =   encyclopedia_section.find_all('li')

        for topics in encyclo_list:
            names   =   topics.a.get_text()

            #print names
            #logging.info("Name : {}" .format(names))
            encyclopedia_list.append(names)

    except:
        logging.debug("No Encyclopedia Section")

    return encyclopedia_list


def find_related_side_topics(url):

    page_html   =   url_to_html(url)
    soup        =   BeautifulSoup(page_html, 'html.parser')

    related_side_section    =   soup.find(id='related-topics')
    #print related_side_section
    related_side_topics_list    =   []

    print "Finding Related Health Topics ... "

    try:
        related_side_topics     =   related_side_section.find_all('li')

        for topics in related_side_topics:
            names   =   topics.a.get_text()

            #logging.info("Name : {}".format(names))
            related_side_topics_list.append(names)
    except:
        logging.debug("No Related Side topics Found")

    return related_side_topics_list

def find_governing_body(url):

    page_html   =   url_to_html(url)
    soup        =   BeautifulSoup(page_html, 'html.parser')

    organization_section    =   soup.find(id='primary-institute-section')
    org_name    =   ''

    try:
        org_name    =   organization_section.a.get_text()
    except:
        logging.debug("No Health Institute Found")

    return org_name

def find_illnesses(disease_type):

    for category_names, links in disease_type:
        #logging.info("Names : {}, Links: {}" .format(category_names, links))

        page_html = url_to_html(links)
        soup = BeautifulSoup(page_html, 'html.parser')
        sub_illness_section = soup.find('div', attrs={'id':'tpgp'})

        relation_type   = "RelatedTo"
        relation_type_2 = "IsTypeOf"
        relation_type_3 = "GovernedBy"

        sub_illness_list    =   []
        related_topics      =   []

        specifics_list      =   []
        encyclo_list        =   []
        related_health_list =   []
        health_institute    =   ''


        for list in sub_illness_section.find_all('li'):
            main_illness_name       =   list.get_text()
            sub_illness_name        =   list.a.get_text()
            illness_link            =   list.a['href']

            main_illness_name       =   main_illness_name.replace(' see ' + sub_illness_name, '')

            if sub_illness_name not in sub_illness_list:
                #print illness_link
                specifics_list      =   find_specifics(illness_link)            #Topics from specifics
                encyclo_list        =   find_med_encylo(illness_link)           #Topics from Encyclopedia
                related_health_list =   find_related_side_topics(illness_link)  #Topics from Related Health

                related_topics      =   specifics_list + encyclo_list + related_health_list

                health_institute    =   find_governing_body(illness_link)

            sub_illness_list.append(sub_illness_name)
            logging.info("{}, {}, {}, {}, {}, {}, {}, {}, {}" .format(main_illness_name, relation_type,
                                                                      sub_illness_name, relation_type, related_topics,
                                                                      relation_type_2, category_names, relation_type_3,
                                                                      health_institute ))


disease_type = find_health_topics(page)
find_illnesses(disease_type)