from flask import Flask, jsonify, render_template
import tobii_research as tr
import threading
import math

app = Flask(__name__)

# 視線データを保持する変数
gaze_data = {'x': 0, 'y': 0, 'blink_count': 0}
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

        print(f"視線座標 - X: {gaze_data['x']}, Y: {gaze_data['y']}")  # デバッグ出力
        print(f"移動距離: {distance}, 総移動距離: {distance_travelled}")  # デバッグ出力

    if gaze_data_response['left_eye_validity'] == 0 and gaze_data_response['right_eye_validity'] == 0:
        gaze_data['blink_count'] += 1

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

    app.run(debug=True, port=3000)





<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>視線スクロールテスト</title>
    <style>
        body {
            height: 2000px;
            font-size: 18px;
            line-height: 1.6;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        .page-button {
            position: fixed;
            top: 10px;
            width: 80px;
            height: 80px;
            background-color: rgba(0, 0, 255, 0.2);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 18px;
            font-weight: bold;
            color: black;
            cursor: pointer;
        }
        #page-content {
            text-align: center;
            margin-top: 100px;
            font-size: 32px;
        }
        #page-number {
            position: fixed;
            bottom: 20px;
            right: 20px;
            font-size: 18px;
        }
    </style>
</head>
<body>
    <div class="content">
        <h1>視線スクロールテスト</h1>
        <p id="page-content">{{ page_text }}</p>
        <a href="/distance_travelled">視線移動距離のページを見る</a>
    </div>
    <div id="page-number" class="page-number">Page: 1</div>

    <script>
        let hasScrolled = false;
        let lastGazeX = 0;

        function updatePageContent(pageNumber) {
            const contentElement = document.getElementById('page-content');
            contentElement.textContent = `
          ${contentText}
          Page: ${pageNumber}`;
        }

        function getGazeData() {
            fetch('/gaze_data')
                .then(response => response.json())
                .then(data => {
                    const x = data.x;
                    const currentTime = Date.now();

                    // 左から中央へ移動したときに一度だけスクロール
                    if (x > 0.9 && !hasScrolled && lastGazeX < x) {
                        window.scrollBy(0, 30); // 100px下にスクロール
                        hasScrolled = true;
                    } else if (x < 0.4) { // 左に戻ったらリセット
                        hasScrolled = false;
                    }

                    lastGazeX = x; // 前回のX位置を更新
                })
                .catch(error => console.error("視線データ取得エラー:", error));
        }

        // 定期的に視線データを取得
        setInterval(getGazeData, 300);
    </script>
</body>
</html>

