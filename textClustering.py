#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Sat May 26 23:36:43 2018

@author: chenzhong
"""

#https://s3.amazonaws.com/files.dezyre.com/images/students/source_code_files
#/1467372776_2b24d495052a8ce66358eb576b8912c8/IBM_Text_Project_Final.html
'''
import tweepy
from tweepy import OAuthHandler

consumer_key = 'NgbszsMy18esxzBRpnS6YJSg5'
consumer_secret = 'fUlGwElm7B7Q5UUl99TdnMewBA3xW9Cw5xmzBAq1xU9j5O6wUa'

access_token = '3847979172-1TNy6qbn1DvF2lHuUMpM86hAyRSxN8Uc9WpZzET'
access_secret = 'ZCooGbFqAqxCyFtZGqMPczAhD6IkZW1TfT1hocKVPm8pV'

auth = OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)

api = tweepy.API(auth)
'''

import pandas as pd
import numpy as np
import datetime
import sys
import codecs
import re
import urllib, urllib2
import itertools, collections

import nltk  # Natural Language Processing
#nltk.download('punkt')
#nltk.download('all')
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import stopwords # list of words
from collections import Counter  # optimized way to do this
import string  # list(string.punctuation) - produces a list of punctuations
import copy
from itertools import product, tee, combinations, chain
from nltk.stem import PorterStemmer
from operator import itemgetter # help with dataframes

from scipy.spatial.distance import cosine

from sklearn.cluster import KMeans
from sklearn.metrics import pairwise_distances_argmin
from sklearn.utils import shuffle

#from tweepy import Stream

encodingTot = sys.stdout.encoding or 'utf-8'

# Similarity Measure *******************************************************************************************
def cosine_sim(v1, v2):
        
    rho = round(1.0 - cosine(v1, v2), 3)
    rho = rho if(not np.isnan(rho)) else 0.0
    return rho

# Words Replacement ***************************************************************************************
def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text

# Function to find element with Maximum Frequency in TDM  *******************************************************************
def nanargmax(a):
    idx = np.argmax(a, axis=None)
    multi_idx = np.unravel_index(idx, a.shape)
    if np.isnan(a[multi_idx]):
        nan_count = np.sum(np.isnan(a))

        idx = np.argpartition(a, -nan_count-1, axis=None)[-nan_count-1]
        multi_idx = np.unravel_index(idx, a.shape)
    return multi_idx

# Define Top K Neighbours to the WORD or TWEET ***************************************************************************
def K_neighbor(k, term, list_t):
    
    # list_t - a list of tuples
    # term - value of criteria (tweet or word)
    
    neighbor = []
    neighbor = [item for item in list_t if term in item] 
    neighbor.append(item) 
    
    neighbor.sort(key = itemgetter(0), reverse=True)
      
    print 'Top ', k, ' elements for ', term   
    print '**********************************************'
        
    for i in xrange(k):
        print neighbor[i]
    
    return neighbor[:k]

# Determine Pair of Words Counter method ******************************************************************************
def Pair_words(word_list, tweet_clean_fin, n_top):

    pairs = list(itertools.combinations(word_list, 2)) # order does not matter

    #pairs = set(map(tuple, map(sorted, _pairs)))
    pairs = set(pairs)
    c = collections.Counter()

    for tweet in tweet_clean_fin:
        for pair in pairs:
            if pair[0] == pair[1]: 
                pass
            elif pair[0] in tweet and pair[1] in tweet:
                #c.update({pair: 1})
                c[pair] +=1
 
    return c.most_common(n_top)

# BIC score function ********************************************************************************

from sklearn import cluster
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler

def compute_bic(kmeans,X):
    """
    Computes the BIC metric for given clusters

    Parameters:
    -----------------------------------------
    kmeans:  List of clustering object from scikit learn

    X     :  multidimension np array of data points

    """
    # assign centers and labels
    centers = [kmeans.cluster_centers_]
    labels  = kmeans.labels_
    #number of clusters
    m = kmeans.n_clusters
    # size of the clusters
    n = np.bincount(labels)
    #size of data set
    N, d = X.shape

    #compute variance for all clusters beforehand
    cl_var =  (1.0 / (N - m) / d) * sum([sum(distance.cdist(X[np.where(labels == i)], [centers[0][i]], 'euclidean')**2) for i in range(m)])
    const_term = 0.5 * m * np.log(N) * (d+1)

    BIC = np.sum([n[i] * np.log(n[i]) -
               n[i] * np.log(N) -
             ((n[i] * d) / 2) * np.log(2*np.pi*cl_var) -
             ((n[i] - 1) * d/ 2) for i in range(m)]) - const_term

    return(BIC)
    
# Store to file text, who and time
'''
columns = ['Screen_Name', 'Time_Stamp', 'Tweet']
todays_date = datetime.datetime.now().date()

tweetDF = pd.DataFrame(columns=columns)


num_tweets = 500

for tweet in tweepy.Cursor(api.search, q="google", lang="en").items(num_tweets):
    
    lenDF = len(tweetDF)

    tweetDF.loc[lenDF] = [tweet.user.screen_name, tweet.created_at, tweet.text]
        
tweetDF.to_csv("C:/Users/Toly/Documents/Big Data/DeZyre/Data Science/IBM Project/tweetDF", sep='\t', encoding = encodingTot)
'''
#tweetDF = pd.read_csv("C:/Users/Toly/Documents/Big Data/DeZyre/Data Science/IBM Project/tweetDF", sep='\t')


directory = '/Volumes/FREESPACE/workspace/python/twitter_analysis/data/tweet-extractor-kenya/'
filelist = ['active2014_geo.csv','active2015_geo.csv','active2016_geo.csv','active2017_geo.csv']

df = pd.read_csv(open(directory + filelist[0],'rU'), encoding='utf-8', engine='c')
df = df.append(pd.read_csv(open(directory + filelist[1],'rU'), encoding='utf-8', engine='c'))
df = df.append(pd.read_csv(open(directory + filelist[2],'rU'), encoding='utf-8', engine='c'))
df = df.append(pd.read_csv(open(directory + filelist[3],'rU'), encoding='utf-8', engine='c'))

df["text"].head(5)

tweet_list_org = df["text"].tolist() # convert DF to list (tweets only) NOT a nested list

# Regex from Gagan ************************************************************

emoticons_str = r"""
    (?:
        [:=;] # Eyes
        [oO\-]? # Nose (optional)
        [D\)\]\(\]/\\OpP] # Mouth
    )"""

# Regex_str is used to GET text from CSV file

regex_str = [
    
    r'<[^>]+>', # HTML tags
    r'(?:@[\w_]+)', # @-signs
    r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)", # hash-tags
    r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+', # URLs 
    r'(?:(?:\d+,?)+(?:\.?\d+)?)', # numbers
    r"(?:[a-z][a-z'\-_]+[a-z])", # words with - and '
    r'(?:[\w_]+)' # other words
]

# These Regex are used to EXCLUDE items from the text AFTER IMPORTING from csv with regex_str

numbers = r'(?:(?:\d+,?)+(?:\.?\d+)?)'
URL = r'http[s]?://(?:[a-z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-f][0-9a-f]))+'
html_tag = r'<[^>]+>'
hash_tag = r"(?:\#+[\w_]+[\w\'_\-]*[\w_]+)"
at_sign = r'(?:@[\w_]+)'
dash_quote = r"(?:[a-z][a-z'\-_]+[a-z])"
other_word = r'(?:[\w_]+)'
other_stuff = r'(?:\S)' # anything else - NOT USED
start_pound = r"([#?])(\w+)" # Start with #
start_quest_pound = r"(?:^|\s)([#?])(\w+)" # Start with ? or with #
cont_number = r'(\w*\d\w*)' # Words containing numbers

# My REGEX **************************************************************************

#      Remove '[' and ']' brackets

sq_br_f = r'(?:[[\w_]+)' # removes '['
sq_br_b = r'(?:][\w_]+)' # removes ']'

rem_bracket = r'(' + '|'.join([sq_br_f, sq_br_b]) +')'
rem_bracketC = re.compile(rem_bracket, re.VERBOSE)

# Removes all words of 3 characters or less *****************************************************

short_words = r'\W*\b\w{1,3}\b' # Short words of 3 character or less
short_wordsC = re.compile(short_words, re.VERBOSE | re.IGNORECASE)

# REGEX remove all words with \ and / combinations

slash_back =  r'\s*(?:[\w_]*\\(?:[\w_]*\\)*[\w_]*)'
slash_fwd = r'\s*(?:[\w_]*/(?:[\w_]*/)*[\w_]*)'
slash_all = r'\s*(?:[\w_]*[/\\](?:[\w_]*[/\\])*[\w_]*)'

# REGEX numbers, short words and URL only to EXCLUDE +++++++++++++++++++++++++++++++++++++++++++++++++++

num_url_short = r'(' + '|'.join([numbers, URL, short_words + sq_br_f + sq_br_b]) +')'  # Exclude from tweets
comp_num_url_short = re.compile(num_url_short, re.VERBOSE | re.IGNORECASE)

# Master REGEX to INCLUDE from the original tweets ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

list_regex = r'(' + '|'.join(regex_str) + ')'

master_regex = re.compile(list_regex, re.VERBOSE | re.IGNORECASE) # TAKE from tweets INITIALLY


# Filters IMPORTED from csv file data

def filterPick(list, filter):
    return [ ( l, m.group(1) ) for l in list for m in (filter(l),) if m]

search_regex = re.compile(list_regex, re.VERBOSE | re.IGNORECASE).search

# Use tweetList -  that is a list from DF (using .tolist())

outlist_init = filterPick(tweet_list_org, search_regex) # It is a tuple: initial list from all tweets

char_remove = [']', '[', '(', ')', '{', '}'] # characters to be removed
words_keep = ['old', 'new', 'age', 'lot', 'bag', 'top', 'cat', 'bat', 'sap', 'jda', 'tea', 'dog', 'lie', 'law', 'lab',\
             'mob', 'map', 'car', 'fat', 'sea', 'saw', 'raw', 'rob', 'win', 'can', 'get', 'fan', 'fun', 'big',\
             'use', 'pea', 'pit','pot', 'pat', 'ear', 'eye', 'kit', 'pot', 'pen', 'bud', 'bet', 'god', 'tax', 'won', 'run',\
              'lid', 'log', 'pr', 'pd', 'cop', 'nyc', 'ny', 'la', 'toy', 'war', 'law', 'lax', 'jfk', 'fed', 'cry', 'ceo',\
              'pay', 'pet', 'fan', 'fun', 'usd', 'rio']

emotion_list = [':)', ';)', '(:', '(;', '}', '{','}']
word_garb = ['here', 'there', 'where', 'when', 'would', 'should', 'could','thats', 'youre', 'thanks', 'hasn',\
             'thank', 'https', 'since', 'wanna', 'gonna', 'aint', 'http', 'unto', 'onto', 'into', 'havent',\
             'dont', 'done', 'cant', 'werent', 'https', 'u', 'isnt', 'go', 'theyre', 'each', 'every', 'shes', 'youve', 'youll',\
            'weve', 'theyve']

# Dictionary with Replacement Pairs ******************************************************************************
repl_dict = {'googleele': 'goog', 'lyin': 'lie', 'googles': 'goog', 'aapl':'apple',\
             'msft':'microsoft', 'google': 'goog', 'googl':'goog'}

exclude = list(string.punctuation) + emotion_list + word_garb

# Convert tuple to a list, then to a string; Remove the characters; Stays as a STRING. Porter Stemmer

stemmer=PorterStemmer()
lmtzr = WordNetLemmatizer()


# Convert tuple to a list, then to a string; Remove the characters; Stays as a STRING. Porter Stemmer

# Preparing CLEAN tweets tp keep SEPARATELY from WORDS in TWEETS

tweet_clean_fin = [] # Cleaned Tweets - Final Version
for tweet in outlist_init:

    tw_clean = []
    tw_clean = [ch for ch in tweet if ch not in char_remove]

    tw_clean = re.sub(URL, "", str(tw_clean))
    tw_clean = re.sub(html_tag, "",str(tw_clean))
    tw_clean = re.sub(hash_tag, "",str(tw_clean))
    tw_clean = re.sub(slash_all,"", str(tw_clean))
    tw_clean = re.sub(cont_number, "",str(tw_clean))
    tw_clean = re.sub(numbers, "",str(tw_clean))
    tw_clean = re.sub(start_pound, "",str(tw_clean))
    tw_clean = re.sub(start_quest_pound, "",str(tw_clean))
    tw_clean = re.sub(at_sign, "",str(tw_clean))
    tw_clean = re.sub("'", "",str(tw_clean))
    tw_clean = re.sub('"', "",str(tw_clean))
    tw_clean = re.sub(r'(?:^|\s)[@#].*?(?=[,;:.!?]|\s|$)', r'', tw_clean) # Removes # and @ in words (lookahead)

    tw_clean = lmtzr.lemmatize(str(tw_clean))
    #tw_clean = stemmer.stem(str(tw_clean))
    
    tw_clean_lst = re.findall(r'\w+', str(tw_clean))
    
    tw_clean_lst = [tw.lower() for tw in tw_clean_lst if tw.lower() not in stopwords.words('english')]
    tw_clean_lst = [word for word in tw_clean_lst if word not in exclude]
    tw_clean_lst = str([word for word in tw_clean_lst if len(word)>3 or word.lower() in words_keep])
    
    tw_clean_lst = re.findall(r'\w+', str(tw_clean_lst))
    tw_clean_lst = [replace_all(word, repl_dict) for word in tw_clean_lst]
    
    tweet_clean_fin.append(list(tw_clean_lst))

# Delete various elements from the text (LIST OF WORDS)

out_list_fin = []
out_string_temp = ''.join([ch for ch in str(list(outlist_init)) if ch not in char_remove])

out_string_temp = re.sub(URL, "", out_string_temp)
out_string_temp = re.sub(html_tag, "", out_string_temp)
out_string_temp = re.sub(hash_tag, "", out_string_temp)
out_string_temp = re.sub(slash_all,"", str(out_string_temp))
out_string_temp = re.sub(cont_number, "", out_string_temp) 
out_string_temp = re.sub(numbers, "", out_string_temp)
out_string_temp = re.sub(start_pound, "", out_string_temp)
out_string_temp = re.sub(start_quest_pound, "", out_string_temp)
out_string_temp = re.sub(at_sign, "", out_string_temp)
out_string_temp = re.sub("'", "", out_string_temp)
out_string_temp = re.sub('"', "", out_string_temp)
out_string_temp = re.sub(r'(?:^|\s)[@#].*?(?=[,;:.!?]|\s|$)', r'', out_string_temp) # Removes # and @ in words (lookahead)

out_list_w = re.findall(r'\w+', out_string_temp)

out_string_short = str([word.lower() for word in out_list_w if len(word)>3 or word.lower() in words_keep])

out_list_w = re.findall(r'\w+', out_string_short)   

out_list_w = [lmtzr.lemmatize(word) for word in out_list_w]
#out_list_w = [stemmer.stem(word) for word in out_list_w]
out_list_w = [word.lower() for word in out_list_w if word.lower() not in stopwords.words('english')]  # Remove stopwords
out_list_w = str([word.lower() for word in out_list_w if word not in exclude])
out_string_rpl = replace_all(out_list_w, repl_dict) # replace all words from dictionary

# Convert "Cleaned" STRING to a LIST

out_list_fin = re.findall(r'\w+', out_string_rpl)

list_len = len(out_list_fin)
word_list = set(out_list_fin) # list of unique words from all tweets - SET
word_list_len = len(word_list)

print "Set = ", word_list_len, "Original Qty = ", list_len
print word_list
print '********************************************************************************************************'
print tweet_clean_fin
print len(tweet_clean_fin)

# Create a matrix of frequencies for word pairs

words = {v:k for (k, v) in enumerate(word_list)}
keys = words.keys() # List all UNIQUE words in the dictionary from all CLEANED tweets   
l_keys = len(keys) 

matrix_pair = np.zeros([l_keys, l_keys]) # store all combination of keys

for tweet in tweet_clean_fin:
    word_l = []
    
    for word in tweet:
        word_l.append(word)         # List of words from ONE CLEANED tweet
    
    items = set(word_l)  #set of words in from ONE CLEANED tweet
    items = [term for term in items if term in keys] # take only words from a tweet that are in keys
    index = [words[pos] for pos in items] # positions of the words

    for i1 in index: 
        for i2 in index:
            if i1< i2:
                matrix_pair[i1][i2] += 1  #frequency
                
print "Frequency Matrix *********************************************"
print matrix_pair
print "                                                              "

print 'Maximum Frequency', np.max(matrix_pair)
print "                                                             "

idx1, idx2 = nanargmax(matrix_pair)

print "Indexes for a pair with max frequency - ", idx1, idx2
print "Pair of Words with Max Frequency: Word1 - ", words.keys()[idx1], "  Word2 - ", words.keys()[idx2]
print "                                                            "

# Selecting TOP N elements from the Matrix ##########################################################################

n_top = 10

matrix_pairF = matrix_pair.flatten()
idx_f = matrix_pairF.argsort()[-n_top:]
x_idx, y_idx = np.unravel_index(idx_f, matrix_pair.shape)

for x, y, in zip(x_idx, y_idx):
    print("Frequency = ", matrix_pair[x][y], "index1 = ", x, "index2 = ", y, "Word1 - ", words.keys()[x], "  Word2 - ", words.keys()[y])
    
    
# Create document-term-matrix

columns = word_list
ncols = word_list_len + 1

term_doc = pd.DataFrame(columns = columns)
term_doc.insert(0, "Tweet", " ")
term_doc["Tweet"] = tweetDF["Tweet"]
term_doc.fillna(0, inplace=True)

i_row = 0
for line in tweet_clean_fin:
    
    for word in line:

        for col in xrange(1, ncols-1):
            if word == term_doc.columns[col]: term_doc.iloc[i_row, col] += 1

    i_row += 1

# DataFrame for Statistics with Totals by Row and by Column
    
statDF = copy.deepcopy(term_doc)
columns_cl = ["Tweet", "Sim"]
tweet_sim = pd.DataFrame(columns = columns_cl)
tweet_sim = tweetDF["Tweet"]
tweet_sim.fillna(0.0, inplace=True)

# Sum Rows by Columns
row_sum = statDF.sum(axis=1)
statDF["Total"] = row_sum
print 'Row Max Value = ', row_sum.max()
print "Max Value DF = ", statDF["Total"].max(axis=0)

# Sum Columns by Row:
col_list = list(statDF)
col_list.remove('Tweet')

rsum = {col: statDF[col].sum() for col in col_list}
# Turn the sums into a DataFrame with one row with an index of 'Total':
sum_df = pd.DataFrame(rsum, index=["Total"])
# Now append the row:
statDF = statDF.append(sum_df)

# Calculate Similarity of Unique Words
tup_word = [] # need to pull column headers and rows af words
sim_word = np.zeros((ncols, ncols))

for i in xrange(ncols-1):
    
    v1 = [0.0]*ncols
    v1 = term_doc.iloc[:, i+1]
    
    for k in xrange(ncols-1):
        
        v2 = [0.0]*ncols 
        if i >= k: pass
        else:
            v2 = term_doc.iloc[:, k+1]
            similar = cosine_sim(v1, v2)
            tup_w = (similar, list(columns)[i], list(columns)[k])

            tup_word.append(tup_w)
            sim_word[i,k] = similar
            sim_word[k,i] = similar
    
    sim_word[i,i] = 1.0

sim_word[ncols-1,ncols-1] = 1.0

print 'Similarity for Words: Words = ', word_list_len
print sim_word

# SIMILARITY for TWEETS
tu_tweet = []
sim_tweet = np.zeros((num_tweets, num_tweets))

for i in xrange(num_tweets):
    
    v1 = [0.0]*num_tweets
    v1 = term_doc.iloc[i, 1:]
    
    for k in xrange(num_tweets):
        
        v2 = [0.0]*num_tweets
        if i >= k: pass
        else:
            v2 = term_doc.iloc[k, 1:]
            similar = cosine_sim(v1, v2)
            tup_twe = (similar, term_doc['Tweet'][i], term_doc['Tweet'][k])
            tu_tweet.append(tup_twe)
            
            sim_tweet[i, k] = similar
            sim_tweet[k, i] = similar
    sim_tweet[i,i] = 1.0

print '                                                                                         '
print "Similarity for Tweets: Tweets = ", num_tweets
print sim_tweet

statDF.tail()

# Determine Top N TWEETS / WORDS

K_neighbor(n_top, tweetDF['Tweet'][498], tu_tweet)  #Top tweets for a given tweet

K_neighbor(n_top, 'accelerator', tup_word)  #Top words for a given word



def tweet_prep(df):
    
    tweet_list = df['Tweet'].tolist()
    tweet_list_clean = df['Clean_Tweet'].tolist()
    word_list_cl = [[word for word in str(line).split()] for line in tweet_list_clean]
    word_list_tot = list(chain.from_iterable(word_list_cl))
    
    set_word = set(word_list_tot) # from clean tweets
    
    return Pair_words(set_word, tweet_list_clean, n_top)

print "Top ", n_top, " pairs of words"

most_comm = Pair_words(word_list, tweet_clean_fin, n_top)

print most_comm


from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import HashingVectorizer
from sklearn.feature_extraction.text import TfidfTransformer

from sklearn.preprocessing import Normalizer
from sklearn import metrics

# K-Means Processing
n_clst = 200
cluster_doc = term_doc.drop(['Tweet'], axis=1)

kmeans = KMeans(n_clusters=n_clst, init='k-means++', random_state=0, max_iter=100, n_init=10, verbose=True)
print("Clustering sparse data with %s" % kmeans)

kmeans.fit(cluster_doc)

cluster_num = kmeans.predict(cluster_doc)
tweet_clean_list = [" ".join(tweet) for tweet in tweet_clean_fin]

labels = kmeans.labels_
cluster_centers = kmeans.cluster_centers_
labels_unique = np.unique(labels)

lenlb = len(labels_unique)
label_elem = np.zeros([lenlb])

print len(cluster_num), len(term_doc), len(tweet_clean_list), len(tweet_clean_fin)

cluster_tweet = pd.DataFrame({"Tweet": term_doc["Tweet"], "Cluster_Num": cluster_num, "Clean_Tweet": tweet_clean_list})
tweet_prep(cluster_tweet)

cluster_top_pair = cluster_tweet.groupby("Cluster_Num").apply(tweet_prep)
elem_cluster = np.bincount(labels) # Number of elements per Cluster
print "Top Cluster Pair"
print cluster_top_pair

for i in labels_unique:
    label_elem[i] = 0
    
    for l in labels:
        if l == i: label_elem[i] +=1
    print "Label = ", i, "  Number of Elements = ", label_elem[i] 

samp_size = min(num_tweets, 300) 

silh_score = metrics.silhouette_score(cluster_doc, labels, metric='euclidean', sample_size=samp_size)
print "Silhouette score = ", round(silh_score, 3), "  for Sample Size = ", samp_size

cluster_arr = cluster_doc.as_matrix()
BIC = compute_bic(kmeans,cluster_arr)
print 'BIC Score = ', round(BIC, 3)




