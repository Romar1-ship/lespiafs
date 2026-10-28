const CACHE = "board-v1";
self.addEventListener("install", () => self.skipWaiting());
self.addEventListener("activate", e => e.waitUntil(self.clients.claim()));
self.addEventListener("fetch", e => {
  const r = e.request, u = new URL(r.url);
  if (r.method !== "GET" || u.origin !== location.origin || u.pathname.includes("/api/")) return;
  e.respondWith(fetch(r).then(rep => {
    if (rep.ok && rep.type === "basic") { const copie = rep.clone(); caches.open(CACHE).then(c => c.put(r, copie)); }
    return rep;
  }).catch(() => caches.match(r)));
});
