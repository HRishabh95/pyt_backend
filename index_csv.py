import pandas as pd
from pymongo import MongoClient
import json
from misinformation_score import *

def mongoimport(csv_path, db_name, coll_name, client):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(csv_path)
    payload = json.loads(data.to_json(orient='records'))
    x=coll.insert_many(payload)
    return x.inserted_ids

#mongoimport('./tmp.csv','tmp','tmp1')

def mongo_find(db_name, coll_name, db_url='localhost', db_port=27017):
    mongo_url = 'mongodb://mongo_user:mongo_secret@%s:%s' % (db_url, db_port)
    client = MongoClient(mongo_url)
    db = client[db_name]
    coll = db[coll_name]
    for x in coll.find():
        print(x)

#mongo_find('trec','trec')

def mongo_find_one(ids,db_name, coll_name, db_url='localhost', db_port=27017):
    mongo_url = 'mongodb://mongo_user:mongo_secret@%s:%s' % (db_url, db_port)
    client = MongoClient(mongo_url)
    db = client[db_name]
    coll = db[coll_name]
    print(coll.find_one({
        "ids": {"$eq": ids}
    })['text'])

#mongo_find_one('1','tmp','tmp1')


def mongo_find_many(search_result,db_name, coll_name, client):
    # db_name='trec'
    # coll_name='trec'
    # db_url='localhost'
    # db_port=27017

    db = client[db_name]
    coll = db[coll_name]
    final_text_list=[]
    ids=search_result.docno.values
    results=coll.find({
        "id": { "$in": [i for i in ids]}})

    for row in results:
        final_text_list.append([row['id'],row['text']])

    df=pd.DataFrame(final_text_list)
    df.columns=['docno','text']
    return df

