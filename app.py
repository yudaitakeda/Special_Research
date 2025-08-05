from flask import Flask, jsonify, render_template
import threading
import math
import csv
import time
import os
import dotenv
from flask_cors import CORS

import asyncio
from g3pylib import connect_to_glasses

app = Flask(__name__)
CORS(app)

gaze_data = {'x': 0, 'y': 0}
last_gaze_data = {'x': 0, 'y': 0}
distance_travelled = 0

# CSV保存
def save_gaze_data_to_csv(gaze_data):
    with open('gaze_data.csv', mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([time.time(), gaze_data['x'], gaze_data['y']])

# 非同期でTobii Glassesからgazeデータを取得
async def stream_gaze():
    global gaze_data, last_gaze_data, distance_travelled

    async with connect_to_glasses.with_hostname(
        os.environ["G3_HOSTNAME"], using_zeroconf=True
    ) as g3:
        async with g3.stream_rtsp(scene_camera=False, gaze=True) as streams:
            async with streams.gaze.decode() as gaze_stream:
                while True:
                    gaze, gaze_timestamp = await gaze_stream.get()
                    while gaze_timestamp is None:
                        gaze, gaze_timestamp = await gaze_stream.get()

                    if "gaze2d" in gaze:
                        x, y = gaze["gaze2d"]
                        gaze_data['x'], gaze_data['y'] = x, y

                        # 移動距離を加算
                        distance = math.sqrt((x - last_gaze_data['x'])**2 + (y - last_gaze_data['y'])**2)
                        distance_travelled += distance
                        last_gaze_data['x'], last_gaze_data['y'] = x, y

                        save_gaze_data_to_csv(gaze_data)

# 非同期イベントループをスレッドで起動
def start_async_loop():
    asyncio.run(stream_gaze())

# API：視線データ
@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)

# API：移動距離
@app.route('/distance_travelled')
def get_distance_travelled():
    return jsonify({'distance_travelled': distance_travelled})

# メインページ
@app.route('/')
def index():
    with open('data/content.txt', 'r', encoding='utf-8') as f:
        page_text = f.read()
    return render_template('index.html', page_text=page_text)

if __name__ == '__main__':
    dotenv.load_dotenv()  # G3_HOSTNAMEを読み込み

    t = threading.Thread(target=start_async_loop)
    t.daemon = True
    t.start()

    app.run(debug=True, port=5001)
