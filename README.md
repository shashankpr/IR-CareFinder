# ir-group13
Repository for Information Retrieval, Group 13.

## Project 1: CareFinder
**Owner: https://mytomorrows.com & Web Information Systems (Alessandro Bozzon)**

To date, no Web search engine allows to search for hospitals and clinics by the type of  specialist care they offer. This is information typically available on an hospital’s Website, but not structured in such a way to allow exploration. Also, there is little information about the quality of the doctors, for which some information could be available on-line. For instance, by looking in online repositories for articles published by doctors of the hospital (e.g. on https://www.ncbi.nlm.nih.gov/pubmed) , or for ongoing clinical trials (e.g. https://clinicaltrials.gov)

**Assignment:** design and implement a sensemaking system that, given a country or region of references, scouts from social data (e.g. FourSquare) hospitals, identify their public information (e.g Website), extract the list of disciplines and related doctors, and provide a measure of quality of care based on the scientific productivity such doctors, and on the presence of active clinical trials. 


## Tools used

- python-dotenv [https://github.com/theskumar/python-dotenv]
- rq [http://python-rq.org/]
- rq-dashboard [https://github.com/eoranged/rq-dashboard]

The rq package give an simple and easy task queue in python. 
Internally it uses a redis server and doesn't require a special task queue server.
The queue's can be monitored with the rq-dashboard tool.

To prevent leaking secrets with our source repository we will use so called environment variables.
By using the dotenv package we can define these variables in a .env file and exclude this from our repo.



## installation for development

Make sure you've installed python 2.7 and pip.


Install the django framework
`pip install django`

Install a database
`sudo apt-get install mariadb-server`




