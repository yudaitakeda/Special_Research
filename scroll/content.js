(() => {
  let lastGazeX = 0;
  let lastGazePosition = null;
  let gazeHoldStartTime = null;
  const HOLD_DURATION = 500;
  let hasScrolledX = false;
  let hasScrolledY = false;
  let scrollBackStartTime = null;
  let gazeTimerUp = null;
  let gazeTimerDown = null;

  // カーソル要素を作成・初期化
  const CURSOR_ID = 'gaze-cursor';
  function createCursor() {
    if (document.getElementById(CURSOR_ID)) return;
    const cursor = document.createElement('div');
    cursor.id = CURSOR_ID;
    Object.assign(cursor.style, {
      position: 'fixed',
      width: '30px',
      height: '30px',
      backgroundColor: 'transparent',
      border: '3px solid red',
      borderRadius: '50%',
      pointerEvents: 'none',
      transform: 'translate(-50%, -50%)',
      zIndex: 9999,
      display: 'none',
      alignItems: 'center',
      justifyContent: 'center',
      fontWeight: 'bold',
    });
    document.body.appendChild(cursor);
  }

  // アニメーション：下にスクロールしつつカーソルを上に滑らか移動
  function scrollDownAndMoveCursorUp(startX, startY) {
    const scrollAmount = window.innerHeight / 2;
    const startScroll = window.scrollY;
    const targetScroll = Math.min(document.body.scrollHeight - window.innerHeight, startScroll + scrollAmount);
    const startTime = performance.now();
    const duration = 1000;

    const cursor = document.getElementById(CURSOR_ID);
    const startCursorY = window.innerHeight * startY;
    const targetCursorY = Math.max(0, startCursorY - scrollAmount);
    const startCursorX = window.innerWidth * startX;

    function animate(time) {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = progress < 0.5
        ? 2 * progress * progress
        : -1 + (4 - 2 * progress) * progress;

      const newScroll = startScroll + (targetScroll - startScroll) * ease;
      const newCursorY = startCursorY + (targetCursorY - startCursorY) * ease;

      window.scrollTo(0, newScroll);
      cursor.style.top = `${newCursorY}px`;
      cursor.style.left = `${startCursorX}px`;
      cursor.style.display = 'flex';

      if (progress < 1) {
        requestAnimationFrame(animate);
      } else {
        setTimeout(() => {
          cursor.style.display = 'none';
        }, 500);
      }
    }
    requestAnimationFrame(animate);
  }

  function isSamePosition(pos1, pos2) {
    const THRESHOLD = 0.01;
    return Math.abs(pos1.x - pos2.x) < THRESHOLD && Math.abs(pos1.y - pos2.y) < THRESHOLD;
  }

  // 上矢印アイコン注視チェック（1秒で上にスクロール）
  function checkGazeOnIcon(x, y) {
    const icon = document.getElementById('scroll-icon');
    if (!icon) return false;
    const rect = icon.getBoundingClientRect();
    const screenX = window.innerWidth * x;
    const screenY = window.innerHeight * y;

    if (screenX >= rect.left && screenX <= rect.right && screenY >= rect.top && screenY <= rect.bottom) {
      if (!gazeTimerUp) {
        gazeTimerUp = setTimeout(() => {
          const scrollAmount = window.innerHeight / 2;
          window.scrollTo({ top: Math.max(0, window.scrollY - scrollAmount), behavior: 'smooth' });
          gazeTimerUp = null;
        }, 1000);
      }
      return true;
    } else if (gazeTimerUp) {
      clearTimeout(gazeTimerUp);
      gazeTimerUp = null;
    }
    return false;
  }

  // 下矢印アイコン注視チェック（1秒で下にスクロール）
  function checkGazeOnDownIcon(x, y) {
    const icon = document.getElementById('scroll-icon-down');
    if (!icon) return false;
    const rect = icon.getBoundingClientRect();
    const screenX = window.innerWidth * x;
    const screenY = window.innerHeight * y;

    if (screenX >= rect.left && screenX <= rect.right && screenY >= rect.top && screenY <= rect.bottom) {
      if (!gazeTimerDown) {
        gazeTimerDown = setTimeout(() => {
          const scrollAmount = window.innerHeight / 2;
          window.scrollTo({ top: Math.min(document.body.scrollHeight - window.innerHeight, window.scrollY + scrollAmount), behavior: 'smooth' });
          gazeTimerDown = null;
        }, 1000);
      }
      return true;
    } else if (gazeTimerDown) {
      clearTimeout(gazeTimerDown);
      gazeTimerDown = null;
    }
    return false;
  }

  // メインループ：視線データ取得＆処理
  function getGazeData() {
    fetch('http://localhost:5001/gaze_data')
      .then(response => response.json())
      .then(data => {
        const x = data.x;
        const y = data.y;
        const currentTime = Date.now();

        const currentPosition = { x, y };
        const gazeCursor = document.getElementById(CURSOR_ID);
        gazeCursor.style.left = `${window.innerWidth * x}px`;
        gazeCursor.style.top = `${window.innerHeight * y}px`;

        // 0.5秒注視で下にスクロール
        if (lastGazePosition && isSamePosition(currentPosition, lastGazePosition)) {
          if (!gazeHoldStartTime) {
            gazeHoldStartTime = currentTime;
          } else if (currentTime - gazeHoldStartTime >= HOLD_DURATION) {
            scrollDownAndMoveCursorUp(x, y);
            gazeHoldStartTime = null;
          }
        } else {
          gazeHoldStartTime = null;
        }

        // // 画面右下スクロール判定（y > 0.8） ※縦スクロールを滑らかに発火
        // if (y > 0.8 && !hasScrolledY) {
        //   const scrollAmount = window.innerHeight / 2;
        //   window.scrollTo({ top: Math.min(document.body.scrollHeight - window.innerHeight, window.scrollY + scrollAmount), behavior: 'smooth' });
        //   hasScrolledY = true;
        // } else if (y < 0.5) {
        //   hasScrolledY = false;
        // }

        // 画面左上注視で一番上に戻る
        if (x < 0.2 && y < 0.2) {
          if (!scrollBackStartTime) {
            scrollBackStartTime = currentTime;
          } else if (currentTime - scrollBackStartTime > 500) {
            window.scrollTo({ top: 0, behavior: 'smooth' });
            scrollBackStartTime = null;
          }
        } else {
          scrollBackStartTime = null;
        }

        checkGazeOnIcon(x, y);
        checkGazeOnDownIcon(x, y);

        lastGazeX = x;
        lastGazePosition = currentPosition;
      })
      .catch(error => {
        console.error('視線データ取得エラー:', error);
        const gazeCursor = document.getElementById(CURSOR_ID);
        gazeCursor.style.display = 'none';
      });
  }

  function init() {
    createCursor();
    setInterval(getGazeData, 100);
  }

  init();
})();
