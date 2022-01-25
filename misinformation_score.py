import re
import string
import numpy as np
from gensim.models.keyedvectors import KeyedVectors
from stop_words import get_stop_words
stop_word = get_stop_words('english')
import pickle
import pandas as pd
import sys

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def first_stringInt(s):
    try:
        int(s[0])
        return True
    except ValueError:
        return False


def clean_doc(doc):
    doc = doc.lower()
    doc = doc.translate(str.maketrans({key: " " for key in string.punctuation}))
    doc = " ".join([w for w in doc.split() if
                    w.lower() not in stop_word and len(w) > 1 and not RepresentsInt(w) and not first_stringInt(w)])
    return doc


def clean_str(string):
    string = re.sub(r"[^A-Za-z0-9(),!?\'\`]", " ", string)
    string = re.sub(r"\'s", " \'s", string)
    string = re.sub(r"\'ve", " \'ve", string)
    string = re.sub(r"n\'t", " n\'t", string)
    string = re.sub(r"\'re", " \'re", string)
    string = re.sub(r"\'d", " \'d", string)
    string = re.sub(r"\'ll", " \'ll", string)
    string = re.sub(r",", " , ", string)
    string = re.sub(r"!", " ! ", string)
    string = re.sub(r"\(", " \( ", string)
    string = re.sub(r"\)", " \) ", string)
    string = re.sub(r"\?", " \? ", string)
    string = re.sub(r"\s{2,}", " ", string)
    return string.strip().lower()

def load_data(data_nor):
    # Load data from files
    data_examples = [s.strip() for s in data_nor]

    # Split by words
    x_text = data_examples
    x_text = [clean_str(sent) for sent in x_text]
    x_text = [clean_doc(xx) for xx in x_text]
    x_text = [sent.translate(str.maketrans('', '', string.punctuation)) for sent in x_text]
    #x_text = [s.split(" ") for s in x_text]

    return x_text

def get_sent_emb(x_text,fe='bert',misinfo_path='/Users/ricky/PycharmProjects/pyt_backend/misinfo'):
    x_text_word=[i.split(" ") for i in x_text]
    if fe!='bert':
        w2v = '%s/pubmed2018_w2v_200D.bin'%misinfo_path
        # "/Users/rishabh/Downloads/GoogleNews-vectors-negative300.bin"
        model = KeyedVectors.load_word2vec_format(w2v,
                                                  binary=True)
        vec = 200
        embedding_matrix = np.zeros((len(x_text_word), vec))
        for jj, sent in enumerate(x_text_word):
            sent_vec = np.zeros((len(sent), vec))
            for ii, word in enumerate(sent):
                try:
                    embedding_vector = model.get_vector(word)
                    if embedding_vector is not None:
                        sent_vec[ii] = embedding_vector
                except:
                    pass
            embedding_matrix[jj] = np.mean(sent_vec, axis=0)
    else:
        print('BERT Modeling')
    return embedding_matrix

def process_data(ranked_df):
    d=load_data(ranked_df.text.values)
    misinfo_path='/Users/ricky/PycharmProjects/pyt_backend/misinfo'
    x_test_fe=get_sent_emb(d,fe='PUB')
    mod = pickle.load(open('%s/clef_20_21_lr_pubmedw2v.sav'%misinfo_path, 'rb'))
    pred_y = mod.predict_proba(x_test_fe)
    final_pred = np.empty((len(pred_y), 2), dtype=object)
    final_pred[:, 0] = ranked_df.docno
    final_pred[:, 1] = pred_y[:, 1]
    final_pred=pd.DataFrame(final_pred, columns=['docno', 'cred_score'])
    merged_result=pd.merge(final_pred,ranked_df,on='docno')
    return merged_result