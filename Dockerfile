FROM python:3.6-slim

COPY requirements.txt requirements.txt

RUN apt-get update
RUN apt-get install -y apt-utils build-essential gcc

RUN bash -c 'mkdir -p /usr/share/man/man{1,2,3,4,5,6,7,8}' && \
  apt-get install -y openjdk-11-jre-headless && \
  rm -rf /usr/share/man/man


RUN pip install pip
RUN pip3 install -r requirements.txt

RUN mkdir /python/

COPY api.py /python/api.py
COPY search_api.py /python/search_api.py
COPY index_csv.py /python/index_csv.py
COPY core /python/core

ENV PYTHONPATH=/python/

WORKDIR /python/

CMD ["python3" ,"api.py"]
