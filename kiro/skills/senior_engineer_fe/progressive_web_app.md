---
id: progressive_web_app
version: 1.0.0
owners: [senior_engineer_fe, frontend_lead]
tags: [pwa, service-worker, offline, web-app-manifest, cache-api, push-notifications, installable]
when_to_use: |
  When you need: offline support, installability (Add to Home Screen),
  background sync, or push notifications on the web.
  Good candidate when > 40% of users are on mobile.
inputs:
  - offline_requirements, notification_needs, mobile_traffic_percentage
outputs:
  - "pwa_design: service worker strategy + cache config + manifest + offline fallback"
---

# Progressive Web App (PWA)

> PWA = three things: HTTPS + Service Worker + Web App Manifest.
> All three required for installability. Each adds value independently.

## Web App Manifest

```json
// public/manifest.json
{
  "name": "My App",
  "short_name": "MyApp",
  "description": "Product catalog and orders",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#ffffff",
  "theme_color": "#1a73e8",
  "icons": [
    { "src": "/icons/icon-192.png", "sizes": "192x192", "type": "image/png" },
    { "src": "/icons/icon-512.png", "sizes": "512x512", "type": "image/png" },
    { "src": "/icons/icon-512-maskable.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable" }
  ]
}
```

## Service Worker caching strategies

```javascript
// public/sw.js (or use Workbox)

const CACHE_NAME = 'v1'
const STATIC_ASSETS = ['/', '/index.html', '/styles.css', '/main.js']

// Cache-first: static assets (JS, CSS, images)
self.addEventListener('fetch', event => {
  if (isStaticAsset(event.request.url)) {
    event.respondWith(
      caches.match(event.request).then(cached => cached ?? fetch(event.request))
    )
  }
})

// Network-first: API calls (fresh data preferred, cache as fallback)
self.addEventListener('fetch', event => {
  if (event.request.url.includes('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then(response => {
          const clone = response.clone()
          caches.open(CACHE_NAME).then(cache => cache.put(event.request, clone))
          return response
        })
        .catch(() => caches.match(event.request))  // offline fallback
    )
  }
})

// Stale-while-revalidate: content that can be slightly stale (product lists)
// Return cached immediately, update cache in background
```

## Workbox (recommended — don't write SW from scratch)

```javascript
// vite-plugin-pwa or next-pwa handles this
// In vite.config.ts:
import { VitePWA } from 'vite-plugin-pwa'

VitePWA({
  registerType: 'autoUpdate',
  workbox: {
    globPatterns: ['**/*.{js,css,html,ico,png,svg}'],
    runtimeCaching: [
      {
        urlPattern: /^https:\/\/api\.example\.com\//,
        handler: 'NetworkFirst',
        options: {
          cacheName: 'api-cache',
          expiration: { maxEntries: 50, maxAgeSeconds: 300 },
        },
      },
    ],
  },
})
```

## Offline page

```javascript
// Return offline.html when navigation request fails
self.addEventListener('fetch', event => {
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request).catch(() => caches.match('/offline.html'))
    )
  }
})
```

## Push notifications

```javascript
// Request permission (soft prompt first — don't immediately show OS prompt)
async function requestNotificationPermission() {
  // Show your own UI asking permission first
  const userSaid = await showInAppPrompt()
  if (!userSaid) return

  const permission = await Notification.requestPermission()
  if (permission !== 'granted') return

  const registration = await navigator.serviceWorker.ready
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: urlBase64ToUint8Array(VAPID_PUBLIC_KEY),
  })

  await api.saveSubscription(subscription)
}
```

## Anti-patterns

- **Caching everything with cache-first**: API responses go stale. Use network-first for data.
- **Not providing an offline fallback page**: users see browser's generic error page.
- **Requesting push notification permission on page load**: permission denied before user understands value.
- **SW update loops**: `registerType: 'autoUpdate'` with no user notification can cause reload loops. Show a "New version available — reload" banner.

## Validation

- [ ] Lighthouse PWA audit score 100 (installable, offline page, manifest).
- [ ] Static assets use cache-first; API calls use network-first.
- [ ] Offline fallback page exists and is cached on SW install.
- [ ] Push permission requested after user interaction, not on page load.
- [ ] SW update handled gracefully (user notified, not silent reload).
