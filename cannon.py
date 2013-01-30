import os
import time
from json import loads

import twitter
from redis import Redis, from_url

try:
    REDIS_CONN = Redis()
except:
    REDIS_CONN = from_url(os.environ['REDISTOGO_URL'])

TWITTER_API = twitter.Api(
    consumer_key=os.environ['CONSUMER_KEY'],
    consumer_secret=os.environ['CONSUMER_SECRET'],
    access_token_key=os.environ['ACCESS_TOKEN_KEY'],
    access_token_secret=os.environ['ACCESS_TOKEN_SECRET']
)


def tweet(content):
    tweet_text = '{0} - {1}'.format(content['bill'], content['bill_text'])
    if len(tweet_text) > 116:
        tweet_text = tweet_text[:116].strip() + '...'
    tweet_text = tweet_text + ' ' + content['bill_url']
    print(tweet_text)
    print(len(tweet_text))
    TWITTER_API.PostUpdate(tweet_text)


def main():
    try:
        while True:
            if REDIS_CONN.llen('tweets'):
                oldest_tweet = REDIS_CONN.lindex('tweets', 0)
                try:
                    tweet(loads(oldest_tweet))
                except twitter.exceptions.TwitterError:
                    print("Twitter is unhappy with something.")
                    time.sleep(60)
                    continue
                REDIS_CONN.lpop('tweets')
                time.sleep(60 * 5)  # 5 minutes
            else:
                time.sleep(60)

    except KeyboardInterrupt:
        print('Stopping...')


if __name__ == '__main__':
    main()
