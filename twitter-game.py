#!/usr/bin/env python3
#this is a shebang line: https://en.wikipedia.org/wiki/Shebang_(Unix)

import random, json, re
from requests_oauthlib import OAuth1Session
from html import unescape as html_unescape

# Also called api_key & api_secret in the twitter developer portal under projects
client_key = input('Please Enter Your Client Key (available in your developer portal as API Key): ')
client_secret = input('Please Enter Your Client Secret (available in your developer portal as API Key Secret): ')


# Some regexes we will use to filter our tweets and detect urls
re_tagged_username_pattern = re.compile('@(\w){1,15}')
re_link_pattern = re.compile('https:\/\/t.co\/(\w){1,10}')


# A Helper class which handles authentication upon intialization and all subsequent communication with the Twitter API
class Twitter_OAuth_Session:
    client_key = ''
    client_secret = ''

    # These are Twitter's provided base oauth endpoints
    request_token_url = 'https://api.twitter.com/oauth/request_token'
    authorization_url = 'https://api.twitter.com/oauth/authorize'
    access_token_url = 'https://api.twitter.com/oauth/access_token'

    # This will eventually be an OAuth1Session
    oauth_session = None

    # The following are python dictionaries we will eventually populate with some pertinent information
    # They are not actually needed throughout this process, but we provide it for clarity and debugging purposes
    oauth_request = None
    oauth_access = None

    # Constructor function, will intiate and authorize our session
    # returns None
    def __init__(self, client_key, client_secret): 
        self.client_key = client_key
        self.client_secret = client_secret

        #Step 0: Initialize Session Variables
        self.init_oauth_session()

        #Step 1: Fetch Request Tokens
        self.fetch_request_token()

        #Step 2: App Authorization
        self.manual_authorizization()

        #Step 3: Get Access Tokens for this Session
        self.fetch_access_token()


    # Initializes Client Varibles in self.oauth_session
    # returns None
    def init_oauth_session(self):
        self.oauth_session = OAuth1Session(
            self.client_key, 
            client_secret=self.client_secret, 
            callback_uri='oob') #we have no callback uri as we are not hosting a local or public server so we provide the expected out of bounds (oob) value 

    # Populates 'oauth_token', 'oauth_token_secret', 'oauth_callback_confirmed' in oauth_request
    # Actually, this method technically also updates the oauth_session but we will just reinitiate the oauth_session variable for clarity
    # returns None
    def fetch_request_token(self):
        self.oauth_request = self.oauth_session.fetch_request_token(self.request_token_url)
    
    # Manual Step, Prompts user for authorization, populates 'oauth_verifier' in oauth_request with user-provided PIN
    # As we do not callback (lack of local/public server), we simply reinitiate the oauth_session using the PIN as our verifier instead of passing the verifier to the current oauth_session
    # returns None
    def manual_authorizization(self):
        # Prompt the user for authorization during this session
        print(f'Please authorize this application at {self.authorization_url}?oauth_token={self.oauth_request["oauth_token"]}')

        # Try to open the user's webbrowser and direct them to webpage
        # Then we ask to user to enter the PIN
        try:
            import webbrowser
            webbrowser.open(f'{self.authorization_url}?oauth_token={self.oauth_request["oauth_token"]}', new=2)
        finally:
            self.oauth_request['oauth_verifier'] = input('Upon authorization, please enter your PIN here: ')
        
        # Reinitalize the oauth session with new resource parameters
        # We could technically just update the current oauth_session with the verifier (PIN), but reinitialization makes it clearer exactly what exactly our oauth_session is using for verification
        self.oauth_session = OAuth1Session(
            self.client_key, 
            client_secret= self.client_secret, 
            resource_owner_key = self.oauth_request['oauth_token'], 
            resource_owner_secret = self.oauth_request['oauth_token_secret'], 
            verifier = self.oauth_request['oauth_verifier'], 
            signature_method="HMAC-SHA1")
    
    # Populates 'oauth_token' & 'oauth_token_secret' in oauth_access, updates oauth_session with these variables internally
    # returns None
    def fetch_access_token(self):
        self.oauth_access = self.oauth_session.fetch_access_token(self.access_token_url)
    
    # This is how information can be pulled or posted during a session: intercepts the default request to inject authorization headers
    # method: typically 'GET' or 'POST'
    # url: designated endpoint
    # returns: a response object
    def request(self, method, url, data=None, headers=None):
        return self.oauth_session.request(method, url, data=data, headers=headers)


# twitter_oauth_session: any authenticated Twitter_OAuth_Session()
# screen_name: the target user's whose historical tweets you want to pull
# n: the max number of tweets you want to pull
# returns a list of the target user's latest tweets whose length is between 0 and n
#   - filtered to skip unoriginal tweets (retweets or replies) and tweets with user tags in it
#   - returned tweets have all urls redacted
def get_last_n_filtered_tweets(twitter_oauth_session, screen_name, n):
    base_URI = f'https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name={screen_name}&count=200'

    all_tweet_texts = []
    last_id = 0
    while( len(all_tweet_texts) < n ):
        current_tweets = json.loads(twitter_oauth_session.request('GET', f"{base_URI}&max_id={last_id}" if last_id else base_URI).text)

        if current_tweets[-1]['id'] == last_id: break

        for tweet in current_tweets:           
            #Skip replies
            if current_tweets[0]['in_reply_to_status_id']: continue

            #Skip retweets
            if current_tweets[0]['retweeted']: continue

            #Skip tweets with any users tagged in it
            if bool(re_tagged_username_pattern.search(tweet['text'])): continue

            #Redact all urls, twitter automatically converts urls to the t.co shortened format so we simply replace those
            tweet['text'] = re_link_pattern.sub('[url redacted]', tweet['text']).strip()
            if tweet['text'] == '[url redacted]': continue

            #If it passed all these checks, we add it to our all_tweet_texts list to eventually return
            all_tweet_texts.append(html_unescape(tweet['text']))
        last_id = current_tweets[-1]['id']
    
    return all_tweet_texts[:n]

    
#Game Logic
if __name__ == "__main__":
    # Connect to the Twitter API
    twitter_oauth_session = Twitter_OAuth_Session(client_key, client_secret)

    # Get our twitter handles
    id1 = input('\nPlease enter the handle of a twitter user: ')
    id2 = input('Please enter the handle of a second twitter user: ')

    # Load the past 3200 tweets
    print(f'\nLoading the latest <=3200 tweets from {id1} & {id2}...')
    id1_tweets = get_last_n_filtered_tweets(twitter_oauth_session, id1, 3200)
    id2_tweets = get_last_n_filtered_tweets(twitter_oauth_session, id2, 3200)

    keep_playing = True
    round_number = 0 #number of total rounds played
    right = 0 #number of total rounds won
    while(keep_playing):
        round_number += 1

        selected_id = random.randint(1, 2)
        tweet = ''

        # Pull a tweet from whichever ID we selected
        if selected_id == 1:
            #id1
            tweet = id1_tweets[random.randint(0, len(id1_tweets))]
        else:
            #id2
            tweet = id2_tweets[random.randint(0, len(id2_tweets))]
        
        # Print Round # & Tweet
        print()
        print(f"Round #{round_number}")
        print(f"Tweet: {tweet}")

        # Get the user to guess what tweet we've pulled
        choice = -1
        while(True):
            choice = input(f"\tDo you think this came from {id1} (type {id1}) or {id2} (type {id2})?: ")
            if choice == id1: choice = 1
            elif choice == id2: choice = 2
            else:
                print('\tInvalid selection, try again.')
                continue
            break
        
        # Tell the User if They're Right or Wrong
        if choice == selected_id:
            print("\tCongrats, you guessed right!")
            right += 1
        else: print("\tSorry, you guessed wrong.")

        # Ask the User if they want to continue
        keep_playing = 'q' != input("\tType 'q' and press enter to quit, or enter anything else to continue: ")

    # Print the User's score
    print(f"Your Score: {right}/{round_number}")