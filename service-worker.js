/**
 * Service Worker for Trick Generator
 * Enables offline functionality and app-like experience
 */

const CACHE_NAME = "trick-generator-v0.9.0-beta";
const urlsToCache = [
	"/",
	"/index.html",
	"/sports-config.json",
	"/sports/rollerblading/app.html",
	"/sports/rollerblading/schema.json",
	"/sports/rollerblading/generator.js",
];

// Install event - cache resources
self.addEventListener("install", (event) => {
	event.waitUntil(
		caches
			.open(CACHE_NAME)
			.then((cache) => {
				console.log("Opened cache");
				return cache.addAll(urlsToCache);
			})
			.catch((err) => {
				console.log("Cache install failed:", err);
			}),
	);
});

// Fetch event - serve from cache when offline
self.addEventListener("fetch", (event) => {
	event.respondWith(
		caches.match(event.request).then((response) => {
			// Cache hit - return response
			if (response) {
				return response;
			}
			return fetch(event.request);
		}),
	);
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
	const cacheWhitelist = [CACHE_NAME];
	event.waitUntil(
		caches.keys().then((cacheNames) => {
			return Promise.all(
				cacheNames.map((cacheName) => {
					if (cacheWhitelist.indexOf(cacheName) === -1) {
						return caches.delete(cacheName);
					}
				}),
			);
		}),
	);
});
