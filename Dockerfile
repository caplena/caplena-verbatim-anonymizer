FROM python:3.8

COPY requirements.txt /tmp/requirements.txt
RUN pip install -r requirements.txt
RUN python -m spacy download de_core_news_lg

COPY . src/
WORKDIR src/