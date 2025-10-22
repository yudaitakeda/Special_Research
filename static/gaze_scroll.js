// ===============================
// gaze_scroll.js
// ===============================
// Flaskサーバー (/gaze_data) から取得した視線データを用いて
// ページのスクロールを制御するスクリプト。
// 視線位置の注視・上下・左右・左上の位置などを判定して、
// スムーズなスクロール操作を行う。

// ==== グローバル変数定義 ====
let lastGazeX = 0;               // 前回のx座標を保存
let lastGazePosition = null;     // 前回の視線位置 {x, y}
let gazeHoldStartTime = null;    // 注視開始時刻
const HOLD_DURATION = 500;       // 0.5秒注視でスクロール発動
let hasScrolledX = false;        // 横方向のスクロール制御用フラグ
let scrollBackStartTime = null;  // 左上注視で「戻る」機能のタイマー
let gazeTimerUp = null;          // 上向きアイコン注視時のタイマー
let gazeTimerDown = null;        // 下向きアイコン注視時のタイマー


// ======================================================
// 共通：スクロール＋カーソル（赤丸）アニメーション関数
// ======================================================
function scrollWithCursor(x, y, direction) {
  const cursor = document.getElementById('gaze-cursor');

  // スクロール量：画面高さの半分
  const scrollAmount = window.innerHeight / 2;

  // 現在のスクロール位置とカーソル位置を取得
  const startScrollY = window.scrollY;
  const startCursorY = window.innerHeight * y;
  const startCursorX = window.innerWidth * x;

  // スクロール方向設定
  let deltaY = 0;
  if (direction === 'up') deltaY = -scrollAmount;
  if (direction === 'down') deltaY = scrollAmount;

  const targetScroll = startScrollY + deltaY;
  const startTime = performance.now();
  const duration = 1000; // 1秒でアニメーション完了

  // ---- アニメーションループ ----
  function animate(time) {
    const elapsed = time - startTime;
    const progress = Math.min(elapsed / duration, 1);

    // イージング関数（二次曲線）
    const ease = progress < 0.5
      ? 2 * progress * progress
      : -1 + (4 - 2 * progress) * progress;

    // 新しいスクロール位置とカーソル位置を計算
    const newScroll = startScrollY + deltaY * ease;
    const newCursorY = startCursorY - deltaY * ease;

    window.scrollTo(0, newScroll);
    cursor.style.left = `${startCursorX}px`;
    cursor.style.top = `${newCursorY}px`;
    cursor.style.display = 'block';

    // アニメーション継続
    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      // 終了後カーソルを消す
      setTimeout(() => cursor.style.display = 'none', 500);
    }
  }

  requestAnimationFrame(animate);
}


// ======================================================
// 視線位置の比較（移動の有無を判定）
// ======================================================
function isSamePosition(pos1, pos2) {
  const THRESHOLD = 0.05; // 5%以内なら同じ位置とみなす
  return Math.abs(pos1.x - pos2.x) < THRESHOLD &&
         Math.abs(pos1.y - pos2.y) < THRESHOLD;
}


// ======================================================
// アイコン注視でスクロール（⬆️⬇️アイコン対応）
// ======================================================
function checkGazeOnIcon(x, y) {
  const iconUp = document.getElementById('scroll-icon');
  const iconDown = document.getElementById('scroll-icon-down');
  const screenX = window.innerWidth * x;
  const screenY = window.innerHeight * y;

  // --- 上アイコン注視時 ---
  if (iconUp) {
    const rect = iconUp.getBoundingClientRect();
    if (screenX >= rect.left && screenX <= rect.right &&
        screenY >= rect.top && screenY <= rect.bottom) {
      // 1秒間注視したらスクロールアップ
      if (!gazeTimerUp) {
        gazeTimerUp = setTimeout(() => {
          window.scrollBy({ top: -window.innerHeight / 2, behavior: 'smooth' });
          gazeTimerUp = null;
        }, 1000);
      }
    } else if (gazeTimerUp) {
      clearTimeout(gazeTimerUp);
      gazeTimerUp = null;
    }
  }

  // --- 下アイコン注視時 ---
  if (iconDown) {
    const rect = iconDown.getBoundingClientRect();
    if (screenX >= rect.left && screenX <= rect.right &&
        screenY >= rect.top && screenY <= rect.bottom) {
      // 1秒間注視したらスクロールダウン
      if (!gazeTimerDown) {
        gazeTimerDown = setTimeout(() => {
          window.scrollBy({ top: window.innerHeight / 2, behavior: 'smooth' });
          gazeTimerDown = null;
        }, 1000);
      }
    } else if (gazeTimerDown) {
      clearTimeout(gazeTimerDown);
      gazeTimerDown = null;
    }
  }
}


// ======================================================
// 視線データ取得処理
// Flaskの /gaze_data API から定期的に取得
// ======================================================
function getGazeData() {
  fetch('/gaze_data')
    .then(res => res.json())
    .then(data => {
      const x = data.x;
      const y = data.y;
      const currentTime = Date.now();
      const position = { x, y };

      // カーソル位置更新
      const cursor = document.getElementById('gaze-cursor');
      cursor.style.left = `${window.innerWidth * x}px`;
      cursor.style.top = `${window.innerHeight * y}px`;

      // ==============================
      // 0.5秒以上注視で上下スクロール
      // ==============================
      if (lastGazePosition && isSamePosition(position, lastGazePosition)) {
        if (!gazeHoldStartTime) gazeHoldStartTime = currentTime;
        else if (currentTime - gazeHoldStartTime > HOLD_DURATION) {
          // 上エリア（y < 0.3）を注視 → 上スクロール
          if (y < 0.3 && (x > 0.3 && x < 0.7)) scrollWithCursor(x, y, 'up');
          // 下エリア（y > 0.8）を注視 → 下スクロール
          else if (y > 0.8 && (x > 0.3 && x < 0.7)) scrollWithCursor(x, y, 'down');
          gazeHoldStartTime = null;
        }
      } else {
        gazeHoldStartTime = null;
      }

      // ==============================
      // 左右端注視で横スクロール
      // ==============================
      if (x > 0.8 && !hasScrolledX) {
        hasScrolledX = true;
      } else if (x < 0.2 && hasScrolledX) {
        window.scrollBy(0, 30);
        hasScrolledX = false;
      }

      // ==============================
      // 左上注視でページ先頭に戻る
      // ==============================
      if (x < 0.2 && y < 0.2) {
        if (!scrollBackStartTime) scrollBackStartTime = currentTime;
        else if (currentTime - scrollBackStartTime > 500) {
          window.scrollTo({ top: 0, behavior: 'smooth' });
          scrollBackStartTime = null;
        }
      } else {
        scrollBackStartTime = null;
      }

      // アイコン注視判定（⬆️⬇️）
      checkGazeOnIcon(x, y);

      // 状態更新
      lastGazeX = x;
      lastGazePosition = position;
    })
    .catch(e => console.error('視線データ取得エラー:', e));
}


// ======================================================
// 定期取得タイマー
// ======================================================
setInterval(getGazeData, 100); // 100msごとに視線を取得（10Hz）
