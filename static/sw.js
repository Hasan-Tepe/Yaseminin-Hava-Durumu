const CACHE_NAME = 'weather-assistant-v1';
const urlsToCache = [
  '/',
  '/settings',
  '/static/css/output.css',
  '/static/manifest.json',
  '/static/img/icon.svg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Cache hit - return response
        if (response) {
          return response;
        }
        return fetch(event.request).catch(() => {
            // Eğer fetch hata verirse (örneğin offline isek) ve bu bir HTML isteğiyse offline sayfasını veya var olan cache'i dönebiliriz.
            // Bu basit versiyonda fail down işlemi yapılmıyor
        });
      }
    )
  );
});

self.addEventListener('activate', event => {
  const cacheWhitelist = [CACHE_NAME];
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheWhitelist.indexOf(cacheName) === -1) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});
