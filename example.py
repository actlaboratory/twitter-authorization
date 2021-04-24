import twitterAuthorization
import webbrowser
import time
import tweepy

TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""
LOCAL_PORT = 9401

manager = twitterAuthorization.TwitterGrant(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET,LOCAL_PORT)
url = manager.getUrl()
webbrowser.open(url, new=1, autoraise=True)

# polling
while(True):
	time.sleep(0.01)

	# return tupple, "" or None
	token=manager.getToken()
	if token=="":
		print("Authorization failed.  May be user disagreed.")
		break
	elif token:
		print(token)
		break
	# when token==None: continue polling

manager.shutdown()

if token:
	auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	auth.set_access_token(*token)
	twitterApi = tweepy.API(auth)

	user = twitterApi.get_user(screen_name="yamahubuki")
	print(user.screen_name)
	friendsCount = user.friends_count
	print(friendsCount)
	cursor=-1
	try:
		friends = tweepy.Cursor(twitterApi.friends,screen_name="yamahubuki",include_user_entities=False,skip_status=True,count=2).items()
		for friend in friends:
			print(friend.screen_name)
	except tweepy.error.RateLimitError:
		pass

