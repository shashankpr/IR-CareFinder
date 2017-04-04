from pony.orm import *
from Models import db

class ClinicalTrial(db.Entity):
    id = PrimaryKey(str)
    clinical_trials = Set('Hospital')
    title = Required(LongStr)
    condition = Required(LongStr)
    condition_browse = Optional(LongStr)
    keyword = Optional(LongStr)


