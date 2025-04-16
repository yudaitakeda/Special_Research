from flask import Flask, jsonify, render_template
import tobii_research as tr
import threading
import math
import csv
import time

app = Flask(__name__)

# 視線データを保持する変数
gaze_data = {'x': 0, 'y': 0}
last_gaze_data = {'x': 0, 'y': 0}  # 前回の視線位置
distance_travelled = 0  # 視線の総移動距離

# デバイスの初期化
found_eyetrackers = tr.find_all_eyetrackers()
if len(found_eyetrackers) > 0:
    eyetracker = found_eyetrackers[0]
else:
    eyetracker = None
    print("Tobiiデバイスが見つかりませんでした")

# 視線データ取得のコールバック関数
def gaze_data_callback(gaze_data_response):
    global gaze_data, last_gaze_data, distance_travelled

    if gaze_data_response['left_gaze_point_validity'] and gaze_data_response['right_gaze_point_validity']:
        # 視線の座標（中央の視線）を計算
        gaze_data['x'] = (gaze_data_response['left_gaze_point_on_display_area'][0] +
                          gaze_data_response['right_gaze_point_on_display_area'][0]) / 2
        gaze_data['y'] = (gaze_data_response['left_gaze_point_on_display_area'][1] +
                          gaze_data_response['right_gaze_point_on_display_area'][1]) / 2

        # 視線の移動距離を計算
        distance = math.sqrt((gaze_data['x'] - last_gaze_data['x'])**2 + (gaze_data['y'] - last_gaze_data['y'])**2)
        distance_travelled += distance  # 総移動距離に加算

        # 現在の視線位置を前回位置として保存
        last_gaze_data['x'] = gaze_data['x']
        last_gaze_data['y'] = gaze_data['y']

        # 視線データをCSVに保存
        save_gaze_data_to_csv(gaze_data)

# CSVに視線データを保存する関数
def save_gaze_data_to_csv(gaze_data):
    with open('gaze_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        # 視線データをCSVに書き込む（時間も一緒に記録）
        writer.writerow([time.time(), gaze_data['x'], gaze_data['y']])

# content.txtファイルの読み込み関数
def get_page_text():
    with open('data/content.txt', 'r', encoding='utf-8') as f:
        return f.read()

# 視線データを取得するAPI
@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)

# 視線の総移動距離を取得するAPI
@app.route('/distance_travelled')
def get_distance_travelled():
    return jsonify({'distance_travelled': distance_travelled})

# メインページ
@app.route('/')
def index():
    page_text = get_page_text()  # content.txtから文章を取得
    return render_template('index.html', page_text=page_text)

if __name__ == '__main__':
    if eyetracker:
        tracking_thread = threading.Thread(target=lambda: eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True))
        tracking_thread.daemon = True
        tracking_thread.start()

    app.run(debug=True, port=5001)





































































