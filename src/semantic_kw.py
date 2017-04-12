from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
from BaseTask import BaseTask
import logging

logging.basicConfig(level=logging.INFO)

gdb = GraphDatabase("http://localhost:7474", username='neo4j', password='test123')


class AddRelatedKeywordsToClinicalTrials(BaseTask):
    def __init__(self, metadata):
        super(AddRelatedKeywordsToClinicalTrials, self).__init__(metadata)

    def execute(self):

        for clinicaltrial in self.metadata['clinicaltrials']:
            self.enhanceTrial(clinicaltrial)

        print self.metadata

    def enhanceTrial(self, clinicaltrial):

        main_keywords = set()
        related_kws = set()
        illness_type = set()

        if 'conditions' not in clinicaltrial:
            return

        for condition in clinicaltrial['conditions']:

            graph_result = self.query_cypher(condition)
            if len(graph_result) > 0:
                main_keywords.add(graph_result['main_related'])

                related_kws.update(graph_result['related_kw_list'])
                illness_type.add(graph_result['illness_type'])

        clinicaltrial['main_keywords'] = main_keywords
        clinicaltrial['related_kws'] = related_kws
        clinicaltrial['illness_type'] = illness_type

    def query_cypher(self, keyword):
        self.info('Keyword: {}'.format(keyword))
        processed_kw = self.process_keyword(keyword)
        self.info(processed_kw)
        q1 = 'MATCH (i)-[:RELATED_TO]->(r)'
        q2 = 'MATCH (i)-[:KW_RELATED]->(ar)'
        q3 = 'MATCH (r)-[:KW_RELATED]->(ar)'
        q4 = 'MATCH (i)-[:TYPE_OF]->(t)'
        q5 = 'WHERE i.name=~' + processed_kw + ' or r.name=~' + processed_kw
        q6 = ' RETURN i, r, ar, t'
        q = q1 + q2 + q3 + q4 + q5 + q6

        results = gdb.query(q, returns=(client.Node, client.Node, client.Node, client.Node))
        semantic_dict = {}

        for i in results:
            semantic_dict['main_query'] = i[0]['name']
            semantic_dict['main_related'] = i[1]['name']
            semantic_dict['related_kw_list'] = eval(i[2]['name'])
            semantic_dict['illness_type'] = i[3]['name']

        logging.info(semantic_dict)
        return semantic_dict

    def process_keyword(self, keyword):
        kw = str(keyword)
        double_q = '"'
        regex = '.*'
        processed_kw = double_q + kw + regex + double_q

        return processed_kw
