from flask import Flask, jsonify, render_template
import tobii_research as tr
import threading

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
        gaze_data['x'] = (gaze_data_response['left_gaze_point_on_display_area'][0] +
                          gaze_data_response['right_gaze_point_on_display_area'][0]) / 2
        gaze_data['y'] = (gaze_data_response['left_gaze_point_on_display_area'][1] +
                          gaze_data_response['right_gaze_point_on_display_area'][1]) / 2
        print(f"視線座標 - X: {gaze_data['x']}, Y: {gaze_data['y']}")  # デバッグ出力

    if gaze_data_response['left_eye_validity'] == 0 and gaze_data_response['right_eye_validity'] == 0:
        gaze_data['blink_count'] += 1

# 視線データを取得するAPI
@app.route('/gaze_data')
def get_gaze_data():
    return jsonify(gaze_data)

# メインページ
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    if eyetracker:
        tracking_thread = threading.Thread(target=lambda: eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True))
        tracking_thread.daemon = True
        tracking_thread.start()

    app.run(debug=True, port=5000)



<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>視線追跡ページナビゲーション</title>
    <style>
        body {
            height: 2000px;  /* 各ページをスクロール可能にするための高さ */
            font-size: 32px;
            line-height: 1.6;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-direction: column;
        }
        #gaze-indicator {
            position: absolute;
            width: 20px;
            height: 20px;
            background-color: red;
            border-radius: 50%;
            pointer-events: none;
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
            font-size: 24px;
        }
        #page-number {
            position: fixed;
            bottom: 10px;
            font-size: 24px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div id="gaze-indicator"></div>
<div id="page-content">
</div>
<script>
    let lastScrollTime = 0;
    let lastGazeX = 0;
    const scrollDelay = 300; // スクロールの間隔（ミリ秒）
    const maxPage = 5;
    const gazeIndicator = document.getElementById('gaze-indicator');
    const pageContent = document.getElementById('page-content');
    const pageNumberDisplay = document.getElementById('page-number');

    // スクロールフラグ
    let hasScrolled = false;

    // ページの内容を更新
    function updatePageContent() {
        pageContent.textContent = `
            人々が普段通りの生活の中で、臨時として町の中心に現れた不思議な箱。 それは大きさや形が一定ではなく、目を凝らすと箱自体がまるで人間の顔のように見えることもあった箱には「誰でも願いを叶えます」と書かれた小さなプレートが貼られているだけで、周囲に説明書やその他の情報は一切なかった。

最初は近づかなかった。人々は不安と疑念を抱きながら、その箱が何かの装置や装飾であると考えていた。

その箱の前に立ち、手を合わせと、願いが叶うという噂が広がり始めたのだ。 最初に願いをたの試みは、町の小さな商店を営む田中さんだった。

田中さんは家族が病気で困っています、治療費を稼ぐために商売を続けるのが難しかったです。そんなとき、町の噂を聞きつけ、「試しに一度期待してみよう」と思いました。

「もし、あなたが本当に願いを叶えてくれるなら、うちの妻が元気になりますように。」 田中さんは静かに箱に向かってそう言った。

すると、箱はゆっくりと反応を示し、金属的な音を立てながら一瞬で光り輝き、田中さんの願いがかなった。のだ。

これを見た町の人々は驚き、すぐに自分たちの願いを叶えてもらえるよう、今度と箱の前に並んだ。来た。

「もし、願いが叶う代わりに何か代償があるのではないか？」という疑念が生まれたのだ。

最初にそのことに気づいたのは、町で唯一の教師である石井さんだった。

「私は、町の教育を良くしたい。」 石井さんは静かに願った。 「この町に素晴らしい教育を提供できるような施設が欲しい。」

その願いを叶えた瞬間、箱がまた光り輝き、石井さんは長くなった。数週間後、町に素晴らしい学校ができて、子供達の新しい教室で学び始めた。

しかし、そこには不自然な空気が漂っていた。 新しい学校ができることで、町の他の施設がだんだん使われなくなり、町の景観が変わっていた。が何かを変える度に、他のものが失われていくような感覚があったのだ。

最も大きな問題は、箱が「願いを叶える」ことに対して、その反動を隠している点だった。 最初に金持ちになった者は、かなり自分の人間関係が不安定で、孤立してしまった病気が治った人は、後にある精神問題を驚くようになり、治療を受けることが多かった。

そして、箱の前に並んだ最後の人物は、町議員であった佐藤さんだった。

「私はこの町を豊かにしたい。箱、あなたに願う。私に最高の権限を与えて、この町を素晴らしい場所に変えてみよう。」佐藤さんは強い決意を持って言った。

箱はしばらく沈黙した後、暴力その願いを受け入れた。 しかし、翌日から町は不穏な空気に包まれ、すぐに佐藤さんが町のトップとして君臨するようになった。 彼は次第に権力を使って周囲を支配し、町が自由に少しずつ奪われていった。

町の人々は次第に気づき始めた。箱の願いは、表面上は叶えられるが、それに伴う代償は見えない形で積み重なってゆく。誰かの幸福が他の誰かの不幸に変わり、願いを叶えるためには何かが失われる。


「こんなにたくさんのものが変わったのに、幸せを感じられる人間は一人として誰もいない…。」

その言葉がきっかけとなり、町の人々はついに箱の本当の意味を理解した。 願いを叶えることは、幸福を実現するものではない。

そして、町の人々は箱の前に立つことをやめ、その箱を恐る恐る奥に据えた。願いが叶うことが本当に必要なのか、ということを考える時間をかけて町全体に訪れた。

箱はもう、誰の目にも見えない場所に眠り続けることになった。 でも、誰もその存在を忘れることはなかった。 願いを叶える力を持つ箱、その力が本当に必要かどうかをそれが、この町に残された、唯一の予告となったのだ。
            `;
    }
    // 初回のページ内容を表示
    updatePageContent();

    // サーバーから視線データを取得し、スクロールやページ移動を制御
    function getGazeData() {
        fetch('/gaze_data')
            .then(response => response.json())
            .then(data => {
                const x = data.x;
                const y = data.y;

                // 視線位置を画面上の座標に変換
                const screenX = x * window.innerWidth;
                const screenY = y * window.innerHeight + window.scrollY;

                // 視線インジケータの位置を更新
                gazeIndicator.style.left = screenX + 'px';
                gazeIndicator.style.top = screenY + 'px';

                const currentTime = Date.now();

                // 中央付近を通過した場合に一度だけスクロール
                if (x > 0.9 && !hasScrolled && lastGazeX < x && currentTime - lastScrollTime > scrollDelay) {
                    window.scrollBy(0, 32); // 下に100pxスクロール
                    hasScrolled = true; // スクロール済みフラグを立てる
                    lastScrollTime = currentTime;
                } else if (x < 0.4) { // 左に戻ったらスクロールフラグをリセット
                    hasScrolled = false;
                }

                lastGazeX = x; // 前回の視線X位置を更新

               
            })
            .catch(error => console.error("視線データの取得に失敗しました:", error));
    }

    // 300msごとに視線データを取得
    setInterval(getGazeData, 100);
</script>

</body>
</html>
