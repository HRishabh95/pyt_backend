import flask
from flask import request, jsonify
import json
from search_api import *
from pymongo import MongoClient
from flask_cors import CORS
from core import argsparser


app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

ARGS = argsparser.prepare_args()
mongo_url = 'mongodb://%s:%s@%s:%s' % (ARGS.mongo_user,ARGS.mongo_password,ARGS.mongo_host,ARGS.mongo_port)
client = MongoClient(mongo_url)
dbname=ARGS.db_name
coll_name=ARGS.collection_name
mapping_path = ARGS.mapping_path
mongo_build=ARGS.mongo_build
mongo_clean=ARGS.mongo_clean


# @app.before_first_request

# @atexit.register
def cleanup():
    print("Cleaning up")
    db=client[dbname]
    db.drop_collection(coll_name)

def before_first_request_func():
    print("Building Mongo")
    ids = mongoimport('%s/mapping.csv' % mapping_path, dbname, coll_name, client)


@app.route('/search', methods=['GET'])
def query_records():
    if mongo_build:
        before_first_request_func()
    request_args = request.get_json(force=True)
    pid,querys=request_args['id'],request_args['query']
    result = process_query(querys,mapping_path,client,dbname,coll_name)
    payload = json.loads(result.to_json(orient='records'))
    if mongo_clean:
        cleanup()
    return jsonify(payload)


app.run(host=ARGS.host, port=ARGS.port)
