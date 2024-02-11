from .base_posts_harvester import BasePostsHarvester
import requests
import datetime as dt

class _NewsAPIHttpConnector:
    def __init__(self, api_key):
        self.api_key = api_key
        self.sources = "abc-news,abc-news-au,al-jazeera-english,ars-technica,associated-press,australian-financial-review,axios,bbc-news,bbc-sport,bleacher-report,bloomberg,breitbart-news,business-insider,business-insider-uk,buzzfeed,cbc-news,cbs-news,cnn,crypto-coins-news,engadget,entertainment-weekly,espn,espn-cric-info,financial-post,football-italia,fortune,four-four-two,fox-news,fox-sports,google-news,google-news-au,google-news-ca,google-news-in,google-news-uk,hacker-news,ign,independent,mashable,medical-news-today,msnbc,mtv-news,mtv-news-uk,national-geographic,national-review,nbc-news,news24,new-scientist,news-com-au,newsweek,new-york-magazine,next-big-future,nfl-news,nhl-news,politico,polygon,recode,reddit-r-all,reuters,rte,talksport,techcrunch,techradar,the-american-conservative,the-globe-and-mail,the-hill,the-hindu,the-huffington-post,the-irish-times,the-jerusalem-post,the-lad-bible,the-next-web,the-sport-bible,the-times-of-india,the-verge,the-wall-street-journal,the-washington-post,the-washington-times,time,usa-today,vice-news,wired"
        self.sortBy = "popularity"
        
    
    def get(self, url, params: dict = {}):
        params['apiKey'] = self.api_key
        params['sources'] = self.sources
        params['sortBy'] = self.sortBy
        resp = requests.get( url, params)
        return resp.json()

        

class NewsAPIPostsHarvester(BasePostsHarvester):
    def __init__(self, api_key):
        self.http = _NewsAPIHttpConnector(api_key)
        self.url = "https://newsapi.org/v2/everything"
        self.max_posts_per_request = 100
        self.date = dt.datetime.today() - dt.timedelta(days=1)
    
    def get_posts(self, days: int, quantity: int=-1) -> list:
        if quantity == -1:
            quantity = 100
        
        posts_per_day = quantity//days
        
        posts = []

        date_str = self.date.strftime('%Y-%m-%d')
        next_posts = self.get_posts_by_date(date_str, 100)
        posts.extend(next_posts)
        self.date -= dt.timedelta(days=1)
        date_str = self.date.strftime('%Y-%m-%d')
        next_posts = self.get_posts_by_date(date_str, 100)
        posts.extend(next_posts)
        self.date -= dt.timedelta(days=1)
        
        return posts

    def get_posts_by_date(self, date, quantity) -> list:
        posts = []
        page = 1
        number_of_posts = 100
        params = {'pageSize': number_of_posts, 'page': page, 'from': date, 'to': date}
        posts_data = self.http.get(self.url, params)
        quantity -= number_of_posts
        page += 1
        posts.extend(self.convert(posts_data))
        
        return posts
    
    def convert(self, json_data):
        posts = []
        if json_data.get('articles', None) is None:
            return posts
        for post in json_data['articles']:
            title = ""
            if not(post.get('title', None) is None):
                title = post['title']
            description = ""
            if not(post.get('description', None) is None):
                description = post['description']
            posts.append({
                'title': title,
                'text': title + "\n" + description,
                'created_utc': post['publishedAt'], # need to convert to utc timestamp
                'link': post['url']
            })
        
        return posts

    def get_name(self):
        return 'News'