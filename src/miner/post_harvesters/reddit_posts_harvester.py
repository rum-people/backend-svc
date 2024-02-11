from .base_posts_harvester import BasePostsHarvester
import requests
from datetime import datetime, timedelta

class _RedditHttpConnector:
    def __init__(self, use_script, secret, username, password):
        self.use_script = use_script
        self.secret = secret
        self.username = username
        self.password = password
    
        auth = requests.auth.HTTPBasicAuth(use_script, secret)

        data = {'grant_type': 'password',
                'username': username,
                'password': password}

        self.headers = {'User-Agent': 'MyBot/0.0.1'}

        res = requests.post('https://www.reddit.com/api/v1/access_token',
                            auth=auth, data=data, headers=self.headers)

        TOKEN = res.json()['access_token']

        self.headers = {**self.headers, **{'Authorization': f"bearer {TOKEN}"}}
    
    def get(self, url, params: dict = {}):
        resp = requests.get( url, params, headers=self.headers)
        return resp.json()

        

class RedditPostsHarvester(BasePostsHarvester):
    def __init__(self, use_script, secret, username, password):
        self.http = _RedditHttpConnector(use_script, secret, username, password)
        self.popular_subredits_endpoint = "https://oauth.reddit.com/subreddits/popular"
        self.subredit_popular_template = 'https://oauth.reddit.com{}/hot'
        self.number_of_popular_subredits = 50
        self.max_posts_per_request = 20
        self.base_link = "https://www.reddit.com"

        popular_subredits = self.get_subredits()
        self.subredits_data = []
        for subredit in popular_subredits:
            subredit_data = {
                'url': subredit,
                'fullname': None
            }
            self.subredits_data.append(subredit_data)


    def get_posts(self, days: int, quantity: int=-1) -> list:
        if quantity == -1:
            quantity = 1500
        
        
        delta = timedelta(days=1)
        current_date = datetime.now() - delta
        posts_per_day = quantity//30
        posts = []

        for i in range(days):
            new_posts = self.get_posts_for_date(current_date, 100, self.subredits_data)
            posts.extend(new_posts)
            current_date -= delta
        
        return posts
    
    def is_accepted_date(self, date, posts):
        for post in posts:
            if datetime.strptime(post['created_utc'], '%Y-%m-%d %H:%M:%S') < date:
                return True
            
        return False

    def get_posts_for_date(self, date, quantity, subredits_data):
        posts = []
        finding_point = False
        while quantity > 0:
            for subredit in subredits_data:
                if quantity <= 0:
                    break

                if finding_point:
                    number_of_posts = 100
                else:
                    number_of_posts = min(quantity, self.max_posts_per_request)
                params = {'limit': number_of_posts, 'after': subredit['fullname']}
                posts_data = self.http.get(self.subredit_popular_template.format(subredit['url']), params)
                if posts_data.get('data', None) is None:
                    continue
                subredit['fullname'] = posts_data['data']['after']
                converted_datra = self.convert(posts_data)
                if not self.is_accepted_date(date, converted_datra):
                    finding_point = True
                    continue
                if finding_point:
                    finding_point = False
                    continue
                print("post_data", len(converted_datra), flush=True)

                quantity -= number_of_posts
                posts.extend(converted_datra)
            
        return posts

    def convert(self, json_data):
        posts = []
        for post in json_data['data']['children']:
            post_data = post['data']
            unix_timestamp = int(post_data['created_utc'])
            posts.append({
                'title': post_data['title'],
                'text': post_data['title'] + "\n" + post_data['selftext'],
                'created_utc': datetime.utcfromtimestamp(unix_timestamp).strftime('%Y-%m-%d %H:%M:%S'),
                'link': self.base_link + post_data['permalink']
            })
        
        return posts

    def get_subredits(self):
        json_data = self.http.get(self.popular_subredits_endpoint, {'limit': self.number_of_popular_subredits})

        subredits = []
        for subredit in json_data['data']['children']:
            subredits.append(subredit['data']['url'])
        
        return subredits
    
    def get_name(self):
        return 'Reddit'
