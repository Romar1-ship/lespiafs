/* ============================================================
   BOARD ATELIER · la barre
   Reprise de la barre du board ANAÏS (elle-même adaptée du board
   Minerya), le 22.10.2026. Le menu n'est plus écrit ici : il est tiré
   de plan.js et de l'état vivant que board.js a chargé.

   Une ligne à poser en bas de chaque page, après board.js :
     <script src="../_moteur/nav.js" data-base="../" defer></script>
   data-base est le chemin relatif de la page vers la racine du
   site : "" à la racine, "../" dans un dossier, "../../" plus bas.

   Le menu : Accueil, un item par chapitre, la Table à dessin.
   Dans un chapitre, une colonne par état : Validé, En affinage, Retenu, Idées.
   Un chapitre sans document reste au menu, en pâle.

   Posés par ce fichier, jamais écrits dans le HTML : la barre, le
   bouton de remontée, le sprite des pictos, le pliage des parties
   et le suivi du sommaire.
   ============================================================ */
(function () {
  "use strict";

  // -------- la base relative, lue sur la balise de ce script --------
  var moi = document.currentScript
    || document.querySelector('script[src*="nav.js"]');
  var BASE = "";
  if (moi) {
    if (moi.hasAttribute("data-base")) BASE = moi.getAttribute("data-base");
    else BASE = (moi.getAttribute("src") || "").replace(/nav\.js(\?.*)?$/, "");
  }
  if (BASE && BASE.charAt(BASE.length - 1) !== "/") BASE += "/";
  function lien(p) { return /^(https?:|#|\/)/.test(p) ? p : BASE + p; }
  // la clé d'une adresse : absolue, sans requête ni ancre, sans index.html
  function cle(u) {
    var a = document.createElement("a"); a.href = u;
    return a.href.split("#")[0].split("?")[0].replace(/index\.html$/, "");
  }

  var PLAN = window.PLAN || { chapitres: [], pages: [] };
  var B = window.BOARD || {
    pret: Promise.resolve(),
    lieu: function (d) { return d.statut === "validee" || d.statut === "lancee" ? "chapitre" : (d.statut === "ecartee" || d.statut === "remplacee" ? "archives" : "table"); }
  };
  var MARQUE = PLAN.marque || {};
  var ESPACE = PLAN.espace || "le board";
  var SECTIONS = [];

  // Le menu d'un chapitre : une colonne par état, titrée et comptée, dans l'ordre du cycle.
  // Les mêmes mots que la pastille de chaque page. Le nom du chapitre, dans la barre, ouvre sa page.
  var COLONNES = [["validee", "Validé"], ["lancee", "Lancé"], ["affinage", "En affinage"], ["retenue", "Retenu"], ["idee", "Idées"]];
  function etatDe(d) { return B.statutDe ? B.statutDe(d).statut : d.statut; }
  function construire() {
    var NOMS = PLAN.noms || {};
    var accueil = NOMS.accueil || "Accueil";
    SECTIONS = [{ id: "accueil", titre: accueil, page: "index.html", direct: true, groupes: [{ titre: null, liens: [["index.html", accueil]] }] }];
    PLAN.chapitres.forEach(function (ch) {
      var docs = PLAN.pages.filter(function (d) { return d.chapitre === ch.id && B.lieu(d) !== "archives"; });
      var menu = ch.menu || ch.titre;
      // menu simple : chaque chapitre est un lien direct, sa page présente ses pièces
      if (PLAN.menuSimple) {
        SECTIONS.push({ id: ch.id, titre: menu, page: ch.page, direct: true, avenir: !docs.length, groupes: [{ titre: null, liens: [[ch.page, ch.titre]].concat(docs.map(function (d) { return [d.chemin, d.titre, null, null, d.sous || null]; })) }] });
        return;
      }
      if (!docs.length) {
        SECTIONS.push({ id: ch.id, titre: menu, page: ch.page, direct: true, avenir: true, groupes: [{ titre: null, liens: [[ch.page, ch.titre]] }] });
        return;
      }
      var groupes = [{ titre: "Le chapitre", liens: [[ch.page, "Vue d'ensemble"]] }];
      COLONNES.forEach(function (c) {
        var l = docs.filter(function (d) { return etatDe(d) === c[0]; });
        if (l.length) groupes.push({ titre: c[1] + " · " + l.length, liens: l.map(function (d) { return [d.chemin, d.titre, null, null, d.sous || null]; }) });
      });
      SECTIONS.push({ id: ch.id, titre: menu, page: ch.page, groupes: groupes });
    });
    var n = PLAN.pages.filter(function (d) { return B.lieu(d) === "table"; }).length;
    var seuils = NOMS.table || "Table à dessin", pageT = NOMS.tablePage || "table/index.html";
    SECTIONS.push({ id: "table", titre: seuils + (n ? " · " + n : ""), page: pageT, direct: true, groupes: [{ titre: null, liens: [[pageT, seuils]] }] });
  }

  var MAISON = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    + '<path d="M3.6 10.4 12 3.8l8.4 6.6M5.6 9v10.2h12.8V9" stroke="currentColor"'
    + ' stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round"/></svg>';

  var CHEV = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
    + '<path d="M6 9l6 6 6-6" stroke="currentColor" stroke-width="2.4" stroke-linecap="round" stroke-linejoin="round"/></svg>';


  var CSS = ".mbn-colonnes.est-ligne{justify-content:center;padding:22px clamp(20px,3.2vw,40px) 26px}.mbn-colonnes.est-ligne .mbn-gt{display:none}.mbn-colonnes.est-ligne .mbn-g{min-width:0}.mbn-colonnes.est-ligne .mbn-g ul{display:flex!important;flex-wrap:wrap;justify-content:center;gap:12px}.mbn-colonnes.est-ligne .mbn-g a{padding:12px 22px;border:1px solid var(--line-2,rgba(43,20,32,.2));border-radius:999px;font-size:15px;text-decoration:none!important}.mbn-colonnes.est-ligne .mbn-g a:hover,.mbn-colonnes.est-ligne .mbn-g a[aria-current]{background:var(--bd-accent);border-color:var(--bd-accent);color:var(--bd-fond)}@media(max-width:1080px){.mbn-colonnes.est-ligne{justify-content:flex-start;padding:4px 0 16px 18px}.mbn-colonnes.est-ligne .mbn-g ul{justify-content:flex-start}}.mb-pages{position:sticky;z-index:8000;background:var(--bd-fond);border-bottom:1px solid var(--bd-filet)}.mb-pages__rail{max-width:1280px;margin:0 auto;display:flex;flex-wrap:wrap;justify-content:center;gap:10px;padding:14px clamp(16px,3vw,40px)}.mb-pages a{font-family:var(--bd-texte);font-weight:500;font-size:13px;letter-spacing:.16em;text-transform:uppercase;text-decoration:none;color:var(--bd-accent);padding:11px 20px;border:1px solid var(--bd-filet);border-radius:999px;transition:background .2s,color .2s}.mb-pages a:hover{background:color-mix(in srgb,var(--bd-accent) 8%,transparent)}.mb-pages a[aria-current]{background:var(--bd-accent);color:var(--bd-fond);border-color:var(--bd-accent)}@media(max-width:820px){.mb-pages__rail{flex-wrap:nowrap;justify-content:flex-start;overflow-x:auto}.mb-pages a{flex:0 0 auto}}.mbn{position:sticky;z-index:9000;background:var(--voile-barre,var(--sheet,rgba(255,255,255,.86)));-webkit-backdrop-filter:blur(10px) saturate(1.3);backdrop-filter:blur(10px) saturate(1.3);border-bottom:1px solid var(--line,rgba(43,20,32,.07));font-family:'Jost',system-ui,sans-serif;color:var(--ink,rgba(43,20,32,.84));-webkit-font-smoothing:antialiased}.mbn.sur-visuel{background:transparent;border-bottom-color:transparent;-webkit-backdrop-filter:none;backdrop-filter:none;transition:background .3s ease,border-color .3s ease,backdrop-filter .3s ease}.mbn.sur-visuel .mbn-accueil{color:rgba(255,255,255,.88)}.mbn.sur-visuel .mbn-accueil:hover,.mbn.sur-visuel .mbn-accueil[aria-current]{color:#fff}.mbn.sur-visuel .mbn-lien{color:rgba(255,255,255,.92)}.mbn.sur-visuel .mbn-lien:hover{color:#fff}.mbn.sur-visuel .mbn-item.est-ici .mbn-lien{color:#fff}.mbn.sur-visuel .mbn-item.est-ici .mbn-lien::after,.mbn.sur-visuel .mbn-accueil[aria-current]::after{background:rgba(255,255,255,.92)}.mbn.sur-visuel .mbn-chev{color:rgba(255,255,255,.82)}.mbn.sur-visuel .mbn-chev:hover{color:#fff}.mbn.sur-visuel:has(.mbn-item.est-ouvert){background:var(--voile-barre-ouverte,var(--sheet,rgba(255,255,255,.965)));border-bottom-color:var(--line,rgba(43,20,32,.07));-webkit-backdrop-filter:blur(10px) saturate(1.3);backdrop-filter:blur(10px) saturate(1.3)}.mbn.sur-visuel:has(.mbn-item.est-ouvert) .mbn-accueil,.mbn.sur-visuel:has(.mbn-item.est-ouvert) .mbn-lien,.mbn.sur-visuel:has(.mbn-item.est-ouvert) .mbn-chev{color:var(--ink-soft,rgba(43,20,32,.64))}@media(prefers-reduced-motion:reduce){.mbn.sur-visuel{transition:none}}.mbn *{box-sizing:border-box}.mbn-titre{display:none}.mbn-bar{display:grid;grid-template-columns:1fr auto 1fr;align-items:center;gap:24px;padding:11px clamp(20px,2.6vw,34px);min-height:64px}.mbn-marque{grid-column:1;justify-self:start;display:flex;align-items:baseline;gap:13px;text-decoration:none;color:inherit}.mbn-centre{grid-column:2;justify-self:center;display:flex;align-items:center;gap:14px}.mbn-droite{grid-column:3;justify-self:end;display:flex;align-items:center}@media(max-width:820px){.mbn-bar{grid-template-columns:auto 1fr auto;gap:10px}.mbn-centre{justify-self:end;gap:2px}}.mbn-accueil{display:inline-flex;align-items:center;padding:0 12px;margin-left:-12px;color:var(--stone,rgba(43,20,32,.42));text-decoration:none;flex:0 0 auto}.mbn-accueil svg{width:18px;height:18px;display:block}.mbn-accueil:hover{color:var(--ink,rgba(43,20,32,.84))}.mbn-accueil[aria-current]{color:var(--ink,rgba(43,20,32,.84))}.mbn-item{position:static;display:flex;align-items:center;flex:0 0 auto}.mbn-lien{display:inline-flex;align-items:center;padding:9px 3px 9px 17px;text-decoration:none;color:var(--ink-soft,rgba(43,20,32,.69));font-size:13.5px;white-space:nowrap}.mbn-item.est-ici .mbn-lien{color:var(--ink,rgba(43,20,32,.84));font-weight:500}.mbn-item.est-ici{box-shadow:none}.mbn-lien{position:relative}.mbn-item.est-ici .mbn-lien::after{content:\"\";position:absolute;left:17px;right:3px;bottom:3px;height:2px;border-radius:1px;background:var(--ink,rgba(43,20,32,.84))}.mbn-lien.est-direct{padding-right:17px}.mbn-item.est-ici .mbn-lien.est-direct::after{right:17px}.mbn-accueil{position:relative}.mbn-accueil[aria-current]{box-shadow:none}.mbn-accueil[aria-current]::after{content:\"\";position:absolute;left:12px;right:12px;bottom:3px;height:2px;border-radius:1px;background:var(--ink,rgba(43,20,32,.84))}.mbn-accueil{padding:9px 12px}.mbn-lien:hover{color:var(--ink,rgba(43,20,32,.84))}.mbn-item{border-radius:999px;transition:background .16s ease}.mbn-item:hover{background:color-mix(in srgb,var(--ink,#000) 6%,transparent)}.mbn-accueil{border-radius:999px;transition:background .16s ease,color .16s ease}.mbn-accueil:hover{background:color-mix(in srgb,var(--ink,#000) 6%,transparent)}.mbn.sur-visuel .mbn-item:hover,.mbn.sur-visuel .mbn-accueil:hover{background:rgba(255,255,255,.2)}.mbn-chev{display:inline-flex;align-items:center;padding:9px 16px 9px 7px;cursor:pointer;background:none;border:0;color:var(--stone,rgba(43,20,32,.42));font:inherit}.mbn-chev svg{width:13px;height:13px;display:block;transition:transform .18s ease}.mbn-chev:hover{color:var(--ink,rgba(43,20,32,.84))}.mbn-item.est-ouvert .mbn-chev svg{transform:rotate(180deg)}.mbn-item.est-ouvert .mbn-chev{color:var(--ink,rgba(43,20,32,.84))}.mbn-lien.est-bouton{cursor:pointer;background:none;border:0;font:inherit;font-size:13.5px;color:var(--ink-soft,rgba(43,20,32,.69))}@media(max-width:560px){}.mbn-volet{position:absolute;top:100%;left:0;right:0;z-index:20;display:grid;grid-template-rows:0fr;visibility:hidden;transition:grid-template-rows .4s cubic-bezier(.3,.13,.12,1),visibility 0s linear .4s;background:var(--voile-volet-menu,var(--sheet,rgba(255,255,255,.985)));-webkit-backdrop-filter:saturate(1.3) blur(10px);backdrop-filter:saturate(1.3) blur(10px);border-top:1px solid var(--line,rgba(43,20,32,.07));border-bottom:1px solid var(--line,rgba(43,20,32,.07))}.mbn-item.est-ouvert .mbn-volet{grid-template-rows:1fr;visibility:visible;transition-delay:0s}.mbn-volet-in{overflow:hidden}.mbn-colonnes{max-width:1280px;margin:0 auto;padding:34px clamp(20px,3.2vw,40px) 40px;display:flex;gap:clamp(40px,7vw,96px);flex-wrap:wrap}@media(prefers-reduced-motion:reduce){.mbn-volet{transition:none}}.mbn-g{min-width:172px;display:grid;gap:14px;align-content:start}.mbn-g.est-seul{flex:1 1 auto}.mbn-g.est-seul ul{display:grid;gap:10px 40px;grid-auto-flow:column;grid-template-rows:repeat(5,auto);grid-auto-columns:minmax(200px,1fr)}@media(max-width:900px){.mbn-g.est-seul ul{grid-auto-flow:row;grid-template-rows:none;grid-template-columns:1fr}}.mbn-gt{margin:0;padding-bottom:9px;border-bottom:1px solid var(--line,rgba(43,20,32,.07));font-size:12px;letter-spacing:.16em;text-transform:uppercase;font-family:var(--mono);color:var(--stone,rgba(43,20,32,.42));line-height:1.4;font-weight:500}.mbn-g ul{margin:0;padding:0;list-style:none;display:grid;gap:10px}.mbn-g.deux-col{min-width:0}.mbn-g.deux-col{margin-left:clamp(24px,5vw,88px)}.mbn-g.deux-col ul{grid-auto-flow:column;grid-template-columns:none;grid-auto-columns:max-content;column-gap:clamp(48px,6vw,96px)}@media(max-width:1080px){.mbn-g.deux-col{margin-left:0}.mbn-g.deux-col ul{grid-auto-flow:row!important;grid-template-rows:none!important;grid-auto-columns:auto;grid-template-columns:1fr}}.mbn-g li{display:flex;align-items:center;gap:8px}.mbn-g a{display:block;padding-block:2px;text-decoration:none;color:var(--ink,rgba(43,20,32,.84));font-size:15px;line-height:1.35;flex:1 1 auto;min-width:0;transition:color .2s ease}.mbn-g a:hover{color:var(--bd-accent)}.mbn-g a[aria-current]{font-weight:500}.mbn-g .dk{flex:0 0 auto;padding:3px 9px;border:1px solid currentColor;border-radius:20px;font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--stone,rgba(43,20,32,.42));text-decoration:none}.mbn-g .dk:hover{color:var(--bd-accent)}.mbn-g .mbn-st{display:block;padding-top:6px;margin-bottom:-4px;font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;color:var(--stone,rgba(43,20,32,.42))}.mbn-g .mbn-st:first-child{padding-top:0}.mbn-g .mbn-sep{display:block;height:0;margin:8px 0 4px;border-top:1px solid var(--line-2,rgba(43,20,32,.16));list-style:none}.mbn-g .wip{display:block;padding-block:2px;font-size:15px;color:var(--stone,rgba(43,20,32,.42))}.mbn-g .wip i{font-style:normal;font-size:12px;font-weight:500;letter-spacing:.14em;text-transform:uppercase;margin-left:8px}.mbn-g .wip .cad{display:inline-block;width:10px;height:10px;margin:-1px 5px 0 0;vertical-align:middle}.mbn-g .hors{display:inline-flex;align-items:center;gap:6px}.mbn-g .hors .fl{width:11px;height:11px;flex:0 0 auto;opacity:.55}.mbn-g .hors:hover .fl{opacity:1}.mbn-note{flex:0 0 100%;margin:0;font-size:12px;line-height:1.4;color:var(--stone,rgba(43,20,32,.42))}.mbn-haut{position:fixed;right:clamp(16px,2.4vw,28px);bottom:clamp(16px,2.4vw,28px);z-index:8500;width:44px;height:44px;border-radius:50%;border:1px solid var(--line-2,rgba(43,20,32,.16));background:var(--ground-2,#FDFDFC);color:var(--ink,rgba(43,20,32,.84));display:flex;align-items:center;justify-content:center;cursor:pointer;padding:0;box-shadow:0 6px 20px -10px rgba(43,20,32,.35);opacity:0;visibility:hidden;transform:translateY(10px);transition:opacity .22s ease,transform .22s ease,visibility 0s linear .22s,background-color .16s ease,border-color .16s ease}.mbn-haut.se-voit{opacity:1;visibility:visible;transform:none;transition-delay:0s}.mbn-haut:hover{background:color-mix(in srgb,var(--bd-accent) 12%,var(--ground-2,#FDFDFC));border-color:color-mix(in srgb,var(--bd-accent) 45%,transparent);color:var(--green-deep,#5E0030)}.mbn-haut:active{transform:translateY(1px)}.mbn-haut svg{width:19px;height:19px}@media(prefers-reduced-motion:reduce){.mbn-haut{transition:opacity .01s}}.mbn a:focus-visible,.mbn button:focus-visible{outline:2px solid var(--bd-accent);outline-offset:-2px}@media(prefers-reduced-motion:reduce){.mbn *{transition:none!important}}.mbn-burger{display:none}@media(max-width:1080px){.mbn-bar{grid-template-columns:1fr auto;gap:8px;padding:9px max(14px,env(safe-area-inset-left)) 9px max(14px,env(safe-area-inset-right));min-height:56px}.mbn-marque{grid-column:1}.mbn-droite{grid-column:2;gap:8px}.mbn-burger{display:inline-grid;place-items:center;width:34px;height:34px;border-radius:50%;border:1px solid var(--line-2,rgba(43,20,32,.16));background:none;color:var(--ink-soft,rgba(43,20,32,.64));cursor:pointer;padding:0}.mbn-burger svg{width:16px;height:16px;display:block}.mbn.sur-visuel .mbn-burger{border-color:rgba(255,255,255,.45);color:rgba(255,255,255,.92)}.mbn.sur-visuel.est-deploye .mbn-burger{border-color:var(--line-2,rgba(43,20,32,.16));color:var(--ink-soft,rgba(43,20,32,.64))}.mbn-centre{position:absolute;top:100%;left:0;right:0;z-index:30;flex-direction:column;align-items:stretch;gap:0;justify-self:stretch;padding:4px 0 max(10px,env(safe-area-inset-bottom));background:var(--ground-2,#FDFDFC);border-top:1px solid var(--line,rgba(43,20,32,.07));border-bottom:1px solid var(--line,rgba(43,20,32,.07));max-height:calc(100dvh - var(--mbn-haut,74px) + 2px);min-height:calc(100dvh - var(--mbn-haut,74px) + 2px);overflow-y:auto;box-shadow:0 20px 44px -26px rgba(43,20,32,.45)}.mbn:not(.est-deploye) .mbn-centre{display:none}.mbn-item{flex-wrap:wrap;padding:0 14px;border-radius:0}.mbn-item:hover{background:none}.mbn-lien{flex:1 1 auto;padding:13px 2px;font-size:15px}.mbn-lien.est-bouton{font-size:15px;text-align:left}.mbn-item.est-ici .mbn-lien::after{left:2px;right:2px}.mbn-lien.est-direct{padding-right:2px}.mbn-item.est-ici .mbn-lien.est-direct::after{right:2px}.mbn-chev{padding:13px 8px}.mbn-volet{position:static;order:3;flex:0 0 100%;background:none;-webkit-backdrop-filter:none;backdrop-filter:none;border-top:0;border-bottom:0;box-shadow:none}.mbn-colonnes{flex-direction:column;max-width:none;margin:0;padding:0 0 14px;gap:18px}.mbn-g{min-width:0}.mbn-item + .mbn-item{margin-top:6px;border-top:1px solid var(--line,rgba(43,20,32,.07))}.mbn-item.est-ouvert .mbn-lien{font-weight:500;color:var(--ink,rgba(43,20,32,.84))}.mbn.sur-visuel.est-deploye .mbn-item.est-ouvert .mbn-lien{color:var(--bd-encre)}.mbn-item .mbn-colonnes{padding:2px 0 18px 18px;gap:26px}.mbn-item .mbn-g ul{padding-left:12px}.mbn-item .mbn-gt{padding-bottom:7px}.mbn-g.est-seul ul{grid-auto-flow:row;grid-template-rows:none;grid-template-columns:1fr}.mbn-accueil{padding:13px 14px;margin:0;gap:10px}.mbn-accueil::after{content:\"Accueil\";font-size:15px;color:inherit}.mbn.sur-visuel.est-deploye{background:var(--voile-barre-ouverte,var(--sheet,rgba(255,255,255,.965)));border-bottom-color:var(--line,rgba(43,20,32,.07));-webkit-backdrop-filter:blur(10px) saturate(1.3);backdrop-filter:blur(10px) saturate(1.3)}.mbn.sur-visuel.est-deploye .mbn-accueil,.mbn.sur-visuel.est-deploye .mbn-lien,.mbn.sur-visuel.est-deploye .mbn-chev{color:var(--ink-soft,rgba(43,20,32,.64))}.mbn.sur-visuel.est-deploye .mbn-accueil[aria-current],.mbn.sur-visuel.est-deploye .mbn-item.est-ici .mbn-lien{color:var(--bd-encre)}.mbn.sur-visuel.est-deploye .mbn-item.est-ici .mbn-lien::after{background:currentColor}.mbn.sur-visuel.est-deploye .mbn-accueil[aria-current]::after{background:none}.mbn.sur-visuel.est-deploye .mbn-item:hover,.mbn.sur-visuel.est-deploye .mbn-accueil:hover{background:none}}.mbn-marque{align-items:center}.mbn-marque img{display:block;height:40px;width:auto}.mbn-lien,.mbn-lien.est-bouton{font-family:var(--mono);font-weight:500;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase}.mbn-item.est-ici .mbn-lien{font-weight:500}.mbn-item.est-ici .mbn-lien::after,.mbn-accueil[aria-current]::after,.mbn.sur-visuel .mbn-item.est-ici .mbn-lien::after,.mbn.sur-visuel .mbn-accueil[aria-current]::after{background:var(--gold,#C29C7B)}.mbn-g a{font-weight:400}.mbn-g a[aria-current]{font-weight:500;text-decoration:underline;text-decoration-color:var(--gold,#C29C7B);text-decoration-thickness:1px;text-underline-offset:5px}.mbn-gt{border-bottom-color:var(--gold,#C29C7B)}@media(max-width:1080px){.mbn-marque img{height:32px}.mbn-accueil::after{font-family:var(--mono);font-weight:500;font-size:12.5px;letter-spacing:.16em;text-transform:uppercase}.mbn-item.est-ouvert .mbn-lien{font-weight:500}.mbn.sur-visuel.est-deploye .mbn-item.est-ici .mbn-lien::after{background:var(--gold,#C29C7B)}}";

  var BURGER = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
    + '<path d="M2 4h12M2 8h12M2 12h12" stroke="currentColor" stroke-width="1.5" '
    + 'stroke-linecap="round"/></svg>';
  var CROIX = '<svg viewBox="0 0 16 16" fill="none" aria-hidden="true">'
    + '<path d="M3.5 3.5l9 9M12.5 3.5l-9 9" stroke="currentColor" stroke-width="1.5" '
    + 'stroke-linecap="round"/></svg>';

  function echappe(s) {
    return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function total(sec) {
    var n = 0, g;
    for (g = 0; g < sec.groupes.length; g++) n += sec.groupes[g].liens.length;
    return n;
  }

  // Les pages sœurs de la page courante : celles de son document s'il en a,
  // sinon celles de sa rubrique. Elles forment la barre sous le bandeau.
  function soeurs(ici) {
    var s, g, k, q, l;
    for (s = 0; s < SECTIONS.length; s++) {
      var sec = SECTIONS[s];
      if (sec.direct) continue;
      var toutes = [];
      for (g = 0; g < sec.groupes.length; g++) for (k = 0; k < sec.groupes[g].liens.length; k++) {
        l = sec.groupes[g].liens[k];
        if (!l[0]) continue;
        toutes.push(l);
        if (l[4]) for (q = 0; q < l[4].length; q++) if (cle(lien(l[4][q][0])) === ici) return l[4];
      }
      // une pièce d'une seule page n'a pas de barre : le menu du haut suffit
    }
    return null;
  }

  function init() {
    if (document.querySelector(".mbn")) return;
    // chaque page s'ouvre en haut, même après un clic en bas de page
    try { if ("scrollRestoration" in history) history.scrollRestoration = "manual"; } catch (e) {}
    if (!location.hash) { window.scrollTo(0, 0); addEventListener("load", function () { window.scrollTo(0, 0); }); setTimeout(function () { window.scrollTo(0, 0); }, 60); }

    var ici = cle(location.href);

    var st = document.createElement("style");
    st.textContent = CSS;
    document.head.appendChild(st);

    // sommes-nous dans cette section
    function estIci(s) {
      var g, k;
      for (g = 0; g < s.groupes.length; g++) {
        for (k = 0; k < s.groupes[g].liens.length; k++) {
          var l = s.groupes[g].liens[k];
          if (l[0] && cle(lien(l[0])) === ici) return true;
          if (l[4]) for (var q = 0; q < l[4].length; q++) if (cle(lien(l[4][q][0])) === ici) return true;
        }
      }
      return false;
    }

    var html = '<div class="mbn-bar">'
      + '<a class="mbn-marque" href="' + lien("index.html") + '" aria-label="Accueil de ' + echappe(ESPACE) + '">'
      + (MARQUE.logo ? '<img src="' + lien(MARQUE.logo) + '" alt="' + echappe(MARQUE.alt || ESPACE) + '" height="40">' : '<span class="mbn-nom">' + echappe(MARQUE.alt || ESPACE) + "</span>") + "</a>"
      + '<div class="mbn-centre">';

    var s, g, k, i = 0;
    for (s = 0; s < SECTIONS.length; s++) {
      var sec = SECTIONS[s];
      i++;
      var ouvertIci = estIci(sec);

      html += '<div class="mbn-item' + (ouvertIci ? " est-ici" : "") + (sec.avenir ? " est-avenir" : "") + '" data-section="'
        + sec.id + '">';

      // une section directe n'a pas de deroulant : le texte charge sa page
      if (sec.direct && sec.page) {
        html += '<a class="mbn-lien est-direct" href="' + lien(sec.page) + '"' + (ouvertIci ? ' aria-current="page"' : "") + ">"
          + echappe(sec.titre) + (sec.avenir ? '<span class="mbn-avenir">à venir</span>' : "") + "</a></div>";
        continue;
      }
      // le texte charge la page de section ; sans page, il ouvre le deroulant
      if (sec.page) {
        html += '<a class="mbn-lien" href="' + lien(sec.page) + '">' + echappe(sec.titre) + "</a>";
      } else {
        html += '<button class="mbn-lien est-bouton" type="button">' + echappe(sec.titre)
          + "</button>";
      }
      html += '<button class="mbn-chev" type="button" aria-expanded="false" aria-label="Ouvrir '
        + echappe(sec.titre) + '">' + CHEV + "</button>"
        + '<div class="mbn-volet"><div class="mbn-volet-in">'
        + '<div class="mbn-colonnes' + (sec.groupes.length === 1 && total(sec) <= 12 ? ' est-ligne' : '') + '">';

      for (g = 0; g < sec.groupes.length; g++) {
        var grp = sec.groupes[g];
        // au-dela de sept liens, un groupe passe sur deux colonnes : la liste
        // s'etale en largeur au lieu de faire descendre tout le volet. A sept,
        // Écosystème France reste sur une colonne et les Dossiers tiennent a
        // sa droite, sur deux colonnes de sept : le volet garde sa hauteur.
        html += '<div class="mbn-g' + (sec.groupes.length === 1 ? " est-seul" : "")
          + (grp.liens.length > 7 ? " deux-col" : "") + '">';
        if (grp.titre) html += '<p class="mbn-gt">' + echappe(grp.titre) + "</p>";
        html += grp.liens.length > 7
          ? '<ul style="grid-template-rows:repeat(' + Math.ceil(grp.liens.length / 2) + ',auto)">' : "<ul>";
        for (k = 0; k < grp.liens.length; k++) {
          var l = grp.liens[k];
          // [null, "titre"] : un mini titre qui range les liens qui le suivent
          if (l[0] === null) {
            // un titre vide est un simple trait de séparation
            html += l[1] ? '<li class="mbn-st">' + echappe(l[1]) + "</li>" : '<li class="mbn-sep" aria-hidden="true"></li>';
            continue;
          }
          if (!l[0]) {
            html += '<li><span class="wip">' + echappe(l[1]) + "<i>à venir</i></span></li>";
            continue;
          }
          var u = lien(l[0]);
          html += "<li><a href=\"" + u + "\""
            + (cle(u) === ici ? ' aria-current="page"' : "") + ">" + echappe(l[1]) + "</a>";
          html += "</li>";
        }
        html += "</ul></div>";
      }
      html += "</div></div></div></div>";
    }

    html += "</div>"
      + '<div class="mbn-droite">'
      + '<button class="mbn-burger" type="button" aria-expanded="false"'
      + ' aria-label="Ouvrir le menu">' + BURGER + "</button></div></div>";

    var bar = document.createElement("nav");
    bar.className = "mbn";
    bar.setAttribute("aria-label", "Navigation de " + ESPACE);
    bar.innerHTML = html;

    document.body.insertBefore(bar, document.body.firstChild);

    var visuelTete = document.querySelector(".hero");
    var pagesSoeurs = soeurs(ici);
    if (visuelTete && pagesSoeurs && pagesSoeurs.length > 1 && !document.querySelector(".mb-sousnav")) {
      var bp = document.createElement("nav");
      bp.className = "mb-pages";
      bp.setAttribute("aria-label", "Les pages de cette rubrique");
      var hp = '<div class="mb-pages__rail">';
      for (k = 0; k < pagesSoeurs.length; k++) {
        var up = lien(pagesSoeurs[k][0]);
        hp += '<a href="' + up + '"' + (cle(up) === ici ? ' aria-current="page"' : "") + ">" + echappe(pagesSoeurs[k][1]) + "</a>";
      }
      bp.innerHTML = hp + "</div>";
      visuelTete.parentNode.insertBefore(bp, visuelTete.nextSibling);
    }

    // -------- les deroulants : un seul ouvert a la fois --------
    var items = bar.querySelectorAll(".mbn-item");
    function fermerTout(sauf) {
      for (var j = 0; j < items.length; j++) {
        if (items[j] === sauf) continue;
        items[j].className = items[j].className.replace(" est-ouvert", "");
        var c = items[j].querySelector(".mbn-chev");
        if (c) c.setAttribute("aria-expanded", "false");
      }
    }
    function basculer(item) {
      var ouvert = item.className.indexOf("est-ouvert") !== -1;
      fermerTout(item);
      item.className = ouvert ? item.className.replace(" est-ouvert", "")
                              : item.className + " est-ouvert";
      var c = item.querySelector(".mbn-chev");
      if (c) c.setAttribute("aria-expanded", ouvert ? "false" : "true");
    }
    for (k = 0; k < items.length; k++) {
      (function (item) {
        var chev = item.querySelector(".mbn-chev");
        if (!chev) return;                            // une section directe, sans deroulant
        chev.addEventListener("click", function (e) { e.stopPropagation(); basculer(item); });
        var bouton = item.querySelector(".mbn-lien.est-bouton");
        if (bouton) {
          bouton.addEventListener("click", function (e) { e.stopPropagation(); basculer(item); });
        }
      })(items[k]);
    }
    // -------- le bouton menu, sous 1080 px --------
    // Il ne fait que basculer une classe sur la barre : tout le reste est
    // du CSS. Fermer le panneau ferme aussi les deroulants ouverts dedans,
    // sinon on rouvre le menu sur un etat qu'on avait quitte.
    var burger = bar.querySelector(".mbn-burger");
    function replier() {
      bar.className = bar.className.replace(" est-deploye", "");
      burger.setAttribute("aria-expanded", "false");
      burger.setAttribute("aria-label", "Ouvrir le menu");
      burger.innerHTML = BURGER;
      fermerTout(null);
    }
    burger.addEventListener("click", function (e) {
      e.stopPropagation();
      if (bar.className.indexOf("est-deploye") !== -1) { replier(); return; }
      bar.className += " est-deploye";
      // le panneau part du bas de la barre et descend jusqu'en bas de l'ecran
      bar.style.setProperty("--mbn-haut", Math.round(bar.getBoundingClientRect().bottom) + "px");
      burger.setAttribute("aria-expanded", "true");
      burger.setAttribute("aria-label", "Fermer le menu");
      burger.innerHTML = CROIX;
    });
    // un lien suivi ferme le panneau : sur telephone, la page change sous lui
    bar.addEventListener("click", function (e) {
      var a = e.target.closest ? e.target.closest("a[href]") : null;
      if (a && bar.contains(a)) replier();
    });
    // revenu en grand format, le panneau n'a plus lieu d'etre
    addEventListener("resize", function () {
      if (innerWidth > 1080 && bar.className.indexOf("est-deploye") !== -1) replier();
    });

    document.addEventListener("click", function (e) {
      if (!bar.contains(e.target)) { fermerTout(null); replier(); }
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") { fermerTout(null); replier(); }
    });


    // -------- la barre sur le visuel --------
    // Tant que le visuel de tete est sous la barre, elle reste transparente.
    var visuel = document.querySelector('.hero,.cover,.cov');
    if (visuel) {
      // le visuel remonte SOUS la barre, et recupere la hauteur en remplissage :
      // sans ca la barre flotte sur le fond de page, pas sur l'image.
      var glisser = function () {
        var h = bar.offsetHeight;
        visuel.style.marginTop = (-h) + 'px';
        visuel.style.paddingTop = 'calc(' + h + 'px + clamp(40px,5vw,70px))';
      };
      glisser();
      var seuil = 0;
      var mesurer = function () {
        glisser();
        var r = visuel.getBoundingClientRect();
        seuil = r.height + (window.pageYOffset || 0) + r.top - bar.offsetHeight - 8;
      };
      var suivre = function () {
        var y = window.pageYOffset || document.documentElement.scrollTop || 0;
        var dessus = y < seuil;
        if (dessus !== bar.classList.contains('sur-visuel')) {
          bar.classList.toggle('sur-visuel', dessus);
        }
      };
      mesurer(); suivre();
      window.addEventListener('scroll', suivre, { passive: true });
      window.addEventListener('resize', function () { mesurer(); suivre(); });
      if (window.ResizeObserver) new ResizeObserver(function () { mesurer(); suivre(); }).observe(visuel);
    }

    // -------- decalage des elements collants de la page --------
    // La barre s'installe en tete ; tout ce qui etait colle en haut descend d'autant.
    var colles = [];
    var tous = document.querySelectorAll("body *");
    for (k = 0; k < tous.length; k++) {
      var el = tous[k];
      if (el === bar || bar.contains(el)) continue;
      var cs = getComputedStyle(el);
      if (cs.position !== "sticky" && cs.position !== "-webkit-sticky") continue;
      if (cs.top === "auto") continue;
      colles.push({ el: el, base: parseFloat(cs.top) || 0 });
    }
    function placer() {
      bar.style.top = "0px";
      var h = bar.offsetHeight;
      for (var j = 0; j < colles.length; j++) {
        colles[j].el.style.top = (colles[j].base + h) + "px";
      }
    }
    placer();
    window.addEventListener("resize", placer);
    if (window.ResizeObserver) new ResizeObserver(placer).observe(bar);


    // -------- le bouton de remontee --------
    var haut = document.createElement("button");
    haut.className = "mbn-haut";
    haut.type = "button";
    haut.setAttribute("aria-label", "Revenir en haut de la page");
    haut.title = "Revenir en haut";
    haut.innerHTML = '<svg viewBox="0 0 24 24" fill="none" aria-hidden="true">'
      + '<path d="M12 19V5M5 12l7-7 7 7" stroke="currentColor" stroke-width="2"'
      + ' stroke-linecap="round" stroke-linejoin="round"/></svg>';
    document.body.appendChild(haut);
    haut.addEventListener("click", function () {
      var doux = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
      window.scrollTo({ top: 0, behavior: doux ? "smooth" : "auto" });
    });
    var voirHaut = function () {
      var y = window.pageYOffset || document.documentElement.scrollTop || 0;
      // il apparait une fois le visuel de tete passe, ou a defaut apres
      // un ecran de defilement
      var seuilH = visuel ? visuel.offsetHeight * .8 : window.innerHeight * .9;
      haut.classList.toggle("se-voit", y > seuilH);
    };
    voirHaut();
    window.addEventListener("scroll", voirHaut, { passive: true });
    window.addEventListener("resize", voirHaut);

    // -------- la ligne de navigation du document --------
    // Elle vit sous le hero et marque la partie ou l'on se trouve. Sans ca
    // on sait ou aller, jamais ou on est : six liens identiques du debut a
    // la fin de la lecture.
    var sous = document.querySelector(".mb-sousnav");
    if (sous) {
      var liens = sous.querySelectorAll("a[href^='#']"), cibles = [];
      for (k = 0; k < liens.length; k++) {
        var c = document.getElementById(liens[k].getAttribute("href").slice(1));
        if (c) cibles.push({ lien: liens[k], cible: c });
      }
      var marquer = function () {
        // La partie courante est la derniere dont le haut est passe sous la
        // ligne : on lit ce qui est sous les yeux, pas ce qui arrive.
        var limite = sous.getBoundingClientRect().bottom + 4, ici = null;
        for (var j = 0; j < cibles.length; j++) {
          if (cibles[j].cible.getBoundingClientRect().top <= limite) ici = cibles[j];
        }
        for (j = 0; j < cibles.length; j++) {
          if (cibles[j] === ici) cibles[j].lien.setAttribute("aria-current", "true");
          else cibles[j].lien.removeAttribute("aria-current");
        }
      };
      marquer();
      window.addEventListener("scroll", marquer, { passive: true });
      window.addEventListener("resize", marquer);
    }
  }

  /* ------------------------------------------------------------
     Les pictogrammes. Le sprite vit dans ce fichier : un <use>
     vers un fichier externe ne charge plus rien, et un fetch ne
     marche pas en file://. Il ne s'insère que sur les pages qui
     l'appellent.
     ------------------------------------------------------------ */
  var PICTOS = "<svg xmlns=\"http://www.w3.org/2000/svg\" style=\"display:none\"><defs><symbol id=\"p-reglement\" viewBox=\"0 0 24 24\"><path d=\"M5.2 2.8h8.2L18.8 8.2v13H5.2z\"/><path d=\"M13.4 2.8v5.4h5.4\"/><path d=\"M8.4 12.6h7.2M8.4 16.2h7.2\"/></symbol><symbol id=\"p-matiere\" viewBox=\"0 0 24 24\"><path d=\"M12 2.8 21 7.4v9.2L12 21.2 3 16.6V7.4z\"/><path d=\"M3 7.4 12 12l9-4.6M12 12v9.2\"/></symbol><symbol id=\"p-usine\" viewBox=\"0 0 24 24\"><path d=\"M2.8 20.8h18.4\"/><path d=\"M4.6 20.8V10.4l5 3.2V10.4l5 3.2V6.2h4.8v14.6\"/><path d=\"M8 17.4h1.6M13 17.4h1.6M18 17.4h.8\"/></symbol><symbol id=\"p-euros\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M15.4 8.6a4.4 4.4 0 0 0-6.6 1.6 5 5 0 0 0 0 3.6 4.4 4.4 0 0 0 6.6 1.6\"/><path d=\"M6.8 11h5.6M6.8 13.4h5.6\"/></symbol><symbol id=\"p-lieu\" viewBox=\"0 0 24 24\"><path d=\"M12 21.4s7-5.6 7-11a7 7 0 1 0-14 0c0 5.4 7 11 7 11z\"/><circle cx=\"12\" cy=\"10.2\" r=\"2.6\"/></symbol><symbol id=\"p-societe\" viewBox=\"0 0 24 24\"><path d=\"M3.4 20.8h17.2\"/><rect x=\"5\" y=\"8.4\" width=\"6.4\" height=\"12.4\"/><rect x=\"13\" y=\"12\" width=\"6\" height=\"8.8\"/><path d=\"M7 11.4h2.4M7 14.6h2.4M7 17.8h2.4M15 15h2M15 18h2\"/></symbol><symbol id=\"p-regard\" viewBox=\"0 0 24 24\"><path d=\"M1.8 12S5.4 5.4 12 5.4 22.2 12 22.2 12 18.6 18.6 12 18.6 1.8 12 1.8 12z\"/><circle cx=\"12\" cy=\"12\" r=\"3.2\"/></symbol><symbol id=\"p-suivi\" viewBox=\"0 0 24 24\"><rect x=\"3.2\" y=\"5\" width=\"17.6\" height=\"16\" rx=\"1.4\"/><path d=\"M3.2 10.2h17.6\"/><path d=\"M8 3v4.2M16 3v4.2\"/><path d=\"M7.6 14.2l2 2 4.4-4.4\"/></symbol><symbol id=\"p-marche\" viewBox=\"0 0 24 24\"><path d=\"M3.2 20.4V3.6\"/><path d=\"M3.2 20.4h17.2\"/><path d=\"M6.8 16.6l4-4.6 3.4 2.6 5.2-6.4\"/><path d=\"M15.6 8.2h4v4\"/></symbol><symbol id=\"p-recherche\" viewBox=\"0 0 24 24\"><path d=\"M8.2 2.9h7.6\"/><path d=\"M9.6 2.9v6.3L4.5 17.9a2.2 2.2 0 0 0 1.9 3.3h11.2a2.2 2.2 0 0 0 1.9-3.3l-5.1-8.7V2.9\"/><path d=\"M7 14.4h10\"/></symbol><symbol id=\"p-recyclage\" viewBox=\"0 0 24 24\"><path d=\"M19.6 12a7.6 7.6 0 1 1-2.7-5.8\"/><path d=\"M19.6 3.4v4.4h-4.4\"/><path d=\"M8.8 12.2l2.2 2.2 4.2-4.4\"/></symbol><symbol id=\"p-equipe\" viewBox=\"0 0 24 24\"><circle cx=\"9\" cy=\"7.8\" r=\"3.2\"/><path d=\"M2.8 20.4a6.2 6.2 0 0 1 12.4 0\"/><path d=\"M16.2 5a3.2 3.2 0 0 1 0 5.6\"/><path d=\"M17.6 14.4a6.2 6.2 0 0 1 3.6 6\"/></symbol><symbol id=\"p-calendrier\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"9\"/><path d=\"M12 6.4V12l3.8 2.3\"/></symbol><symbol id=\"p-alerte\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"8.8\"/><path d=\"M12 7.4v5.4M12 16.2v.2\"/></symbol><symbol id=\"p-fait\" viewBox=\"0 0 24 24\"><circle cx=\"12\" cy=\"12\" r=\"8.8\"/><path d=\"M8.4 12.2l2.4 2.4 4.8-5\"/></symbol><symbol id=\"p-doc\" viewBox=\"0 0 24 24\"><path d=\"M5.6 2.8h7.6L18.4 8v13.2H5.6z\"/><path d=\"M13.2 2.8V8h5.2\"/><path d=\"M8.6 12.4h6.8M8.6 16h4.4\"/></symbol><symbol id=\"p-fleche\" viewBox=\"0 0 24 24\"><path d=\"M3.4 12h17.2\"/><path d=\"M15 6.4 20.6 12 15 17.6\"/></symbol><symbol id=\"p-boucle\" viewBox=\"0 0 24 24\"><path d=\"M20 12a8 8 0 0 0-8-8 8 8 0 0 0-6.9 4\"/><path d=\"M4 12a8 8 0 0 0 8 8 8 8 0 0 0 6.9-4\"/><path d=\"M4.3 4.2 5 8l3.8-.7\"/><path d=\"M19.7 19.8 19 16l-3.8.7\"/></symbol></defs></svg>";
  function pictos() {
    if (document.getElementById("mb-pictos")) return;
    if (!document.querySelector('use[href^="#p-"], use[*|href^="#p-"]')) return;
    var hote = document.createElement("div");
    hote.id = "mb-pictos";
    hote.setAttribute("aria-hidden", "true");
    hote.style.cssText = "position:absolute;width:0;height:0;overflow:hidden";
    hote.innerHTML = PICTOS;
    document.body.insertBefore(hote, document.body.firstChild);
  }

  function plier() {
    var secs = document.querySelectorAll(".doc section");
    Array.prototype.forEach.call(secs, function (sec) {
      var tete = sec.firstElementChild;
      if (!tete || !tete.classList.contains("tete-sec") || sec.closest(".sec")) return;
      var d = document.createElement("details");
      d.className = "sec"; d.open = true;
      var s = document.createElement("summary");
      var corps = document.createElement("div");
      while (tete.nextSibling) corps.appendChild(tete.nextSibling);
      var in_ = tete.querySelector(".in-w") || tete;
      if (!tete.querySelector(".plier")) {
        var b = document.createElement("span");
        b.className = "plier"; b.setAttribute("aria-hidden", "true");
        b.innerHTML = '<span class="pl-ouvre">Déplier</span><span class="pl-ferme">Replier</span>';
        in_.appendChild(b);
      }
      s.appendChild(tete);
      d.appendChild(s); d.appendChild(corps);
      sec.appendChild(d);
    });
    // un lien vers une partie repliee la rouvre
    function ouvrir() {
      var c = location.hash && document.getElementById(location.hash.slice(1));
      var d = c && c.closest("details.sec");
      if (d && !d.open) { d.open = true; c.scrollIntoView(); }
    }
    window.addEventListener("hashchange", ouvrir); ouvrir();
  }
  function sommaire() {
    var som = document.querySelector("nav.som");
    if (!som) return;
    var liens = som.querySelectorAll("a[href^='#']"), cibles = [];
    Array.prototype.forEach.call(liens, function (a) {
      var c = document.getElementById(decodeURIComponent(a.getAttribute("href").slice(1)));
      if (!c) return;
      var sec = c.closest("section") || c;
      var no = sec.querySelector(".tete-sec .no");
      // seulement quand le lien vise la partie elle-meme (son titre), pas un element dedans
      var vise = c === sec || c.closest(".tete-sec");
      if (vise && no && /^\s*\d+\s*$/.test(no.textContent)) a.setAttribute("data-no", no.textContent.trim());
      cibles.push({ lien: a, cible: sec });
    });
    if (!cibles.length) return;
    var marquer = function () {
      var limite = window.innerHeight * 0.3, ici = null;
      for (var j = 0; j < cibles.length; j++) {
        if (cibles[j].cible.getBoundingClientRect().top <= limite) ici = cibles[j];
      }
      for (j = 0; j < cibles.length; j++) {
        if (cibles[j] === ici) cibles[j].lien.setAttribute("aria-current", "true");
        else cibles[j].lien.removeAttribute("aria-current");
      }
    };
    marquer();
    window.addEventListener("scroll", marquer, { passive: true });
    window.addEventListener("resize", marquer);
  }
  function demarrer() { B.pret.then(function () { construire(); init(); plier(); sommaire(); pictos(); }); }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
