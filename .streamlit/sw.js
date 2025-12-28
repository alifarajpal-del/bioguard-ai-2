const CACHE_NAME = 'bioguard-ai-v1.0';
const urlsToCache = [
  '/',
  '/static/css/style.css',
  '/static/js/app.js'
];

// Install Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Opened cache');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached version or fetch from network
        return response || fetch(event.request);
      }
    )
  );
});

// Background sync for offline functionality
self.addEventListener('sync', event => {
  if (event.tag === 'background-sync') {
    event.waitUntil(doBackgroundSync());
  }
});

function doBackgroundSync() {
  console.log('Background sync triggered');
  // Handle offline data synchronization here
}

// Push notifications
self.addEventListener('push', event => {
  const options = {
    body: event.data.text(),
    icon: '/icon-192.png',
    badge: '/badge-72.png'
  };

  event.waitUntil(
    self.registration.showNotification('BioGuard AI', options)
  );
});