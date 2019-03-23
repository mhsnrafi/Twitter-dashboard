from flask import Flask, render_template
from flask import request
#from nocache import nocache
import matplotlib.pyplot as plt


import plotly.plotly as py
import plotly.graph_objs as go

import ast,requests,boto3,os,json
from datetime import datetime
import plots,copy,random,string
import numpy as np
import io
import base64
import re
access_key_id = 'ASIA37PBWIRNEDGEMZO2'
secret_access_key = "oowQ5wSl6GmkVaDzuvxxydb8YoY+QT0v4mCGOxm7"
session_token = 'FQoGZXIvYXdzEEIaDMjat7dw9kMwK4esmSKUAbvUrzkQ6jiD5GoYqUCt1rxTnLL70+dP/EIgDIcZgOUcuzlLHRY9glf+sqJexnhFY6I6s5Vjv6AtT66gUKo4t3PkdkTGtYr/SYI6CBvnEYPOtumiuqdCgHJZLUrYjZx0AsENG9BMgodHcFk8u/cSppfhzjYwWbGKzyBuNiWvpQrpNwVrpO+O+J3ORApG0/jnIv8ibN8oxqLa4QU='

app = Flask(__name__,static_folder='/Users/muhammadahsan/Desktop/Freelance/mysite-3/static')
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0


types = {"Government" : 0, "Education" : 0, "Invalid URL" : 0, "Social Media" : 0,
  "News" : 0, "Blog" : 0, "Commercial Health" : 0, "Fake News" : 0, "Scientific" : 0,
  "Videos" : 0, "Commercial" : 0, "HealthMagazines" : 0, "HealthInsurance" : 0,
  "NMPSocieties" : 0, "None Found" : 0}

table_dict = {"vaccine" : (copy.deepcopy(types),copy.deepcopy(types),copy.deepcopy(types)),
            "abortion" : (copy.deepcopy(types),copy.deepcopy(types),copy.deepcopy(types)),
            "weed" : (copy.deepcopy(types),copy.deepcopy(types),copy.deepcopy(types)),
            "ecig" : (copy.deepcopy(types),copy.deepcopy(types),copy.deepcopy(types)),
            "aids" : (copy.deepcopy(types),copy.deepcopy(types),copy.deepcopy(types))}


region = 'us-east-2'
session = boto3.session.Session()
aws_secret = 'aXL3ndaT/BilMryekSWpQ78BYsnstGgTFfW3ObrV'
aws_pub = 'AKIAIFL3OJZQZDFSJOQQ'




db = boto3.resource('dynamodb',aws_access_key_id=aws_pub,aws_secret_access_key=aws_secret, region_name=region)
img_folder = '/Users/muhammadahsan/Desktop/Freelance/mysite-3/static/img/'


topic_table = db.Table('topics')
tweet_table = db.Table('AllTweet')
response = topic_table.scan()
for item in response['Items']:
    table_dict[item['topic'].split()[0]] = (copy.deepcopy(types),copy.deepcopy(types),copy.deepcopy(types))

# No caching at all for API endpoints.
@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

"""
Uses Twitter oEmbed api to fetch the html code for embedding the tweet.
Uses fix_twitter_html_response because the api escapes '/', even though its not necessary,which
messes up the code

@param tweet_url : url of the tweet to fetch html code for
@return html code to embed passed tweet
"""
def get_embed_html(tweet_url):
  r = requests.get('https://publish.twitter.com/oembed?url='+tweet_url)

  if(r.text[0] == '{'):
      eval = r.json()
      return (fix_twitter_html_response(eval['html']))
  else:
      return ""

def fix_twitter_html_response(html):
  new_string = ""
  for i in range(len(html)):
    if not (html[i] == "\\" and html[i:i+2] == '\\/'):
      new_string += html[i]
  return new_string

"""
Some of the JSONs have false/true/null instead of False/True/None
So this method just replaces all of false/true/null with False/True/None so ast.literal_eval can
parse it extremely easily
"""
def fix_malformed_dict_string(dict_string):
  no_null = dict_string.replace('null','None')
  no_false = no_null.replace('false','False')
  no_true = no_false.replace('true','True')
  return no_true

def get_latest_tweets(table_name,num_tweets,topic):
  table = db.Table(table_name)
  response = table.scan()
  tweets = []

  for item in response['Items']:
    if item['topic'] == topic.lower():
        tweets.append('https://twitter.com/web/status/'+ item['TweetID'])
  index_n = -1*num_tweets
  return [get_embed_html(tweet) for tweet in tweets[index_n:]]

def update_counts(table_name,dictionary):
  table = db.Table(table_name)

  response = table.scan()

  for item in response["Items"]:
    category = item['topic']
    url_type = item['type']
    dictionary[category][0][url_type] += 1 #overall count
    if item['user_type'] == 'Bot':
      dictionary[category][2][url_type] += 1
    else:
      dictionary[category][1][url_type] += 1

def update_plots(category):
  update_counts('URLsTable',table_dict)
  cat = category
  plots.type_histogram_overall(table_dict[cat][0],True, category + '_PLOT_'+ generate_random_string(10) + '.png')
  plots.type_histogram_overall(table_dict[cat][2],True, category + '_PLOT_'+ generate_random_string(10) + '_human_' +'.png')
  plots.type_histogram_overall(table_dict[cat][2],True, category + '_PLOT_'+ generate_random_string(10) + '_bot_'+ '.png')

def generate_random_string(n):
  return ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(n))

def get_plot_html(category):
  existing_files = [file for file in os.listdir(img_folder) if file.find(category + '_PLOT_') == 0]

  for file in existing_files:
    os.remove(os.path.join(img_folder,file))
  update_plots(category)

  files = os.listdir(img_folder)
  files = [file for file in files if file.find(category + '_PLOT_') == 0]
  html_blocks = []

  for file in files:
    html_blocks.append('<img src=\"' + '/static/img/' + file + '\" alt=\"' + file[:file.find('.png')] + '\">')
  return html_blocks

@app.route('/', methods=['GET','POST'])
def dash():
    print('dict in dash',request.form)
    print(request.form.get("customtopic", False))
    if(request.form.get("customtopic", False) != False):
        topic_table.put_item(
            Item={
                'topic' : request.form.get("customtopic", False),
                'date' : str(datetime.now())
                })
    return render_template('pages/dashboard.html',tweets=[])


# @app.route('/twitterDashboard', methods=['GET','POST'])
# def dash():
#     return render_template('dashboard-2.html')

@app.route('/analyze', methods=['GET','POST'])
def analyze():
    print('topic',request.form.get("predefined_topic"))
    print('type',request.form.get("type"))
    print("chosen analysis type",request.form.get("type",False))
    return render_template('analyze.html',tweets=get_latest_tweets('AllTweet',15,'aids'))

@app.route('/about', methods=['GET','POST'])
def about():
  return render_template('about.html')


@app.route('/twiiterdashboard', methods=['GET','POST'])
def twiiterdashboard():
    table = db.Table('AllTweet')
    response = table.scan()
    bot_count = 0
    human_count = 0
    pos = 0
    neg = 0
    neu = 0
    url_sup = []
    polarity = []
    account = []
    tweets = []
    date_time = []


    for item in response['Items']:
        #print(item)
        # Getting How many bot an Human Accounts
        if item['user_type'] == 'Bot':
            bot_count += 1
        else:
            human_count += 1

        url_sup.append(item['text'])
        account.append(item['username'])
        polarity.append(item['sentiment'])
        tweets.append(item['text'])
        date_time.append(item['created_at'])


    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(url_sup))
    total_tweets = len(tweets)
    total_accounts = len(account)
    total_urls = len(urls)
    true_account = round((human_count / total_tweets) * 100)
    url_support = round((total_urls / total_tweets)* 100)

    polarity_chart()
    #urlsupport_chart()
    for value in date_time:
        date_time_obj = datetime.strptime(str(value), '%Y-%m-%d %H:%M:%S')

   #print(date_time_obj.day)


    d = {
        'tweets': total_tweets,
        'account': human_count,
        'bot_account': bot_count,
        'true_account': true_account,
        'tweets_url': total_urls,
        'url_support': url_support,

        }
    return render_template('pages/graph.html', d=d)



def polarity_chart():
    table = db.Table('AllTweet')
    response = table.scan()
    pos = 0
    neg = 0
    neu = 0
    polarity = []

    for item in response['Items']:
        polarity.append(item['sentiment'])


    for item in polarity:
        if item == "Positive":
            pos += 1
        elif item == "Negative":
            neg += 1
        else:
            neu += 1
    labels = 'Positive', 'Negative', 'Neutral'
    sizes = [pos, neg, neu]
    colors = ['gold', 'lightcoral', 'yellowgreen']
    explode = (0.1, 0, 0)  # explode 1st slice

    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=140)
    plt.savefig('static/assets1/img/new_plot.png')
    return




def urlsupport_chart():
    table = db.Table('AllTweet')
    response = table.scan()
    url_sup = []
    tweets = []

    for item in response['Items']:
        url_sup.append(item['text'])
        tweets.append(item['TweetID'])


    urls = re.findall('https?://(?:[-\w.]|(?:%[\da-fA-F]{2}))+', str(url_sup))
    no_urls_count = len(tweets) - len(urls)
    url_count = len(urls)

    labels = 'URL', 'No URL'
    sizes = [url_count, no_urls_count]
    colors = ['gold', 'lightcoral']
    explode = (0.1, 0.1)  # explode 1st slice

    # Plot
    plt.pie(sizes, explode=explode, labels=labels, colors=colors,
            autopct='%1.1f%%', shadow=True, startangle=170)
    plt.savefig('static/assets1/img/url_sup.png')
    return


@app.route('/vaccines', methods=['GET','POST'])
def vaccines():
  #tweetss = get_latest_tweets('tweets_by_ID',15)
  graphs = get_plot_html("vaccine")
  return render_template('vaccines.html',charts=graphs)

@app.route('/abortion', methods=['GET','POST'])
def abortion():
    #tweetss = get_latest_tweets('abortion_tweets_by_ID',15)
    graphs = get_plot_html("abortion")
    return render_template('abortion.html',charts=graphs)
@app.route('/marijuana', methods=['GET','POST'])
def weed():
    #tweetss = get_latest_tweets('weed_tweets_by_ID',15)
    graphs = get_plot_html('weed')
    return render_template('weed.html', charts = graphs)
@app.route('/aids', methods=['GET','POST'])
def aids():
    #tweetss = get_latest_tweets('aids_tweets_by_ID',15)
    graphs = get_plot_html('aids')
    return render_template('aids.html', charts = graphs)
@app.route('/ecigs', methods=['GET','POST'])
def ecigs():
    #tweetss = get_latest_tweets('ecig_tweets_by_ID',15)
    graphs = get_plot_html('ecig')
    return render_template('ecigs.html', charts = graphs)


if __name__ == '__main__':
    app.run()