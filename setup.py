# -*- coding: utf-8 -*-

from setuptools import setup
from setuptools import find_packages
from os import path
import re

package_name = "twitterAuthorization"

root_dir = path.abspath(path.dirname(__file__))

with open(path.join(root_dir, package_name, '__init__.py')) as f:
    init_text = f.read()
    version = re.search(
        r'__version__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    license = re.search(
        r'__license__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author = re.search(
        r'__author__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    author_email = re.search(
        r'__author_email__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)
    url = re.search(r'__url__\s*=\s*[\'\"](.+?)[\'\"]', init_text).group(1)

assert version
assert license
assert author
assert author_email
assert url

long_description = "デスクトップアプリケーションにおけるOAuth1/OAuth2を用いたTwitterユーザからの認可取得を最低限のユーザ操作とコーディングで実現することを目的に、localhostで稼働するシンプルなウェブサーバ、レスポンスの検証などの機能を提供するライブラリ"


setup(
    name=package_name,

    version=version,

    license=license,

    author=author,
    author_email=author_email,

	# 本モジュール作成時点での最新版tweepy4.5.0には不具合があるため、一時的に代わりのモジュールで対応
    #packages=[package_name],
    packages=[package_name, "tweepy450_twitterAuthorization"],

    url=url,

    description='Twitter OAuth1.0/2.0 Helper for desktop Apps',
    long_description=long_description,

    install_requires=('tweepy==4.5.0'),

)
