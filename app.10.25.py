#10/25 視線オートスクロールと左右領域注視でのページ移動機能まで実装
#ここから→アイジェスチャによる操作機能と実験タスク用のwebページ作成,比較実験の項目作成
# app.py (Flaskアプリケーション)
from flask import Flask, jsonify, render_template
import tobii_research as tr
import threading
import time

app = Flask(__name__)

# 視線データを保持する変数
gaze_data = {'x': 0, 'y': 0, 'blink_count': 0}

# デバイスの初期化
found_eyetrackers = tr.find_all_eyetrackers()
if len(found_eyetrackers) > 0:
    eyetracker = found_eyetrackers[0]
else:
    eyetracker = None
    print("Tobiiデバイスが見つかりませんでした")

# 視線データ取得のコールバック関数
def gaze_data_callback(gaze_data_response):
    global gaze_data

    if gaze_data_response['left_gaze_point_validity'] and gaze_data_response['right_gaze_point_validity']:
        # 両目が有効な場合、座標を平均化して取得
        gaze_data['x'] = (gaze_data_response['left_gaze_point_on_display_area'][0] +
                          gaze_data_response['right_gaze_point_on_display_area'][0]) / 2
        gaze_data['y'] = (gaze_data_response['left_gaze_point_on_display_area'][1] +
                          gaze_data_response['right_gaze_point_on_display_area'][1]) / 2
    # 瞬きの検出
    if gaze_data_response['left_eye_validity'] == 0 and gaze_data_response['right_eye_validity'] == 0:
        gaze_data['blink_count'] += 1

# 瞬きカウントをリセットするAPI
@app.route('/reset_blink_count')
def reset_blink_count():
    global gaze_data
    gaze_data['blink_count'] = 0
    return jsonify({'status': 'blink count reset'})

# 視線データを取得するAPI
@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)

@app.route('/')
def index():
    return render_template('index.html')  # index.htmlをテンプレートとしてレンダリング

if __name__ == '__main__':
    # 追跡をバックグラウンドで開始
    if eyetracker:
        tracking_thread = threading.Thread(target=lambda: eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True))
        tracking_thread.daemon = True
        tracking_thread.start()

    app.run(debug=True, port=8000)




   <!-- index.html -->
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eye Gesture Web Control</title>
    <style>
        body {
            height: 3000px;
            font-size: 18px;
            line-height: 1.6;
        }
        .scroll-zone {
            position: fixed;
            height: 100px;
            width: 100%;
            background-color: rgba(0, 0, 255, 0.2);
        }
        .scroll-zone.top {
            top: 0;
        }
        .scroll-zone.bottom {
            bottom: 0;
        }
        .page-zone {
            position: fixed;
            width: 30%;
            height: 100%;
            background-color: rgba(0, 255, 0, 0.2);
        }
        .page-zone.left {
            left: 0;
        }
        .page-zone.right {
            right: 0;
        }
        #gaze-indicator {
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: red;
            border-radius: 50%;
            pointer-events: none; /* ポインターイベントを無効にして、インジケータがマウス操作に干渉しないようにする */
        }
        #page-number {
            position: fixed;
            top: 10px;
            right: 10px;
            font-size: 24px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div class="scroll-zone top"></div>
<div class="scroll-zone bottom"></div>
<div class="page-zone left"></div>
<div class="page-zone right"></div>
<div id="gaze-indicator"></div>
<div id="page-number">Page: 1</div>

<!-- 大量の文章を表示 -->
<div>
    <h1>テスト文章</h1>
    <p>...（ここに大量の文章を追加）...</p>
</div>

<script>
    let blinkCount = 0;
    let fixationStartTime = null;
    let currentPage = 1;
    const gazeIndicator = document.getElementById('gaze-indicator');
    const pageNumberDisplay = document.getElementById('page-number');
    let lastPageChange = Date.now();
    const delayBetweenPages = 2000; // ページ移動の間隔を2秒に設定

    function getGazeData() {
        fetch('/gaze_data')
            .then(response => response.json())
            .then(data => {
                const x = data.x;
                const y = data.y;

                // ウィンドウサイズとマージンを考慮して視線位置を調整
                const screenX = x * window.innerWidth; // xの範囲が0〜1に基づく
                const screenY = y * window.innerHeight + window.scrollY; // yの範囲が0〜1に基づく

                // 視線ポインタの位置を設定
                gazeIndicator.style.left = screenX + 'px';
                gazeIndicator.style.top = screenY + 'px';

                // スクロール処理
                if (y < 0.3) {
                    window.scrollBy(0, -50); // 上にスクロール
                } else if (y > 0.7) {
                    window.scrollBy(0, 50); // 下にスクロール
                }

                // 注視または瞬きでのページ移動
                if (data.blink_count > blinkCount) {  // 瞬きが増加した場合
                    blinkCount = data.blink_count;
                    if (screenX < window.innerWidth * 0.3 && Date.now() - lastPageChange > delayBetweenPages) {
                        moveToPreviousPage(); // 左エリアでの瞬きで前のページへ
                        lastPageChange = Date.now();
                    } else if (screenX > window.innerWidth * 0.7 && Date.now() - lastPageChange > delayBetweenPages) {
                        moveToNextPage(); // 右エリアでの瞬きで次のページへ
                        lastPageChange = Date.now();
                    }
                } else if (screenX < window.innerWidth * 0.3) {
                    // 左側の領域に注視
                    if (!fixationStartTime) fixationStartTime = Date.now();
                    else if (Date.now() - fixationStartTime >= 500 && Date.now() - lastPageChange > delayBetweenPages) {
                        moveToPreviousPage();
                        lastPageChange = Date.now();
                    }
                } else if (screenX > window.innerWidth * 0.7) {
                    // 右側の領域に注視
                    if (!fixationStartTime) fixationStartTime = Date.now();
                    else if (Date.now() - fixationStartTime >= 500 && Date.now() - lastPageChange > delayBetweenPages) {
                        moveToNextPage();
                        lastPageChange = Date.now();
                    }
                } else {
                    fixationStartTime = null; // 中央に視線があるときはリセット
                }
            });
    }

    // ページ移動の関数
    function moveToNextPage() {
        currentPage++;
        updatePageNumber();
        console.log("次のページに移動しました");
    }

    function moveToPreviousPage() {
        if (currentPage > 1) {
            currentPage--;
            updatePageNumber();
            console.log("前のページに移動しました");
        }
    }

    function updatePageNumber() {
        pageNumberDisplay.textContent = "Page: " + currentPage;
    }

    // 300msごとに視線データを取得
    setInterval(getGazeData, 300);
</script>

</body>
</html> 