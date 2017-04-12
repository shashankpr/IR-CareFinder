from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
import pandas as pd

gdb = GraphDatabase("http://localhost:7474", username='neo4j', password='test123')


def query_cypher(keyword):

    processed_kw = process_keyword(keyword)
    q1 = 'match (i)-[:RELATED_TO]->(r)'
    q2 = 'match (i)-[:ALSO_RELATED_TO]->(ar)'
    q3 = 'where i.name=' + processed_kw
    q4 = ' return i, r, ar'
    q = q1 + q2 + q3 + q4

    results = gdb.query(q, returns=(client.Node, client.Node, client.Node))

    for i in results:
        print i[0]['name'], i[1]['name'], i[2]['name']
    return results

def process_keyword(keyword):
    kw = str(keyword)
    double_q = '"'
    processed_kw = double_q + kw + double_q

    return processed_kw

#process_keyword('Adenoma')
query_cypher('Adenoma')