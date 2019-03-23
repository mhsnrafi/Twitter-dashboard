import  boto3
import csv

db = boto3.resource('dynamodb', endpoint_url="http://localhost:8000")
dbtable = db.Table('AllTweets')

dbtable.put_item(

    Item={
        'TweetID (S)' : 123,
        'location' : 'Pakistan'
    }
)



