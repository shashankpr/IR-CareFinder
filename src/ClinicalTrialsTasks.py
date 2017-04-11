from BaseTask import BaseTask
from elastic import elastic
from helpers import normalize_hospital_name
import logging

logging.basicConfig(level=logging.INFO)

class StoreCTInElastic(BaseTask):
    def __init__(self, metadata):
        super(StoreCTInElastic, self).__init__(metadata)

    def execute(self):
        # Pull Hospital Record from ElasticSearch
        hosp_id = normalize_hospital_name(self.metadata['query'])
        hospital = elastic.get(index="hospital-index", doc_type='hospital', id=hosp_id)['_source']

        for ct in self.metadata['results'].itervalues():
            ct_id = ct['nct_id']

            # Search if CT already exists in ElasticSearch
            search_CT = elastic.search(index="clinicaltrials-index", body={"query": {"match_all": {}}})
            if search_CT['hits'] == 1:
                # Pull CT record from Elastic
                result = elastic.get(index="clinicaltrials-index", doc_type='hospital', id=ct_id)['_source']

                # Add Hospital to CT
                # Add CT to Hospital

                # Store Result
                elastic.update(index="clinicaltrials-index", doc_type='clinicaltrials', id=ct_id, body=result)


            # If not -> add new record
            elif search_CT['hits'] == 0:

                # Add Hospital to CT
                # Add CT to Hospital

                # Store Result
                res = elastic.index(index="clinicaltrials-index", doc_type='clinicaltrials', id=ct_id, body=ct)
                print(res['created'])

            # Else error, because things are broken.
            else:
                try:
                    raise RuntimeError
                except RuntimeError:
                    logging.error('Duplicate ClinicalTrials IDs found in index!')
                    raise

        elastic.update(index="hospital-index", doc_type='hospital', id=hosp_id, body=hospital)
