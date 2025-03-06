#app.py 視線解析(未完成)

from flask import Flask, jsonify, render_template
import random

app = Flask(__name__)

# モックデータを提供するためのエンドポイント
@app.route('/gaze_data')
def gaze_data():
    # ランダムな視線データを生成
    gaze_x = round(random.uniform(0.0, 1.0), 2)
    gaze_y = round(random.uniform(0.0, 1.0), 2)
    return jsonify({'x': gaze_x, 'y': gaze_y})

# HTMLページを提供
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=3000)






#HTML

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>視線スクロールと解析システム</title>
    <style>
        body {
            font-size: 18px;
            line-height: 1.6;
            width: 60%;
            margin: 0 auto;
            position: relative;
        }
        .placeholder {
            height: 800px;
        }
        #gaze-pointer {
            position: absolute;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background-color: red;
            pointer-events: none;
        }
        #analysis-results {
            position: fixed;
            top: 10px;
            left: 10px;
            background-color: rgba(255, 255, 255, 0.8);
            padding: 10px;
            border-radius: 5px;
            z-index: 10;
        }
    </style>
</head>
<body>
    <h1>視線スクロールと解析システム</h1>
    <p>視線でページをスクロールしながら、目の動きや位置のずれを解析します。</p>
    <div class="placeholder"></div>
    <p>人々が普段通りの生活を送る中、突如として町の中心に現れた不思議な箱。それは大きさや形が一定ではなく、目を凝らすと箱自体がまるで人間の顔のように見えることもあった。箱には「誰でも願いを叶えます」と書かれた小さなプレートが貼られているだけで、周囲に説明書やその他の情報は一切なかった。

        最初は誰も近づかなかった。人々は不安と疑念を抱きながら、その箱が何かの装置や装飾であると考えていた。だが、時間が経つにつれ、次第に興味を持つ者が現れ始めた。
        
        その箱の前に立ち、手を合わせると、願いが叶うという噂が広がり始めたのだ。最初に願いを試みたのは、町の小さな商店を営む田中さんだった。
        
        田中さんは家族が病気で困っており、治療費を払うために商売を続けるのが難しくなっていた。そんなとき、町の噂を聞きつけ、「試しに一度願ってみよう」と思ったのだ。
        
        「もし、あなたが本当に願いを叶えてくれるのなら、うちの妻が元気になりますように。」田中さんは静かに箱に向かってそう言った。
        
        すると、箱はゆっくりと反応を示し、金属的な音を立てながら一瞬で光り輝き、田中さんの願いがかなった。帰宅すると、妻は元気を取り戻し、病院での診断も「治癒」と言われたのだ。
        
        これを見た町の人々は驚き、すぐに自分たちの願いを叶えてもらうべく、次々と箱の前に並んだ。だが、少し経つと、一部の人々の中に次第に不安の色が広がってきた。
        
        「もし、願いが叶う代わりに何か代償があるのではないか？」という疑念が生まれたのだ。
        
        最初にそのことに気づいたのは、町で唯一の教師である石井さんだった。石井さんは箱の前に立ち、慎重にその願いを考えていた。
        
        「私は、町の教育を良くしたい。」石井さんは静かに願った。「この町に素晴らしい教育を提供できるような施設が欲しい。」
        
        その願いを叶えた瞬間、箱がまた光り輝き、石井さんは目を見張った。数週間後、町に立派な学校ができ、子供たちは新しい教室で学び始めた。
        
        しかし、そこには不自然な空気が漂っていた。新しい学校ができることで、町の他の施設が次第に使われなくなり、町の景観が変わっていった。最初は誰も気づかなかったが、箱が何かを変える度に、他のものが失われていくような感覚が広がったのだ。
        
        最も大きな問題は、箱が「願いを叶える」ことに対して、その反動を隠している点だった。最初に金持ちになった者は、急激に自分の人間関係が崩れ、孤立してしまった。病気が治った者は、後に精神的な問題を抱えるようになり、治療を受けることが増えた。
        
        そして、箱の前に並んだ最後の人物は、町の議員であった佐藤さんだった。
        
        「私はこの町を豊かにしたい。箱、あなたに願う。私に最高の権力を与えて、この町を素晴らしい場所に変えてみせる。」佐藤さんは強い決意を持って言った。
        
        箱はしばらく沈黙した後、やがてその願いを受け入れた。だが、翌日から町は不穏な空気に包まれ、すぐに佐藤さんが町のトップとして君臨するようになった。彼は次第に権力を使って周囲を支配し、町の自由が徐々に奪われていった。
        
        町の人々は次第に気づき始めた。箱の願いは、表面上は叶えられるが、それに伴う代償は見えない形で積み重なっていく。誰かの幸福が他の誰かの不幸に変わり、願いを叶えるためには何かが失われる。
        
        ある日、箱の前に立った田中さんがつぶやいた。
        「こんなに多くのものが変わったのに、幸せを感じられる人間は誰一人としていない…。」
        
        その言葉がきっかけとなり、町の人々はついに箱の本当の意味を理解した。願いを叶えることは、必ずしも幸福をもたらすものではない。時には、過剰な欲望が破壊を招くことがあるのだ。
        
        そして、町の人々は箱の前に立つことをやめ、その箱を町外れの山奥に埋めた。願いが叶うことが本当に必要なのか、ということを考える時間が町全体に訪れた。
        
        箱はもう、誰の目にも見えない場所に眠り続けることになった。しかし、誰もがその存在を忘れることはなかった。願いを叶える力を持つ箱、その力が本当に必要かどうかを考えること。それが、この町に残された、唯一の教訓となったのだ。</p>
    <div class="placeholder"></div>

    <!-- 視線位置を示す赤い円 -->
    <div id="gaze-pointer"></div>

    <!-- 解析結果を表示 -->
    <div id="analysis-results">
        <p>スクロール前後のずれ: <span id="gaze-shift"></span></p>
        <p>速度: <span id="gaze-speed"></span> pixels/sec</p>
        <p>方向: <span id="gaze-angle"></span> 度</p>
    </div>

    <script>
        let lastGazeX = 0;
        let lastGazeY = 0;
        let hasScrolled = false;
        let gazeHistory = []; // 視線位置の履歴を保存
        let scrollHistory = []; // スクロール時の位置データを保存
        const gazePointer = document.getElementById('gaze-pointer');

        // 視線データを取得
        function getGazeData() {
            fetch('/gaze_data')
                .then(response => response.json())
                .then(data => {
                    const x = data.x;
                    const y = data.y; // Y座標も取得
                    const currentTime = Date.now();

                    // 視線位置を履歴に記録
                    gazeHistory.push({ x, y, time: currentTime });

                    // 視線の位置を赤円で表示
                    gazePointer.style.left = `${x * window.innerWidth - gazePointer.offsetWidth / 2}px`;
                    gazePointer.style.top = `${y * window.innerHeight - gazePointer.offsetHeight / 2}px`;

                    // スクロール操作
                    if (x > 0.9 && !hasScrolled && lastGazeX < x) {
                        window.scrollBy(0, 32);
                        hasScrolled = true;

                        // スクロール後の視線位置を記録
                        scrollHistory.push({
                            preScroll: { x: lastGazeX, y: y },
                            postScroll: { x, y },
                            time: currentTime,
                        });
                    } else if (x < 0.4) {
                        hasScrolled = false;
                    }

                    lastGazeX = x;
                    lastGazeY = y;
                })
                .catch(error => console.error("視線データ取得エラー:", error));
        }

        // 視線のずれ幅を計算
        function calculateGazeShift() {
            scrollHistory.forEach(scroll => {
                const dx = Math.abs(scroll.preScroll.x - scroll.postScroll.x);
                const dy = Math.abs(scroll.preScroll.y - scroll.postScroll.y);
                document.getElementById('gaze-shift').innerText = `dx=${dx.toFixed(2)}, dy=${dy.toFixed(2)}`;
            });
        }

        // 視線の動き解析
        function analyzeEyeMovement() {
            if (gazeHistory.length > 1) {
                for (let i = 1; i < gazeHistory.length; i++) {
                    const prev = gazeHistory[i - 1];
                    const curr = gazeHistory[i];
                    const timeDelta = (curr.time - prev.time) / 1000; // 秒単位
                    const dx = curr.x - prev.x;
                    const dy = curr.y - prev.y;

                    // 速度 (pixels/second)
                    const speed = Math.sqrt(dx * dx + dy * dy) / timeDelta;

                    // 方向 (角度)
                    const angle = Math.atan2(dy, dx) * (180 / Math.PI);

                    // 表示
                    document.getElementById('gaze-speed').innerText = speed.toFixed(2);
                    document.getElementById('gaze-angle').innerText = angle.toFixed(2);
                }
            }
        }

        // 定期的に視線データを取得と解析
        setInterval(getGazeData, 100);
        setInterval(calculateGazeShift, 5000);
        setInterval(analyzeEyeMovement, 5000);
    </script>
</body>
</html>

