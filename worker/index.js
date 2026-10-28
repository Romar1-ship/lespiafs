// Worker du site Les Piafs des Collines. Le site public est servi tel quel depuis site/ (assets statiques) :
// le Worker ne passe en premier que pour le board, /board et /board/*, et porte son API sous /board/api/.

import { api } from "./board.js";

// Le board ne doit jamais apparaître dans Google.
function sansIndex(r) {
  const h = new Headers(r.headers);
  h.set("x-robots-tag", "noindex, nofollow");
  return new Response(r.body, { status: r.status, statusText: r.statusText, headers: h });
}

export default {
  async fetch(request, env) {
    const p = new URL(request.url).pathname;
    if (p.startsWith("/board/api/")) return api(request, env, p.slice(11));
    if (p === "/board" || p.startsWith("/board/")) return sansIndex(await env.ASSETS.fetch(request));
    return env.ASSETS.fetch(request);
  },
};
