// Les pages vivantes du board des Piafs : À faire, le carnet, les plateformes, le score.
// Une seule source pour toutes : chaque partie ne s'active que si son conteneur est là.
// Tout passe par /board/api/ (worker/board.js) ; ClickUp garde tout.

const $ = s => document.querySelector(s);
const esc = s => String(s ?? "").replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" })[c]);
let D = null;

async function appel(route, corps) {
  const r = await fetch("/board/api/" + route, corps ? { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify(corps) } : {});
  const j = await r.json().catch(() => ({}));
  if (r.status === 401) { location.reload(); throw new Error("Reconnexion…"); }
  if (!r.ok) throw new Error(j.erreur || "Une erreur est survenue.");
  return j;
}

function message(t, erreur = false) {
  const m = document.createElement("div");
  m.className = "pi-message" + (erreur ? " erreur" : "");
  m.textContent = t;
  document.body.appendChild(m);
  setTimeout(() => m.remove(), erreur ? 6000 : 3000);
}

// Le texte des descriptions ClickUp : intertitres, listes, gras, liens.
function rendre(md) {
  const ligne = s => esc(s).replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>").replace(/`([^`]+)`/g, "<code>$1</code>")
    .replace(/\[([^\]]+)\]\((https?:[^)\s]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>')
    .replace(/(^|\s)(https?:\/\/[^\s<]+)/g, '$1<a href="$2" target="_blank" rel="noopener">$2</a>');
  const out = [];
  let liste = null;
  const fermer = () => { if (liste) { out.push(`</${liste}>`); liste = null; } };
  for (const brut of String(md || "").replace(/\r/g, "").split("\n")) {
    const l = brut.trim();
    let m;
    if (!l) { fermer(); continue; }
    if ((m = /^#{1,4}\s+(.*)/.exec(l))) { fermer(); out.push(`<h3>${ligne(m[1])}</h3>`); continue; }
    if ((m = /^\d+[.)]\s+(.*)/.exec(l))) { if (liste !== "ol") { fermer(); out.push("<ol>"); liste = "ol"; } out.push(`<li>${ligne(m[1])}</li>`); continue; }
    if ((m = /^[-*•]\s+(.*)/.exec(l))) { if (liste !== "ul") { fermer(); out.push("<ul>"); liste = "ul"; } out.push(`<li>${ligne(m[1])}</li>`); continue; }
    fermer();
    out.push(`<p>${ligne(l)}</p>`);
  }
  fermer();
  return out.join("");
}

const LIB = {
  etape: { afaire: "À faire", encours: "En cours", fait: "Fait" },
  article: { afaire: "Proposé", encours: "Retenu, en écriture", fait: "En ligne" },
  plateforme: { afaire: "À faire", encours: "En préparation", fait: "En ligne" },
};

function item(t, genre, mere, actions) {
  const detail = t.description ? `<details class="pi-detail"><summary>Le détail</summary>${rendre(t.description)}</details>` : "";
  return `<li class="pi-item" data-etat="${t.etat}" data-id="${t.id}"><b>${esc(t.nom)}</b><span class="pi-badge">${LIB[genre][t.etat]}</span>${detail}`
    + `<div class="pi-actions">${actions}</div></li>`;
}

function bouton(id, mere, etat, texte, cl = "") {
  return `<button type="button" class="pi-btn ${cl}" data-id="${id}" data-mere="${mere}" data-etat="${etat}">${texte}</button>`;
}

function groupe(titre, items, genre, mere, actionsDe) {
  if (!items.length) return "";
  return `<div class="pi-groupe"><h3>${titre}<small>${items.length}</small></h3><ul class="pi-liste">${items.map(t => item(t, genre, mere, actionsDe(t))).join("")}</ul></div>`;
}

function dessinerEtapes() {
  const E = D.etapes;
  const act = t => t.etat === "fait" ? bouton(t.id, "feuille", "afaire", "Rouvrir") : bouton(t.id, "feuille", "fait", "C'est fait", "pi-btn--plein")
    + (t.etat === "afaire" ? bouton(t.id, "feuille", "encours", "Je m'y mets") : "");
  $("#pi-etapes").innerHTML = groupe("À faire", E.filter(t => t.etat === "afaire"), "etape", "feuille", act)
    + groupe("En cours", E.filter(t => t.etat === "encours"), "etape", "feuille", act)
    + groupe("Fait", E.filter(t => t.etat === "fait"), "etape", "feuille", act) || '<p class="pi-vide">Aucune étape.</p>';
}

function dessinerArticles() {
  const A = D.articles, V = D.valides || {};
  const enLigne = A.filter(t => t.etat === "fait"), retenus = A.filter(t => t.etat === "encours"), proposes = A.filter(t => t.etat === "afaire");
  const actLigne = t => V[t.id] ? `<span class="pi-valide">Validé le ${esc(V[t.id].date)}${V[t.id].par ? " par " + esc(V[t.id].par) : ""}</span>`
    : `<button type="button" class="pi-btn pi-btn--plein" data-valider="${t.id}" data-nom="${esc(t.nom)}">Je valide ce texte</button>`;
  const actProp = t => bouton(t.id, "carnet", "encours", "On l'écrit", "pi-btn--plein") + bouton(t.id, "carnet", "ecarte", "Écarter", "pi-btn--corail");
  const actRet = t => bouton(t.id, "carnet", "afaire", "Remettre en proposition");
  const valides = enLigne.filter(t => V[t.id]).length;
  $("#pi-articles").innerHTML = (enLigne.length ? `<p class="pi-k">Guides validés : ${valides} sur ${enLigne.length}</p><div class="pi-jauge"><span style="width:${Math.round(100 * valides / enLigne.length)}%"></span></div>` : "")
    + groupe("En ligne", enLigne, "article", "carnet", actLigne)
    + groupe("Retenus, en écriture", retenus, "article", "carnet", actRet)
    + groupe("Propositions à choisir", proposes, "article", "carnet", actProp) || '<p class="pi-vide">Aucun article.</p>';
}

function dessinerPlateformes() {
  const P = D.plateformes;
  const fait = P.filter(t => t.etat === "fait").length;
  const act = t => t.etat === "fait" ? bouton(t.id, "plateformes", "encours", "Pas encore en ligne")
    : bouton(t.id, "plateformes", "fait", "En ligne", "pi-btn--plein") + (t.etat === "afaire" ? bouton(t.id, "plateformes", "encours", "En préparation") : bouton(t.id, "plateformes", "afaire", "Pas commencé"));
  $("#pi-plateformes").innerHTML = `<p class="pi-k">En ligne : ${fait} sur ${P.length}</p><div class="pi-jauge"><span style="width:${P.length ? Math.round(100 * fait / P.length) : 0}%"></span></div>`
    + groupe("À faire", P.filter(t => t.etat === "afaire"), "plateforme", "plateformes", act)
    + groupe("En préparation", P.filter(t => t.etat === "encours"), "plateforme", "plateformes", act)
    + groupe("En ligne", P.filter(t => t.etat === "fait"), "plateforme", "plateformes", act);
}

function dessinerScore() {
  const n = (l, e) => l.filter(t => t.etat === e).length;
  const V = D.valides || {};
  const guides = D.articles.filter(t => t.etat === "fait");
  const dernier = ind => (D.releves || []).filter(r => r.indicateur === ind).sort((a, b) => b.date.localeCompare(a.date))[0];
  const cases = [
    [n(D.plateformes, "fait") + " / " + D.plateformes.length, "Plateformes en ligne", "ClickUp, Plateformes"],
    [guides.filter(t => V[t.id]).length + " / " + guides.length, "Guides validés", "Le carnet"],
    [n(D.articles, "encours"), "Articles en écriture", "Le carnet"],
    [n(D.etapes, "fait") + " / " + D.etapes.length, "Étapes faites", "À faire"],
    ...["Demandes reçues", "Baux signés", "Mois loués"].map(ind => { const r = dernier(ind); return [r ? r.valeur : "·", ind, r ? "Saisi le " + r.date : "À saisir"]; }),
  ];
  $("#pi-score").innerHTML = '<div class="score">' + cases.map(([v, l, s]) => `<div class="score__c"><b>${esc(v)}</b><span>${esc(l)}</span><small>${esc(s)}</small></div>`).join("") + "</div>";
  const R = (D.releves || []).slice().sort((a, b) => b.date.localeCompare(a.date));
  $("#pi-releves").innerHTML = R.length ? `<h3 class="pi-h">Les chiffres saisis</h3><ul class="pi-liste">` + R.map(r =>
    `<li class="pi-item" data-etat="fait"><b>${esc(r.indicateur)} : ${esc(r.valeur)}</b><span class="pi-badge">${esc(r.date)}</span>`
    + (r.note ? `<div class="pi-detail">${esc(r.note)}</div>` : "")
    + `<div class="pi-actions"><button type="button" class="pi-btn pi-btn--corail" data-retirer="${esc(r.saisi)}">Retirer</button></div></li>`).join("") + "</ul>" : "";
}

function dessiner() {
  if ($("#pi-etapes")) dessinerEtapes();
  if ($("#pi-articles")) dessinerArticles();
  if ($("#pi-plateformes")) dessinerPlateformes();
  if ($("#pi-score")) dessinerScore();
}

async function charger() {
  try { D = await appel("tout"); }
  catch (e) { document.querySelectorAll(".pi-vide").forEach(x => x.textContent = "La page ne s'est pas chargée : " + e.message + " Réessaie dans un instant."); return; }
  dessiner();
}

document.addEventListener("click", async ev => {
  const b = ev.target.closest("button[data-etat], button[data-valider], button[data-retirer]");
  if (!b) return;
  b.disabled = true;
  try {
    if (b.dataset.valider) {
      await appel("valider", { id: b.dataset.valider, nom: b.dataset.nom });
      message("Validé. Le guide s'ouvrira à Google à la prochaine publication du site.");
    } else if (b.dataset.retirer) {
      D.releves = (await appel("releve-retirer", { saisi: b.dataset.retirer })).releves;
      dessiner(); return;
    } else {
      await appel("etat", { id: b.dataset.id, mere: b.dataset.mere, etat: b.dataset.etat });
      message(b.dataset.etat === "ecarte" ? "Proposition écartée." : "C'est noté.");
    }
    await charger();
  } catch (e) { message(e.message, true); b.disabled = false; }
});

const ajout = $("#pi-ajout");
if (ajout) ajout.addEventListener("submit", async ev => {
  ev.preventDefault();
  const f = new FormData(ajout), btn = ajout.querySelector("button");
  btn.disabled = true;
  try {
    await appel("ajouter", { type: f.get("type"), nom: f.get("nom"), consigne: f.get("consigne") });
    ajout.reset();
    message("Ajouté dans ClickUp.");
  } catch (e) { message(e.message, true); }
  btn.disabled = false;
});

const releve = $("#pi-releve");
if (releve) releve.addEventListener("submit", async ev => {
  ev.preventDefault();
  const f = Object.fromEntries(new FormData(releve)), btn = releve.querySelector("button");
  btn.disabled = true;
  try {
    D.releves = (await appel("releve", f)).releves;
    releve.reset();
    dessiner();
    message("Chiffre enregistré.");
  } catch (e) { message(e.message, true); }
  btn.disabled = false;
});

if ($("#pi-etapes") || $("#pi-articles") || $("#pi-plateformes") || $("#pi-score")) charger();
