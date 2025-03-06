#~11/11　タイトル「」
# 　　　　視線でのオートスクロール、左から右に視線を移動させ、
# 　　　　中央を過ぎるとページが少しスクロールされる
#        midas touch problemの緩和のためのアイジェスチャによるクリック


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
            font-size: 18px;
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
        #prev-page {
            left: 30px;
        }
        #next-page {
            right: 30px;
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
<div id="prev-page" class="page-button">前のページ</div>
<div id="next-page" class="page-button">次のページ</div>
<div id="page-content">これはページのコンテンツです。
</div>
<div id="page-number">Page: 1</div>
<script>
    let blinkCount = 0;
    let lastBlinkCount = 0;
    let lastScrollTime = 0;
    let lastGazeX = 0;
    const scrollDelay = 300; // スクロールの間隔（ミリ秒）
    let currentPage = 1;
    const maxPage = 5;
    const gazeIndicator = document.getElementById('gaze-indicator');
    const pageContent = document.getElementById('page-content');
    const pageNumberDisplay = document.getElementById('page-number');

    // スクロールフラグ
    let hasScrolled = false;

    // ページの内容を更新
    function updatePageContent() {
        pageContent.textContent = `<div>
            <h1>テスト文章</h1>
            <p>ここはサンプルテキストです。このテキストは視線追跡によるスクロールテストのために用意されています。</p>
            <p>ここはサンプルテキストです。このテキストは視線追跡によるスクロールテストのために用意されています。</p>
    <p>視線が画面の中央付近に到達すると、スクロールが自動的に実行されます。これにより、手動でスクロールすることなく、視線の動きに合わせてページを読み進めることができます。</p>
    <p>日本には、四季折々の美しい風景があります。春には桜が満開になり、街中がピンク色に染まります。夏には青々とした山々や涼しい川のせせらぎを楽しむことができます。秋には紅葉が美しく、冬には雪景色が広がります。こうした季節の移ろいが、人々の心を豊かにし、生活に彩りを加えます。</p>
    <p>日本文化には多くの伝統的な行事や習慣があります。例えば、正月には神社に参拝して一年の健康と幸せを祈る「初詣」が行われます。また、夏には「お盆」という祖先を敬う行事があり、多くの人々が故郷に帰り家族と過ごします。こうした行事は、家族や友人との絆を深める大切な機会でもあります。</p>
    <p>現代の日本は、伝統と革新が共存しています。古くからの伝統を守りながらも、技術の発展により新しい文化が生まれています。例えば、和紙の製造技術は現代アートやインテリアデザインに取り入れられ、新たな価値が創出されています。また、茶道や華道といった伝統的な日本文化も、若い世代の間で再び注目されています。</p>
    <p>日本の食文化は世界中で愛されています。寿司や天ぷら、ラーメンなど、さまざまな料理があり、その味わいは多様です。また、四季折々の食材を大切にする日本の料理は、季節感を楽しむことができるため、多くの人々に支持されています。特に、海外でも人気の寿司は、日本の食文化を象徴する料理として知られています。</p>
    <p>テクノロジー分野でも、日本は世界に誇る技術力を持っています。ロボット技術や自動車産業、エレクトロニクスなど、多くの分野で革新を続けています。これらの技術は、国内外で広く利用され、人々の生活を豊かにしています。未来の日本がどのように進化していくのか、非常に興味深いです。</p>
    <p>日本の観光地には、歴史的な名所や美しい自然がたくさんあります。京都や奈良には、千年以上の歴史を持つ寺院や神社があり、訪れる人々を魅了しています。また、富士山や北海道の美しい自然も多くの観光客に愛されています。日本を訪れる際には、こうした場所で日本の歴史や自然を感じることができます。</p>
    <p>ここまでお読みいただきありがとうございます。この文章は、視線追跡技術を利用したスクロールテストのためのサンプルです。続けて読んでいただき、視線が画面右端に達するごとにスクロールが行われることをお楽しみください。</p>
    <p>日本には、四季折々の美しい風景があります。春には桜が満開になり、街中がピンク色に染まります。夏には青々とした山々や涼しい川のせせらぎを楽しむことができます。秋には紅葉が美しく、冬には雪景色が広がります。こうした季節の移ろいが、人々の心を豊かにし、生活に彩りを加えます。</p>
    <p>日本文化には多くの伝統的な行事や習慣があります。例えば、正月には神社に参拝して一年の健康と幸せを祈る「初詣」が行われます。また、夏には「お盆」という祖先を敬う行事があり、多くの人々が故郷に帰り家族と過ごします。こうした行事は、家族や友人との絆を深める大切な機会でもあります。</p>
    <p>現代の日本は、伝統と革新が共存しています。古くからの伝統を守りながらも、技術の発展により新しい文化が生まれています。例えば、和紙の製造技術は現代アートやインテリアデザインに取り入れられ、新たな価値が創出されています。また、茶道や華道といった伝統的な日本文化も、若い世代の間で再び注目されています。</p>
    <p>日本の食文化は世界中で愛されています。寿司や天ぷら、ラーメンなど、さまざまな料理があり、その味わいは多様です。また、四季折々の食材を大切にする日本の料理は、季節感を楽しむことができるため、多くの人々に支持されています。特に、海外でも人気の寿司は、日本の食文化を象徴する料理として知られています。</p>
    <p>テクノロジー分野でも、日本は世界に誇る技術力を持っています。ロボット技術や自動車産業、エレクトロニクスなど、多くの分野で革新を続けています。これらの技術は、国内外で広く利用され、人々の生活を豊かにしています。未来の日本がどのように進化していくのか、非常に興味深いです。</p>
    <p>日本の観光地には、歴史的な名所や美しい自然がたくさんあります。京都や奈良には、千年以上の歴史を持つ寺院や神社があり、訪れる人々を魅了しています。また、富士山や北海道の美しい自然も多くの観光客に愛されています。日本を訪れる際には、こうした場所で日本の歴史や自然を感じることができます。</p>
    <p>ここまでお読みいただきありがとうございます。この文章は、視線追跡技術を利用したスクロールテストのためのサンプルです。続けて読んでいただき、視線が画面右端に達するごとにスクロールが行われることをお楽しみください。</p>
        <p>日本の観光地には、歴史的な名所や美しい自然がたくさんあります。京都や奈良には、千年以上の歴史を持つ寺院や神社があり、訪れる人々を魅了しています。また、富士山や北海道の美しい自然も多くの観光客に愛されています。日本を訪れる際には、こうした場所で日本の歴史や自然を感じることができます。</p>
    <p>ここまでお読みいただきありがとうございます。この文章は、視線追跡技術を利用したスクロールテストのためのサンプルです。続けて読んでいただき、視線が画面右端に達するごとにスクロールが行われることをお楽しみください。</p>
    <p>日本には、四季折々の美しい風景があります。春には桜が満開になり、街中がピンク色に染まります。夏には青々とした山々や涼しい川のせせらぎを楽しむことができます。秋には紅葉が美しく、冬には雪景色が広がります。こうした季節の移ろいが、人々の心を豊かにし、生活に彩りを加えます。</p>
    <p>日本文化には多くの伝統的な行事や習慣があります。例えば、正月には神社に参拝して一年の健康と幸せを祈る「初詣」が行われます。また、夏には「お盆」という祖先を敬う行事があり、多くの人々が故郷に帰り家族と過ごします。こうした行事は、家族や友人との絆を深める大切な機会でもあります。</p>
    <p>現代の日本は、伝統と革新が共存しています。古くからの伝統を守りながらも、技術の発展により新しい文化が生まれています。例えば、和紙の製造技術は現代アートやインテリアデザインに取り入れられ、新たな価値が創出されています。また、茶道や華道といった伝統的な日本文化も、若い世代の間で再び注目されています。</p>
    <p>日本の食文化は世界中で愛されています。寿司や天ぷら、ラーメンなど、さまざまな料理があり、その味わいは多様です。また、四季折々の食材を大切にする日本の料理は、季節感を楽しむことができるため、多くの人々に支持されています。特に、海外でも人気の寿司は、日本の食文化を象徴する料理として知られています。</p>
    <p>テクノロジー分野でも、日本は世界に誇る技術力を持っています。ロボット技術や自動車産業、エレクトロニクスなど、多くの分野で革新を続けています。これらの技術は、国内外で広く利用され、人々の生活を豊かにしています。未来の日本がどのように進化していくのか、非常に興味深いです。</p>
    <p>日本の観光地には、歴史的な名所や美しい自然がたくさんあります。京都や奈良には、千年以上の歴史を持つ寺院や神社があり、訪れる人々を魅了しています。また、富士山や北海道の美しい自然も多くの観光客に愛されています。日本を訪れる際には、こうした場所で日本の歴史や自然を感じることができます。</p>
    <p>ここまでお読みいただきありがとうございます。この文章は、視線追跡技術を利用したスクロールテストのためのサンプルです。続けて読んでいただき、視線が画面右端に達するごとにスクロールが行われることをお楽しみください。</p>
        <p>日本の観光地には、歴史的な名所や美しい自然がたくさんあります。京都や奈良には、千年以上の歴史を持つ寺院や神社があり、訪れる人々を魅了しています。また、富士山や北海道の美しい自然も多くの観光客に愛されています。日本を訪れる際には、こうした場所で日本の歴史や自然を感じることができます。</p>
    <p>ここまでお読みいただきありがとうございます。この文章は、視線追跡技術を利用したスクロールテストのためのサンプルです。続けて読んでいただき、視線が画面右端に達するごとにスクロールが行われることをお楽しみください。</p>
    <p>日本には、四季折々の美しい風景があります。春には桜が満開になり、街中がピンク色に染まります。夏には青々とした山々や涼しい川のせせらぎを楽しむことができます。秋には紅葉が美しく、冬には雪景色が広がります。こうした季節の移ろいが、人々の心を豊かにし、生活に彩りを加えます。</p>
    <p>日本文化には多くの伝統的な行事や習慣があります。例えば、正月には神社に参拝して一年の健康と幸せを祈る「初詣」が行われます。また、夏には「お盆」という祖先を敬う行事があり、多くの人々が故郷に帰り家族と過ごします。こうした行事は、家族や友人との絆を深める大切な機会でもあります。</p>
    <p>現代の日本は、伝統と革新が共存しています。古くからの伝統を守りながらも、技術の発展により新しい文化が生まれています。例えば、和紙の製造技術は現代アートやインテリアデザインに取り入れられ、新たな価値が創出されています。また、茶道や華道といった伝統的な日本文化も、若い世代の間で再び注目されています。</p>
    <p>日本の食文化は世界中で愛されています。寿司や天ぷら、ラーメンなど、さまざまな料理があり、その味わいは多様です。また、四季折々の食材を大切にする日本の料理は、季節感を楽しむことができるため、多くの人々に支持されています。特に、海外でも人気の寿司は、日本の食文化を象徴する料理として知られています。</p>
    <p>テクノロジー分野でも、日本は世界に誇る技術力を持っています。ロボット技術や自動車産業、エレクトロニクスなど、多くの分野で革新を続けています。これらの技術は、国内外で広く利用され、人々の生活を豊かにしています。未来の日本がどのように進化していくのか、非常に興味深いです。</p>
    <p>日本の観光地には、歴史的な名所や美しい自然がたくさんあります。京都や奈良には、千年以上の歴史を持つ寺院や神社があり、訪れる人々を魅了しています。また、富士山や北海道の美しい自然も多くの観光客に愛されています。日本を訪れる際には、こうした場所で日本の歴史や自然を感じることができます。</p>
    <p>ここまでお読みいただきありがとうございます。この文章は、視線追跡技術を利用したスクロールテストのためのサンプルです。続けて読んでいただき、視線が画面右端に達するごとにスクロールが行われることをお楽しみください。</p>
        </div>`;
        pageNumberDisplay.textContent = `Page: ${currentPage}`;
    }

    // ページ移動
    function moveToNextPage() {
        if (currentPage < maxPage) {
            currentPage++;
            window.scrollTo(0, 0);  // 新しいページの先頭に移動
            updatePageContent();
        }
    }

    function moveToPreviousPage() {
        if (currentPage > 1) {
            currentPage--;
            window.scrollTo(0, 0);  // 新しいページの先頭に移動
            updatePageContent();
        }
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
                blinkCount = data.blink_count;

                // 視線位置を画面上の座標に変換
                const screenX = x * window.innerWidth;
                const screenY = y * window.innerHeight + window.scrollY;

                // 視線インジケータの位置を更新
                gazeIndicator.style.left = screenX + 'px';
                gazeIndicator.style.top = screenY + 'px';

                const currentTime = Date.now();

                // 中央付近を通過した場合に一度だけスクロール
                if (x > 0.6 && !hasScrolled && lastGazeX < x && currentTime - lastScrollTime > scrollDelay) {
                    window.scrollBy(0, 100); // 下に100pxスクロール
                    hasScrolled = true; // スクロール済みフラグを立てる
                    lastScrollTime = currentTime;
                } else if (x < 0.4) { // 左に戻ったらスクロールフラグをリセット
                    hasScrolled = false;
                }

                lastGazeX = x; // 前回の視線X位置を更新

                // ウィンクによるページ移動
                if (blinkCount > lastBlinkCount) { // ウィンクが検出された場合
                    if (screenX < window.innerWidth * 0.3) {
                        moveToPreviousPage(); // 左上でウィンクした場合
                    } else if (screenX > window.innerWidth * 0.7) {
                        moveToNextPage(); // 右上でウィンクした場合
                    }
                    lastBlinkCount = blinkCount; // 最新の瞬きカウントを記録
                }
            })
            .catch(error => console.error("視線データの取得に失敗しました:", error));
    }

    // 300msごとに視線データを取得
    setInterval(getGazeData, 300);
</script>

</body>
</html>