(function () {
  'use strict';

  function getCookie(name) {
    if (!document.cookie) return null;
    var parts = document.cookie.split(';');
    for (var i = 0; i < parts.length; i++) {
      var p = parts[i].trim();
      if (p.indexOf(name + '=') === 0) return decodeURIComponent(p.slice(name.length + 1));
    }
    return null;
  }

  function urlB64ToUint8Array(base64String) {
    var padding = '='.repeat((4 - (base64String.length % 4)) % 4);
    var base64 = (base64String + padding).replace(/-/g, '+').replace(/_/g, '/');
    var raw = atob(base64);
    var out = new Uint8Array(raw.length);
    for (var j = 0; j < raw.length; ++j) out[j] = raw.charCodeAt(j);
    return out;
  }

  function cfg() {
    return window.__PUSH__ || null;
  }

  function postJson(url, body) {
    var token = getCookie('csrftoken');
    return fetch(url, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': token || '',
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: JSON.stringify(body),
    });
  }

  async function syncSubscription() {
    var c = cfg();
    if (!c || !c.vapidPublicKey || !('serviceWorker' in navigator) || !('PushManager' in window)) return;

    if (Notification.permission !== 'granted') return;

    var reg = await navigator.serviceWorker.ready;
    var sub = await reg.pushManager.getSubscription();
    if (!sub) return;

    await postJson(c.subscribeUrl, sub.toJSON());
  }

  window.enablePushNotifications = async function () {
    var c = cfg();
    if (!c || !c.vapidPublicKey || !('serviceWorker' in navigator) || !('PushManager' in window)) {
      return { ok: false, error: 'unsupported' };
    }

    var perm = await Notification.requestPermission();
    if (perm !== 'granted') return { ok: false, error: 'denied' };

    var reg = await navigator.serviceWorker.ready;
    var key = urlB64ToUint8Array(c.vapidPublicKey);
    var sub = await reg.pushManager.subscribe({ userVisibleOnly: true, applicationServerKey: key });
    var res = await postJson(c.subscribeUrl, sub.toJSON());
    if (!res.ok) return { ok: false, error: 'save_failed' };
    return { ok: true };
  };

  window.disablePushNotifications = async function () {
    var c = cfg();
    if (!c || !('serviceWorker' in navigator)) return { ok: false };
    var reg = await navigator.serviceWorker.ready;
    var sub = await reg.pushManager.getSubscription();
    if (sub) {
      await postJson(c.unsubscribeUrl, { endpoint: sub.endpoint });
      await sub.unsubscribe();
    }
    return { ok: true };
  };

  document.addEventListener('DOMContentLoaded', function () {
    syncSubscription().catch(function () {});
  });
})();
