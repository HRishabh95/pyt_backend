import pandas as pd
from pymongo import MongoClient
import json

def mongoimport(csv_path, db_name, coll_name, client,sep=','):
    """ Imports a csv file at path csv_name to a mongo colection
    returns: count of the documants in the new collection
    """
    db = client[db_name]
    coll = db[coll_name]
    data = pd.read_csv(csv_path,sep=sep)
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

    db = client[db_name]
    coll = db[coll_name]
    final_text_list=[]
    ids=search_result.docno.values
    results=coll.find({
        "docno": { "$in": [i for i in ids]}})

    for row in results:
        final_text_list.append([row['docno'],row['title'],row['summary_des'],row['eligibility']])


    df=pd.DataFrame(final_text_list)
    df.columns=['docno','title','summary_des','eligibility']
    return df

def mongo_find_explain(pid,search_result,dbname,client):
    db = client[dbname]
    coll = db['explain']
    final_text_list=[]
    ids=search_result.docno.values

    results=coll.find({
        "docno": { "$in": [i for i in ids]},
    "id" : {"$eq": pid}})


    results=list(results)
    if len(results)>0:
        for row in results:
            final_text_list.append([row['docno'],row['explainability']])
        df = pd.DataFrame(final_text_list)

    else:
        df=pd.DataFrame(columns=['docno','explain'])
        for ii,id in enumerate(ids):
            df.at[ii,'docno']=id
            df.at[ii,'explain']=''

    df.columns=['docno','explain']
    return df

