# twitterAuthorization

## 概要

　Python製デスクトップアプリケーションにおいて、OAuth1/OAuth2を用いたTwitterユーザからの認可取得を簡単に行うためのモジュール

## 機能

	- 認証に使うURLの生成
	- ローカルでウェブサーバを立ち上げ、最低限のユーザ操作で認証を実現
	- トークンの取得
	- v1では、得られたトークンをtweepyでの利用に便利な辞書で返却
	- v2では、tweepyのClientの生成、有効期限の管理と自動更新(リフレッシュ)も実装

## 使い方

　example.pyをご覧ください。認可取得後、認証に用いたアカウントの情報を表示するコンソールアプリケーションです。
　なお、v2ではリクエストのたびに当モジュールのgetClient()を用いてtweepy.Clientオブジェクトを取得していただくことで、トークンの有効期限を気にすることなくアプリケーションを開発可能です。
　v2のトークンは更新するとrefresh_tokenも含めて更新されるため、アプリケーション側で保存/読込を実装する際には当モジュールのgetData()およびsetData()を利用してください。

## 注意事項
	- コンピュータ名に非ASCII文字が含まれているとUnicodeDecodeErrorとなる問題に対処するため、
	  http.server.HTTPServer内の関数を強制的に書き換えています。
	  この変更はPython3.8.5にて動作確認しています。
	- tweepy4.5.0にはv2での利用に不具合があるため、当方で若干の修正を加えたものを同梱しています。
　　　tweepyの同梱はMIT Licenseに基づき行っています。
　　　Copyright (c) 2009-2022 Joshua Roesslein

## 更新履歴
	- v1.0.0 (2021.04.24)
		- 初版
	- v1.0.1 (2021.04.29)
		- 特定の場合に、デコンストラクタの呼出しにおいてエラーが発生してしまう不具合を修正
	- v1.0.2 (2022.02.01)
		- tweepyに破壊的変更が行われたため、旧バージョンを必ず使用するように変更
	- v1.0.3 (2022.02.04)
		- tweepy最新版に対応
	- v2.0.0 (2022.02.06)
		- twitterAPIv2での利用に対応しました。
		- v1.0.3への更新によりexample.pyが動作しなくなっていたため修正しました。
	- v2.0.1 (2022.02.07)
		- 同梱のtweepyが文法エラーで動作しなかったのを修正
	- v2.0.2 (2022.02.16)
		- トークンの更新が正しく動作しなかったのを修正
