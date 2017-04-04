"""Example of Python client calling Knowledge Graph Search API."""
import json
import urllib
import pprint
import logging

logging.basicConfig(level=logging.DEBUG)


def api_call(query_list):
    api_key = open('api_key.txt').read()
    #query = 'Mount Sinai Beth Israel'
    service_url = 'https://kgsearch.googleapis.com/v1/entities:search'
    #response    = []

    for query in query_list:
        params = {
            'query': query,
            'limit': 1,
            'indent': True,
            'key': api_key,
        }
        url = service_url + '?' + urllib.urlencode(params)
        response = json.loads(urllib.urlopen(url).read())

        #print response
        check_if_type_hospital(response)
        get_hospital_url(response)

    #return response

#pp = pprint.PrettyPrinter(indent=4)


#print pp.pprint(response)


def check_if_type_hospital(api_response):

    try:
        for element in api_response['itemListElement']:
            if 'Hospital' in element['result']['@type']:
                logging.info("{} is a Hospital" .format(element['result']['name']))
            else:
                logging.info("{} is NOT a Hospital".format(element['result']['name']))
    except:
        logging.debug("No item list from KG")

def get_hospital_url(api_response):

    try:
        for element in api_response['itemListElement']:
            logging.info("Name: {}, URL: {}".format(element['result']['name'], element['result']['url']))
    except:
        logging.debug("No URL Found from KG")




query_list = ["8A Neuroscience Critical Care - Mt. Sinai Roosevelt Hospital"
                ,"Radiation Oncology - Mt. Sinai Roosevelt Hospital"
                ,"Cafe 58 @ Roosevelt Hospital"
                ,"Ambulatory Surgery at Roosevelt Hospital"
                ,"Roosevelt Hospital Mail Room"
                ,"Parks @ St. Lukes Roosevelt Hospital"
                ,"St Luke's Roosevelt Hospital 2nd Floor-Waiting room"
                ,"Banfield Pet Hospital"
                ,"Animal Hospital and Laser Surgery Center of Secaucus"
                ,"Ambassador Veterinary Hospital"
                ,"Meadowview Psychiatric hospital"
                ,"Palisade hospital"
                ,"Holy Name Hospital"
                ,"St. Joseph's Children Hospital"
                ,"Secaucus Doll and Teddy Bear Hospital"
                ,"Meadowlands Hospital Medical Center"
                ,"Secaucus Animal Hospital"
                ,"Meadowlands Hospital Cafeteria"
                ,"Medowlands Hospital"
                ,"Arlington Dog And Cat Hospital"
                ,"Amity Animal Hospital"
                ,"West Hudson Hospital"
                ,"West hudson hospital parking garage"
                ,"West Hudson Hospital / 257"
                ,"Elmhurst Hospital Center"
                ,"Juniper Valley Animal Hospital"
              ]

#query_list1 = ["8A Neuroscience Critical Care - Mt. Sinai Roosevelt Hospital", "Radiation Oncology - Mt. Sinai Roosevelt Hospital", "Mount Sinai Beth Israel"]

api_call(query_list)
