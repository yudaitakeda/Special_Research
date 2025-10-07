from flask import Flask, render_template, url_for, jsonify
import os
import tobii_research as tr
import threading
import math
import time

app = Flask(__name__)

# ----------------------------
# 視線データ管理
# ----------------------------
gaze_data = {'x': 0.5, 'y': 0.5}  # 初期値中央
last_gaze_data = {'x': 0.5, 'y': 0.5}

# ----------------------------
# Tobiiデバイス検出
# ----------------------------
found_eyetrackers = tr.find_all_eyetrackers()
if len(found_eyetrackers) > 0:
    eyetracker = found_eyetrackers[0]
    print(f"Tobiiデバイス検出: {eyetracker.model} ({eyetracker.address})")
else:
    eyetracker = None
    print("Tobiiデバイスが見つかりません")

# ----------------------------
# 視線コールバック
# ----------------------------
def gaze_data_callback(response):
    global gaze_data, last_gaze_data
    if response['left_gaze_point_validity'] and response['right_gaze_point_validity']:
        x = (response['left_gaze_point_on_display_area'][0] +
             response['right_gaze_point_on_display_area'][0]) / 2
        y = (response['left_gaze_point_on_display_area'][1] +
             response['right_gaze_point_on_display_area'][1]) / 2
        gaze_data['x'] = x
        gaze_data['y'] = y
        last_gaze_data['x'] = x
        last_gaze_data['y'] = y

# ----------------------------
# ディレクトリ設定
# ----------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, 'data', 'files', 'text')  # textフォルダまで

# ----------------------------
# ルート：視線データ取得
# ----------------------------
@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)

# ----------------------------
# トップページ：作者一覧
# ----------------------------
@app.route('/')
def index():
    authors = [name for name in os.listdir(DATA_DIR)
               if os.path.isdir(os.path.join(DATA_DIR, name))]
    authors.sort()
    return render_template('index.html', authors=authors)

# ----------------------------
# 作者ページ：作品一覧
# ----------------------------
@app.route('/author/<author>')
def author_page(author):
    author_path = os.path.join(DATA_DIR, author)
    if not os.path.exists(author_path):
        return f"{author} は存在しません", 404

    works = [f for f in os.listdir(author_path)
             if os.path.isfile(os.path.join(author_path, f))]
    works.sort()
    return render_template('author.html', author=author, works=works)

# ----------------------------
# 作品ページ：本文表示
# ----------------------------
@app.route('/files/<author>/<work>')
def serve_file(author, work):
    path = os.path.join(DATA_DIR, author, work)
    if os.path.exists(path) and os.path.isfile(path):
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
        return render_template(
            'work.html',
            author=author,
            work_name=work,
            content=content
        )
    else:
        return "作品が見つかりません", 404

# ----------------------------
# メイン処理
# ----------------------------
if __name__ == '__main__':
    # Tobiiがある場合は別スレッドで視線データ取得
    if eyetracker:
        thread = threading.Thread(target=lambda: eyetracker.subscribe_to(
            tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True))
        thread.daemon = True
        thread.start()

    app.run(debug=True, port=5001)
