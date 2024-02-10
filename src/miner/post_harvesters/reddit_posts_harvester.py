import base_posts_harvester as base
import requests

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

        

class RedditPostsHarvester(base.BasePostsHarvester):
    def __init__(self, use_script, secret, username, password):
        self.http = _RedditHttpConnector(use_script, secret, username, password)
        self.popular_subredits_endpoint = "https://oauth.reddit.com/subreddits/popular"
        self.subredit_popular_template = 'https://oauth.reddit.com{}/hot'
        self.number_of_popular_subredits = 100
        self.max_posts_per_request = 50
        self.base_link = "www.reddit.com"

    def get_posts(self, days: int, quantity: int=-1) -> list:
        if quantity == -1:
            quantity = 100
        
        popular_subredits = self.get_subredits()
        subredits_data = []
        for subredit in popular_subredits:
            subredit_data = {
                'url': subredit,
                'fullname': None
            }
            subredits_data.append(subredit_data)
        posts = []

        while quantity > 0:
            for subredit in subredits_data:
                if quantity <= 0:
                    break
                number_of_posts = min(quantity, self.max_posts_per_request)
                quantity -= number_of_posts
                params = {'limit': number_of_posts, 'after': subredit['fullname']}
                posts_data = self.http.get(self.subredit_popular_template.format(subredit['url']), params)
                subredit['fullname'] = posts_data['data']['after']
                posts.append(self.convert(posts_data))
        
        return posts        

    def convert(self, json_data):
        posts = []
        for post in json_data['data']['children']:
            post_data = post['data']
            posts.append({
                'text': post_data['title'] + '\n' + post_data['selftext'],
                'created_utc': post_data['created_utc'],
                'link': self.base_link + post_data['permalink']
            })
        
        return posts

    def get_subredits(self):
        json_data = self.http.get(self.popular_subredits_endpoint, {'limit': self.number_of_popular_subredits})

        subredits = []
        for subredit in json_data['data']['children']:
            subredits.append(subredit['data']['url'])
        
        return subredits
