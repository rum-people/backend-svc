from fastapi import FastAPI
from src.model.keywords import KeywordExtractorKeyBERT
from src.model.sentiment import BertSentimentAnalyser
from src.miner.post_harvesters import RedditPostsHarvester
from src.miner.scrapper import Scrapper
import psycopg2


app = FastAPI()
keyword_extractor_bert = KeywordExtractorKeyBERT()
sentiment_analyser_bert = BertSentimentAnalyser()
connection = psycopg2.connect(database='rum',
                        host='postgres',
                        user='postgres',
                        password='password',
                        port='5432')

if connection.status:
    print('Connection to the database is down.')    
    exit()

with connection as cursor:
    cursor.execute(open("schema.sql", "r").read())

scrapper = Scrapper(
    harvesters=[RedditPostsHarvester()],
    keywords_extractor=keyword_extractor_bert,
    sentiment_analysator=sentiment_analyser_bert,
    connection=connection
)

scrapper.start()


@app.get('/')
def get_test_connection():
    return {'text': 'Hello world!'}


@app.get('/technical/keywords')
def get_keywords_of_text(text):
    keywords = keyword_extractor_bert.predict(texts=[text])
    return {'keywords': keywords[0]}


@app.get('/technical/sentiment')
def get_sentiment_analysis(text: str):
    analysis = sentiment_analyser_bert.predict(texts=[text])
    return {'sentiment': analysis[0]}


@app.get('/posts')
def get_posts(keyword: str | None=None, social_network: str | None=None, quantity: int | None=10):
    return [{
        'post' : 'link or text',
        'socialNetwork': 'reddit',
        'emotions' : [
            {
                'label' : 'joy',
                'value' : 0.3
            },
            {
                'label' : 'anger',
                'value' : 0.4
            },
            {
                'label' : 'fear',
                'value' : 0.9
            }
        ] 
    }]


@app.get('/analytics/keywords')
def get_analytics_keywords(days: int, social_network: str | None=None, keyword : str | None=None):
    return [
        {
            'keyword' : 'some_keyword',
            'timestamp' : 'DD/MM/YY HH:MM:SS',
            'frequency' : 10
        },
    ]

@app.get('/analytics/sentiment')
def get_analytics_sentiment(days: int, social_network: str | None=None, keyword : str | None=None):
    return [
        {
            'emotions' : [
                {
                    'label' : 'joy',
                    'value' : 0.3
                },
                {
                    'label' : 'anger',
                    'value' : 0.4
                },
                {
                    'label' : 'fear',
                    'value' : 0.9
                }
            ],
            'timestamp' : 'DD/MM/YY HH:MM:SS'
        }
    ]