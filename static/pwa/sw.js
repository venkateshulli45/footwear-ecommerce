/* Minimal PWA service worker — enables install + light offline shell. */
const CACHE = 'jagam-store-v1';

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
