import pyterrier as pt
import os
import pandas as pd
from index_csv import mongo_find_many,mongo_find_explain,mongoimport
if not pt.started():
  pt.init()
import mcdm
import numpy as np



def search(query,model_path):

  if os.path.isfile('%s/data.properties' % model_path):
    indexref = pt.IndexRef.of('%s/data.properties' % model_path)

    BM25 = pt.BatchRetrieve(indexref, num_results=10000, controls={"wmodel": "BM25"}, properties={
      # 'tokeniser': 'UTFTokeniser',
       })

    search_result=BM25.search(query)

    return search_result[['docno','score']]



def process_query(pid,querys,model_path,client,dbname,coll_name):
  query_1,query_2=querys.split("|")[0],querys.split("|")[-1]

  # main criteria
  index_path=f'''{model_path}/main_criteria/'''
  main_df=search(query_1,index_path)

  #incl criteria
  index_path=f'''{model_path}/incl_criteria/'''
  incl_df=search(query_2,index_path)

  # excl criteria
  index_path = f'''{model_path}/excl_criteria/'''
  excl_df = search(query_2, index_path)


  concat_df=concat_query_scores_per_field(main_df,incl_df,excl_df)

  benefits=[True, True, False]
  weights=[.5, .4, .1]
  auto_weights=False
  keep_original_scores=True
  top_n=8

  topsis = TOPSIS_agg(benefits,weights,auto_weights,keep_original_scores,top_n,concat_df)

  df_map_result=mongo_find_many(topsis,dbname,coll_name,client)

  merged_result=pd.merge(topsis,df_map_result,on='docno')
  cleaned_merged_result=merged_result[['docno','title','summary_des','eligibility']]

  explain_df=mongo_find_explain(pid,cleaned_merged_result,dbname,client)
  explain_merged_df=pd.merge(explain_df,cleaned_merged_result,on='docno')
  cleaned_explain_merged_df=explain_merged_df[['docno','title','summary_des','eligibility','explain']]

  return cleaned_explain_merged_df


def concat_query_scores_per_field(df1, df2, df3):
  df1 = df1.rename(columns={"score": "score_top_dd"})
  df2 = df2.rename(columns={"score": "score_top_in"})
  df3 = df3.rename(columns={"score": "score_top_ex"})


  # Merging Time 0.2sec per query
  qDecision_Matrix = pd.merge(pd.merge(df1, df2, on=['docno'], how='outer'), df3,
                              on=['docno'], how='outer')


  qDecision_Matrix = qDecision_Matrix.fillna(0.00011)

  return qDecision_Matrix


def TOPSIS_agg(benefits,weights,auto_weights,keep_original_scores,top_n,res):
  alt_names = res['docno']


  ##Prepare the numpy matrix with the criteria (relevance scores)
  qDecision_Matrix = res.drop(['docno'], axis=1)
  qDecision_Matrix_TOPSIS = qDecision_Matrix.to_numpy(dtype=np.float64)

  ##Apply TOPSIS aggregation either with manual or automatic weights
  if not auto_weights:
    ranked_alt = mcdm.rank(qDecision_Matrix_TOPSIS, n_method="Vector", alt_names=alt_names, w_vector=weights, is_benefit_x=benefits, s_method="TOPSIS")
  else:
    ranked_alt = mcdm.rank(qDecision_Matrix_TOPSIS, n_method="Vector", alt_names=alt_names, w_method="MW", is_benefit_x=benefits, s_method="TOPSIS")

  ##Create a dataframe with the ranked alternatives
  ranked_alt = pd.DataFrame(ranked_alt,columns = ['docno','score'])

  ## Create a .res file (used for PyTerrier to evaluate)
  topsis_rank = pd.merge(ranked_alt, res, on=['docno'], how='outer')


  if not keep_original_scores:
    topsis_rank = topsis_rank.drop(['incl_criteria',	'excl_criteria',	'title_summ_descr'], axis=1)

  return topsis_rank.head(top_n)