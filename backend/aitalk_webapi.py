#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__copyright__ 	= 'Copyright (C) 2018 AI, Inc.'
__url__ 		= 'https://www.ai-j.jp/'


import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from google.cloud import firestore

OUTPUT_FILE = './test.mp3'
OUTPUT_EXT = os.path.splitext(OUTPUT_FILE)[1][1:].lower()


class AITalkWebAPI:
	"""AITalk WebAPIを扱うクラス"""

	URL = 'https://webapi.aitalk.jp/webapi/v2/ttsget.php'	# WebAPI URL

	#  【通知されたものを指定してください】
	ID = 'riko0724_1008'	# ユーザ名(接続ID)
	PW = 'NrZ,3ORc=SMOY70L'	# パスワード(接続パスワード)


	def __init__(self):
		"""コンストラクタ"""
		# 合成パラメータ（詳細はWebAPI仕様書を参照）
		self.username = self.ID
		self.password = self.PW
		self.speaker_name 	= 'nozomi_emo'	# 話者名
		self.style 			= '{"j":"1.0"}'	# 感情パラメータ
		self.input_type 	= 'text'		# 合成文字種別
		self.text 			= ''			# 合成文字
		self.volume 		= 1.0			# 音量（0.01-2.00）
		self.speed 			= 1.0			# 話速（0.50-4.00）
		self.pitch 			= 1.2			# ピッチ（0.50-2.00）
		self.range 			= 1.5			# 抑揚（0.00-2.00）
		self.output_type 	= 'sound'		# 出力形式
		self.ext 			= 'mp3'			# 出力音声形式

		# 合成結果データ
		self._headers = None
		self._sound = None
		self._err_msg = None


	def synth(self):
		"""
		音声合成
		@return 正常終了か
		"""
		# 合成パラメータを辞書化
		dic_param = {
			'username'		: self.username,
			'password'		: self.password,
			'speaker_name'	: self.speaker_name,
			'style'			: self.style,
			'input_type'	: self.input_type,
			'text'			: self.text,
			'volume'		: self.volume,
			'speed'			: self.speed,
			'pitch'			: self.pitch,
			'range'			: self.range,
			'output_type'	: self.output_type,
			'ext'			: self.ext,
		}

		# URLエンコードされた合成パラメータの生成
		encoded_param = urllib.parse.urlencode(dic_param).encode('ascii')
		# HTTPヘッダーの生成
		header = {'Content-Type': 'application/x-www-form-urlencoded',}
		# URLリクエストの生成
		req = urllib.request.Request(self.URL, encoded_param, header)

		ret = False
		try:
			# URL接続
			with urllib.request.urlopen(req) as response:
				# HTTPステータスコード、ヘッダー、音声データの取得
				self.code = response.getcode()
				self.headers = response.info()
				self.sound = response.read()
				ret = self.code == 200
		except urllib.error.HTTPError as e:
			self._err_msg = 'HTTPError, Code: ' + str(e.code) + ', ' + e.reason
		except urllib.error.URLError as e:
			self._err_msg = e.reason
		return ret

	
	def get_error(self):
		"""
		合成エラーメッセージの取得
		@return 合成エラーメッセージ
		"""
		return self._err_msg if self._err_msg is not None else ''


	def save_to_file(self, output_filepath):
		"""
		音声データのファイル出力
		@param output_filepath 出力ファイルパス
		@return 正常終了か
		"""
		if self.sound is None:
			return False
		
		try:
			with open(output_filepath, 'wb') as f:
				f.write(self.sound)
		except IOError as e:
			return False
		return True


# Firestore クライアントの作成
db = firestore.Client(project=os.environ['PROJECT_ID'])

def display_blood_alcohol_levels():
    participants_ref = db.collection('drinking_records')
    docs = participants_ref.stream()

    print("各参加者の血中アルコール濃度:")
    for doc in docs:
        data = doc.to_dict()
        name = doc.id
        blood_alcohol_level = data.get('blood_alcohol_level', 0)
        print(f"名前: {name}, 血中アルコール濃度: {blood_alcohol_level}")

def get_lowest_blood_alcohol_user():
    participants_ref = db.collection('drinking_records')
    docs = participants_ref.stream()

    lowest_user = None
    lowest_level = float('inf')

    for doc in docs:
        data = doc.to_dict()
        user_name = doc.id
        blood_alcohol_level = data.get('blood_alcohol_level', 0)

        if blood_alcohol_level < lowest_level:
            lowest_level = blood_alcohol_level
            lowest_user = user_name

    return lowest_user, lowest_level

def main(lowest_user):
    """メイン処理"""

    # (1) 合成内容設定
    target_text = f'{lowest_user}、飲んでなくないー？うおううぉおー！'
    target_file = 'static/audio/output.mp3'

    # 出力ファイルから出力形式を決定
    ext = os.path.splitext(target_file)[1][1:]
    if ext == 'm4a':
        ext = 'aac'

    # (2) AITalkWebAPI インスタンス作成
    aitalk = AITalkWebAPI()

    # (3) パラメータ設定
    aitalk.text = target_text
    aitalk.ext = ext

    # (4) 合成処理
    if not aitalk.synth():
        print(aitalk.get_error(), file=sys.stderr)
        return 1

    # (5) ファイル保存
    if not aitalk.save_to_file(target_file):
        print('failed to save', file=sys.stderr)
        return 1

    print("音声ファイルが保存されました:", target_file)
    return 0

if __name__ == '__main__':
    # 最も血中アルコール濃度が低い人を取得
    lowest_user, lowest_level = get_lowest_blood_alcohol_user()

    # 結果を表示
    if lowest_user:
        print(f"最も血中アルコール濃度が低い人は: {lowest_user}（{lowest_level} mg/dL）です。")
        # main 関数に lowest_user を渡して実行
        main(lowest_user)
    else:
        print("ユーザーが見つかりませんでした。")