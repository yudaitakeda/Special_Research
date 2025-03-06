let blinkCount = 0;
const gazeIndicator = document.getElementById('gaze-indicator');
const pageNumber = document.getElementById('page-number');
let currentPage = window.location.pathname.includes('page2') ? 2 : window.location.pathname.includes('page3') ? 3 : 1;

function getGazeData() {
    fetch('/gaze_data')
        .then(response => response.json())
        .then(data => {
            const x = data.x;
            const y = data.y;

            // ウィンドウサイズとマージンを考慮して視線位置を調整
            const screenX = x * window.innerWidth; // xの範囲が0〜1に基づく
            const screenY = y * window.innerHeight; // yの範囲が0〜1に基づく

            // 視線ポインタの位置を設定
            gazeIndicator.style.left = screenX + 'px';
            gazeIndicator.style.top = screenY + 'px';

            // スクロール処理
            if (y < 0.3) {
                window.scrollBy(0, -50); // 上にスクロール
            } else if (y > 0.7) {
                window.scrollBy(0, 50); // 下にスクロール
            }
        });
}

function handleBlinkDetection() {
    fetch('/gaze_data')
        .then(response => response.json())
        .then(data => {
            const x = data.x;
            const y = data.y;

            // 右側のナビゲーション領域で瞬きを検出
            if (data.blink_count > blinkCount) {
                blinkCount = data.blink_count;
                if (x > 0.7 && currentPage < 3) {
                    currentPage++;
                    window.location.href = `/page${currentPage}`;  // 次のページに移動
                } else if (x < 0.3 && currentPage > 1) {
                    currentPage--;
                    window.location.href = `/page${currentPage}`;  // 前のページに移動
                }
            }
        });
}

setInterval(getGazeData, 100);
setInterval(handleBlinkDetection, 100);

