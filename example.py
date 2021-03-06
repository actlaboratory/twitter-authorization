import twitterAuthorization
import webbrowser
import time
import tweepy

TWITTER_CONSUMER_KEY = ""
TWITTER_CONSUMER_SECRET = ""
LOCAL_PORT = 9339

if not TWITTER_CLIENT_ID:
	print ("please set your TWITTER_CLIENT_ID and try again.")

manager = twitterAuthorization.TwitterAuthorization(TWITTER_CONSUMER_KEY,TWITTER_CONSUMER_SECRET,LOCAL_PORT)
url = manager.getUrl()
webbrowser.open(url, new=1, autoraise=True)

# polling
try:
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
except KeyboardInterrupt:
	pass
except Exception as e:
	print(e)
finally:
	manager.shutdown()

if token:
	auth = tweepy.OAuthHandler(TWITTER_CONSUMER_KEY, TWITTER_CONSUMER_SECRET)
	auth.set_access_token(*token)
	twitterApi = tweepy.API(auth)

	user = twitterApi.get_user(screen_name="act_laboratory")
	print(user)
