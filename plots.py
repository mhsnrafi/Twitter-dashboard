import seaborn as sb
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import os
from wordcloud import WordCloud
from dynamodb_json import json_util as json
import re # for regular expression
import string
#import nltk
#from nltk.tokenize import RegexpTokenizer
#from collections import Counter


sb.set_color_codes("pastel")
plt.switch_backend('SVG')

#URL analysis

#def overall_url_analysis():





def type_histogram_overall(count_dict,save_to_file=False,file_name=''):

  sb.set_color_codes("pastel")
  plt.switch_backend('SVG')
  #print(count_dict)

  dictionary  = url_dict_to_df(count_dict)

  #print("dict",dictionary)
  #print("index",dictionary['amount'].value_counts().index)

  with sb.axes_style('darkgrid'):
    ax = sb.catplot(data=dictionary,x='amount',y='url_type',
        kind='bar',edgecolor=".6")
    if 'human' in file_name:
      ax.set(xlabel='Amount',ylabel='URL Type',title='URL Type Histogram for Humans')
    elif 'bot' in file_name:
      ax.set(xlabel='Amount',ylabel='URL Type',title='URL Type Histogram for Bots')
    else:
      ax.set(xlabel='Amount',ylabel='URL Type',title='Overall URL Type Histogram')
    if save_to_file:
      print('saving',file_name)
      ax.savefig(os.path.join(os.path.dirname(os.path.abspath(__file__)),'static/img/')+file_name)
    else:
      plt.show()


def url_dict_to_df(dictionary):
  new_dict = {'url_type': [], 'amount' : []}
  for item in dictionary.items():
    url_type = item[0]
    amount = item[1]
    if url_type != "None Found":
        new_dict['url_type'].append(url_type)
        new_dict['amount'].append(amount)
  return pd.DataFrame.from_dict(new_dict).sort_values("amount",ascending=False)


# Content analysis
    #sentiment
def sentiment(table,category):

    # read the data file
    data_df= pd.DataFrame(json.loads(table))

    # choose the category
    data_df=data_df[data_df["topic"]==category]

    tweets_by_sentiment = data_df['Sentiment'].value_counts()

    # visualize the results
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=10)

    ax.set_xlabel('Sentiment', fontsize=15)
    ax.set_ylabel('Number of tweets' , fontsize=15)
    ax.set_title('Distribution of sentiment', fontsize=15, fontweight='bold')
    tweets_by_sentiment.plot(ax=ax, kind='bar')

    plt.show()


    #Word cloud
def word_cloud(table,category):

    # read the data file
    data_df= pd.DataFrame(json.loads(table))

    # choose the category
    data_df=data_df[data_df["topic"]==category]

    data_df["clean text"] = data_df['text'].apply(lambda x: processPost(x))

    text = " ".join(tweet for tweet in data_df["clean text"])

    # Generate a word cloud image
    wordcloud = WordCloud(background_color="white").generate(text)

    # Display the generated image:
    # the matplotlib way:
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis("off")
    plt.show()


# preprocess the tweet
def processPost(tweet):

    #Replace @username with empty string
    tweet = re.sub('@[^\s]+', ' ', tweet)

    #Convert www.* or https?://* to " "
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))',' ',tweet)

    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)

    # remove punctuations
    translator = str.maketrans('', '', string.punctuation)
    tweet= tweet.translate(translator)

    return tweet


# User analysis
# human vs bot
def bot_vs_humans(table,category):
    # read the data file
    data_df= pd.DataFrame(json.loads(table))

    # choose the category
    data_df=data_df[data_df["topic"]==category]

    user_type = data_df['user_type'].value_counts()

    # visualize the results
    fig, ax = plt.subplots()
    ax.tick_params(axis='x', labelsize=15)
    ax.tick_params(axis='y', labelsize=10)

    ax.set_xlabel('User Type', fontsize=15)
    ax.set_ylabel('Number of users' , fontsize=15)
    ax.set_title('Distribution of User Type', fontsize=15, fontweight='bold')
    tweets_by_sentiment.plot(ax=ax, kind='bar')

    plt.show()


#top human accounts
def top_humans(table,category):
    # read the data file
    data_df= pd.DataFrame(json.loads(table))

    # choose the category
    data_df=data_df[data_df["topic"]==category]

    # choose humans
    data_df=data_df[data_df["user_type"]=="Human"]
    plt.figure(figsize=(5,5))

    users = data_df.username.value_counts()[10::-1]

    plt.title('Top 10 Tweeting Humans')
    plt.xlabel('Frequency')
    plt.ylabel('User name')
    plt.show()



#top human accounts
def top_bot(table,category):
    # read the data file
    data_df= pd.DataFrame(json.loads(table))

    # choose the category
    data_df=data_df[data_df["topic"]==category]

    # choose humans
    data_df=data_df[data_df["user_type"]=="Bot"]
    plt.figure(figsize=(5,5))

    users = data_df.username.value_counts()[10::-1]

    plt.title('Top 10 Tweeting Bots')
    plt.xlabel('Frequency')
    plt.ylabel('User name')
    plt.show()










"""
types = {"Government" : 1, "Education" : 2, "Invalid URL" : 2, "Social Media" : 3,
  "News" : 4, "Blog" : 5, "Commercial Health" : 6, "Fake News" : 7, "Scientific" : 8,
  "Videos" : 9, "Commercial" : 10, "HealthMagazines" : 11, "HealthInsurance" : 12,
  "NMPSocieties" : 13, "None Found" : 14}

type_histogram_overall(types)
"""
