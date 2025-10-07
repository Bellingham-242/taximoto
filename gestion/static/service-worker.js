self.addEventListener("install", (e) => {
  e.waitUntil(
    caches.open("taximoto-cache-v1").then((cache) => {
      return cache.addAll([
        "/",
        "/static/assets/img/image_1.png",
        "/static/assets/img/moto_3.jpg",
        "/static/manifest.json"
      ]);
    })
  );
  console.log("🚀 Service Worker installé");
});

self.addEventListener("fetch", (e) => {
  e.respondWith(
    caches.match(e.request).then((response) => {
      return response || fetch(e.request);
    })
  );
});
