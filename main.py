from fastapi import FastAPI
from src.model.keywords import KeywordExtractorKeyBERT
from src.model.sentiment import BertSentimentAnalyser
from src.miner.post_harvesters import RedditPostsHarvester
from src.miner.scrapper import Scrapper
import psycopg2
import os
from dotenv import load_dotenv


load_dotenv()

DATABASE_HOST = os.getenv('DATABASE_HOST')
DATABASE_PORT = os.getenv('DATABASE_PORT')
DATABASE_USER = os.getenv('DATABASE_USER')
DATABASE_PASSWORD = os.getenv('DATABASE_PASSWORD')
DATABASE_NAME = os.getenv('DATABASE_NAME')

app = FastAPI()
keyword_extractor_bert = KeywordExtractorKeyBERT()
sentiment_analyser_bert = BertSentimentAnalyser()
connection = psycopg2.connect(database=DATABASE_NAME,
                        host=DATABASE_HOST,
                        user=DATABASE_USER,
                        password=DATABASE_PASSWORD,
                        port=DATABASE_PORT)

with connection.cursor() as cursor:
    cursor.execute(open('schema/init.sql', 'r').read())

scrapper = Scrapper(
    harvesters=[RedditPostsHarvester(use_script = "XYvimDksXdYhPOM2uA5tdg",
        secret = "FD0xriKOeZF155WK5X4jrqrA_4PMyQ",
        username = "Inner_Painter9381",
        password = "gSqp34igj$^a%wK")],
    keywords_extractor=keyword_extractor_bert,
    sentiment_analysator=sentiment_analyser_bert,
    connection=connection,
    quantity=1000
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