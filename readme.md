# twitterAuthorization

## 概要

　Python製デスクトップアプリケーションにおいて、OAuth1.0を用いたTwitterユーザからの認可取得を簡単に行うためのモジュール

## 機能

	- 認証に使うURLの生成
	- ローカルでウェブサーバを立ち上げ、最低限のユーザ操作で認証を実現
	- トークンの取得
	- 得られたトークンをtweepyでの利用に便利な辞書で返却

## 使い方

　example.pyをご覧ください。認可取得後、フォローしているユーザを一覧表示するコンソールアプリケーションです。


## 注意事項
	- コンピュータ名に非ASCII文字が含まれているとUnicodeDecodeErrorとなる問題に対処するため、
	  http.server.HTTPServer内の関数を強制的に書き換えています。
	  この変更はPython3.8.5にて動作確認しています。

## 更新履歴
	- v1.0.0 (2021.04.24)
		- 初版
