import os
from zhon.hanzi import punctuation
import re

punctuation_str = punctuation
def construct_dataset(kind="training"):
    with open("%s_large_sentence.csv" % kind, "r") as fin:
        sentences = fin.readlines()
    with open("%s_large_labels.csv" % kind, "r") as fin:
        labels = fin.readlines()
    # print(sentences[-1])
    # print(labels[-1])
    docs = []
    for i in range(len(sentences)):
        texts = []
        istart, iend, _ = labels[i].split('|||')
        istart = int(istart)
        iend = int(iend)

        for j, w in enumerate(sentences[i].rstrip("\n").split("：")[0]):

            is_speaker = "F"
            if j in range(istart, iend):
                is_speaker = 'T'
            texts.append((w, is_speaker))
        docs.append(texts)
    return docs


docs = construct_dataset()

import nltk
from colorama import Fore
# print(nltk.data.path)
# nltk.download('averaged_perceptron_tagger')
from tqdm import tqdm

data = []


for i, doc in enumerate(tqdm(docs)):
    # Obtain the list of tokens in the document
    tokens = [t for t, label in doc]

    # Perform POS tagging
    tagged = nltk.pos_tag(tokens)

    # Take the word, POS tag, and its label
    data.append([(w, pos, label) for (w, label), (word, pos) in zip(doc, tagged)])


def word2features(doc, i):
    word = doc[i][0]
    postag = doc[i][1]

    # Common features for all words
    features = [
        'bias',
        'word.lower=' + word.lower(),
        'word[-3:]=' + word[-3:],
        'word[-2:]=' + word[-2:],
        'word.isupper=%s' % word.isupper(),
        'word.istitle=%s' % word.istitle(),
        'word.isdigit=%s' % word.isdigit(),
        'postag=' + postag
    ]

    # Features for words that are not
    # at the beginning of a document
    if i > 0:
        word1 = doc[i - 1][0]
        postag1 = doc[i - 1][1]
        features.extend([
            '-1:word.lower=' + word1.lower(),
            '-1:word.istitle=%s' % word1.istitle(),
            '-1:word.isupper=%s' % word1.isupper(),
            '-1:word.isdigit=%s' % word1.isdigit(),
            '-1:postag=' + postag1
        ])
    else:
        # Indicate that it is the 'beginning of a document'
        features.append('BOS')

    # Features for words that are not
    # at the end of a document
    if i < len(doc) - 1:
        word1 = doc[i + 1][0]
        postag1 = doc[i + 1][1]
        features.extend([
            '+1:word.lower=' + word1.lower(),
            '+1:word.istitle=%s' % word1.istitle(),
            '+1:word.isupper=%s' % word1.isupper(),
            '+1:word.isdigit=%s' % word1.isdigit(),
            '+1:postag=' + postag1
        ])
    else:
        # Indicate that it is the 'end of a document'
        features.append('EOS')

    return features


from sklearn.model_selection import train_test_split


# A function for extracting features in documents
def extract_features(doc):
    return [word2features(doc, i) for i in range(len(doc))]


# A function fo generating the list of labels for each document
def get_labels(doc):
    return [label for (token, postag, label) in doc]


X = [extract_features(doc) for doc in data]
y = [get_labels(doc) for doc in data]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
import pycrfsuite

trainer = pycrfsuite.Trainer(verbose=False)

# Submit training data to the trainer
for xseq, yseq in zip(X_train, y_train):
    trainer.append(xseq, yseq)

# Set the parameters of the model
trainer.set_params({
    # coefficient for L1 penalty
    'c1': 0.1,

    # coefficient for L2 penalty
    'c2': 0.01,

    # maximum number of iterations 200
    'max_iterations': 1000,

    # whether to include transitions that
    # are possible, but not observed
    'feature.possible_transitions': True
})

# Provide a file name as a parameter to the train function, such that
# the model will be saved to the file when training is finished
trainer.train('crf.model')
tagger = pycrfsuite.Tagger()
tagger.open('crf.model')
y_pred = [tagger.tag(xseq) for xseq in X_test]
from IPython.display import HTML as html_print, display


def cstr(s, color='black'):
    # return "<text style=color:{}>{}</text>".format(color, s)
    return "<span style=\"color: #ff0000\">{}</span>".format(s)
    # return "**{}**".format(s)


# left, word, right = 'foo' , 'abc' , 'bar'
# html_print(cstr(' '.join([left, cstr(word, color='red'), right]), color='black') )
from IPython.display import Markdown


# Let's take a look at a random sample in the testing set
def check_result(i):
    res = []
    for j, label in enumerate(y_pred[i]):
        word = X_test[i][j][1].split("=")[1]
        if label == 'T':
            res.append(cstr(word, color='red'))
        elif label == 'F':
            res.append(word)
    return len(y_pred[i]), ' '.join(res)


for i in range(100):
    length, res = check_result(i)
    # if length > 10 and length < 20:
    #     display(Markdown(res))


def construct_testing_dataset():
    from history import talks
    x_test = []
    for i, talk in enumerate(tqdm(talks)):
        ctx = talk['context']
        tokens = [t for t in ctx]

        # Perform POS tagging
        tagged = nltk.pos_tag(tokens)

        # Take the word, POS tag, and its label
        doc = tagged

        x_test.append(extract_features(doc))

    return x_test


x_test = construct_testing_dataset()
y_pred_entire = [tagger.tag(xseq) for xseq in x_test]

import numpy as np


def convert_tags_to_indices(tags):
    left_ = False
    res = []
    for t in tags:
        if t == 'T':
            res.append(1)
        else:
            res.append(0)
    res = np.array(res)
    edges = np.abs(res[1:] - res[:-1])
    a = edges.tolist()
    if len(res) > 0:
        a.insert(0, res[0])
        indices = []
        for i, t in enumerate(a):
            if t == 1:
                indices.append(i)
        pairs = []
        for i in range(len(indices) // 2):
            pairs.append([indices[2 * i], indices[2 * i + 1]])
    else:
        pairs = []
    return pairs


# convert_tags_to_indices(y_pred_entire[6])

from history import talks

with open("res_large_crf_history.txt", "w") as fout:
    for i, talk in enumerate(tqdm(talks)):
        ctx = talk['context']
        tags = y_pred_entire[i]
        indicies = convert_tags_to_indices(tags)
        fout.write(ctx)
        fout.write('  |||  ')
        try:
            for index in indicies:
                istart = index[0]
                iend = index[1]
                fout.write("%s" % ctx[istart:iend])
        except:
            print(indicies)
            pass

        fout.write('\n')
        # print(talk["context"], " ||| ", predictions["%s"%i])
