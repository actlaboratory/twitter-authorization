import http.server
import wsgiref.util
import socketserver
import socket
import threading
import time
import tweepy
import tweepy450_twitterAuthorization
import urllib.parse

from wsgiref.simple_server import make_server
from requests_oauthlib import OAuth2Session


def server_bind(self):
	"""Override server_bind to fix UnicodeDecodeError when computer name has non-ascii characters."""
	socketserver.TCPServer.server_bind(self)
	host, port = self.server_address[:2]
	try:
		self.server_name = socket.getfqdn(host)
	except UnicodeDecodeError:
		self.server_name = "localhost"
	self.server_port = port


http.server.HTTPServer.server_bind = server_bind


class TwitterAuthorizationBase:
	def startServer(self):
		# start local web server
		self.wsgi_app = _RedirectWSGIApp(
			self.port,
			self._registToken,
			self._failedRequest
		)
		self.localServer = wsgiref.simple_server.make_server("localhost", self.port, self.wsgi_app, handler_class=_WSGIRequestHandler)
		thread = threading.Thread(target=self._localServerThread, args=(self.localServer,))
		thread.start()

	def _localServerThread(self, server):
		server.serve_forever()

	def setMessage(self, lang, success, failed, transfer):
		"""
						Set Message that viewd in browser
						Args:
										lang (string): The message language code (ex:ja,en,...)
										success (string): The success message
										failed (string): The failed message
										transfer (string): The transfer error message that appear in old or Javascript disabled browser
		"""
		self.wsgi_app.setMessage(lang, success, failed, transfer)

	def getUrl(self):
		"""
						Get Authorization url
						Returns:
										AuthorizationUrl (string)

		"""
		return self.url

	def getToken(self):
		"""
						Get accesstoken (success), "" (failed) or None (waiting)
						If returned "" and the browser stays open, software should close that.

						Returns:
										tokenData (dict) or None
		"""
		if self.result != None:
			self.shutdown()
		return self.result

	def _failedRequest(self):
		self.result = ""

	def shutdown(self):
		if self.localServer:
			self.localServer.shutdown()
			self.localServer = None

	def __del__(self):
		self.shutdown()


# v2
class TwitterAuthorization2(TwitterAuthorizationBase):
	def __init__(self, clientId, receivePort, scopes):
		"""
						Args:
										clientId (string): The clientId from Twitter developper portal
										receivedPort (string): The port number to receive request
										scopes (list): the list of need scopes
		"""
		self.result = None

		self.key = clientId
		self.port = receivePort
		self.redirect_uri = "http://localhost:%d" % self.port
		self.scopes = scopes
		self.localServer = None
		self.refresh_mergin = 1200

		# generate request URL
		self.tweepy = tweepy.OAuth2UserHandler(client_id=self.key, redirect_uri=self.redirect_uri, scope=scopes)

		try:
			self.url = self.tweepy.get_authorization_url()
		except (tweepy.TweepyException, tweepy.HTTPException) as e:
			raise Exception(e)
		self.startServer()

	def _registToken(self, uri):
		"""
						Args:
										url (string): Authorization Response URL
		"""
		self.result = self.tweepy.fetch_token(uri)
		return self.result

	def getClient(self):
		if not self.result:
			return None

		# check expires_at
		if time.time() - self.refresh_mergin > self.result["expires_at"]:
			self.refresh()
		return tweepy450_twitterAuthorization.Client(bearer_token=self.result["access_token"])

	def getData(self):
		return self.result

	def setData(self, data):
		self.result = data

	def refresh(self):
		#self.result = self.tweepy.refresh_token(self.result["refresh_token"])
		session = OAuth2Session(self.key, redirect_uri=self.redirect_uri, scope=self.scopes)
		self.result = session.refresh_token(
			"https://api.twitter.com/2/oauth2/token",
			refresh_token=self.result["refresh_token"],
			body="client_id="+self.key
		)
		return self.result

	def setRefreshMergin(self,mergin):
		assert type(mergin) == int
		self.refresh_mergin = mergin


# v1
class TwitterAuthorization(TwitterAuthorizationBase):
	def __init__(self, consumerKey, consumerSecret, receivePort):
		"""
						Args:
										consumerKey (string): The consumerKey from Twitter developper portal
										consumerSecret (string): The consumerSecret from Twitter developper portal
										receivedPort (string): The port number to receive request
		"""
		self.result = None

		self.key = consumerKey
		self.secret = consumerSecret
		self.port = receivePort
		self.localServer = None

		# generate request URL
		self.tweepy = tweepy.OAuth1UserHandler(self.key, self.secret, "http://localhost:%d" % self.port)

		try:
			self.url = self.tweepy.get_authorization_url()
		except (tweepy.TweepyException, tweepy.HTTPException) as e:
			raise Exception(e)

		self.startServer()

	def _registToken(self, uri):
		query = urllib.parse.urlparse(uri).query
		result = urllib.parse.parse_qs(query)
		self.result = self.tweepy.get_access_token(result["oauth_verifier"][0])


class _WSGIRequestHandler(wsgiref.simple_server.WSGIRequestHandler):
	def __init__(self, *args, **argv):
		super().__init__(*args, *argv)
		# コネクションは毎回切断する
		self.close_connection = True

	def log_message(self, *args):
		# disable logger
		pass


class _RedirectWSGIApp(object):
	"""
					WSGI app to handle the authorization redirect.
					Stores the request URI and displays the given success message.
	"""

	def __init__(self, port, hook, failedHook):
		"""
						Args:
										port (int): The port number That receive request
										hook (callable): The function when got token
										failedHook (callable): The function when authorization failed (ex: disagreed authorize)
		"""

		self.successMessage = "Authorization successful.  Close this window and go back to your application."
		self.failedMessage = "Authorization failed.  Please try again."
		self.transferMessage = "If the screen does not change after a while, open this page in another browser."
		self.lang = "en"

		self.port = port
		self.hook = hook
		self.failedHook = failedHook

	def setMessage(self, lang, success, failed, transfer):
		"""
						Set Message that viewd in browser
						Args:
										lang (string): The message language code (ex:ja,en,...)
										success (string): The success message
										failed (string): The failed message
										transfer (string): The transfer error message that appear in old or Javascript disabled browser
		"""
		self.lang = lang
		self.successMessage = success
		self.failedMessage = failed
		self.transferMessage = transfer

	def __call__(self, environ, start_response):
		"""
						Args:
										environ (Mapping[str, Any]): The WSGI environment.
										start_response (Callable[str, list]): The WSGI start_response
														callable.
						Returns:
										Iterable[bytes]: The response body.
		"""
		try:
			uri = wsgiref.util.request_uri(environ)

			# 例外発生しなければ正当なリクエスト
			# サーバ側で処理
			query = urllib.parse.urlparse(uri).query
			if query != "":
				uri = "https"+uri[4:]
				self.hook(uri)

			start_response('200 OK', [('Content-type', 'text/html; charset=utf-8')])
			response = [("<html lang='" + self.lang + "'><head><title>Authorization result</title><meta charset='utf-8'></head><body>" + self.successMessage + "<script><!--\n").encode('utf-8')]
			response.append("window.close()\n".encode("utf-8"))
			response.append("--></script></body></html>".encode("utf-8"))
			return response
		except Exception as e:
			if query != "":  # favicon.icoなどの不要なリクエストへの対策
				self.failedHook()
			start_response('400 Bad Request', [('Content-type', 'text/html; charset=utf-8')])
			return [("<html lang='" + self.lang + "'><head><title>Authorization result</title><meta charset='utf-8'></head><body>" + self.failedMessage + "</body></html>").encode('utf-8')]

