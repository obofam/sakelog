// 酒ログ Service Worker — シンプルな cache-first
const CACHE_NAME = 'sakelog-v18';
const STAMPS_CACHE = 'sakelog-stamps-v1'; // 肴スタンプ（APNG）専用。アプリのキャッシュ更新でも消さない
const ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/apple-touch-icon.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(
        keys.filter((key) => key !== CACHE_NAME && key !== STAMPS_CACHE).map((key) => caches.delete(key))
      )
    ).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return;

  // 肴スタンプ（/stamps/ 配下）は専用キャッシュに cache-first で保存。一度見たら残す
  let isStamp = false;
  try { isStamp = new URL(event.request.url).pathname.includes('/stamps/'); } catch (e) { /* 無視 */ }
  if (isStamp) {
    event.respondWith(
      caches.open(STAMPS_CACHE).then((cache) =>
        cache.match(event.request).then((cached) => {
          if (cached) return cached;
          return fetch(event.request).then((res) => {
            if (res && res.ok) cache.put(event.request, res.clone());
            return res;
          }).catch(() => cached);
        })
      )
    );
    return;
  }

  // ページ本体（ナビゲーション / index.html）は network-first。オンラインなら常に最新版、オフラインならキャッシュ
  const isPage = event.request.mode === 'navigate' || /\/(index\.html)?(\?.*)?$/.test(new URL(event.request.url).pathname + '');
  if (isPage) {
    event.respondWith(
      fetch(event.request).then((res) => {
        if (res && res.ok) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return res;
      }).catch(() => caches.match(event.request).then((c) => c || caches.match('./index.html')))
    );
    return;
  }

  event.respondWith(
    caches.match(event.request).then((cached) => {
      if (cached) return cached;
      return fetch(event.request).then((res) => {
        // 同一オリジンのGETだけキャッシュに追加しておく
        if (res && res.ok && event.request.url.startsWith(self.location.origin)) {
          const clone = res.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        }
        return res;
      }).catch(() => cached);
    })
  );
});
