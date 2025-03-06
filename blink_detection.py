import sys
import tobii_research as tr
import time
from flask import Flask, render_template
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

eyetrackers = tr.find_all_eyetrackers()
if len(eyetrackers) >= 1:
    eyetracker = eyetrackers[0]
else:
    print("Error: Not Found EyeTracker")
    sys.exit()

wink_counter = 0
blink_counter = 0
last_blink_state = False  # 瞬きの前回の状態

@app.route('/')
def index():
    return render_template('index.html')

def MyCallBack(gaze_data):
    global wink_counter, blink_counter, last_blink_state
    left_point = gaze_data.left_eye.gaze_point.position_on_display_area
    right_point = gaze_data.right_eye.gaze_point.position_on_display_area

    # ウインクの検出
    if str(left_point[0]) == 'nan' or str(right_point[0]) == 'nan':
        wink_counter += 1
        print("Wink detected")
        socketio.emit('change_color', {'color': 'blue'})  # ウインク時に青色に変更
        
        # 色を元に戻す処理を新しいスレッドで実行
        socketio.start_background_task(change_color_back)

def change_color_back():
    time.sleep(0.5)  # 0.5秒待機
    socketio.emit('change_color', {'color': 'black'})  # 背景色を黒に戻す

eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, MyCallBack, as_dictionary=False)

if __name__ == '__main__':
    try:
        socketio.run(app, host='127.0.0.1', port=9000)  # ポート9000でFlaskを起動
    except KeyboardInterrupt:
        eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, MyCallBack)




<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gaze Control</title>
    <style>
        body {
            background-color: black; /* 初期背景色を黒に設定 */
            color: white; /* テキスト色を白に設定 */
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            font-size: 2em;
        }
    </style>
</head>
<body>
    <div id="message">Gaze Control Page</div>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script>
        var socket = io.connect('http://127.0.0.1:9000');
        socket.on('change_color', function(data) {
            document.body.style.backgroundColor = data.color; // 背景色を変更
        });
    </script>
</body>
</html>