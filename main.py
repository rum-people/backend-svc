from fastapi import FastAPI
from src.model.keywords import KeywordExtractorYAKE
import json


app = FastAPI()
keyword_extractor = KeywordExtractorYAKE()


@app.get('/')
def get_test_connection():
    return {'text': 'Hello world!'}


@app.get('/technical/keywords')
def get_keywords_of_text(text):
    keywords = keyword_extractor.predict(texts=[text])
    return {'keywords': keywords[0]}


@app.get('/posts')
def get_post_by_keywords_soc_network(keywords: list, scoial_network: str):
    return {'error': 0}


@app.get('/analytics/keywords/{days}')
def get_analytics_keywords(days: int, social_network: str):
    return {'error': 0}


@app.get('/analytics/sentiment/{days}')
def get_analytics_sentiment(days: int, social_network: str):
    return {'error': 0}