# Clinical Cruise - Retrieval

Retrieval service for Cruise Clinical Trails

## Requirements:
```
1. Mongo DB 
2. Pyterrier Indexed folder with records dataset ('docno','title','summary_des','eligibility')
```


## Mongo Build:

```bash
cd ./mongo
docker-compose up -d
```

## Docker (Still in process please use without Docker): 

```bash
docker build -t <docker image name>:tag .
docker-compose up -d
```
Update the env in docker-compose.


## Volume mounts
1. <host-data-path>:/python/data


## Without Docker:

```bash
pip install -r requirements.txt
python api.py
```

## Indexed file

Download it from this [link](https://drive.google.com/drive/folders/1hBdYQ4GPy7CAUKCPF_c2IdJ99onhG9ba?usp=sharing)

## API for search

### Request
`GET http://host-name:service-port/search`

```json
{
  "id" : "Patient ID", 
  "query" : "Query for Current symptoms|Query for other relevant options",
}
```

### Response

    200

    {[docno:'', eligibility:'',summary_desc:'',exclusion:'']}


## Demo Script:

```python
import json
import requests

# post queries in the database
query='one-sided vision lost facial weakness dysarthria and numbness single plaque in the brainstem treatment of RRMS| experienced lower extremities weakness  lesion left cerebral hemisphere Relapsing Remitting Multiple Sclerosis (RRMS) C-section mother non sexually active smoker drinks alcohol'
b=requests.get('http://0.0.0.0:7778/search',data=json.dumps({'id':'1b058b5d-f879-4150-a7e0-4ae19be807f3','query':query}))
```

## Changes in Args:

For changes in the args, use ./core/argsparser.py