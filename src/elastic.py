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
                            "default_field": "normalized-name.keyword",
                            "query": normalized_name
                        }
                    }
                ]
            }
        }
    }
    res = elastic.search(index="hospital-index", body=search_query)
    logging.info('Elasticsearch returned {} hits'.format(res['hits']['total']))

    results = [hospital['_source'] for hospital in res['hits']['hits']]

    return results


def get_all_hospitals():
    search_query = {
        "query": {
            "match_all": {}
        }
    }

    res = elastic.search(index="hospital-index", body=search_query)
    logging.info('Elasticsearch returned {} hits'.format(res['hits']['total']))

    results = [hospital['_source'] for hospital in res['hits']['hits']]

    return results

