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












<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>視線追跡スクロール</title>
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
        #page-content {
            text-align: center;
            margin-top: 100px;
            font-size: 24px;
        }
        #page-number {
            position: fixed;
            bottom: 10px;
            font-size: 32px;
            font-weight: bold;
        }
    </style>
</head>
<body>

<div id="page-content">これはページのコンテンツです。
    <p>石柱の陰に身を潜めて、依頼人のルイス・イダルゴ聴罪司祭に目を走らせると、すでにそこらのワイン樽と同じように、全身穴だらけになっていた。
        その虚ろな目には、もはやなにも映っていない。石畳の床にほとばしるワインが、司祭の血を洗い流していく。
        こうなると分かっていたから、私は彼を帯同したくなかったのだ。
        ルイス・イダルゴは聞かなかった。処女をたぶらかしたという汚名を、どうしても己の手でそそぎたいと強く主張した。
        私になにができるだろう。忠告はした。それでもなお、ついて来ると言い張るのなら、私にはどうすることもできない。
        自由身分を獲得した私のようなフリー・マニピュレイテッドは、自分の寿命を縮めかねない命令を拒むことができる。
        しかし、依頼人の決意を邪魔立てすることはできない。ルイス・イダルゴが危険を承知で、どうしても悪魔祓いに同行すると言うのなら、私としては拒むことはできない。
        彼が縮めることになるのは彼自身の寿命であり、私のではないからだ。私たちの寿命と、彼の寿命は違う。私たちの寿命は、耐用年数と言い換えることができる。
        が、今はそんなことを考えている場合ではない。私は石壁に背を押しつけて、ピチャ、ピチャ、と迫りくる足音に耳を澄ませた。
        ガブリエラ・デ・ラ・エレーラに取り憑いていた夢魔が、地下室の床を浸したワインを蹴散らしながら、ゆっくりと近づいてきていた。
        「ロリンズ！！」どう説明したらいいのか分からない低くて異様な声で、インキュバスが居丈高に呼ばわった。「出てこい、ユマ・ロリンズ！！」
        敢えて言うなら、獅子の咆哮と、蠅の翅音と、ガラスをひっかく音が混じり合ったような声だ。私のイメージセンサーには、そのような音声サンプルのストックはない。
        地下の酒蔵には、年代物のワイン樽が、幾列にもわたって棚に並んでいる。あちこちの樽から、血のように赤い酒が幾筋も噴出していた。ガブリエラ・デ・ラ・エレーラの家は、街でも有数の酒屋なのだ。
        三カ月前、十六歳の彼女は夜中に突然苦しみだした。家の者たちが心配していると、ガブリエラは彼女の聴罪司祭、つまりルイス・イダルゴの名を切ない声で呼びながら、口にするのも憚られるほど艶めかしく若い肉体をよじったという。
        うら若い娘のふしだらなふるまいほど、家名に泥を塗るものはない。以来、ガブリエラはこの地下の酒蔵に閉じ込められ、家族はルイス・イダルゴの悪行を異端審問所に訴え出た。聴罪にかこつけて、生娘を手籠めにするような生臭司祭は、悪魔の手先に違いないからだ。
        医師の見立てによれば、ガブリエラ・デ・ラ・エレーラはたしかにすでに処女ではなかった。しかし、彼女の小水を混ぜたデビルズ・カットでインキュバスをおびき出せたということは、少なくともガブリエラは人によって処女を奪われたわけではないことを意味する。
        この一事をもってして、ルイス・イダルゴは身の潔白が証明されたも同然だ。なぜなら、彼は血と肉を持った、れっきとした人間なのだから。だからルイス・イダルゴは、私とアグリの悪魔狩りに同行する必要など、まったくなかったのだ。
        そのアグリはといえば、私の外套のなかで、珍しくおとなしくしている。今のところは、という意味だが。
        いずれにせよ、信者にふしだらな行為をしたとして、ルイス・イダルゴを職務濫用の廉で教会から追放する決定を下した自由都市サン・ハドクの異端審問委員会は、いずれその決定を取り下げることになるだろう。
        だが、もう遅い。いまさら名誉を回復してもらったところで、死人が生き返るわけではない。破壊された樽からあふれ出たワインが、倒れ伏した哀れな聴罪司祭の黒い法衣を濡らしていた。
        「お前はオレをおびき出したと思ってるな、ロリンズ？」インキュバスの笑い声が地下室にした。「違うぞ。このオレがお前をおびき出したんだ」
        そうだろう。さもなければ、こいつが私の名を知るわけがない。
        「あの女に取り憑けば」と、得意げに続けた。「そのうちお前が現れると思っていた」
        「ずいぶん、やることが地味ですね」私は柱の陰から叫び返した。「ルキフェルの鎖を壊すために人間を一人一人堕落させるなんて、気が遠くなるような話だとは思いませんか」
        「堕落は伝染する」やつはまた、ひとしきり笑った。「一人の女を堕落させれば、十人の男が堕落する。十人の男が堕落すれば、百人の女が堕落する。百人の女が堕落すれば、千人の男が堕落する」
        「そして、お前たちの仲間はいたるところにいる、というわけですね」
        「そのとおりだ」
        私は斃れた司祭に目を走らせた。その体には、無数の黒い釘が突き刺さっている。
        かく言う私も左の腕がもげ、右目をやられていた。
        私は外套の上からアグリを揺さぶり、拳銃を握り締めて、柱の陰から飛び出す。
        インキュバスが、サッと手洟をかんだ。毛むくじゃらの黒い手で片方の鼻の孔をふさぎ、フンッ、と強く息を吐く。つぶれたその鼻孔から、釘が弾丸のように飛び出す。
        が、その釘が捉えたのは私の残像だけで、破壊したのはワイン樽だけだった。
        ガコンッ！！という音とともに、樽に新しい穴が開き、中身のワインが噴き出す。
        私はインキュバスに向けて、銃弾を二発放った。一発は胸の真ん中に、もう一発は眉間に命中したが、いずれもやつにかすり傷ひとつ負わせられなかった。やはり、通常弾では歯が立たない。
        樽棚の陰に飛び込む前に、ほんの一瞬ではあったが、初めてやつの全身を目の当たりにした。
        さほど大きくないその体は、黒い毛にびっしりと覆われ、ネズミのような長い尻尾があった。顔は蝙蝠にそっくりで、違うところといえば双眸が赤く、瞳孔が羊の目のように横に広がっていることだった。
        つまり、こいつの視界は左右に広いが、上下はさほどでもない。
        瞳の形は、ある程度その悪魔の類型を規定する。動物と同じだ。草食動物の左右に長い瞳孔は、視界を広げ、捕食者を発見しやすくする。逆に肉食獣の上下に長い瞳孔は、狭い範囲のなかで獲物の動きを的確に捉えるためだ。
        「守備タイプだね」外套のボタンの隙間から、アグリが顔を覗かせた。「横に動くのは不利だよ」
        「分かっています」
        私は相棒を外套のなかにギュッと押し込み、飛び散るワインを浴びながら、樽棚にはさまれた通路を走った。
        ハックション！！
        黒い釘が追いかけてくる。そのうちの一本に、またしても肩を刺し貫かれた。
        「……ッ！！」
        やつが樽の上に跳び上がり、私は素早く樽棚の下に滑り込む。
        盛大なくしゃみが、耳朶を打つ。
        フランスから取り寄せた高価なワイン樽が、木端微塵になった。愛好家たちがこれを見たら、地団駄を踏んでくやしがるだろう。
        案の定、インキュバスは私たちを見失ったようだった。こいつは釘を飛ばすしか能がない。樽の上を歩きまわるやつの荒い鼻息を聞きながら、私はそう断じた。つまり、下級の悪魔だ。
        「アグリッパを渡せ、ロリンズ」
        「ボクのことを言ってるよ……ちくしょう、呼び捨てにしやがって」
        「必要なときは呼びますから」ケンカ腰で外套から出てこようとするアグリを、私はふたたび押し戻した。「おとなしくしててください」
        天井からぶら下がった角灯が揺れるたびに、インキュバスの禍々しい影が伸びたり、縮んだりした。
        「アグリッパはどこだ、ロリンズ？」インキュバスが呼ばわる。「お前はマニピュレイテッドだろ？　マニーのお前があんなものを持ってたってしようがあるまい」
        「あんなろくでもない本はもう燃やしてしまいましたよ」
        私がそう切り返すと、懐のなかでアグリが腹を立てて暴れた。なにかわめいたようだが、よく聞き取れない。だから、外套の胸を少しだけ開いてやった。
        「いつまで遊んでるんだよ、ユマ」アグリが顔を出して文句を言った。「あんな雑魚、さっさとやっちまいなよ。今日はシオリが新曲を歌うんだよ。早くうちに帰ってテレビを観ないと」
        アグリの声をかき消したのは、空気を吸い込むような音だった。
        私がアグリを懐に押し込むのと、インキュバスがまたくしゃみをするのと、ほとんど同時だった。
        ハックション！！
        その拍子に、やつの口から鼻から、黒い釘が四方八方に飛び出す。釘は私が先ほどまで身を隠していた石柱を削り取り、丸天井に突き刺さり、すでに蜂の巣のイダルゴ司祭をもっと穴だらけにした。
        もちろん、私の上にうずたかく積まれた樽をも破壊したので、私とアグリは全身にワインをたっぷり浴びてしまった。
        「あいつ、もう許せない！！」アグリがわめいた。「紙のボクをこんなに濡らすなんて……ユマ、さっさとボクをやつに渡すか、やつに名前をつけろったら！！」
        「しようがないですね」
        アグリが怒っている。もたもたしていると、どんなとばっちりを受けるか知れたものではない。
        「もう少しあの夢魔を観察したかったのですが」
        胸のホルスターからリボルバーを引き抜くと、私は弾倉をふり出して残弾を確認した。
        残り二発。
        
        もう撃ち損じは許されない。
        そのあいだにも、インキュバスは樽棚の上を跳ねまわって、私とアグリを探している。
        私が弾倉を銃身にふり戻す、ガチャッ、という音に、インキュバスが反応した。
        
        ハア──ハア……
        
        やつが何度か、短く息を吸い込む。
        ハックション！！
        
        その口と鼻から釘が乱射された直後、私は壁を蹴って樽棚の下から滑り出た。
        
        樽の上に立つインキュバスが、サッと手洟を飛ばしてくる。
        私は顔を逸らし、わずか一インチのところで釘をかわす。黒い釘は、石の床に、頭まで埋まった。
        「汝の名はスニーズ（くしゃみ）である」私は言った。
        インキュバスがニヤリと笑った。
        私が拳銃をやつの顔に向け、引き金を引き絞ったときにも、まだ笑っていた。だから、他の悪魔たちと同じように、やつもアグリの能力のことをなにも知らないのだと分かった。
        銃声が轟き、銃弾がスニーズの頭を半分ほど吹き飛ばした。そのときになってようやく、やつは残った片目をパチクリさせた。人間の銃弾に身を削られたことが、信じられないようだった。
        やつはよろめき、樽棚から仰向けにドサリと落ちた。
        「油断しましたね」私は立ち上がり、スニーズを見下ろした。「私がお前の名を知らないと、高をくくっていたのでしょう？」
        「オレたちを殺すことはできん」やつが言った。「お前たちにできることは、せいぜいオレたちを追い払うことくらいだ……いいか、ロリンズ、オレは戻ってくるぞ。必ず戻ってきて、お前を破滅させてやる」
        スニーズは喉の奥でグルルルと低くうめき、大きく息を吸い込む。
        やつがくしゃみをする前に、私は最後の一発をその口に撃ち込んでやった。銃声が轟き、夢魔の頭が跳ね上がった。
        それでもまだ、赤い目で睨みつけてくる。胸が大きく波打ち、銃弾に引き裂かれた口から悪臭を放つ液体を嘔吐したが、そのなかには黒い釘がいくつか紛れ込んでいた。
        名もなき下級の悪魔を退治するときは、その名を呼べば、体に傷を負わせることができる。しかし、やつの名は「スニーズ」ではない。それは、私が咄嗟につけた名前にすぎない。せめてもの慈悲に、私はスニーズの無言の問いに答えてやることにした。
        「たしかに、私はお前の本当の名を知りません」懐からアグリを取り出す。「しかし、私の相棒はお前に新しい名前をつけることができるんです」
        スニーズが目を見開く。
        「こんなに小さな本だとは思わなかったでしょう？」私はアグリをかざした。「これがお前たちが探しているアグリッパです」
        「ボクたちにはお前を殺せないだって？」アグリは心底楽しそうに、ケッケッケッ、と笑った。「でもね、お前みたいな弱虫はボクの大好物なんだよね」
        このとき初めて、スニーズの赤い目が、後悔と恐怖に支配された。
        私はアグリを開き、それをスニーズに向けた。黒く塗りつぶされたそのページでは、すでにアグリが牙の生えた口を大きく開けて待っていた。
        「我が黒き聖書の血肉となれ」
        ゴウッと旋風が巻き起こり、目を見開いたインキュバスがアグリの口へと吸い込まれていく。アグリは舌なめずりをし、悪魔の体を無慈悲に嚙み砕いた。
        スニーズのほうは口を吹き飛ばされているので、泣くこともわめくことも、もちろん文句を言うこともできない。
        アグリは「いただきます」に相当する言葉を、七カ国語で叫んだ。しばらく一心不乱にバリバリ、ボリボリと貪り食っていたが、やがて悪魔のような野太いゲップをして、それでおしまいだった。
        ガブリエラ・デ・ラ・エレーラの純潔を奪い、ルイス・イダルゴ聴罪司祭にその罪を着せた夢魔は、こうして我が黒き相棒の腹に収まり、アグリッパの体に「スニーズ」のページが新たに書き加えられたのだった。</p>
</div>

<script>
    let lastGazeX = 0;
    let lastGazeY = 0;
    let lastScrollTime = 0;
    let isScrollingUp = false;

    // サーバーから視線データを取得し、スクロールやページ移動を制御
    function getGazeData() {
        fetch('/gaze_data')
            .then(response => response.json())
            .then(data => {
                const x = data.x;
                const y = data.y;

                const currentTime = Date.now();

                // 下方向のスクロール
                if (x > 0.6 && lastGazeX < x && currentTime - lastScrollTime > 300) {
                    window.scrollBy(0, 32); // 下に100pxスクロール
                    lastScrollTime = currentTime;
                }

                // 上方向のスクロール
                if (y > 0.7) {
                    if (!isScrollingUp) {
                        isScrollingUp = true;
                        setTimeout(() => {
                            if (y > 0.7) {
                                window.scrollBy(0, -100); // 上に100pxスクロール
                            }
                            isScrollingUp = false;
                        }, 1000); // 1秒以上注視した場合のみスクロール
                    }
                }

                lastGazeX = x;
                lastGazeY = y;
            })
            .catch(error => console.error("視線データの取得に失敗しました:", error));
    }

    // 300msごとに視線データを取得
    setInterval(getGazeData, 100);
</script>

</body>
</html>
