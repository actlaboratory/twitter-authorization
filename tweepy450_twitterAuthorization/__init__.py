# tweepy450_twitterAuthorization
# Copyright 2009-2022 Joshua Roesslein
# See LICENSE for details.

"""
Tweepy Twitter API library
"""
__version__ = '4.5.0'
__author__ = 'Joshua Roesslein'
__license__ = 'MIT'

from tweepy450_twitterAuthorization.api import API
from tweepy450_twitterAuthorization.auth import (
    AppAuthHandler, OAuthHandler, OAuth1UserHandler, OAuth2AppHandler,
    OAuth2BearerHandler, OAuth2UserHandler
)
from tweepy450_twitterAuthorization.cache import Cache, FileCache, MemoryCache
from tweepy450_twitterAuthorization.client import Client, Response
from tweepy450_twitterAuthorization.cursor import Cursor
from tweepy450_twitterAuthorization.errors import (
    BadRequest, Forbidden, HTTPException, NotFound, TooManyRequests,
    TweepyException, TwitterServerError, Unauthorized
)
from tweepy450_twitterAuthorization.list import List
from tweepy450_twitterAuthorization.media import Media
from tweepy450_twitterAuthorization.pagination import Paginator
from tweepy450_twitterAuthorization.place import Place
from tweepy450_twitterAuthorization.poll import Poll
from tweepy450_twitterAuthorization.space import Space
from tweepy450_twitterAuthorization.streaming import Stream
from tweepy450_twitterAuthorization.tweet import ReferencedTweet, Tweet
from tweepy450_twitterAuthorization.user import User

# Global, unauthenticated instance of API
api = API()

def debug(enable=True, level=1):
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = level
