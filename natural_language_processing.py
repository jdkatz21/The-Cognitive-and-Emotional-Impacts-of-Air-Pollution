#!/usr/bin/env python3
# This file uses NLP tools to get the outcome variables needed for running regressions
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import textstat
import time
from ast import literal_eval
from better_profanity import profanity
import os
import multiprocessing as mp
from pandarallel import pandarallel
from operator import add
import tweetnlp
import dask.dataframe as dd
from dask.diagnostics import ProgressBar



def get_tweet_summary_statistics(tweets):

    # split into individual tweets
    broken_up_tweets = tweets.splitlines()

    num_tweets = len(broken_up_tweets)

    day_compound, day_neg, day_pos, day_curse, day_grade = 0, 0, 0, 0, 0

    grades, scores, curses = [], [], []

    # for every tweet, get the sentiment score, grade level, curse rate. Append to lists and sums
    
    for tweet in broken_up_tweets:
        compound, neg, pos = get_compound(tweet)
        curse = get_curse_word(tweet)
        grade_lev = get_grade_level(tweet)

        day_compound = day_compound + compound
        day_neg = day_neg + neg
        day_pos = day_pos + pos
        day_curse = day_curse + curse
        day_grade = day_grade + grade_lev

        grades.append(grade_lev)
        curses.append(curse)
        scores.append(compound)

    # Take the sums of outcome variables and divide by the number of tweets to get averages
    day_compound = day_compound / num_tweets
    day_neg = day_neg / num_tweets
    day_pos = day_pos / num_tweets
    day_curse = day_curse / num_tweets
    day_grade = day_grade / num_tweets
    
    return (num_tweets, day_compound, day_neg, day_pos, day_curse, day_grade, grades, scores, curses)

def get_tweet_topic(tweets, model, sent_model):
    # split into individual tweets
   
    broken_up_tweets = tweets.splitlines()

    classes = [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
    sentiments = [0,0,0]

    # for every tweet, get the sentiment score, grade level, curse rate. Append to lists and sums
    
    for tweet in broken_up_tweets:    
        topics = model.predict(tweet, return_probability=True)['probability']
        scores = list(topics.values())
        classes = list(map(add, classes, scores))

        sent = sent_model.predict(tweet, return_probability=True)['probability']
        sents = list(sent.values())
        sentiments = list(map(add, sentiments, sents))

    net_sum = sum(classes)
    classes[:] = [x / net_sum for x in classes] 
    net_sent = sum(sentiments)
    sentiments[:] = [x / net_sent for x in classes] 

    print(classes, sentiments)
    return (classes, sentiments)

# Gets VADER sentiment measures
def get_compound(sentence):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(sentence)
    return (ss.get('compound'), ss.get('neg'), ss.get('pos'))

# Determines if a tweet has a curse word
def get_curse_word(sentence):
    if profanity.contains_profanity(sentence):
        return 1
    return 0

# Gets flesch-kincaid grade level
def get_grade_level(sentence):
    return textstat.flesch_kincaid_grade(sentence)

# loads data
if __name__ == '__main__':

    ProgressBar().register()


    location_day_data = pd.read_csv('./dataset.csv', names=['index', 'date', 'coordinates', 'tweets', 'avg_pm25', 'avg_aqi'])
    location_day_data = location_day_data.dropna()
    print(location_day_data)
    location_day_data.reset_index()

    # PT
    model = tweetnlp.load_model('topic_classification')
    sent_model = tweetnlp.load_model('sentiment')

    location_day_data = dd.from_pandas(location_day_data, npartitions=32)
    location_day_data['results'] = location_day_data['tweets'].apply(get_tweet_topic, model=model, sent_model=sent_model)

    location_day_data.to_csv('./topics.csv')
