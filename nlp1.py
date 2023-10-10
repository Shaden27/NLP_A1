# -*- coding: utf-8 -*-
"""NLP1

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1KHWdFLsmMKOJM1TfRgQmKCZ9IOUCIm1E

Imports and Downloads
"""

import nltk
nltk.download('punkt')
from nltk import word_tokenize
import re
import string

"""Preprocess Functions"""

def remove_punctuation(text):
    return text.translate(str.maketrans('', '', string.punctuation))

def extraspaces(text):
  return re.sub(' +', ' ', text)

def remove_special_characters(text):
    return re.sub(r"[^\w\s]", '', text)

"""Unigram Functions"""

def unigram_preprocessing(text):
  text = remove_punctuation(text)
  text = extraspaces(text)
  tokens = word_tokenize(text)
  return tokens

def unigram_count(tokens):
    unigram_counts={}
    for token in tokens:
        if token in unigram_counts:
            unigram_counts[token]+=1
        else:
            unigram_counts[token]=1
    return unigram_counts

def uni_probability(uni_count):
    unigram_probability={}
    total_words=sum(uni_count.values())
    for w in uni_count:
        unigram_probability[w]=uni_count[w]/total_words
    return unigram_probability

"""Bigram Functions"""

def n_grams(s,n,i=0):
    while(len(s[i:i+n])==n):
        yield s[i:i+n]
        i+=1

def preprocess(text):
  text = text.translate(str.maketrans('', '', string.punctuation))
  text = word_tokenize(text)
  return text

import nltk

def bigram_preprocessing(text):
    text = extraspaces(text)
    sentences = nltk.tokenize.sent_tokenize(text)  # Tokenize Sentences

    all_bigrams = []

    for sentence in sentences:
        sent_tokens = preprocess(sentence)  # Assuming preprocess function returns a list of tokens
        sent_bigrams = list(zip(sent_tokens[:-1], sent_tokens[1:]))  # Generate bigrams from tokens
        all_bigrams.extend(sent_bigrams)  # Add the bigrams of this sentence to the main list

    return all_bigrams


def bigram_count(bigrams):
    bigram_counts = {}
    for bigram in bigrams:
        if bigram in bigram_counts:
            bigram_counts[bigram] += 1
        else:
            bigram_counts[bigram] = 1
    return bigram_counts


def bi_probability(bi_count, uni_count):
    bigram_probability = {}  # Initialize a new dictionary for bigram probabilities

    for bigram, count in bi_count.items():  # bigram is a tuple (word1, word2)
        word1 = bigram[0]
        if word1 in uni_count and uni_count[word1] != 0:
            prob = count / uni_count[word1]
            bigram_probability[bigram] = prob

    return bigram_probability

"""Read File"""

#Preprocessing
file = open('train.txt', 'r')
data = file.read()
#print(data)
file.close()
words=data.split()
N=len(words)
clean_data=str(data)
clean_data=clean_data.lower()

"""Unigram Probability"""

tokens = unigram_preprocessing(clean_data)
len(tokens)
uni_count=unigram_count(tokens)
print(uni_count)

uni_probab=uni_probability(uni_count)
print(uni_probab)

"""Bigram Probability"""

bigrams = bigram_preprocessing(clean_data) # Bigram Preprocessing
print(bigrams)
bigram_counts = bigram_count(bigrams)
print(bigram_counts)
bi_probab=bi_probability(bigram_counts,uni_count)

"""Unigram Unknown Handling"""

count=0
uni_unknown_words=[]
uni_sorted_dict={}
for key, value in uni_count.items():
  if value<2:
      count+=1
      # print(key)
      uni_unknown_words.append(key)
  else:
      uni_sorted_dict[key]=value

uni_sorted_dict['<UNK>'] = 300
print(uni_sorted_dict)

"""Bigram Unknown Handling"""

count = 0
unknown_words_train = []
new_sorted_dict = {}

for bigram, value in bigram_counts.items():
    if value < 2:
        count += 1
        unknown_words_train.append(bigram)
    else:
        new_sorted_dict[bigram] = value

new_sorted_dict[('<UNK>', '')] = 500
print(new_sorted_dict)

"""Unigram Smoothing"""

def uni_laplace_smoothing(uni_counts,k):
    smooth_uni_prob={}
    V=len(uni_counts)
    for w,count in uni_counts.items():
        smooth_uni_prob[w]=(count+k)/(N+(V*k))
    return smooth_uni_prob

smooth_uni_prob=uni_laplace_smoothing(uni_sorted_dict,k=1)
print(smooth_uni_prob)

"""Bigram Smoothing"""

def bigram_laplace_smoothing(bi_count, uni_count,k):
    V=len(uni_count)
    for key in bi_count:
      word1,word2=key
      count=value
    smooth_bigram_prob = {}
    N = sum(bi_count.values())

    for (word1, word2), count in bi_count.items():
        if word1 in uni_count and uni_count[word1] != 0:
            smooth_bigram_prob[(word1,word2)] = (bi_count[(word1,word2)]+k)/(uni_count[word1]+(V*k))

    return smooth_bigram_prob
smooth_bigram_prob = bigram_laplace_smoothing(new_sorted_dict, uni_sorted_dict,k=1)
print(smooth_bigram_prob)

"""Train.txt Perplexity"""

import math
def perplexity(probabilities):
  M=len(probabilities)
  log_sum=0
  for p in probabilities.values():
    if p>0:
      log_sum=log_sum+math.log(p)
  return math.exp(-log_sum/len(unigram_preprocessing(clean_data)))

pp_uni=perplexity(smooth_uni_prob)
pp_bi=perplexity(smooth_bigram_prob)
print('Unigram Perplexity on train.txt',pp_uni)
print('Bigram Perplexity on train.txt',pp_bi)

file = open('val.txt', 'r')
val_set = file.read()
val_set=val_set.lower()
val_set=remove_punctuation(val_set)
val_set=extraspaces(val_set)
val_set=remove_special_characters(val_set)
file.close()
#print(val_set)

"""Unigram val.txt Perplexity"""

log_unigram=0
sentence_unigram=unigram_preprocessing(val_set)
unigram_val_counts=unigram_count(sentence_unigram)
for word in sentence_unigram:
  if word in smooth_uni_prob:
    log_unigram+=math.log(smooth_uni_prob[word])
  else:
     log_unigram+=math.log(smooth_uni_prob['<UNK>'])

pp_val_uni=math.exp(-log_unigram/len(sentence_unigram))
print('Unigram perplexity of val.txt =',pp_val_uni)

"""Bigram val.txt Perplexity"""

log_bigram=0
sentence_bigram=bigram_preprocessing(val_set)
bigram_val_counts=bigram_count(sentence_bigram)
#print('Bigram value counts',bigram_val_counts)
for (word1, word2) in sentence_bigram:
  if (word1, word2) in smooth_bigram_prob:
    log_bigram+=math.log(smooth_bigram_prob[(word1, word2)])
  else:
     log_bigram+=math.log(smooth_bigram_prob['<UNK>',''])
  #break
  #print(log_unigram)
pp_val_bi=math.exp(-log_bigram/len(sentence_bigram))
print('Bigram perplexity of val.txt =',pp_val_bi)

