from threading import Thread
from .post_harvesters import BasePostsHarvester
from ..model.base import Model
import time


class Scrapper(Thread):
    '''
        This Scrapper initiates itself every day and loads new data from the harvesters.
    '''
    def __init__(self, harvesters: list[BasePostsHarvester],
                 keywords_extractor: Model,
                 sentiment_analysator: Model,
                 delay: int = 60 * 60 * 24,
                 days: int = 30,
                 quantity: int=3000,
                 connection=None):
        super().__init__()
        self.harvesters = harvesters
        self.keyword_extractor = keywords_extractor
        self.sentiment_analysator = sentiment_analysator
        self.delay = delay
        self._stop = False
        self.days = days
        self.quantity = quantity
        self.connection = connection

    def stop(self):
        self._stop = True

    def _generate_insert_into_posts(self, harvester: BasePostsHarvester, emotional_traits: list[str], posts: list[dict]) -> str:
        values = [
            str((harvester.get_name(), post['text'], post['created_utc'], emotional_traits[index], post['link'])) 
            for index, post in enumerate(posts)
        ]
        return ', '.join(values)
    
    def _extract_emotional_trait(self, raw_traits: list[dict]) -> str:
        max_score = 0
        index_max = 0
        for index, trait in enumerate(raw_traits):
            if trait['score'] >= 0.50:
                return trait['label']
            elif trait['score'] > max_score:
                max_score = trait['score']
                index_max = index
        return index_max

    def run(self):
        print('Thread on harvesting data has started!')
        while not self._stop:
            cursor = self.connection.cursor()
            
            for harvester in self.harvesters:
                posts = harvester.get_posts(days=self.days, quantity=self.quantity)
                texts = list(map(lambda post: post['text'], posts))

                emotional_traits_raw = self.sentiment_analysator.predict(texts=texts)
                emotional_traits = [self._extract_emotional_trait(raw_traits) for raw_traits in emotional_traits_raw]

                cursor.execute('''
                    INSERT INTO posts (provider_name, text, timestamp, emotional_trait, link)
                    VALUES %s RETURNING id;''', self._generate_insert_into_posts(harvester, emotional_traits, posts))
                
                text_ids = cursor.fetchall()
                l_keywords = self.keyword_extractor.predict(texts=texts)
                for index, keywords in enumerate(l_keywords):
                    for keyword in keywords:
                        cursor.execute(
                            '''
                            INSERT INTO post_keywords (post_id, keyword)
                            VALUES (%d, %s);
                            ''', (text_ids[index], keyword)
                        )

                self.connection.commit()

            time.sleep(self.delay)