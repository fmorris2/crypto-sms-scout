import time, twitter, re, datetime
from requests import get
from twilio.rest import Client
from lxml import html

class Scout:
    MOBILE_NUMBERS_FILE_PATH = '/data/mobile_numbers'
    TWILIO_CREDS_FILE_PATH = '/data/twilio_credentials'
    SCOUTED_COINS_FILE_PATH = '/data/scouted_coins'
    TWITTER_KEYS_PATH = '/data/keys'

    CYCLE_TIME = 600 #seconds
    START_RANK = 300
    MAX_MARKET_CAP = 1000000
    TWEETS_IN_A_WEEK = 2 #how many tweets a week is considered active
    API_ENDPOINT = 'https://api.coinmarketcap.com/v1/ticker/?start='+str(START_RANK)+'&limit=100000'
    COIN_PAGE_URL = 'https://coinmarketcap.com/currencies/'

    mobile_numbers = []
    twilio_creds = []
    scouted_coins = []
    twitter_handles = {}

    def __init__(self):
        from main import ROOT_PATH
        self.root_path = ROOT_PATH
        self.load_mobile_numbers()
        self.load_twilio_creds()
        self.load_scouted_coins()
        self.load_twitter_keys()
        self.sms_client = Client(self.twilio_creds[0], self.twilio_creds[1])
        self.twitter_api = twitter.Api(consumer_key=self.twitter_keys[0],
                                      consumer_secret=self.twitter_keys[1],
                                      access_token_key=self.twitter_keys[2],
                                      access_token_secret=self.twitter_keys[3])

    def run(self):
        while(True):
            api_response = self.get_api_response_json()
            new_coins = self.parse_new_coins_from_json(api_response)
            self.notify_sms(new_coins)
            time.sleep(self.CYCLE_TIME)

    def get_api_response_json(self):
        try:
            response = get(self.API_ENDPOINT)
            return response.json()
        except Exception:
            return None

    def parse_new_coins_from_json(self, json):
        new_coins = []
        if json is None:
            return new_coins

        coins_checked = 0
        for coin in json:
            if(coins_checked % 100 == 0):
                print 'Checked ' + str(coins_checked) + '/' + str(len(json)) + ' coins'
            if self.is_notable_new_coin(coin):
                new_coins.append(coin)
            coins_checked += 1

        return new_coins

    def is_notable_new_coin(self, coin):
        if coin['id'] in self.scouted_coins:
            return False

        if coin['market_cap_usd'] is None or \
                float(coin['market_cap_usd']) > self.MAX_MARKET_CAP:
            return False

        if not self.coin_has_active_social_media(coin):
            return False

        return True

    def coin_has_active_social_media(self, coin):
            twitter_account_name = self.get_twitter_account_name(coin)
            tweets_in_past_week = 0
            if(twitter_account_name is not None):
                try:
                    tweets = self.twitter_api.GetUserTimeline(screen_name=twitter_account_name, count=20)
                    current_date = datetime.datetime.now()
                    margin = datetime.timedelta(days=7)
                    for tweet in tweets:
                        tweet_date = datetime.datetime.fromtimestamp(tweet.created_at_in_seconds)
                        if current_date - tweet_date <= margin:
                            tweets_in_past_week += 1
                except Exception:
                    return False

            return tweets_in_past_week >= self.TWEETS_IN_A_WEEK

    def get_twitter_account_name(self, coin):
        try:
            if(coin['id'] in self.twitter_handles):
                return self.twitter_handles[coin['id']]

            response = get(self.COIN_PAGE_URL + coin['id'] + '/#social')
            tree = html.fromstring(response.content)
            url = tree.cssselect('.twitter-timeline')[0].attrib['href']
            handle = re.search(r"[^/]+$", url).group(0)
            self.twitter_handles[coin['id']] = handle
            return handle
        except Exception:
            return None

    def notify_sms(self, new_coins):
        for coin in new_coins:
            print 'Notifying SMS clients for new coin: ' + coin['name']
            msg = 'INVESTMENT OPPORTUNITY:\n'\
              + coin['name'] + " (" + coin['symbol'] + ")\n" \
              + "Market cap: $" + self.human_format(float(coin['market_cap_usd'])) + "\n" \
              + "Price: $" + self.human_format(float(coin['price_usd'])) + "\n" \
              + "1h: " + self.plus_prepended(coin['percent_change_1h']) + "%\n" \
              + "24h: " + self.plus_prepended(coin['percent_change_24h']) + "%\n" \
              + "7d: " + self.plus_prepended(coin['percent_change_7d']) + "%\n"

            for number in self.mobile_numbers:
                self.sms_client.messages.create(to=number,
                                                from_=self.twilio_creds[2],
                                                body=msg)
            self.scouted_coins.append(coin['id'])
            scouted_coins_file = open(self.root_path + self.SCOUTED_COINS_FILE_PATH, 'a')
            scouted_coins_file.write(coin['id']+'\n')
            scouted_coins_file.close()

    def plus_prepended(self, str):
        if str is None:
            return 'N/A'
        
        return '' if str is None else \
                str if "-" in str else "+" + str

    def human_format(self, num):
        num = float('{:.3g}'.format(num))
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '{}{}'.format('{:f}'.format(num).rstrip('0').rstrip('.'), ['', 'K', 'M', 'B', 'T'][magnitude])

    def load_mobile_numbers(self):
        self.mobile_numbers = open(self.root_path + self.MOBILE_NUMBERS_FILE_PATH).read().splitlines()

    def load_twilio_creds(self):
        self.twilio_creds = open(self.root_path + self.TWILIO_CREDS_FILE_PATH).read().splitlines()

    def load_scouted_coins(self):
        self.scouted_coins = open(self.root_path + self.SCOUTED_COINS_FILE_PATH).read().splitlines()

    def load_twitter_keys(self):
        self.twitter_keys = open(self.root_path + self.TWITTER_KEYS_PATH).read().splitlines()