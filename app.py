# =========================================
# Flask + Tobii 視線データサーバー
# （視線データを取得しつつ、青空文庫風の読書APIを提供）
# =========================================

from flask import Flask, jsonify, render_template
import tobii_research as tr
import threading, math, csv, time, os
from flask_cors import CORS

# Flaskアプリ作成
app = Flask(__name__)
CORS(app)  # 他のページ（例: JSのfetch）からのアクセスを許可

# ========= 視線データ関連 =========

# 現在の視線座標（画面内で正規化された値：0〜1）
gaze_data = {'x': 0, 'y': 0}

# 前回の視線座標（移動距離の計算に使用）
last_gaze_data = {'x': 0, 'y': 0}

# 視線の累計移動距離（オプション用途）
distance_travelled = 0

# Tobiiデバイスを検索
found_eyetrackers = tr.find_all_eyetrackers()
eyetracker = found_eyetrackers[0] if found_eyetrackers else None


# Tobiiから1サンプル届くたびに呼ばれるコールバック関数
def gaze_data_callback(gaze_data_response):
    global gaze_data, last_gaze_data, distance_travelled

    # 両目のデータが有効な場合のみ処理
    if gaze_data_response['left_gaze_point_validity'] and gaze_data_response['right_gaze_point_validity']:
        # 左右の視線点の平均値をとって「注視点座標」を計算
        gaze_data['x'] = (gaze_data_response['left_gaze_point_on_display_area'][0] +
                          gaze_data_response['right_gaze_point_on_display_area'][0]) / 2
        gaze_data['y'] = (gaze_data_response['left_gaze_point_on_display_area'][1] +
                          gaze_data_response['right_gaze_point_on_display_area'][1]) / 2

        # 前回位置との差から移動距離を計算
        distance = math.sqrt(
            (gaze_data['x'] - last_gaze_data['x'])**2 +
            (gaze_data['y'] - last_gaze_data['y'])**2
        )
        distance_travelled += distance

        # 現在座標を更新
        last_gaze_data.update(gaze_data)

        # CSVに保存（追記モード）
        save_gaze_data_to_csv(gaze_data)


# 視線データをCSVに保存する関数
def save_gaze_data_to_csv(data):
    with open('gaze_data.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        # [タイムスタンプ, x座標, y座標] の形式で記録
        writer.writerow([time.time(), data['x'], data['y']])


# ブラウザから現在の視線座標を取得できるAPI
@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)


# ========= 読書データAPI =========

# 青空文庫などのテキストHTMLを格納しているルートディレクトリ
BASE_PATH = "data/files/text"


# トップページ（index.html）を返す
@app.route('/')
def index():
    return render_template('index.html')


# 作者一覧を返すAPI
# 例: /api/authors → ["夏目漱石", "芥川龍之介", ...]
@app.route('/api/authors')
def get_authors():
    authors = [a for a in os.listdir(BASE_PATH) if os.path.isdir(os.path.join(BASE_PATH, a))]
    return jsonify(authors)


# 作者に対応する作品一覧を返すAPI
# 例: /api/works/夏目漱石 → ["坊っちゃん", "こころ", ...]
@app.route('/api/works/<author>')
def get_works(author):
    folder = os.path.join(BASE_PATH, author)
    works = [os.path.splitext(f)[0] for f in os.listdir(folder) if f.endswith('.html')]
    return jsonify(works)


# 作品本文を返すAPI
# 例: /api/work/夏目漱石/坊っちゃん
@app.route('/api/work/<author>/<title>')
def get_work(author, title):
    path = os.path.join(BASE_PATH, author, f"{title}.html")
    try:
        with open(path, encoding='utf-8') as f:
            content = f.read()
        return jsonify({'author': author, 'title': title, 'content': content})
    except FileNotFoundError:
        return jsonify({'error': 'not found'}), 404


# ========= メイン処理 =========
if __name__ == '__main__':
    # Tobiiが見つかった場合は別スレッドで購読開始
    if eyetracker:
        t = threading.Thread(
            target=lambda: eyetracker.subscribe_to(
                tr.EYETRACKER_GAZE_DATA,
                gaze_data_callback,
                as_dictionary=True
            )
        )
        t.daemon = True  # メイン終了時に自動終了
        t.start()

    # Flaskサーバー起動
    app.run(debug=True, port=5001)
