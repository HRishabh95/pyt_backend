import flask
from flask import request, jsonify
import json
from search_api import *
from pymongo import MongoClient
import atexit
import signal
from flask_cors import CORS
from index_csv import *

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

mongo_url = 'mongodb://mongo_user:mongo_secret@%s:%s' % ("localhost",27017)
client = MongoClient(mongo_url)
dbname='trec'
coll_name='trec'
model_path = '/Users/ricky/PycharmProjects/pyt_backend/pyterrier_model/BM25_baseline_cor'


@app.before_first_request
def before_first_request_func():
    print("Building Mongo")
    ids = mongoimport('%s/mapping.lst' % model_path, dbname, coll_name, client)

@atexit.register
def cleanup():
    print("Cleaning up")
    db=client[dbname]
    db.drop_collection(coll_name)

@app.route('/search', methods=['GET'])
def query_records():
    #name = request.get_json(force=True)
    name=request.args.get('query')
    mis_check=request.args.get('mis_check')
    #name='corona side effects'
    result = search(name,model_path,client,mis_check
                    )
    payload = json.loads(result.to_json(orient='records'))
    return jsonify(payload)


@app.route('/updateRel',methods=['POST'])
def updaterel():
    data = request.get_json(silent=True)
    doc_id=data.get('docid')
    relevance=data.get('rel')
    query=data.get('query')
    coll_name='annotations'
    mongoimport_one(doc_id,relevance,query,dbname,coll_name,client)
    return json.dumps(True)

@app.route('/getRel',methods=['GET'])
def get_rel():
    query=request.args.get('query')
    docid=request.args.get('docid')
    ret_files=mongofind_one(docid,query,dbname,client,coll_name='annotations')
    if ret_files:
        return json.dumps(ret_files['rel'])
    else:
        return json.dumps(True)

@app.route('/getAnno',methods=['GET'])
def get_anno():
    ret_files=mongofind_all(dbname,client,coll_name='annotations')
    ret_files=json.loads(json_util.dumps(ret_files))
    return jsonify(ret_files)



app.run(host="127.0.0.1", port=5000)

atexit.register(cleanup)
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)
