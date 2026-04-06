(function () {
  function getCsrfToken() {
    var m = document.cookie.match(/csrftoken=([^;]+)/);
    return m ? decodeURIComponent(m[1].trim()) : '';
  }

  function setUnreadBadge(count) {
    document.querySelectorAll('[data-notification-badge]').forEach(function (el) {
      var n = parseInt(count, 10) || 0;
      if (n > 0) {
        el.textContent = n > 99 ? '99+' : String(n);
        el.hidden = false;
      } else {
        el.textContent = '';
        el.hidden = true;
      }
    });
  }

  function postMarkRead(url, thenFn) {
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
        'X-CSRFToken': getCsrfToken(),
        'X-Requested-With': 'XMLHttpRequest',
      },
      credentials: 'same-origin',
      body: 'csrfmiddlewaretoken=' + encodeURIComponent(getCsrfToken()),
    })
      .then(function (r) {
        return r.json();
      })
      .then(function (d) {
        if (d && typeof d.unread === 'number') setUnreadBadge(d.unread);
        if (thenFn) thenFn();
      })
      .catch(function () {
        if (thenFn) thenFn();
      });
  }

  function initNotifMenu() {
    var trigger = document.getElementById('notif-menu-trigger');
    var panel = document.getElementById('notif-menu-panel');
    if (!trigger || !panel) return;

    trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      var open = panel.hidden;
      panel.hidden = !open;
      trigger.setAttribute('aria-expanded', open ? 'true' : 'false');
    });

    document.addEventListener('click', function () {
      panel.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
    });

    panel.addEventListener('click', function (e) {
      e.stopPropagation();
    });

    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') {
        panel.hidden = true;
        trigger.setAttribute('aria-expanded', 'false');
      }
    });
  }

  function initMarkReadLinks() {
    document.querySelectorAll('a.notif-menu__item[data-mark-read-url], a.notif-row[data-mark-read-url]').forEach(
      function (a) {
        a.addEventListener('click', function (e) {
          var url = a.getAttribute('data-mark-read-url');
          if (!url) return;
          var dest = a.getAttribute('href') || '#';
          e.preventDefault();
          postMarkRead(url, function () {
            window.location.href = dest;
          });
        });
      }
    );
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      initNotifMenu();
      initMarkReadLinks();
    });
  } else {
    initNotifMenu();
    initMarkReadLinks();
  }
})();
