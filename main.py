from fastapi import FastAPI
from src.model.keywords import KeywordExtractorKeyBERT
from src.model.sentiment import BertSentimentAnalyser
from src.miner.post_harvesters import RedditPostsHarvester, NewsAPIPostsHarvester
from src.miner.scrapper import Scrapper
import psycopg2
import os
from datetime import datetime, timedelta
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
        password = "gSqp34igj$^a%wK"),
        NewsAPIPostsHarvester(
            api_key='17712fe5c46f444ca38f3979cb0b5d3f'
        )],
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
    if social_network is not None:
        providers = ' OR '.join(['p.provider_name = %s' % name for name in social_network.split(',')]) + ' AND '
    else:
        providers = ''

    with connection.cursor() as cursor:
        cursor.execute('''
            SELECT * FROM posts p 
            JOIN post_keywords pk ON p.id = pk.post_id
            WHERE 
                %s
                pk.keyword = %s
            LIMIT %s;
        ''', (providers, keyword, quantity))

        data = cursor.fetchall()

    return [{
        'text' : row[2],
        'link' : row[5],
        'socialNetwork': row[1],
        'emotion' : row[4], 
    } for row in data]


@app.get('/analytics/keywords/top')
def get_top_keywords(days: int, social_network: str | None=None):
    with connection.cursor() as cursor:
        if social_network is not None:
            providers = ' OR '.join(['provider_name = %s' % name for name in social_network.split(',')]) + ' AND '
        else:
            providers = ''

        cursor.execute('''
                                SELECT
                                    keyword,
                                    COUNT(*) AS keyword_count
                                FROM
                                    post_keywords
                                JOIN
                                    posts ON post_keywords.post_id = posts.id
                                WHERE
                                    %s
                                    created_at >= NOW() - INTERVAL '%s' DAY 
                                GROUP BY
                                    keyword
                                ORDER BY
                                    keyword_count DESC
                                LIMIT
                                    10;
                            ''', (providers, days,))
            
        data = cursor.fetchall()

    return [{'keyword': row[0], 'frequency': row[1]} for row in data]


@app.get('/analytics/keywords')
def get_analytics_keywords(days: int, keyword : str, social_network: str | None=None):
    result = []
    with connection.cursor() as cursor:
        if social_network is not None:
            providers = ' OR '.join(['p.provider_name = %s' % name for name in social_network.split(',')]) + ' AND '
        else:
            providers = ''
        current_date = datetime.now()
        delta = timedelta(days=1)

        for _ in range(days):
            
            text_date = datetime.strftime(current_date, '%Y-%m-%d')

            cursor.execute(
                    '''
                        SELECT
                            p.provider_name,
                            pk.keyword,
                            COUNT(*) AS keyword_count
                        FROM
                            post_keywords pk
                        JOIN
                            posts p ON pk.post_id = p.id
                        WHERE
                            %s
                            DATE(p.created_at) = %s
                            AND pk.keyword = %s
                        GROUP BY
                            pk.keyword;
                    ''', (providers, text_date, keyword)
            )
            data = cursor.fetchall()

            temp = [{
                    'socialNetwork': row[0],
                    'keyword': row[1],
                    'frequency': row[2],
                    'timestamp': datetime.strftime(current_date, '%Y/%m/%d %H:%M:%S')
            } for row in data]
            result.extend(temp)

            current_date -= delta

    return result


@app.get('/analytics/sentiment')
def get_analytics_sentiment(days: int, social_network: str | None=None, keyword : str | None=None):
    data = []

    with connection.cursor() as cursor:
        delta = timedelta(days=1)
        current_date = datetime.now()

        for _ in range(days):
            text_date = datetime.strftime(current_date, '%Y-%m-%d')

            if keyword is None:
                if social_network is not None:
                    providers = ' OR '.join(['provider_name = %s' % name for name in social_network.split(',')]) + ' AND '
                else:
                    providers = ''

                cursor.execute('''
                                SELECT
                                    emotional_trait,
                                    COUNT(*) AS trait_count
                                FROM
                                    posts
                                WHERE
                                    %s
                                    DATE(created_at) = %s
                                GROUP BY
                                    emotional_trait;
                            ''', (providers, text_date))
            else:
                if social_network is not None:
                    providers = ' OR '.join(['p.provider_name = %s' % name for name in social_network.split(',')]) + ' AND '
                else:
                    providers = ''

                cursor.execute('''
                    SELECT
                        p.emotional_trait,
                        COUNT(*) AS trait_count
                    FROM
                        posts p
                    JOIN
                        post_keywords pk ON p.id = pk.post_id
                    WHERE
                        %s
                        DATE(p.created_at) = %s
                        AND pk.keyword = %s
                    GROUP BY
                        p.emotional_trait;
                ''', (providers, text_date, keyword))
            rows = cursor.fetchall()

            data.append({
                'timestamp' : datetime.strftime(current_date, '%Y/%m/%d %H:%M:%S'),
                'emotions' : [
                    {
                        'label' : row[0],
                        'frequency' : row[1]
                    } for row in rows
                ]
            })

            current_date -= delta

    return data