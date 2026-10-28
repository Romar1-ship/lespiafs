/* La cloche : ce que les autres ont fait depuis ma dernière visite (Géraldine, 27/10/2026).
   Pour Géraldine, les retours des clients ; pour un client, ce que Géraldine lui a envoyé ou répondu.
   Copiée dans site/ par les générateurs (board-maison.py, pages-lcca.py) ; source : atelier/tools/cloche.js.
   La cloche se pose dans la barre du menu et se relit toute seule, toutes les minutes et au retour sur l'onglet.
   La page mises-a-jour/ porte <div data-maj> : la liste s'y affiche, et l'ouvrir marque tout comme vu. */
(function () {
  var base = (document.currentScript && document.currentScript.getAttribute("data-base")) || "";
  var API = base + "api/", MAJ = base + "mises-a-jour/";
  var liste = document.querySelector("[data-maj]");
  var barre = document.querySelector(".menu__barre");
  if (!barre) return;

  var cloche = document.createElement("a");
  cloche.className = "cloche" + (liste ? " est-ici" : "");
  cloche.href = MAJ;
  cloche.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9"/><path d="M10.3 21a1.94 1.94 0 0 0 3.4 0"/></svg><span class="cloche__n" hidden></span>';
  barre.appendChild(cloche);
  var n = cloche.querySelector(".cloche__n"), titre = document.title;

  function compter(k) {
    n.hidden = !k;
    n.textContent = k > 99 ? "99+" : String(k);
    cloche.setAttribute("aria-label", k ? k + " mise" + (k > 1 ? "s" : "") + " à jour" : "Les mises à jour");
    document.title = (k ? "(" + k + ") " : "") + titre;
    try { if (navigator.setAppBadge) k ? navigator.setAppBadge(k) : navigator.clearAppBadge(); } catch (e) {}
  }
  function lire() {
    return fetch(API + "notifs", { credentials: "same-origin" }).then(function (r) { if (!r.ok) throw 0; return r.json(); });
  }
  function relire() { if (!liste) lire().then(function (d) { compter(d.nouveaux); }).catch(function () {}); }

  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };
  var quand = function (s) { var d = new Date(s); return d.toLocaleDateString("fr-FR", { day: "numeric", month: "long" }) + " à " + d.toLocaleTimeString("fr-FR", { hour: "2-digit", minute: "2-digit" }); };
  var ACTE = { commentaire: "a commenté", statut: "a changé l'état", nouveau: "a ajouté" };
  function adresse(e) {
    var p = e.page || "", a = e.ancre ? "#" + encodeURIComponent(e.ancre) : "";
    if (/^\//.test(p)) return p + a;
    p = p === "accueil" ? "" : p.replace(/^\/+|\/+$/g, "") + "/";
    var racine = e.source && /^https:\/\//.test(e.source.url || "") ? e.source.url.replace(/\/?$/, "/") : base;
    return racine + p + a;
  }
  function ligne(e, neuf) {
    var ext = e.source && e.source.url;
    return '<a class="maj__item' + (neuf ? " maj__item--neuf" : "") + '" href="' + esc(adresse(e)) + '"' + (ext ? ' target="_blank" rel="noopener"' : "") + ">"
      + '<span class="maj__k">' + (e.source ? esc(e.source.nom) + " · " : "") + esc(quand(e.date)) + "</span>"
      + '<span class="maj__t">' + esc(e.titre || e.doc) + "</span>"
      + '<span class="maj__x"><b>' + esc(e.par) + "</b> " + ACTE[e.type] + (e.type === "statut" ? " : " + esc(e.texte) : "") + "</span>"
      + (e.type !== "statut" && e.texte ? '<span class="maj__c">' + esc(e.texte.length > 220 ? e.texte.slice(0, 220) + "…" : e.texte) + "</span>" : "")
      + "</a>";
  }
  function afficher(d) {
    var neufs = d.items.filter(function (e) { return e.date > d.vu; }), vus = d.items.filter(function (e) { return e.date <= d.vu; });
    liste.innerHTML = (neufs.length ? '<h3 class="maj__h">Nouveau <span class="cloche__n">' + neufs.length + "</span></h3>" + neufs.map(function (e) { return ligne(e, true); }).join("") : '<p class="maj__rien">Rien de nouveau depuis ta dernière visite.</p>')
      + (vus.length ? '<h3 class="maj__h">Déjà vu</h3>' + vus.map(function (e) { return ligne(e, false); }).join("") : "");
    compter(0);
    if (neufs.length) fetch(API + "vu", { method: "POST", credentials: "same-origin", headers: { "content-type": "application/json" }, body: "{}" });
  }

  if (liste) lire().then(afficher).catch(function () { liste.innerHTML = '<p class="maj__rien">Les mises à jour se lisent une fois connecté au board.</p>'; });
  relire();
  setInterval(relire, 60000);
  document.addEventListener("visibilitychange", function () { if (!document.hidden) relire(); });
})();
