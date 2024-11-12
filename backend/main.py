import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import base64
from google.cloud import firestore

# Firestoreクライアントの作成
db = firestore.Client(project=os.environ['PROJECT_ID'])

# .envファイルの読み込み
load_dotenv()

# API-KEYの設定
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)

# 画像処理が可能なモデルを初期化
gemini_pro = genai.GenerativeModel("gemini-1.5-flash")

# 飲んだ人の名前を入力
person_name = input("飲んだ人の名前を入力してください: ")

# 画像をBase64でエンコード
with open('backend/images/alcohol.png', 'rb') as image_file:
    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

# テキストプロンプトを設定
prompt = "この画像に関して、以下の形式で出力してください。\
        お酒の名前については、なるべく多くわかる情報を出力してください。\
        改行はしないで表示してください。\
        お酒の容量がわからなければ350mlと仮定してください。\
        お酒の容量が画像から読み取れれば、その情報を使ってください。\
        お酒の容量とアルコール度数については、半角英数字のみで表示してください。単位は必要ありません。\
        「書いてあるお酒の名前, お酒の容量, アルコール度数」"

# モデルに画像とテキストプロンプトを送信して回答を生成
response = gemini_pro.generate_content(contents=[prompt, {'mime_type': 'image/png', 'data': encoded_image}])

# 結果を表示
print(response.text)

def get_person_name_and_gender(person_name):
    # 指定された名前のドキュメントを取得
    person_ref = db.collection('drinking_records').document(person_name)
    doc = person_ref.get()

    if doc.exists:
        data = doc.to_dict()
        gender = data.get('gender') #性別を取得する
        return gender
                        
    else:
        print(f"名前 '{person_name}' の飲酒履歴は見つかりませんでした。")


gender = get_person_name_and_gender(person_name)

# 性別によって体重をデフォルト設定
if gender == 1:
    weight = 50

elif gender == 0:
    weight = 60

#データを分割してリストに格納
data = response.text
#name, capacity, alcoholper = data 
data = response.text.split(",")
alcohol_name, capacity, alcohol_percent = data
capacity = int(capacity)
alcohol_percent = int(alcohol_percent)

# 血中アルコール濃度を計算
blood_alcohol = (capacity * float(alcohol_percent)) / (833 * weight) * 100
rounded_value = round(blood_alcohol,2)
print(f"血中アルコール濃度:{rounded_value:.2f}mg/dl")

def update_blood_alcohol_level(person_name, alcohol_name):
    # 'drinking_records' コレクション内の指定した人のドキュメントを取得
    person_ref = db.collection('drinking_records').document(person_name)
    doc = person_ref.get()

    if doc.exists:
        data = doc.to_dict()
        blood_alcohol_level = data.get('blood_alcohol_level', 0)  # 現在の血中アルコール濃度を取得
        updated_level = blood_alcohol_level + rounded_value

        # alcohol_name_listを取得または初期化
        alcohol_name_list = data.get('alcohol_name_list', [])
        if alcohol_name not in alcohol_name_list:
            alcohol_name_list.append(alcohol_name)  # お酒の名前をリストに追加

        # Firestoreに更新
        person_ref.update({
            'blood_alcohol_level': updated_level,
            'alcohol_name_list': alcohol_name_list
        })
        print(f"{person_name}さんの血中アルコール濃度を更新しました。新しい値: {updated_level}")
    else:
        # ドキュメントが存在しない場合、新しいドキュメントを作成
        db.collection('drinking_records').document(person_name).set({
            'blood_alcohol_level': rounded_value,
            'alcohol_name_list': [alcohol_name],
            'gender': gender
        })
        print(f"{person_name}さんの新しい記録を作成しました。")

# 更新または新規作成を実行
update_blood_alcohol_level(person_name, alcohol_name)
