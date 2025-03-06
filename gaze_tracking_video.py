# OpenCVでの動画録画処理
def record_video():
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('output.avi', fourcc, 20.0, (640, 480))

    while True:
        # ウェブカメラやスクリーンキャプチャを取得して録画
        frame = np.zeros((480, 640, 3), dtype=np.uint8)  # ここで動画のフレームを取得します（サンプルとして黒い画面）
        if gaze_data:  # 視線データがある場合
            # 視線位置を表示（例: 青色で視線を示す）
            gaze_x = int(gaze_data['x'] * 640)  # X座標を640の幅に合わせてスケーリング
            gaze_y = int(gaze_data['y'] * 480)  # Y座標を480の高さに合わせてスケーリング
            cv2.circle(frame, (gaze_x, gaze_y), 10, (255, 0, 0), -1)  # 視線を青い円で描画
        
        out.write(frame)  # フレームを保存
        
        cv2.imshow('Recording', frame)  # 録画中の映像を表示
        if cv2.waitKey(1) & 0xFF == ord('q'):  # 'q'キーで終了
            break

    out.release()
    cv2.destroyAllWindows()

# 新たに録画スレッドを作成
record_thread = threading.Thread(target=record_video)
record_thread.daemon = True
record_thread.start()


