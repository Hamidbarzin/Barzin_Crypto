// Service Worker for Crypto Bot PWA

const CACHE_NAME = 'crypto-bot-cache-v1';
const urlsToCache = [
  '/',
  '/minimal_dashboard',
  '/minimal_settings',
  '/static/manifest.json',
  '/static/icons/favicon-32x32.png',
  '/static/icons/apple-touch-icon.png',
  '/static/icons/icon-192x192.png'
];

// Install event - cache resources
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        console.log('Cache opened');
        return cache.addAll(urlsToCache);
      })
  );
});

// Fetch event - serve from cache if available
self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => {
        // Return cached response if found
        if (response) {
          return response;
        }
        
        // Clone request for potential cache
        const fetchRequest = event.request.clone();
        
        // For API requests, don't cache and just fetch from network
        if (event.request.url.includes('/api/')) {
          return fetch(fetchRequest);
        }
        
        // For non-API requests, fetch and cache if successful
        return fetch(fetchRequest).then(
          response => {
            // Check if valid response
            if (!response || response.status !== 200 || response.type !== 'basic') {
              return response;
            }
            
            // Clone response for cache
            const responseToCache = response.clone();
            
            caches.open(CACHE_NAME)
              .then(cache => {
                cache.put(event.request, responseToCache);
              });
              
            return response;
          }
        );
      })
  );
});

// Activate event - clean up old caches
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
