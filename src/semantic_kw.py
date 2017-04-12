from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import pandas as pd
import logging

logging.basicConfig(level=logging.INFO)

gdb = GraphDatabase("http://localhost:7474", username='neo4j', password='test123')


def query_cypher(keyword):

    processed_kw = process_keyword(keyword)
    q1 = 'MATCH (i)-[:RELATED_TO]->(r)'
    q2 = 'MATCH (i)-[:KW_RELATED]->(ar)'
    q3 = 'MATCH (r)-[:KW_RELATED]->(ar)'
    q4 = 'MATCH (i)-[:TYPE_OF]->(t)'
    q5 = 'WHERE i.name=~' + processed_kw  + ' or r.name=~' + processed_kw
    q6 = ' RETURN i, r, ar, t'
    q = q1 + q2 + q3 + q4 + q5 + q6

    results = gdb.query(q, returns=(client.Node, client.Node, client.Node, client.Node))
    semantic_dict = {}

    for i in results:
        semantic_dict['main_query']      = i[0]['name']
        semantic_dict['main_related']    = i[1]['name']
        semantic_dict['related_kw_list'] = i[2]['name']
        semantic_dict['illness_type']    = i[3]['name']

    logging.info(semantic_dict)
    return semantic_dict

def process_keyword(keyword):
    kw = str(keyword)
    double_q = '"'
    regex = '.*'
    processed_kw = double_q + kw + regex + double_q

    return processed_kw

#process_keyword('Adenoma')
query_cypher('Adenoma')