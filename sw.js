// Service Worker：应用壳缓存，离线可用
// 发布新版本时递增 CACHE 版本号，前端会弹出"发现新版本"提示
const CACHE = 'lure-companion-v2';
const SHELL = [
  './',
  './index.html',
  './css/style.css',
  './js/app.js',
  './js/ui.js',
  './js/db.js',
  './js/data.js',
  './js/species.js',
  './js/weather.js',
  './js/backup.js',
  './js/lure-detail.js',
  './js/recommend-engine.js',
  './js/pages/recommend.js',
  './js/pages/log.js',
  './js/pages/dex.js',
  './js/pages/tools.js',
  './js/pages/gear.js',
  './manifest.webmanifest',
  './icons/icon.svg',
  './icons/icon-192.png',
  './icons/icon-512.png',
];

self.addEventListener('install', (e) => {
  // 不主动 skipWaiting：等用户点"立即更新"，避免使用中突然刷新
  e.waitUntil(caches.open(CACHE).then((c) => c.addAll(SHELL)));
});

self.addEventListener('message', (e) => {
  if (e.data === 'skipWaiting') self.skipWaiting();
});

self.addEventListener('activate', (e) => {
  e.waitUntil(
    caches
      .keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

// 同源 GET：缓存优先，后台更新（stale-while-revalidate）
self.addEventListener('fetch', (e) => {
  const url = new URL(e.request.url);
  if (e.request.method !== 'GET' || url.origin !== location.origin) return;
  e.respondWith(
    caches.match(e.request).then((cached) => {
      const fresh = fetch(e.request)
        .then((res) => {
          if (res.ok) {
            const clone = res.clone();
            caches.open(CACHE).then((c) => c.put(e.request, clone));
          }
          return res;
        })
        .catch(() => cached);
      return cached || fresh;
    })
  );
});
