(() => {
  const HOLD_DURATION = 500;
  let lastGazeX = 0;
  let lastGazePosition = null;
  let gazeHoldStartTime = null;
  let hasScrolledX = false;
  let scrollBackStartTime = null;
  let gazeTimerUp = null;
  let gazeTimerDown = null;

  // カーソル生成
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
    });
    document.body.appendChild(cursor);
  }

  function scrollWithCursor(x, y, direction) {
    const scrollAmount = window.innerHeight / 2;
    const cursor = document.getElementById(CURSOR_ID);
    const startScrollX = window.scrollX;
    const startScrollY = window.scrollY;
    const targetScrollX = direction === 'left' ? Math.max(0, startScrollX - scrollAmount) :
                         direction === 'right' ? startScrollX + scrollAmount : startScrollX;
    const targetScrollY = direction === 'up' ? Math.max(0, startScrollY - scrollAmount) :
                         direction === 'down' ? Math.min(document.body.scrollHeight - window.innerHeight, startScrollY + scrollAmount) :
                         startScrollY;

    const startCursorX = window.innerWidth * x;
    const startCursorY = window.innerHeight * y;
    const targetCursorY = direction === 'up' ? startCursorY - scrollAmount :
                         direction === 'down' ? startCursorY + scrollAmount :
                         startCursorY;

    const startTime = performance.now();
    const duration = 800;

    function animate(time) {
      const elapsed = time - startTime;
      const progress = Math.min(elapsed / duration, 1);
      const ease = progress < 0.5 ? 2 * progress * progress : -1 + (4 - 2 * progress) * progress;

      window.scrollTo(
        startScrollX + (targetScrollX - startScrollX) * ease,
        startScrollY + (targetScrollY - startScrollY) * ease
      );
      cursor.style.left = `${startCursorX}px`;
      cursor.style.top = `${startCursorY + (targetCursorY - startCursorY) * ease}px`;
      cursor.style.display = 'block';

      if (progress < 1) requestAnimationFrame(animate);
      else setTimeout(() => cursor.style.display = 'none', 500);
    }
    requestAnimationFrame(animate);
  }

  function isSamePosition(p1, p2) {
    const THRESHOLD = 0.01;
    return Math.abs(p1.x - p2.x) < THRESHOLD && Math.abs(p1.y - p2.y) < THRESHOLD;
  }

  function checkGazeOnIcon(x, y) {
    const icon = document.getElementById('scroll-icon');
    if (!icon) return;
    const rect = icon.getBoundingClientRect();
    const screenX = window.innerWidth * x;
    const screenY = window.innerHeight * y;

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

  function checkGazeOnDownIcon(x, y) {
    const icon = document.getElementById('scroll-icon-down');
    if (!icon) return;
    const rect = icon.getBoundingClientRect();
    const screenX = window.innerWidth * x;
    const screenY = window.innerHeight * y;

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

  function getGazeData() {
    fetch('http://localhost:5001/gaze_data')
      .then(response => response.json())
      .then(data => {
        const x = data.x;
        const y = data.y;
        const currentTime = Date.now();
        const currentPosition = { x, y };

        const cursor = document.getElementById(CURSOR_ID);
        cursor.style.left = `${window.innerWidth * x}px`;
        cursor.style.top = `${window.innerHeight * y}px`;

        // 左・右・上・下の領域注視によるスクロール
        if (lastGazePosition && isSamePosition(currentPosition, lastGazePosition)) {
          if (!gazeHoldStartTime) gazeHoldStartTime = currentTime;
          else if (currentTime - gazeHoldStartTime >= HOLD_DURATION) {
            if (x > 0.7 && y > 0.3 && y < 0.7) scrollWithCursor(x, y, 'right');
            else if (x < 0.3 && y > 0.3 && y < 0.7) scrollWithCursor(x, y, 'left');
            else if (y < 0.3 && x > 0.3 && x < 0.7) scrollWithCursor(x, y, 'up');
            else if (y > 0.7 && x > 0.3 && x < 0.7) scrollWithCursor(x, y, 'down');
            gazeHoldStartTime = null;
          }
        } else {
          gazeHoldStartTime = null;
        }

        // 横方向1行スクロール
        if (x > 0.8 && !hasScrolledX && lastGazeX < x) {
          console.log('横スクロールトリガー: x=', x);
          window.scrollBy(0, 30);
          hasScrolledX = true;
        } else if (x < 0.5) {
          hasScrolledX = false;
        }

        // 左上注視でページ先頭へ
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
        checkGazeOnDownIcon(x, y);

        lastGazeX = x;
        lastGazePosition = currentPosition;
      })
      .catch(e => {
        console.error('視線データ取得エラー:', e);
        document.getElementById(CURSOR_ID).style.display = 'none';
      });
  }

  function init() {
    createCursor();
    setInterval(getGazeData, 100);
  }

  init();
})();
