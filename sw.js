// Smart Inventory - Service Worker
// PWA offline support and caching

const CACHE_NAME = 'smart-inventory-v1';

// Assets to precache on install (root-level HTML served by http.server on port 8080)
const PRECACHE_ASSETS = [
  '/index.html',
  '/login.html',
  '/register.html',
  '/dashboard.html',
  '/products.html',
  '/inventory.html',
  '/sales.html',
  '/reports.html',
  '/replenishment.html',
  '/admin.html',
  '/intergration.html',
  '/product_form.html',
  '/css/style.css',
  '/js/auth.js',
  '/manifest.json',
  '/icons/icon-192x192.png',
  '/icons/icon-512x512.png',
  '/icons/icon-512x512-maskable.png'
];

// API is on a different port (8000) - these are cross-origin, network-only
// Any same-origin API-style path should never be cached
const NETWORK_ONLY_PATHS = [
  '/auth/login',
  '/auth/register',
  '/auth/me',
  '/sales',
  '/products',
  '/inventory'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => cache.addAll(PRECACHE_ASSETS))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((cacheNames) => Promise.all(
        cacheNames
          .filter((name) => name !== CACHE_NAME)
          .map((name) => caches.delete(name))
      ))
      .then(() => self.clients.claim())
  );
});

function isNavigationRequest(request) {
  return request.mode === 'navigate';
}

function isApiRequest(url) {
  return url.pathname.startsWith('/api/') ||
         NETWORK_ONLY_PATHS.some(path => url.pathname.startsWith(path));
}

// Network-first strategy for pages (fallback to cache when offline)
async function networkFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  try {
    const response = await fetch(request);
    if (response && response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    const cached = await cache.match(request);
    if (cached) return cached;
    if (request.mode === 'navigate') {
      const indexResponse = await cache.match('/index.html');
      if (indexResponse) return indexResponse;
    }
    throw error;
  }
}

// Cache-first strategy for static assets
async function cacheFirst(request) {
  const cache = await caches.open(CACHE_NAME);
  const cached = await cache.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response && response.ok) {
      cache.put(request, response.clone());
    }
    return response;
  } catch (error) {
    if (request.mode === 'navigate' || request.destination === 'document') {
      const indexResponse = await cache.match('/index.html');
      if (indexResponse) return indexResponse;
    }
    throw error;
  }
}

self.addEventListener('fetch', (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Cross-origin requests (API on port 8000, CDNs): let them pass through
  if (url.origin !== self.location.origin) {
    // For CDN assets like Chart.js - cache-first with fallback
    if (url.hostname.includes('cdn.jsdelivr.net') || url.hostname.includes('cdnjs.cloudflare.com')) {
      event.respondWith(cacheFirst(request).catch(() => new Response('', { status: 503 })));
    }
    return;
  }

  // API requests: network only, with offline-friendly error
  if (isApiRequest(url)) {
    event.respondWith(
      fetch(request).catch(() => {
        return new Response(JSON.stringify({
          detail: 'You are offline. Please check your internet connection.',
          offline: true
        }), {
          status: 503,
          headers: { 'Content-Type': 'application/json' }
        });
      })
    );
    return;
  }

  // Static assets (CSS, JS, images, manifest, icons): cache-first
  if (request.destination === 'style' ||
      request.destination === 'script' ||
      request.destination === 'image' ||
      request.destination === 'font' ||
      url.pathname.endsWith('.json') ||
      url.pathname.endsWith('.png') ||
      url.pathname.endsWith('.css') ||
      url.pathname.endsWith('.js')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // Pages / navigation: network-first with fallback
  if (isNavigationRequest(request)) {
    event.respondWith(networkFirst(request).catch(() => caches.match('/index.html')));
    return;
  }

  // Default: network-first
  event.respondWith(networkFirst(request));
});

// Handle messages from the page (e.g., skip waiting)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});