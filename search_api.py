import pyterrier as pt
import os
import pandas as pd
from index_csv import mongo_find_many,mongoimport
if not pt.started():
  pt.init()

model_path='./pyterrier_model/BM25_baseline_cor'



def search(search_term,model_path,client):

  if os.path.isfile('%s/data.properties' % model_path):
    indexref = pt.IndexRef.of('%s/data.properties' % model_path)

    BM25 = pt.BatchRetrieve(indexref, num_results=50, controls={"wmodel": "BM25"}, properties={
      'tokeniser': 'UTFTokeniser',
      'termpipelines': 'PorterStemmer', })

    search_result=BM25.search(search_term)

    df_map_result=mongo_find_many(search_result,'trec','trec',client)

    merged_result=pd.merge(search_result,df_map_result,on='docno')
    cleaned_merged_results=merged_result[['docno','rank','score','text']]

    return cleaned_merged_results

