# mytweets.py - Creates an archive of your tweets as a Git repo
# Sankha Narayan Guria <sankha93@gmail.com>

import sys, httplib, os.path, json, subprocess, urlparse
import oauth2 as oauth
from configobj import ConfigObj, ConfigObjError

try:
    config = ConfigObj('config.ini', file_error=True)
except (ConfigObjError, IOError), e:
    print 'Could not read "%s": %s' % ('config.ini', e)
    print 'Please provide your consumer keys'
    config = ConfigObj('config.ini')
    config['consumer'] = {}
    config['consumer']['key']    = raw_input('Consumer Key: ')
    config['consumer']['secret'] = raw_input('Consumer Secret: ')
    config.write()

consumer_key       = config['consumer']['key']
consumer_secret    = config['consumer']['secret']

consumer = oauth.Consumer(consumer_key, consumer_secret)

def getOauthToken(config, consumer):
	request_token_url = 'https://twitter.com/oauth/request_token'
	access_token_url = 'https://twitter.com/oauth/access_token'
	authorize_url = 'https://twitter.com/oauth/authorize'

	consumer = oauth.Consumer(consumer_key, consumer_secret)
	client = oauth.Client(consumer)

	# Step 1: Get a request token. This is a temporary token that is used for
	# having the user authorize an access token and to sign the request to obtain
	# said access token.

	resp, content = client.request(request_token_url, "GET")
	if resp['status'] != '200':
	    raise Exception("Invalid response %s." % resp['status'])

	request_token = dict(urlparse.parse_qsl(content))

	print "Request Token:"
	print "    - oauth_token        = %s" % request_token['oauth_token']
	print "    - oauth_token_secret = %s" % request_token['oauth_token_secret']
	print

	# Step 2: Redirect to the provider. Since this is a CLI script we do not
	# redirect. In a web application you would redirect the user to the URL
	# below.

	print "Go to the following link in your browser:"
	print "%s?oauth_token=%s" % (authorize_url, request_token['oauth_token'])
	print

	# After the user has granted access to you, the consumer, the provider will
	# redirect you to whatever URL you have told them to redirect to. You can
	# usually define this in the oauth_callback argument as well.
	accepted = 'n'
	while accepted.lower() == 'n':
	    accepted = raw_input('Have you authorized me? (y/n) ')
	oauth_verifier = raw_input('What is the PIN? ')

	# Step 3: Once the consumer has redirected the user back to the oauth_callback
	# URL you can request the access token the user has approved. You use the
	# request token to sign this request. After this is done you throw away the
	# request token and use the access token returned. You should store this
	# access token somewhere safe, like a database, for future use.
	token = oauth.Token(request_token['oauth_token'],
	    request_token['oauth_token_secret'])
	token.set_verifier(oauth_verifier)
	client = oauth.Client(consumer, token)

	resp, content = client.request(access_token_url, "POST")
	access_token = dict(urlparse.parse_qsl(content))

	config['oauth'] = {}
	config['oauth']['token']  = access_token['oauth_token']
	config['oauth']['secret'] = access_token['oauth_token_secret']
	config.write()

	print "Access Token:"
	print "    - oauth_token        = %s" % access_token['oauth_token']
	print "    - oauth_token_secret = %s" % access_token['oauth_token_secret']
	print
	print "Tokens saved to config, continuing archiving your tweets.."

def getTweets(num):
	request = "";
	if(num == -1):
		request = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + sys.argv[1] + "&count=200&include_rts=1&trim_user=1"
	else:
		request = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + sys.argv[1] + "&count=200&include_rts=1&trim_user=1&since_id=" + num
	return doRequest(request)

def doRequest(request):
	resp, content = client.request(request, "GET")
	if resp['status'] != '200':
		print content
		raise Exception("Invalid response %s." % resp['status'])
	return json.loads(content)

def processTweets(obj):
	if(len(obj) == 200):
		maxid = (obj[-1])['id'] - 1
		if(tweet_id == -1):
			request = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + sys.argv[1] + "&count=200&include_rts=1&trim_user=1&max_id=" + str(maxid)
		else:
			request = "https://api.twitter.com/1.1/statuses/user_timeline.json?screen_name=" + sys.argv[1] + "&count=200&include_rts=1&trim_user=1&max_id=" + str(maxid) + "&since_id=" + tweet_id
		processTweets(doRequest(request))

	for tweet in reversed(obj):
		f = open("tweet_id",'w')
		f.write(tweet['id_str'])
		f.close()
		subprocess.call(["git", "add", "tweet_id"])
		subprocess.call(["git", "commit", "--date", tweet['created_at'], "-m", tweet['text']])


if 'oauth' not in config:
	getOauthToken(config, consumer)

oauth_token        = config['oauth']['token']
oauth_token_secret = config['oauth']['secret']
token = oauth.Token(oauth_token, oauth_token_secret)
client = oauth.Client(consumer, token)

if len(sys.argv) > 1:
	if(os.path.exists("tweet_id")):
		tweet_id = open("tweet_id", 'r').read()
	else:
		tweet_id = -1
	processTweets(getTweets(tweet_id))
else:
	print("Usage: python mytweets.py username")