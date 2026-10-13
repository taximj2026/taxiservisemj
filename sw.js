// sw.js - Service Worker for Push Notifications

self.addEventListener('install', function(event) {
    self.skipWaiting();
});

self.addEventListener('activate', function(event) {
    event.waitUntil(clients.claim());
});

self.addEventListener('push', function(event) {
    const data = event.data ? event.data.json() : {};
    const title = data.title || 'Easy Auto Taxi';
    const options = {
        body: data.body || 'നിങ്ങളുടെ ട്രിപ്പ് അപ്ഡേറ്റ് ഉണ്ട്!',
        icon: 'https://cdn-icons-png.flaticon.com/512/3448/3448339.png',
        badge: 'https://cdn-icons-png.flaticon.com/512/3448/3448339.png',
        vibrate: [300, 100, 300, 100, 300],
        requireInteraction: true,
        data: { url: data.url || '/' }
    };
    event.waitUntil(self.registration.showNotification(title, options));
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(clients.openWindow(event.notification.data.url));
});