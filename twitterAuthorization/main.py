import threading
import wsgiref.util
from wsgiref.simple_server import make_server
import http.server
import socketserver
import socket
import tweepy
import urllib.parse


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


class TwitterAuthorization:
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

		# start local web server
		self.wsgi_app = _RedirectWSGIApp(
			self.port,
			self._registToken,
			self._failedRequest
		)
		self.localServer = wsgiref.simple_server.make_server("localhost", self.port, self.wsgi_app, handler_class=_WSGIRequestHandler)
		thread = threading.Thread(target=self._localServerThread, args=(self.localServer,))
		thread.start()

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

	def _registToken(self, result):
		self.result = self.tweepy.get_access_token(result["oauth_verifier"][0])
		# (result["oauth_token"][0]

	def _failedRequest(self):
		self.result = ""

	def __del__(self):
		self.shutdown()

	def shutdown(self):
		if self.localServer:
			self.localServer.shutdown()
			self.localServer = None

	def _localServerThread(self, server):
		server.serve_forever()


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
		self.lang = "ja"

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
			query = urllib.parse.urlparse(uri).query
			queryDic = urllib.parse.parse_qs(query)

			# 例外発生しなければ正当なリクエスト
			# サーバ側で処理
			if query != "":
				self.hook(queryDic)

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
