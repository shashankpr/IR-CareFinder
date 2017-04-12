from elasticsearch import Elasticsearch, RequestsHttpConnection
from settings import settings
import logging

elastic = Elasticsearch(
    ['{}:{}'.format(settings['elastic']['host'], settings['elastic']['port'])],
    connection_class=RequestsHttpConnection,
    http_auth=(settings['elastic']['user'], settings['elastic']['pass'])
)

############################
## http://opensourceconnections.com/blog/2013/01/17/escaping-solr-query-characters-in-python/
############################

# These rules all independent, order of
# escaping doesn't matter
escapeRules = {'+': r'\+',
               '-': r'\-',
               '&': r'\&',
               '|': r'\|',
               '!': r'\!',
               '(': r'\(',
               ')': r'\)',
               '{': r'\{',
               '}': r'\}',
               '[': r'\[',
               ']': r'\]',
               '^': r'\^',
               '~': r'\~',
               '*': r'\*',
               '?': r'\?',
               ':': r'\:',
               '"': r'\"',
               ';': r'\;',
               ' ': r'\ '}


def escapedSeq(term):
    """ Yield the next string based on the
        next character (either this char
        or escaped version """
    for char in term:
        if char in escapeRules.keys():
            yield escapeRules[char]
        else:
            yield char


def escapeSolrArg(term):
    """ Apply escaping to the passed in query terms
        escaping special characters like : , etc"""
    term = term.replace('\\', r'\\')  # escape \ first
    return "".join([nextStr for nextStr in escapedSeq(term)])


###############################


def get_hospitals_by_normalized_name(normalized_name):
    """Search for a hospital based on its normailzed name.

    Args:
        normalized_name -- String containing the Normalized name of the hospital to search for.
        
    Returns:
        results -- List containing the found results.
    """
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
    res = elastic.search(index="hospital-index", body=search_query, size=10000)
    logging.info('Elasticsearch returned {} hits'.format(res['hits']['total']))

    results = [hospital['_source'] for hospital in res['hits']['hits']]

    return results


def get_all_hospitals():
    """Retrieve all hospitals in Elastic Search.

    Returns:
        results -- List containing all hospitals in ElasticSearch
    """
    search_query = {
        "query": {
            "match_all": {}
        }
    }

    res = elastic.search(index="hospital-index", body=search_query, size=10000)

    logging.info('Elasticsearch returned {} hits'.format(res['hits']['total']))

    results = [hospital['_source'] for hospital in res['hits']['hits']]

    return results
