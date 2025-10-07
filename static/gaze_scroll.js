// gaze_scroll.js
let lastGazeX = 0;
let lastGazePosition = null;
let gazeHoldStartTime = null;
const HOLD_DURATION = 500; // 0.5秒注視でスクロール
let hasScrolledX = false;
let scrollBackStartTime = null;
let gazeTimerUp = null;
let gazeTimerDown = null;

// ----------------------------
// 共通スクロール関数
// ----------------------------
function scrollWithCursor(x, y, direction) {
  const cursor = document.getElementById('gaze-cursor');
  const scrollAmount = window.innerHeight / 2;
  const startScrollY = window.scrollY;
  const startCursorY = window.innerHeight * y;
  const startCursorX = window.innerWidth * x;

  let deltaY = 0;
  if (direction === 'up') deltaY = -scrollAmount;
  if (direction === 'down') deltaY = scrollAmount;

  const targetScroll = startScrollY + deltaY;
  const targetCursorY = startCursorY - deltaY;
  const startTime = performance.now();
  const duration = 1000;

  function animate(time) {
    const elapsed = time - startTime;
    const progress = Math.min(elapsed / duration, 1);
    const ease = progress < 0.5
      ? 2 * progress * progress
      : -1 + (4 - 2 * progress) * progress;

    const newScroll = startScrollY + deltaY * ease;
    const newCursorY = startCursorY - deltaY * ease;

    window.scrollTo(0, newScroll);
    cursor.style.left = `${startCursorX}px`;
    cursor.style.top = `${newCursorY}px`;
    cursor.style.display = 'block';

    if (progress < 1) {
      requestAnimationFrame(animate);
    } else {
      setTimeout(() => cursor.style.display = 'none', 500);
    }
  }
  requestAnimationFrame(animate);
}

// ----------------------------
// 視線位置の比較
// ----------------------------
function isSamePosition(pos1, pos2) {
  const THRESHOLD = 0.05; // 5%以内なら同じ位置とみなす
  return Math.abs(pos1.x - pos2.x) < THRESHOLD && Math.abs(pos1.y - pos2.y) < THRESHOLD;
}

// ----------------------------
// アイコン注視でスクロール
// ----------------------------
function checkGazeOnIcon(x, y) {
  const iconUp = document.getElementById('scroll-icon');
  const iconDown = document.getElementById('scroll-icon-down');
  const screenX = window.innerWidth * x;
  const screenY = window.innerHeight * y;

  if (iconUp) {
    const rect = iconUp.getBoundingClientRect();
    if (screenX >= rect.left && screenX <= rect.right && screenY >= rect.top && screenY <= rect.bottom) {
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

  if (iconDown) {
    const rect = iconDown.getBoundingClientRect();
    if (screenX >= rect.left && screenX <= rect.right && screenY >= rect.top && screenY <= rect.bottom) {
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

// ----------------------------
// 視線データ取得
// ----------------------------
function getGazeData() {
  fetch('/gaze_data')
    .then(res => res.json())
    .then(data => {
      const x = data.x;
      const y = data.y;
      const currentTime = Date.now();
      const position = { x, y };

      const cursor = document.getElementById('gaze-cursor');
      cursor.style.left = `${window.innerWidth * x}px`;
      cursor.style.top = `${window.innerHeight * y}px`;

      // 0.5秒以上注視で上下スクロール
      if (lastGazePosition && isSamePosition(position, lastGazePosition)) {
        if (!gazeHoldStartTime) gazeHoldStartTime = currentTime;
        else if (currentTime - gazeHoldStartTime > HOLD_DURATION) {
          if (y < 0.3 && (x > 0.3 && x < 0.7)) scrollWithCursor(x, y, 'up');
          else if (y > 0.8 && (x > 0.3 && x < 0.7)) scrollWithCursor(x, y, 'down');
          gazeHoldStartTime = null;
        }
      } else {
        gazeHoldStartTime = null;
      }

      // 左右端注視で横スクロール
      if (x > 0.8 && !hasScrolledX) {
        hasScrolledX = true;
      } else if (x < 0.2 && hasScrolledX) {
        window.scrollBy(0, 30);
        hasScrolledX = false;
      }

      // 左上エリアで先頭に戻る
      if (x < 0.2 && y < 0.2) {
        if (!scrollBackStartTime) scrollBackStartTime = currentTime;
        else if (currentTime - scrollBackStartTime > 500) {
          window.scrollTo({ top: 0, behavior: 'smooth' });
          scrollBackStartTime = null;
        }
      } else {
        scrollBackStartTime = null;
      }

      checkGazeOnIcon(x, y);

      lastGazeX = x;
      lastGazePosition = position;
    })
    .catch(e => console.error('視線データ取得エラー:', e));
}

// ----------------------------
// 100msごとに取得
// ----------------------------
setInterval(getGazeData, 100);
