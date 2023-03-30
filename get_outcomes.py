#!/usr/bin/env python3
# This file uses NLP tools to get the outcome variables needed to replicate the results of this paper
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import textstat
from better_profanity import profanity

"""
This function takes in a CBSA-day of Tweets, breaks the CBSA-day into individual Tweets, and gathers the outcome
variables. It collects the number of Tweets in the observation, then returns the sentiment measures, grade level,
curse percentage, and an array containing all individual scores for within that CBSA-day, along with the number
of Tweets.
"""
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
        day_curse = day_curse + curse
        day_grade = day_grade + grade_lev

        grades.append(grade_lev)
        curses.append(curse)
        scores.append(compound)

    # Take the sums of outcome variables and divide by the number of tweets to get averages
    day_compound = day_compound / num_tweets
    day_neg = day_neg / num_tweets
    day_curse = day_curse / num_tweets
    day_grade = day_grade / num_tweets
    
    return (num_tweets, day_compound, day_neg, day_curse, day_grade, grades, scores, curses)

# Helper Function: Gets VADER sentiment measures
def get_compound(sentence):
    sid = SentimentIntensityAnalyzer()
    ss = sid.polarity_scores(sentence)
    return (ss.get('compound'), ss.get('neg'), ss.get('pos'))

# Helper Function: Determines if a tweet has a curse word
def get_curse_word(sentence):
    if profanity.contains_profanity(sentence):
        return 1
    return 0

# Helper Function: Gets flesch-kincaid grade level
def get_grade_level(sentence):
    return textstat.flesch_kincaid_grade(sentence)
