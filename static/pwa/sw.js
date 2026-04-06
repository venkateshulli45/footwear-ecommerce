/* Minimal PWA service worker — enables install + light offline shell. */
const CACHE = 'jagam-store-v2';

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE).then(async (cache) => {
      const urls = [
        '/static/css/store.css',
        '/static/vendor/bootstrap-icons/font/bootstrap-icons.css',
        '/static/pwa/icon.svg',
      ];
      try {
        await cache.addAll(urls);
      } catch (e) {
        /* ignore precache failures (e.g. dev / wrong base path) */
      }
      try {
        await cache.add('/');
      } catch (e) {
        /* homepage optional for offline */
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k)))
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const { request } = event;
  if (request.method !== 'GET') return;

  const url = new URL(request.url);
  if (url.origin !== self.location.origin) return;

  // Network-first for navigations (HTML) so content stays fresh.
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(
      fetch(request).catch(() => caches.match('/'))
    );
    return;
  }

  // Stale-while-revalidate for same-origin static assets.
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then((cached) => {
        const network = fetch(request)
          .then((response) => {
            if (response.ok) {
              const copy = response.clone();
              caches.open(CACHE).then((cache) => cache.put(request, copy));
            }
            return response;
          })
          .catch(() => cached);
        return cached || network;
      })
    );
  }
});

self.addEventListener('push', (event) => {
  let data = { title: 'Jagam Footwear', body: '', url: '/' };
  try {
    if (event.data) {
      const parsed = event.data.json();
      if (parsed.title) data.title = String(parsed.title).slice(0, 120);
      if (parsed.body != null) data.body = String(parsed.body).slice(0, 240);
      if (parsed.url) data.url = String(parsed.url).slice(0, 2000);
    }
  } catch (e) {
    try {
      const t = event.data && event.data.text();
      if (t) data.body = t.slice(0, 240);
    } catch (e2) {}
  }
  event.waitUntil(
    self.registration.showNotification(data.title, {
      body: data.body || undefined,
      data: { url: data.url },
      icon: '/static/pwa/icon.svg',
      badge: '/static/pwa/icon.svg',
    })
  );
});

self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url) || '/';
  const target = url.startsWith('http') ? url : new URL(url, self.location.origin).href;
  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (let i = 0; i < clientList.length; i++) {
        const c = clientList[i];
        if (c.url && 'focus' in c) return c.focus();
      }
      if (self.clients.openWindow) return self.clients.openWindow(target);
    })
  );
});
