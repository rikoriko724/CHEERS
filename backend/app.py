import os
from dotenv import load_dotenv
from PIL import Image
import google.generativeai as genai
import base64
from google.cloud import firestore
from flask import Flask, render_template, send_from_directory, request, jsonify
from flask_cors import CORS
import random
import subprocess

app = Flask(__name__, static_folder='../frontend/dist', template_folder='../frontend/dist')
CORS(app)

# API-KEYの設定
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
genai.configure(api_key=GOOGLE_API_KEY)
type =  os.getenv("TYPE")
project_id = os.getenv("PROJECT_ID")
private_key_id = os.getenv("PRIVATE_KEY_ID")
private_key = os.getenv("PRIVATE_KEY").replace("\\n", "\n")
client_email = os.getenv("CLIENT_EMAIL")
client_id = os.getenv("CLIENT_ID")
auth_uri = os.getenv("AUTH_URI")
token_uri = os.getenv("TOKEN_URI")
auth_provider_x509_cert_url = os.getenv("AUTH_PROVIDER_X509_CERT_URL")
client_x509_cert_url = os.getenv("CLIENT_X509_CERT_URL")
universe_domain = os.getenv("UNIVERSE_DOMAIN")

print(project_id)
print(private_key)


# 画像を保存するディレクトリ
IMAGE_DIR = 'backend/images'
os.makedirs(IMAGE_DIR, exist_ok=True)

# Firestoreクライアントの作成
db = firestore.Client(project=os.environ['PROJECT_ID'])

# .envファイルの読み込み
load_dotenv()

# 画像処理が可能なモデルを初期化
gemini_pro = genai.GenerativeModel("gemini-1.5-flash")

# 実行する Python ファイルのリスト
scripts = [
    'aitalk_webapi.py',
    'aitalk_webapi2.py',
    'aitalk_webapi3.py'
]

@app.route('/')
def index():
    return render_template('index.html')

@app.route("/<path:path>")
def sendModuleFile(path):
    return send_from_directory(app.static_folder, path)

@app.route('/user/<username>')
def user_profile(username):
    return f"User: {username}"

@app.route('/upload', methods=['POST'])
def upload_image():
    try:

        # リクエストから JSON データを取得
        data = request.get_json() 
        print("Received JSON data:", data)

        # 'image' フィールドから画像データを取得
        image_data = data.get('image')
        user_id = data.get('userId')

        print("Received userId:", user_id)

        if not image_data:
            return jsonify({'error': '画像データが見つかりません'}), 400
        
        # ヘッダー部分を削除 ("data:image/png;base64," など)
        if image_data.startswith("data:image"):
            image_data = image_data.split(",")[1]

        # Base64 データをデコード
        image_bytes = base64.b64decode(image_data)
        image_path = os.path.join(IMAGE_DIR, 'alcohol.png')

        # 画像ファイルとして保存
        with open(image_path, 'wb') as f:
            f.write(image_bytes)
        print("Image saved successfully:", image_path)
                
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

        def get_user_id_and_gender(user_id):
            # 指定された名前のドキュメントを取得
            person_ref = db.collection('drinking_records').document(user_id)
            doc = person_ref.get()

            if doc.exists:
                data = doc.to_dict()
                gender = data.get('gender') #性別を取得する
                return gender
                                
            else:
                print(f"名前 '{user_id}' の飲酒履歴は見つかりませんでした。")


        gender = get_user_id_and_gender(user_id)

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

        def update_blood_alcohol_level(user_id, alcohol_name):
            # 'drinking_records' コレクション内の指定した人のドキュメントを取得
            person_ref = db.collection('drinking_records').document(user_id)
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
                print(f"{user_id}さんの血中アルコール濃度を更新しました。新しい値: {updated_level}")
            else:
                # ドキュメントが存在しない場合、新しいドキュメントを作成
                db.collection('drinking_records').document(user_id).set({
                    'blood_alcohol_level': rounded_value,
                    'alcohol_name_list': [alcohol_name],
                    'gender': gender
                })
                print(f"{user_id}さんの新しい記録を作成しました。")

        # 更新または新規作成を実行
        update_blood_alcohol_level(user_id, alcohol_name)

        # 正常終了時に成功のレスポンスを返す
        return jsonify({'message': '画像が正常にアップロードされました'}), 200

    except Exception as e:
        return jsonify({'error': f'更新に失敗しました: {str(e)}'}), 500

@app.route('/download', methods=['GET'])
def download():
    if not os.path.exists(OUTPUT_FILE):
        return jsonify({'error': 'ファイルが存在しません。'}), 404

    # 音声ファイルを返却
    return send_file(OUTPUT_FILE, as_attachment=True)

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

@app.route('/api/lowest_user', methods=['GET'])
def api_get_lowest_user():
    lowest_user, lowest_level = get_lowest_blood_alcohol_user()

    if lowest_user:
        return jsonify({
            "lowest_user": lowest_user,
            "blood_alcohol_level": lowest_level
        }), 200
    else:
        return jsonify({"error": "ユーザーが見つかりませんでした。"}), 404
    
@app.route('/api/run-random-script', methods=['GET'])
def run_random_script():
    # ランダムに1つのスクリプトを選択
    selected_script = random.choice(scripts)
    try:
        # サブプロセスで Python スクリプトを実行
        result = subprocess.run(['python', selected_script], capture_output=True, text=True)
        output = result.stdout
        return jsonify({"status": "success", "script": selected_script, "output": output})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
    
# 音声ファイルの提供エンドポイント
@app.route('/static/audio/output.mp3')
def serve_audio():
    return send_from_directory('static/audio', 'output.mp3')



if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)