/* ============================================================
   BOARD ATELIER · le moteur
   Chargé après plan.js et avant nav.js, sur chaque page :
     <script src="../plan.js"></script>
     <script src="../_moteur/board.js" data-base="../" defer></script>
     <script src="../_moteur/nav.js" data-base="../" defer></script>

   Ce qu'il porte :
     · l'état de chaque document, selon le cycle de l'Atelier ;
     · les commentaires, déposés sur la tâche ClickUp de mémoire ;
     · la validation, réservée au valideur de l'espace ;
     · les vues posées par un simple conteneur dans le HTML :
         <div data-board="accueil"></div>
         <div data-board="chapitre" data-chapitre="vision"></div>
         <div data-board="table"></div>
         <div data-board="archives"></div>

   Le plan (plan.js) donne les documents et leur état de départ.
   L'état vivant vient de /api/etat et l'emporte toujours.
   ============================================================ */
(function () {
  "use strict";

  var PLAN = window.PLAN || { chapitres: [], pages: [], archives: [] };
  PLAN.pages = PLAN.pages || [];
  PLAN.chapitres = PLAN.chapitres || [];
  PLAN.archives = PLAN.archives || [];

  var moi = document.currentScript;
  var BASE = (moi && moi.getAttribute("data-base")) || "";
  if (BASE && BASE.charAt(BASE.length - 1) !== "/") BASE += "/";

  // -------- le cycle d'un élément : son statut décide où il s'affiche --------
  var CYCLE = {
    idee:      { label: "Idée",        lieu: "table",    classe: "avalider" },
    retenue:   { label: "Retenu",     lieu: "table",    classe: "avalider" },
    affinage:  { label: "En affinage", lieu: "table",    classe: "avalider" },
    validee:   { label: "Validé",     lieu: "chapitre", classe: "valide" },
    lancee:    { label: "Lancé",      lieu: "chapitre", classe: "valide" },
    ecartee:   { label: "Écarté",     lieu: "archives", classe: "remplace" },
    remplacee: { label: "Remplacé",   lieu: "archives", classe: "remplace" }
  };
  var DATES = { validee: 1, lancee: 1, ecartee: 1, remplacee: 1 };
  // les gestes du valideur, dans l'ordre du cycle
  var GESTES = [["retenue", "Retenir"], ["affinage", "En affinage"], ["validee", "Valider"],
    ["lancee", "Lancer"], ["ecartee", "Écarter"]];

  var MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet", "août",
    "septembre", "octobre", "novembre", "décembre"];

  function esc(s) {
    return String(s == null ? "" : s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
      .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
  }
  function lien(p) { return /^(https?:|#|\/)/.test(p) ? p : BASE + p; }
  function cle(u) {
    var a = document.createElement("a"); a.href = u;
    return a.href.split("#")[0].split("?")[0].replace(/index\.html$/, "");
  }
  function dateFr(iso) {
    if (!iso) return "";
    var d = new Date(iso.length === 10 ? iso + "T12:00:00" : iso);
    if (isNaN(d)) return "";
    return d.getDate() + (d.getDate() === 1 ? "er" : "") + " " + MOIS[d.getMonth()]
      + (d.getFullYear() !== new Date().getFullYear() ? " " + d.getFullYear() : "");
  }
  function aujourdhui() { return new Date().toISOString().slice(0, 10); }

  // -------- l'état --------
  var etat = { statuts: {}, commentaires: {} };
  var qui = null;        // { email, nom, valideur }
  var enLigne = false;   // l'API répond : commentaires et validation ouverts

  function api(chemin, corps) {
    var o = { credentials: "same-origin", headers: {} };
    if (corps) {
      o.method = "POST";
      o.headers["content-type"] = "application/json";
      o.body = JSON.stringify(corps);
    }
    return fetch(lien("api/" + chemin), o).then(function (r) {
      return r.json().catch(function () { return {}; }).then(function (j) {
        if (!r.ok) throw new Error(j.erreur || ("erreur " + r.status));
        return j;
      });
    });
  }

  function statutDe(doc) {
    var s = etat.statuts[doc.id];
    if (s && CYCLE[s.statut]) return s;
    return { statut: CYCLE[doc.statut] ? doc.statut : "idee", date: doc.date || "", par: doc.par || "" };
  }
  function libelle(s) {
    var t = CYCLE[s.statut].label;
    if (DATES[s.statut] && s.date) t += " le " + dateFr(s.date);
    return t;
  }
  function lieu(doc) { return CYCLE[statutDe(doc).statut].lieu; }
  function docsDu(ch) { return PLAN.pages.filter(function (d) { return d.chapitre === ch; }); }
  function chapitre(id) {
    for (var i = 0; i < PLAN.chapitres.length; i++) if (PLAN.chapitres[i].id === id) return PLAN.chapitres[i];
    return null;
  }
  function nomChapitre(id) {
    var c = chapitre(id);
    return c ? (c.no ? c.no + " · " : "") + c.titre : "";
  }
  function commentairesDe(id) { return (etat.commentaires && etat.commentaires[id]) || []; }

  // le document de la page courante : sa page ou l'une de ses sous-pages
  function docIci() {
    var ici = cle(location.href), i, k, d;
    for (i = 0; i < PLAN.pages.length; i++) {
      d = PLAN.pages[i];
      if (cle(lien(d.chemin)) === ici) return d;
      if (d.sous) for (k = 0; k < d.sous.length; k++) if (cle(lien(d.sous[k][0])) === ici) return d;
    }
    return null;
  }

  var charge = Promise.all([
    api("etat").then(function (e) {
      etat.statuts = e.statuts || {};
      etat.commentaires = e.commentaires || {};
      enLigne = true;
    }).catch(function () {}),
    api("moi").then(function (m) { qui = m; }).catch(function () {})
  ]);
  // le menu n'attend jamais plus de 2,5 s : sans réponse, il part sur le plan
  var pret = Promise.race([charge, new Promise(function (r) { setTimeout(r, 2500); })]);

  window.BOARD = {
    pret: pret, plan: PLAN, cycle: CYCLE,
    statutDe: statutDe, libelle: libelle, lieu: lieu, docsDu: docsDu, nomChapitre: nomChapitre
  };

  // -------- les cartes --------
  function carte(d, avecChapitre) {
    var s = statutDe(d), n = commentairesDe(d.id).length;
    return '<a class="bd-carte" href="' + esc(lien(d.chemin)) + '">'
      + (avecChapitre ? '<span class="bd-ch">' + esc(nomChapitre(d.chapitre)) + "</span>" : "")
      + '<span class="bd-t">' + esc(d.titre) + "</span>"
      + (d.resume ? '<span class="bd-r">' + esc(d.resume) + "</span>" : "")
      + '<span class="bd-pied"><span class="bd-etat bd-' + s.statut + '">' + esc(libelle(s)) + "</span>"
      + (n ? '<span class="bd-n">' + n + " commentaire" + (n > 1 ? "s" : "") + "</span>" : "")
      + "</span></a>";
  }
  function cartes(liste, avecChapitre) {
    return '<div class="bd-cartes">' + liste.map(function (d) { return carte(d, avecChapitre); }).join("") + "</div>";
  }
  function bloc(titre, sous, contenu) {
    return '<section class="bd-bloc"><h2 class="bd-bt">' + esc(titre) + "</h2>"
      + (sous ? '<p class="bd-bs">' + esc(sous) + "</p>" : "") + contenu + "</section>";
  }
  function vide(texte) { return '<p class="bd-vide">' + esc(texte) + "</p>"; }
  function parDate(a, b) { return (statutDe(b).date || "").localeCompare(statutDe(a).date || ""); }

  // -------- les vues --------
  var VUES = {
    accueil: function () {
      var actes = PLAN.pages.filter(function (d) { return lieu(d) === "chapitre"; });
      var table = PLAN.pages.filter(function (d) { return lieu(d) === "table"; });
      var decisions = PLAN.pages.filter(function (d) { return DATES[statutDe(d).statut] && statutDe(d).date; })
        .sort(parDate).slice(0, 3);
      var coms = [];
      PLAN.pages.forEach(function (d) {
        commentairesDe(d.id).forEach(function (c) { coms.push({ d: d, c: c }); });
      });
      coms.sort(function (a, b) { return (b.c.date || "").localeCompare(a.c.date || ""); });

      var A = PLAN.accueil || {};
      var ouverts = PLAN.chapitres.filter(function (c) { return docsDu(c.id).length; }).length;
      var pl = function (n) { return n > 1 ? "s" : ""; };
      var h = '<div class="bd-chiffres">'
        + '<p><b>' + actes.length + "</b> document" + pl(actes.length) + " validé" + pl(actes.length) + "</p>"
        + '<p><b>' + table.length + "</b> en travail : en affinage, retenu</p>"
        + '<p><b>' + ouverts + "</b> chapitre" + pl(ouverts) + " ouvert" + pl(ouverts) + " sur " + PLAN.chapitres.length + "</p></div>";
      if (A.etape || A.prochaine) {
        h += '<div class="bd-etapes">'
          + (A.etape ? '<div><p class="bd-et">Étape en cours</p><p class="bd-ev">' + esc(A.etape) + "</p></div>" : "")
          + (A.prochaine ? '<div><p class="bd-et">Prochaine étape</p><p class="bd-ev">' + esc(A.prochaine) + "</p></div>" : "")
          + "</div>";
      }
      h += bloc("Les dernières décisions", null, decisions.length ? cartes(decisions, true) : vide("Aucune décision datée pour l'instant."));
      h += bloc("Ce qui se décide maintenant", "La Table à dessin, par ordre d'avancement",
        table.length ? cartes(trierTable(table).slice(0, 6), true)
          + (table.length > 6 ? '<p class="bd-suite"><a class="bd-bouton" href="' + esc(lien((PLAN.noms && PLAN.noms.tablePage) || "table/index.html")) + '">' + esc((PLAN.noms && PLAN.noms.table) || "Toute la Table à dessin") + " · " + table.length + "</a></p>" : "")
          : vide("Rien n'attend de décision."));
      if (coms.length) {
        h += bloc("Les derniers commentaires", null, '<ul class="bd-coms">' + coms.slice(0, 3).map(function (x) {
          return '<li><a href="' + esc(lien(x.d.chemin)) + '"><span class="bd-cq">' + esc(x.c.auteur) + " · " + esc(dateFr(x.c.date))
            + " · " + esc(x.d.titre) + "</span>" + esc(x.c.texte) + "</a></li>";
        }).join("") + "</ul>");
      }
      return h;
    },
    chapitre: function (el) {
      var id = el.getAttribute("data-chapitre"), docs = docsDu(id);
      var actes = docs.filter(function (d) { return lieu(d) === "chapitre"; });
      var table = docs.filter(function (d) { return lieu(d) === "table"; });
      if (!actes.length && !table.length) {
        return vide((chapitre(id) && chapitre(id).avenir) || "Ce chapitre s'ouvre plus tard dans la collaboration.");
      }
      var h = "";
      [["validee", "Validé", "Ce qui fait foi"], ["lancee", "Lancé", "En ligne ou sur le marché"], ["affinage", "En affinage", "Le travail avance, à valider"], ["retenue", "Retenu", "Gardé pour être travaillé"], ["idee", "Idées", "Pas encore trié"]].forEach(function (g) {
        var l = docs.filter(function (d) { return statutDe(d).statut === g[0]; });
        if (l.length) h += bloc(g[1] + " · " + l.length, g[2], cartes(l, false));
      });
      return h;
    },
    table: function () {
      var h = "", groupes = [["affinage", "En affinage", "Le travail avance, les commentaires sont ouverts"],
        ["retenue", "Retenu", "Gardé pour être travaillé"], ["idee", "Idées", "Tout ce qui est venu, pas encore trié"]];
      groupes.forEach(function (g) {
        var l = PLAN.pages.filter(function (d) { return statutDe(d).statut === g[0]; });
        if (l.length) h += bloc(g[1] + " · " + l.length, g[2], cartes(l, true));
      });
      return h || vide("La Table à dessin est vide : tout ce qui a été posé est tranché.");
    },
    archives: function () {
      var l = PLAN.pages.filter(function (d) { return lieu(d) === "archives"; }).sort(parDate);
      var h = l.length ? bloc("Écarté ou remplacé", "Conservé pour mémoire, un autre document fait foi", cartes(l, true)) : "";
      if (PLAN.archives.length) {
        h += bloc("Les anciennes versions du board", "Telles qu'elles étaient avant le passage au modèle de l'Atelier",
          '<ul class="bd-liste">' + PLAN.archives.map(function (a) {
            return '<li><a href="' + esc(lien(a.chemin)) + '">' + esc(a.titre) + "</a>"
              + (a.note ? '<span class="bd-cq">' + esc(a.note) + "</span>" : "") + "</li>";
          }).join("") + "</ul>");
      }
      return h || vide("Rien n'a encore été écarté.");
    }
  };
  // -------- les documents : un texte Markdown, écrit dans la page ou lu en direct dans ClickUp --------
  //   <div data-board="clickup" data-tache="869dwkf6z"></div>     la tâche, telle qu'elle est maintenant
  //   <div data-board="markdown"><script type="text/markdown">…</script></div>
  function enLigneMd(s) {
    return esc(s)
      .replace(/\\([*_\[\]()#`|.-])/g, "$1")
      .replace(/`([^`]+)`/g, "<code>$1</code>")
      .replace(/\*\*([^*]+)\*\*/g, "<b>$1</b>")
      .replace(/(^|[^*])\*([^*\s][^*]*)\*/g, "$1<i>$2</i>")
      .replace(/!\[([^\]]*)\]\(([^)\s]+)\)/g, '<img src="$2" alt="$1" loading="lazy">')
      .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
  }
  function markdown(md) {
    var l = String(md || "").replace(/\r/g, "").split("\n"), h = "", i = 0, m;
    while (i < l.length) {
      var x = l[i];
      if (!x.trim()) { i++; continue; }
      if ((m = /^(#{1,4})\s+(.*)$/.exec(x))) { var n = Math.min(4, m[1].length + 1); h += "<h" + n + ">" + enLigneMd(m[2]) + "</h" + n + ">"; i++; continue; }
      if (/^\s*(\* \* \*|---+|\*\*\*+)\s*$/.test(x)) { h += "<hr>"; i++; continue; }
      if (/^\s*\|/.test(x)) {
        var rangs = [];
        while (i < l.length && /^\s*\|/.test(l[i])) { if (!/^\s*\|[\s:|-]+\|\s*$/.test(l[i])) rangs.push(l[i].trim().replace(/^\||\|$/g, "").split("|")); i++; }
        h += '<div class="bd-table"><table>' + rangs.map(function (r, k) {
          var c = k ? "td" : "th";
          return "<tr>" + r.map(function (v) { return "<" + c + ">" + enLigneMd(v.trim()) + "</" + c + ">"; }).join("") + "</tr>";
        }).join("") + "</table></div>";
        continue;
      }
      if (/^\s*([*+-]|\d+[.)])\s+/.test(x)) {
        var ord = /^\s*\d/.test(x), it = [];
        while (i < l.length && /^\s*([*+-]|\d+[.)])\s+/.test(l[i])) { it.push(l[i].replace(/^\s*([*+-]|\d+[.)])\s+/, "")); i++; }
        h += (ord ? "<ol>" : "<ul>") + it.map(function (v) { return "<li>" + enLigneMd(v) + "</li>"; }).join("") + (ord ? "</ol>" : "</ul>");
        continue;
      }
      if (/^\s*>/.test(x)) {
        var q = [];
        while (i < l.length && /^\s*>/.test(l[i])) { q.push(l[i].replace(/^\s*>\s?/, "")); i++; }
        h += "<blockquote>" + enLigneMd(q.join(" ")) + "</blockquote>";
        continue;
      }
      var p = [];
      while (i < l.length && l[i].trim() && !/^(#{1,4}\s|\s*\||\s*([*+-]|\d+[.)])\s+|\s*>|\s*(\* \* \*|---+)\s*$)/.test(l[i])) { p.push(l[i].trim()); i++; }
      h += "<p>" + enLigneMd(p.join(" ")) + "</p>";
    }
    return h;
  }
  var CU_ETAT = { "réalisé": "fait", "accompli": "fait", "terminé": "fait", "validé": "fait", "attente de validation": "à valider",
    "en cours": "en cours", "planifié": "planifié", "à planifier": "à planifier", "reflexion": "en réflexion", "idées": "idée", "annulé": "annulé" };
  function rendreDocs() {
    Array.prototype.forEach.call(document.querySelectorAll('[data-board="markdown"]'), function (el) {
      var s = el.querySelector('script[type="text/markdown"]');
      if (s) el.innerHTML = '<div class="bd-doc">' + markdown(s.textContent) + "</div>";
    });
    Array.prototype.forEach.call(document.querySelectorAll('[data-board="clickup"]'), function (el) {
      var id = el.getAttribute("data-tache");
      el.innerHTML = vide("Lecture de la tâche dans ClickUp…");
      api("tache?id=" + encodeURIComponent(id)).then(function (t) {
        var h = '<p class="bd-source">Lu en direct dans ClickUp · <b>' + esc(CU_ETAT[t.statut] || t.statut) + "</b>"
          + (t.maj ? " · mis à jour le " + esc(dateFr(t.maj)) : "")
          + ' · <a href="' + esc(t.url) + '" target="_blank" rel="noopener">ouvrir la tâche</a></p>';
        if (t.sous && t.sous.length) {
          h += '<div class="bd-sous"><p class="bd-et">Ses étapes · ' + t.sous.length + "</p><ul>" + t.sous.map(function (s) {
            return '<li><a href="' + esc(s.url) + '" target="_blank" rel="noopener">' + esc(s.nom) + '</a><span class="bd-cu bd-cu-' + esc((CU_ETAT[s.statut] || s.statut).replace(/\W+/g, "-")) + '">' + esc(CU_ETAT[s.statut] || s.statut) + "</span></li>";
          }).join("") + "</ul></div>";
        }
        el.innerHTML = h + '<div class="bd-doc">' + markdown(t.description) + "</div>";
      }).catch(function (e) {
        el.innerHTML = vide(enLigne ? "La tâche ClickUp n'a pas pu être lue : " + e.message : "Ce document se lit en direct dans ClickUp, sur le board en ligne.");
      });
    });
  }

  var RANG = { affinage: 0, retenue: 1, idee: 2 };
  function trierTable(l) {
    return l.slice().sort(function (a, b) { return RANG[statutDe(a).statut] - RANG[statutDe(b).statut]; });
  }

  function rendreVues() {
    Array.prototype.forEach.call(document.querySelectorAll("[data-board]"), function (el) {
      var v = VUES[el.getAttribute("data-board")];
      if (v) el.innerHTML = v(el);
    });
  }

  // l'état écrit dans le bandeau d'une page suit l'état vivant
  function majEtatsEcrits(doc) {
    var s = statutDe(doc), c = CYCLE[s.statut].classe;
    Array.prototype.forEach.call(document.querySelectorAll(".hero .etat, .charte .etat, .hero [class^='etat-'], .charte [class^='etat-']"), function (e) {
      if (e.classList.contains("etat")) e.className = "etat " + c;
      else e.className = "etat-" + c;
      e.textContent = libelle(s);
    });
  }

  // -------- le volet du document : son état, ses commentaires, la validation --------
  var volet, pastille;
  function rendreVolet(doc) {
    var s = statutDe(doc), coms = commentairesDe(doc.id), h = "";
    pastille.className = "bd-pastille bd-" + s.statut;
    pastille.innerHTML = '<span class="bd-point"></span>' + esc(libelle(s))
      + (coms.length ? '<span class="bd-pn">' + coms.length + "</span>" : "");
    pastille.setAttribute("aria-label", libelle(s) + ", " + coms.length + " commentaire" + (coms.length > 1 ? "s" : "") + ". Ouvrir le volet du document");

    h += '<div class="bd-vt"><p class="bd-ch">' + esc(nomChapitre(doc.chapitre)) + "</p>"
      + '<h2>' + esc(doc.titre) + "</h2>"
      + '<p><span class="bd-etat bd-' + s.statut + '">' + esc(libelle(s)) + "</span>"
      + (s.par ? ' <span class="bd-cq">par ' + esc(s.par) + "</span>" : "") + "</p>"
      + '<button class="bd-fermer" type="button" aria-label="Fermer le volet">×</button></div>';

    if (enLigne && qui && qui.valideur) {
      h += '<div class="bd-gestes"><p class="bd-et">Ta décision</p><div>'
        + GESTES.filter(function (g) { return g[0] !== s.statut; }).map(function (g) {
          return '<button type="button" class="bd-geste bd-g-' + g[0] + '" data-statut="' + g[0] + '">' + esc(g[1]) + "</button>";
        }).join("") + "</div></div>";
    }

    h += '<div class="bd-fil"><p class="bd-et">Commentaires · ' + coms.length + "</p>";
    h += coms.length ? '<ul class="bd-coms">' + coms.map(function (c) {
      return '<li><span class="bd-cq">' + esc(c.auteur) + " · " + esc(dateFr(c.date)) + "</span>" + esc(c.texte) + "</li>";
    }).join("") + "</ul>" : vide("Aucun commentaire sur ce document.");
    h += "</div>";

    if (enLigne) {
      h += '<form class="bd-form"><label class="bd-et" for="bd-texte">Ton commentaire</label>'
        + '<textarea id="bd-texte" rows="4" maxlength="4000" required placeholder="Ce qui te parle, ce qui manque, ce qui gêne"></textarea>'
        + '<button class="bd-bouton" type="submit">Déposer</button><p class="bd-msg" role="status"></p></form>';
    } else {
      h += vide("Les commentaires et la validation s'ouvrent sur le board en ligne.");
    }
    volet.innerHTML = h;

    volet.querySelector(".bd-fermer").addEventListener("click", fermer);
    Array.prototype.forEach.call(volet.querySelectorAll(".bd-geste"), function (b) {
      b.addEventListener("click", function () {
        b.disabled = true;
        api("statut", { doc: doc.id, titre: doc.titre, statut: b.getAttribute("data-statut") }).then(function (r) {
          etat.statuts[doc.id] = r.statut;
          rendreVolet(doc); majEtatsEcrits(doc); rendreVues();
        }).catch(function (e) { b.disabled = false; alert("La décision n'est pas enregistrée : " + e.message); });
      });
    });
    var f = volet.querySelector(".bd-form");
    if (f) f.addEventListener("submit", function (e) {
      e.preventDefault();
      var t = f.querySelector("textarea"), m = f.querySelector(".bd-msg"), b = f.querySelector("button");
      if (!t.value.trim()) return;
      b.disabled = true; m.textContent = "Envoi…";
      api("commentaire", { doc: doc.id, titre: doc.titre, page: location.pathname, texte: t.value.trim() }).then(function (r) {
        etat.commentaires[doc.id] = r.commentaires;
        rendreVolet(doc);
      }).catch(function (err) { b.disabled = false; m.textContent = "Le commentaire n'est pas parti : " + err.message; });
    });
  }
  function ouvrir() { volet.classList.add("est-ouvert"); pastille.setAttribute("aria-expanded", "true"); var t = volet.querySelector("textarea"); if (t) t.focus(); }
  function fermer() { volet.classList.remove("est-ouvert"); pastille.setAttribute("aria-expanded", "false"); pastille.focus(); }

  function poserVolet(doc) {
    pastille = document.createElement("button");
    pastille.type = "button";
    pastille.setAttribute("aria-expanded", "false");
    volet = document.createElement("aside");
    volet.className = "bd-volet";
    volet.setAttribute("aria-label", "Le document, son état et ses commentaires");
    document.body.appendChild(pastille);
    document.body.appendChild(volet);
    pastille.addEventListener("click", function () { volet.classList.contains("est-ouvert") ? fermer() : ouvrir(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape" && volet.classList.contains("est-ouvert")) fermer(); });
    rendreVolet(doc);
  }

  function demarrer() {
    pret.then(function () {
      rendreVues();
      rendreDocs();
      var doc = docIci();
      if (doc) { majEtatsEcrits(doc); poserVolet(doc); }
    });
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", demarrer);
  else demarrer();
})();
