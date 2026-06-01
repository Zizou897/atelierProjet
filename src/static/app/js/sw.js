const STATIC_CACHE = 'ctams-static-v1';
const OFFLINE_URL = '/offline/';

const PRE_CACHE_ASSETS = [
  OFFLINE_URL,
  '/static/app/css/ctams.css',
  '/static/app/assets/img/ctams-logo.jpg',
  '/static/app/assets/img/icons/icon-192x192.png',
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(PRE_CACHE_ASSETS))
      .catch(err => console.warn('[CTAMS SW] Pre-cache partial failure:', err))
  );
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(keys.filter(k => k !== STATIC_CACHE).map(k => caches.delete(k)))
    )
  );
  self.clients.claim();
});

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  if (request.method !== 'GET') return;
  if (url.pathname.startsWith('/admin/') || url.pathname.startsWith('/api/')) return;

  // Static assets (CSS, JS, images, fonts) — cache-first
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(
      caches.match(request).then(cached => {
        if (cached) return cached;
        return fetch(request).then(response => {
          if (response.ok) {
            const clone = response.clone();
            caches.open(STATIC_CACHE).then(cache => cache.put(request, clone));
          }
          return response;
        });
      })
    );
    return;
  }

  // HTML navigation — network-first, offline fallback
  if (request.mode === 'navigate') {
    event.respondWith(
      fetch(request).catch(() =>
        caches.match(OFFLINE_URL).then(cached =>
          cached || new Response(
            '<!DOCTYPE html><html lang="fr"><body><h1>Hors ligne</h1><p>Vérifiez votre connexion.</p></body></html>',
            { headers: { 'Content-Type': 'text/html; charset=utf-8' } }
          )
        )
      )
    );
  }
});
