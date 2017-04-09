from elasticsearch import Elasticsearch, RequestsHttpConnection
from settings import settings
import logging

elastic = Elasticsearch(
    ['{}:{}'.format(settings['elastic']['host'], settings['elastic']['port'])],
    connection_class=RequestsHttpConnection,
    http_auth=(settings['elastic']['user'], settings['elastic']['pass'])
)


def get_hospitals_by_normalized_name(normalized_name):
    search_query = {
        "query": {
            "bool": {
                "must": [
                    {
                        "query_string": {
                            "default_field": "id.keyword",
                            "query": normalized_name
                        }
                    }
                ]
            }
        }
    }
    res = elastic.search(index="hospital-index", body=search_query)
    logging.info('Elasticsearch returned {} hits'.format(res['hits']['total']))
    return res['hits']['hits']


def get_all_hospitals():
    search_query = {
        "query": {
            "match_all": {}
        }
    }

    res = elastic.search(index="hospital-index", body=search_query)
    logging.info('Elasticsearch returned {} hits'.format(res['hits']['total']))
    print res['hits']['hits']
    return res['hits']['hits']

