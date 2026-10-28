(function () {
  var API = "/board/api/";
  var parts = [].slice.call(document.querySelectorAll(".pt[id]"));
  if (!parts.length) return;
  var page = location.pathname.replace(/^\/board\//, "").replace(/index\.html$/, "").replace(/\/$/, "") || "accueil";
  function cle(id) {
    var d = (page + "--" + id).toLowerCase().normalize("NFD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (d.length <= 60) return d;
    var h = 0; for (var i = 0; i < d.length; i++) h = (h * 31 + d.charCodeAt(i)) >>> 0;
    return d.slice(0, 52).replace(/-+$/, "") + "-" + h.toString(36).slice(0, 7);
  }
  function sceau(t) { var s = el("span", "valide valide--date"); s.title = t; s.innerHTML = '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg><small></small>'; s.querySelector("small").textContent = t; return s; }
  function el(tag, cls, txt) { var e = document.createElement(tag); if (cls) e.className = cls; if (txt != null) e.textContent = txt; return e; }
  function date(s) { try { return new Date(s).toLocaleDateString("fr-FR", { day: "numeric", month: "long" }); } catch (e) { return ""; } }
  function post(route, corps) {
    return fetch(API + route, { method: "POST", credentials: "same-origin", headers: { "content-type": "application/json" }, body: JSON.stringify(corps) })
      .then(function (r) { return r.json(); });
  }
  Promise.all([fetch(API + "moi", { credentials: "same-origin" }), fetch(API + "etat", { credentials: "same-origin" })])
    .then(function (rs) { if (!rs[0].ok || !rs[1].ok) throw 0; return Promise.all([rs[0].json(), rs[1].json()]); })
    .then(function (d) { var moi = d[0], etat = d[1]; parts.forEach(function (p) { brancher(p, moi, etat); }); })
    .catch(function () {
      document.querySelectorAll('.avis[data-statique] button').forEach(function (b) {
        b.addEventListener("click", function () { alert("Connecte-toi au board avec ton email pour répondre : la page se recharge sur l'écran de connexion."); location.reload(); });
      });
    });

  function brancher(p, moi, etat) {
    var doc = cle(p.id), titre = (p.querySelector(".pt__k") || {}).textContent || p.id;
    var st = (etat.statuts || {})[doc], coms = (etat.commentaires || {})[doc] || [];
    var cont = p.querySelector(".container"), tete = p.querySelector(".pt__tete");
    if (st && st.statut === "validee") {
      var pu = tete && tete.querySelector(".puce"); if (pu) pu.remove();
      if (tete) tete.appendChild(sceau("Validé le " + date(st.date) + " par " + st.par));
      p.dataset.etat = "foi";
      return;
    }
    if (p.dataset.etat === "foi") return;
    var statique = p.querySelector('.avis[data-statique]'); if (statique) statique.remove();
    var barre = el("div", "avis"), fil = el("div", "avis__fil");
    var bc = el("button", "avis__b", "Commenter" + (coms.length ? " · " + coms.length : ""));
    bc.type = "button";
    if (moi.valideur && p.dataset.etat === "retour") {
      var bv = el("button", "avis__b avis__b--valider", "Valider"); bv.type = "button";
      var bm = el("button", "avis__b", "Demander une modification"); bm.type = "button";
      barre.appendChild(bv); barre.appendChild(bm);
      bv.addEventListener("click", function () {
        if (!confirm("Valider « " + titre.trim() + " » ? Une fois validée, cette partie ne bouge plus.")) return;
        post("statut", { doc: doc, statut: "validee", titre: titre.trim(), page: page, ancre: p.id }).then(function (r) {
          if (r.ok) { barre.remove(); fil.remove(); var pu = tete.querySelector(".puce"); if (pu) pu.remove();
            tete.appendChild(sceau("Validé le " + date(r.statut.date) + " par " + r.statut.par)); }
        });
      });
      bm.addEventListener("click", function () { ouvrir("Ce qu'il faudrait changer…"); });
    }
    function rendre() {
      fil.innerHTML = "";
      coms.forEach(function (c) {
        var li = el("div", "avis__c"); li.appendChild(el("b", null, c.auteur + " · " + date(c.date))); li.appendChild(el("p", null, c.texte)); fil.appendChild(li);
      });
      var f = el("form", "avis__form"), t = el("textarea"), ok = el("button", "avis__b avis__b--valider", "Envoyer");
      t.rows = 3; t.required = true; t.placeholder = fil.dataset.invite || "Ton commentaire"; ok.type = "submit";
      f.appendChild(t); f.appendChild(ok); fil.appendChild(f);
      f.addEventListener("submit", function (e) {
        e.preventDefault(); ok.disabled = true;
        post("commentaire", { doc: doc, texte: t.value, titre: titre.trim(), page: page, ancre: p.id }).then(function (r) {
          ok.disabled = false; if (r.ok) { coms = r.commentaires; bc.textContent = "Commenter · " + coms.length; rendre(); }
        });
      });
      return t;
    }
    function ouvrir(invite) { fil.dataset.invite = invite || ""; fil.classList.add("ouvert"); rendre().focus(); }
    barre.appendChild(bc);
    bc.addEventListener("click", function () { if (fil.classList.toggle("ouvert")) rendre().focus(); });
    cont.appendChild(barre); cont.appendChild(fil);
  }
})();
