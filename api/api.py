import flask
from flask import request, jsonify
import json
from search_api import *
from pymongo import MongoClient
import atexit
import signal
from flask_cors import CORS

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
    #name='corona side effects'
    result = search(name,model_path,client)
    payload = json.loads(result.to_json(orient='records'))
    return jsonify(payload)


app.run(host="127.0.0.1", port=5000)

atexit.register(cleanup)
signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)
