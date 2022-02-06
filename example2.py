import twitterAuthorization
import webbrowser
import time

TWITTER_CLIENT_ID = "bDVKekZERkMtNXNVMlFoWnNONWY6MTpjaQ"
LOCAL_PORT = 9339
NEED_SCOPES = ["tweet.read", "users.read","offline.access"]

if not TWITTER_CLIENT_ID:
	print ("please set your TWITTER_CLIENT_ID and try again.")

manager = twitterAuthorization.TwitterAuthorization2(TWITTER_CLIENT_ID, LOCAL_PORT, NEED_SCOPES)
url = manager.getUrl()
webbrowser.open(url, new=1, autoraise=True)
token = None

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
			break
		# when token==None: continue polling
except KeyboardInterrupt:
	pass
except Exception as e:
	print(e)
finally:
	manager.shutdown()

if token:
	print(manager.getClient().get_me())

