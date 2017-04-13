curl -u elastic -XPUT https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/shakespeare -d '
{
 "mappings" : {
  "_default_" : {
   "properties" : {
    "speaker" : {"type": "string", "index" : "not_analyzed" },
    "play_name" : {"type": "string", "index" : "not_analyzed" },
    "line_id" : { "type" : "integer" },
    "speech_number" : { "type" : "integer" }
   }
  }
 }
}
';



curl -elastic -XPOST 'https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/shakespeare/_bulk?pretty' --data-binary @shakespeare_new_format.json


curl -u elastic 'https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/_cat/indices?v'



curl -u elastic 'https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/shakespeare?routing=Henry'


POST -u elastic 'https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/shakespeare?routing=Henry'

POST -u elastic 'https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/shakespeare/_search?q=Henry IV'



curl -u elastic -XPOST 'https://028c28fd6e54b52887ce9357df2ea89c.eu-west-1.aws.found.io:9243/shakespeare/string/_search?q=Henry IV'