from TwitterAPI import TwitterAPI
import json
import boto3


consumer_key = "jZb0ii6znczf"
consumer_secret = "OTKn5tHT76Vh9FrMNiw0321qyQ"
access_token_key = "2796351313-2Qn1o8faximnMQ"
access_token_secret = "uOKCA6Pbf5lRE95Ej4AmWkZ"

client = boto3.client('kinesis')
response = client.create_stream(StreamName='Twitter_Stream',ShardCount=1)

api = TwitterAPI(consumer_key, consumer_secret, access_token_key, access_token_secret)

kinesis = boto3.client('kinesis')

r = api.request('statuses/filter', {'follow':'629747990'})

for item in r:
  kinesis.put_record(StreamName='Twitter_Stream', Data=json.dumps(item), PartitionKey='filler')