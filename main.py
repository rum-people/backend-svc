from fastapi import FastAPI


app = FastAPI()


@app.get('/')
def get_test_connection():
    return {'text': 'Hello world!'}


@app.get('/posts')
def get_post_by_keywords_soc_network(keywords: list, scoial_network: str):
    return {'error': 0}


@app.get('/analytics/keywords/{days}')
def get_analytics_keywords(days: int, social_network: str):
    return {'error': 0}


@app.get('/analytics/sentiment/{days}')
def get_analytics_sentiment(days: int, social_network: str):
    return {'error': 0}