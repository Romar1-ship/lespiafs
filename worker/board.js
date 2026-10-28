// L'API du board des Piafs, sous /board/api/. Cloudflare Access protège /board ; l'identité
// est revérifiée ici sur le jeton signé. Le board ne touche que trois tâches ClickUp et leurs
// sous-tâches : CU_FEUILLE (les étapes), CU_CARNET (les articles), CU_PLATEFORMES (les relais),
// plus la tâche mémoire CLICKUP_MEMOIRE (validations, commentaires, chiffres saisis).
//
// Les statuts se lisent sur la liste : « to do », « in progress », « complete » aujourd'hui ; les noms
// des listes LCCA (planifié, en cours, réalisé…) sont compris aussi, si la liste en change.

import { identite, profil } from "./acces.js";

const CU = "https://api.clickup.com/api/v2";
const json = (data, status = 200) => new Response(JSON.stringify(data), {
  status, headers: { "content-type": "application/json; charset=utf-8", "cache-control": "no-store", "x-robots-tag": "noindex, nofollow" },
});
const propre = (v, n) => String(v || "").replace(/[\u0000-\u0008\u000b\u000c\u000e-\u001f]/g, "").trim().slice(0, n);
const aujourdhui = () => new Date().toLocaleDateString("sv-SE", { timeZone: "Europe/Paris" });

async function cu(env, chemin, init = {}) {
  const r = await fetch(CU + chemin, { ...init, headers: { Authorization: env.CLICKUP_API_TOKEN, "content-type": "application/json", ...(init.headers || {}) } });
  if (!r.ok) throw new Error(`ClickUp ${r.status} sur ${chemin.split("?")[0]}`);
  return r.json();
}

// Les trois états du board, d'après le nom du statut ClickUp.
const FAMILLES = {
  afaire: ["to do", "à planifier", "planifié", "open"],
  encours: ["in progress", "en cours", "retardé", "attente de validation"],
  fait: ["complete", "réalisé", "accompli", "terminé", "closed"],
  ecarte: ["annulé", "cancelled"],
};
const famille = s => Object.keys(FAMILLES).find(k => FAMILLES[k].includes(String(s || "").toLowerCase())) || "afaire";

// Le nom du statut à écrire pour un état : le premier de la famille que la liste connaît.
let statutsListe = null;
async function nomStatut(env, etat) {
  if (!statutsListe) statutsListe = (await cu(env, `/list/${env.CU_LISTE}`)).statuses.map(s => s.status.toLowerCase());
  const nom = FAMILLES[etat].find(s => statutsListe.includes(s));
  if (!nom) throw Object.assign(new Error(etat === "ecarte" ? "la liste n'a pas de statut pour écarter" : "statut inconnu de la liste"), { code: 400 });
  return nom;
}

// Toute la liste en un appel (100 tâches par page) : une page du board coûte 1 ou 2 appels ClickUp, pas un par tâche.
async function liste(env) {
  const toutes = [];
  for (let page = 0; page < 5; page++) {
    const r = await cu(env, `/list/${env.CU_LISTE}/task?subtasks=true&include_closed=true&include_markdown_description=true&page=${page}`);
    toutes.push(...(r.tasks || []));
    if (r.last_page !== false || (r.tasks || []).length < 100) break;
  }
  return toutes;
}

function enfants(toutes, mere) {
  return toutes.filter(t => t.parent === mere)
    .map(t => ({ id: t.id, nom: t.name, etat: famille(t.status?.status), description: t.markdown_description || t.text_content || "", ordre: +t.orderindex || 0 }))
    .filter(t => t.etat !== "ecarte").sort((a, b) => a.ordre - b.ordre);
}

// Une sous-tâche ne se modifie que si elle appartient à l'une des tâches mères du board.
async function sousTache(env, id, mere) {
  if (!/^[a-z0-9]{6,14}$/.test(id || "")) throw Object.assign(new Error("tâche inconnue"), { code: 400 });
  const t = await cu(env, `/task/${id}`);
  if (!mere || t.parent !== mere) throw Object.assign(new Error("tâche hors du board"), { code: 403 });
  return t;
}

// -------- la mémoire du board (avis.js, cloche.js, validations des guides, chiffres saisis) --------
const STATUTS = ["idee", "retenue", "affinage", "validee", "lancee", "ecartee", "remplacee"];
const LIBELLES = { idee: "Idée", retenue: "Retenu", affinage: "En affinage", validee: "Validé", lancee: "Lancé", ecartee: "Écarté", remplacee: "Remplacé" };
const DOC = /^[a-z0-9][a-z0-9-]{0,60}$/;
const ENTETE = "**Ne pas modifier à la main.** Cette description sert de mémoire au board : l'état de chaque document, ses commentaires et leur historique. Le board la lit et la réécrit tout seul.";

async function lireMemoire(env) {
  const t = await cu(env, `/task/${env.CLICKUP_MEMOIRE}?include_markdown_description=true`);
  const m = /```json\s*([\s\S]*?)```/.exec(t.markdown_description || "");
  const etat = m ? JSON.parse(m[1]) : {};
  etat.statuts ||= {};
  etat.commentaires ||= {};
  return etat;
}
const ecrireMemoire = (env, etat) => cu(env, `/task/${env.CLICKUP_MEMOIRE}`, { method: "PUT", body: JSON.stringify({ markdown_content: `${ENTETE}\n\n\`\`\`json\n${JSON.stringify(etat, null, 1)}\n\`\`\`` }) });
const signaler = (env, ligne) => cu(env, `/task/${env.CLICKUP_MEMOIRE}/comment`, { method: "POST", body: JSON.stringify({ comment_text: ligne, notify_all: false }) });

function evenements(etat) {
  const ev = [];
  for (const [doc, l] of Object.entries(etat.commentaires || {}))
    for (const c of l) ev.push({ type: "commentaire", doc, titre: c.titre || "", page: c.page || "", ancre: c.ancre || "", par: c.auteur, email: c.email || "", date: c.date, texte: c.texte, source: null });
  for (const h of etat.historique || [])
    ev.push({ type: h.vers === "nouveau" ? "nouveau" : "statut", doc: h.doc, titre: h.titre || "", page: h.page || "", ancre: h.ancre || "", par: h.par, email: h.email || "",
      date: h.date, texte: h.vers === "nouveau" ? (h.texte || "") : (LIBELLES[h.vers] || h.vers), source: null });
  return ev;
}

async function memoire(env, route, request, moi) {
  if (route === "etat" && request.method === "GET") return json(await lireMemoire(env));
  if (route === "notifs" && request.method === "GET") {
    const etat = await lireMemoire(env);
    const depuis = Date.now() - 60 * 864e5;
    const items = evenements(etat).filter(e => e.date && Date.parse(e.date) > depuis && e.email !== moi.email && e.par !== moi.nom)
      .sort((a, b) => b.date.localeCompare(a.date)).slice(0, 60);
    const vu = (etat.vus || {})[moi.email] || "";
    return json({ vu, nouveaux: items.filter(e => e.date > vu).length, items });
  }
  if (route === "vu" && request.method === "POST") {
    const etat = await lireMemoire(env);
    etat.vus = { ...(etat.vus || {}), [moi.email]: new Date().toISOString() };
    await ecrireMemoire(env, etat);
    return json({ ok: true, vu: etat.vus[moi.email] });
  }
  const b = await request.json().catch(() => ({}));
  if (!DOC.test(b.doc || "")) return json({ erreur: "document inconnu" }, 400);
  if (route === "commentaire" && request.method === "POST") {
    const t = propre(b.texte, 4000);
    if (!t) return json({ erreur: "commentaire vide" }, 400);
    const etat = await lireMemoire(env);
    etat.commentaires[b.doc] = [...(etat.commentaires[b.doc] || []), { auteur: moi.nom, email: moi.email, date: new Date().toISOString(), page: propre(b.page, 200), ancre: propre(b.ancre, 80), titre: propre(b.titre, 160), texte: t }].slice(-500);
    await ecrireMemoire(env, etat);
    await signaler(env, `💬 ${moi.nom} sur « ${propre(b.titre, 160) || b.doc} » : ${t}`);
    return json({ ok: true, commentaires: etat.commentaires[b.doc] });
  }
  if (route === "statut" && request.method === "POST") {
    if (!moi.valideur) return json({ erreur: "la validation revient au valideur de l'espace" }, 403);
    if (!STATUTS.includes(b.statut)) return json({ erreur: "statut inconnu" }, 400);
    const etat = await lireMemoire(env);
    const avant = etat.statuts[b.doc]?.statut;
    const s = { statut: b.statut, date: aujourdhui(), par: moi.nom };
    etat.statuts[b.doc] = s;
    etat.historique = [...(etat.historique || []), { doc: b.doc, de: avant || null, vers: b.statut, date: new Date().toISOString(), par: moi.nom, email: moi.email,
      page: propre(b.page, 200), ancre: propre(b.ancre, 80), titre: propre(b.titre, 160) }].slice(-1000);
    await ecrireMemoire(env, etat);
    await signaler(env, `✅ ${moi.nom} : « ${propre(b.titre, 160) || b.doc} » passe en ${LIBELLES[b.statut]}${avant ? " (avant : " + LIBELLES[avant] + ")" : ""}.`);
    return json({ ok: true, statut: s });
  }
  return json({ erreur: "route inconnue" }, 404);
}

export async function api(request, env, route) {
  const origine = request.headers.get("origin");
  if (request.method !== "GET" && origine && origine !== new URL(request.url).origin) return json({ erreur: "origine refusée" }, 403);
  try {
    const email = await identite(request, env);
    if (!email) return json({ erreur: "visiteur non reconnu" }, 401);
    const moi = profil(email, env);
    if (route === "moi" && request.method === "GET") return json(moi);
    if (!env.CLICKUP_API_TOKEN || !env.CU_FEUILLE || !env.CU_CARNET || !env.CU_PLATEFORMES || !env.CLICKUP_MEMOIRE) return json({ erreur: "board non branché" }, 503);
    if (["etat", "commentaire", "statut", "notifs", "vu"].includes(route) && !(route === "etat" && request.method === "POST")) return memoire(env, route, request, moi);
    const b = request.method === "POST" ? await request.json().catch(() => ({})) : {};
    const MERES = { feuille: env.CU_FEUILLE, carnet: env.CU_CARNET, plateformes: env.CU_PLATEFORMES };

    if (route === "tout" && request.method === "GET") {
      const [toutes, mem] = await Promise.all([liste(env), lireMemoire(env)]);
      const etapes = enfants(toutes, env.CU_FEUILLE), articles = enfants(toutes, env.CU_CARNET), plateformes = enfants(toutes, env.CU_PLATEFORMES);
      const ecartes = mem.ecartes || {};
      return json({ moi, etapes, articles: articles.filter(t => !ecartes[t.id]), plateformes, valides: mem.guides || {}, releves: mem.releves || [] });
    }

    // Tout ce qui écrit revient au valideur de l'espace (Géraldine).
    if (!moi.valideur) return json({ erreur: "réservé à Géraldine" }, 403);

    if (route === "etat" && request.method === "POST") {
      if (!FAMILLES[b.etat]) return json({ erreur: "état inconnu" }, 400);
      const t = await sousTache(env, b.id, MERES[b.mere]);
      // Écarter une proposition : la liste n'a pas de statut « annulé », l'écart se garde dans la mémoire du board.
      if (b.etat === "ecarte") {
        const etat = await lireMemoire(env);
        etat.ecartes = { ...(etat.ecartes || {}), [t.id]: { date: aujourdhui(), par: moi.nom } };
        await ecrireMemoire(env, etat);
        await cu(env, `/task/${t.id}/comment`, { method: "POST", body: JSON.stringify({ comment_text: `✖ ${moi.nom} écarte cette proposition (${aujourdhui()}).`, notify_all: false }) });
        return json({ ok: true });
      }
      await cu(env, `/task/${t.id}`, { method: "PUT", body: JSON.stringify({ status: await nomStatut(env, b.etat) }) });
      return json({ ok: true });
    }

    // Un guide en ligne validé par Géraldine : noté dans la mémoire, signalé en commentaire pour l'ouverture à Google.
    if (route === "valider" && request.method === "POST") {
      const t = await sousTache(env, b.id, env.CU_CARNET);
      const etat = await lireMemoire(env);
      etat.guides = { ...(etat.guides || {}), [t.id]: { date: aujourdhui(), par: moi.nom } };
      etat.historique = [...(etat.historique || []), { doc: "guide-" + t.id, de: null, vers: "nouveau", texte: "Guide validé : " + t.name, date: new Date().toISOString(), par: moi.nom, email: moi.email, page: "carnet", ancre: "articles", titre: t.name }].slice(-1000);
      await ecrireMemoire(env, etat);
      await cu(env, `/task/${t.id}/comment`, { method: "POST", body: JSON.stringify({ comment_text: `✅ ${moi.nom} valide le texte de ce guide (${aujourdhui()}). À ouvrir à Google à la prochaine publication du site.`, notify_all: false }) });
      return json({ ok: true });
    }

    if (route === "ajouter" && request.method === "POST") {
      const nom = propre(b.nom, 160), consigne = propre(b.consigne, 8000);
      if (!nom) return json({ erreur: "Il manque le titre." }, 400);
      const mere = { etape: env.CU_FEUILLE, article: env.CU_CARNET, plateforme: env.CU_PLATEFORMES }[b.type];
      if (!mere) return json({ erreur: "type inconnu" }, 400);
      const t = await cu(env, `/list/${env.CU_LISTE}/task`, { method: "POST", body: JSON.stringify({ name: nom, markdown_description: consigne, status: await nomStatut(env, "afaire"), parent: mere }) });
      return json({ ok: true, id: t.id });
    }

    // Les chiffres saisis à la main (demandes, visites, baux signés…), dans la mémoire du board.
    if (route === "releve" && request.method === "POST") {
      const ind = propre(b.indicateur, 60), val = Number(String(b.valeur).replace(",", "."));
      if (!ind || !isFinite(val)) return json({ erreur: "Il manque l'indicateur ou le chiffre." }, 400);
      const date = /^\d{4}-\d{2}-\d{2}$/.test(b.date || "") ? b.date : aujourdhui();
      const etat = await lireMemoire(env);
      etat.releves = [...(etat.releves || []), { indicateur: ind, valeur: val, date, note: propre(b.note, 200), par: moi.nom, saisi: new Date().toISOString() }].slice(-2000);
      await ecrireMemoire(env, etat);
      return json({ ok: true, releves: etat.releves });
    }
    if (route === "releve-retirer" && request.method === "POST") {
      const etat = await lireMemoire(env);
      etat.releves = (etat.releves || []).filter(r => r.saisi !== b.saisi);
      await ecrireMemoire(env, etat);
      return json({ ok: true, releves: etat.releves });
    }

    return json({ erreur: "route inconnue" }, 404);
  } catch (e) {
    return json({ erreur: String(e.message || e) }, e.code || 502);
  }
}
