# AWS Twitter Analytics/Streaming

This repo contains the files necessary to live stream tweets mentioning vaccines/autism, store in DynamoDB table, and generates a Flask webapp

In order for the webapp to work properly, the user running website.py must have AWS credentials setup correctly.

# Credential setup guide

1) Move your .aws folder to $HOME
2) Call ``` aws configure ``` in AWS CLI 
3) Find access_key_id and secret_key in CSV, region = us-east-2, and output = json

# Guide to running the webapp

The structure of the project is as follows

stream.py should be ran on the AWS machine 
website.py should be ran on local machine

Both are python3 scripts and should be called in the format ``` python3 script.py ```

Easily install requirements for website.py via the following command

```
pip3 install -r requirements.txt
```

