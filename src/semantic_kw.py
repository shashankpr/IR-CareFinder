from neo4jrestclient.client import GraphDatabase
from neo4jrestclient import client
from BaseTask import BaseTask
import logging
from settings import settings

logging.basicConfig(level=logging.INFO)

gdb = GraphDatabase(settings['neo4j']['url'], username=settings['neo4j']['user'], password=settings['neo4j']['pass'])


class AddRelatedKeywordsToClinicalTrials(BaseTask):
    def __init__(self, metadata):
        super(AddRelatedKeywordsToClinicalTrials, self).__init__(metadata)

    def execute(self):

        for clinicaltrial in self.metadata['clinicaltrials']:
            self.enhanceTrial(clinicaltrial)

    def enhanceTrial(self, clinicaltrial):
        """
        Gets keywords from clinicaltrials and returns related key terms from KG
        :param clinicaltrial: 
        :return: 
        """

        main_keywords = set()
        related_kws = set()
        illness_type = set()

        if 'conditions' not in clinicaltrial:
            return

        for condition in clinicaltrial['conditions']:

            graph_result = self.query_cypher(condition)
            try:
                main_keywords.add(graph_result['main_related'])

                related_kws.update(graph_result['related_kw_list'])
                illness_type.add(graph_result['illness_type'])
            except Exception as e:
                self.info(e.message)
                self.info('exception during graph')

        clinicaltrial['main_keywords'] = list(main_keywords)
        clinicaltrial['related_kws'] = list(related_kws)
        clinicaltrial['illness_type'] = list(illness_type)

    def query_cypher(self, keyword):
        """
        Querying Cypher via python API for closeness matching
        :param keyword: 
        :return: Dictionary of result nodes from Neo4j
        """
        try:
            self.info('Keyword: {}'.format(keyword))
        except UnicodeEncodeError:
            pass

        processed_kw = self.process_keyword(keyword)
        self.info(processed_kw)
        q1 = 'MATCH (i)-[:RELATED_TO]->(r)'
        q2 = 'MATCH (i)-[:KW_RELATED]->(ar)'
        q3 = 'MATCH (r)-[:KW_RELATED]->(ar)'
        q4 = 'MATCH (i)-[:TYPE_OF]->(t)'
        q5 = 'WHERE i.name=~' + processed_kw + ' or r.name=~' + processed_kw
        q6 = ' RETURN i, r, ar, t'
        q = q1 + q2 + q3 + q4 + q5 + q6

        semantic_dict = {}
        try:
            results = gdb.query(q, returns=(client.Node, client.Node, client.Node, client.Node))

            for i in results:
                semantic_dict['main_query'] = i[0]['name']
                semantic_dict['main_related'] = i[1]['name']
                semantic_dict['related_kw_list'] = i[2]['name']
                semantic_dict['illness_type'] = i[3]['name']

        except SyntaxError as e:
            self.info('Syntax error neo4')

        logging.info(semantic_dict)
        return semantic_dict

    def process_keyword(self, keyword):
        '''
        Pre-processes the keyword query to suit Cypher 
        :param keyword: 
        :return: Processed keyword
        '''
        kw = str(keyword)
        kw = kw.lower()
        kw = kw.replace('\\', ' ')
        double_q = '"'
        regex = '.*'
        processed_kw = double_q + kw + regex + double_q

        return processed_kw
