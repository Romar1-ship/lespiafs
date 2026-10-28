# Les Piafs des Collines — lespiafsdescollines.com

Site statique, migré de Wix le 23/10/2026.

```
site/                ce qui est publié, et rien d'autre
  index.html         accueil commun : deux entrées
  saisonniere/       l'ancien site Wix, mêmes pages, même contenu, mêmes photos
  bail-mobilite/     l'offre bail mobilité, 1 à 10 mois
  _redirects         les anciennes adresses Wix renvoient vers les nouvelles (301)
  assets/            style.css, img/, icons/
outils/build.py      génère tout site/ ; on modifie ici, puis on relance
outils/board.py      génère site/board/, le board privé (contenu dans board/)
worker/              le Worker du board : /board et son API
_source/             l'aspiration du site Wix du 23/10/2026 (HTML, texte, 119 images d'origine)
```

## Modifier le site

```
python3 outils/build.py      # régénère site/
python3 -m http.server 8793 --directory site   # relecture sur http://127.0.0.1:8793
git add -A && git commit && git push           # publication
```

Le contenu de la partie saisonnière est lu mot pour mot dans `_source/site_wix_2026-10-23/blocs/*.json`.

## Cloudflare : Worker avec assets statiques

Déployé en **Worker**, pas en Pages. La configuration est dans `wrangler.jsonc` : le Worker `lespiafs` sert le dossier `site/`, avec `404.html` en page d'erreur et `_redirects` pour les anciennes adresses Wix.

**En ligne depuis le 23/10/2026**, Worker `lespiafs` du compte Cloudflare LCCA (`319ca0bc4d9526bc7655c49937e301a9`).

**On publie par le dépôt, jamais en direct** (règle de Géraldine, 24/10/2026) : on génère `site/` en local avec `python3 outils/build.py`, on commite, on pousse sur `main`, et Cloudflare déploie depuis GitHub. Aucun `wrangler deploy` lancé depuis un poste.

La liaison se fait dans le tableau de bord, car elle demande l'autorisation GitHub : Workers & Pages › `lespiafs` › Settings › Builds › Connect, dépôt `Romar1-ship/lespiafs`, branche `main`, avec les réglages ci-dessous. Tant qu'elle n'est pas faite, un push ne publie rien.

| Réglage Workers Builds | Valeur |
|---|---|
| Build command | *(vide)* |
| Deploy command | `npx wrangler deploy` |
| Root directory | *(racine)* |

**Domaines.** `lespiafsdescollines.com` et `www.` sont rattachés au Worker (custom domains, déclarés dans `wrangler.jsonc`). Les anciens enregistrements Wix ont été supprimés le 23/10/2026. Les adresses sont courtes : Cloudflare sert `hotes.html` sous `/saisonniere/hotes`, et le générateur écrit directement ces adresses. **Ne jamais toucher aux MX, SPF et SRV : c'est la messagerie OVH.**

## Le board des Piafs

`lespiafsdescollines.com/board`, réservé à Géraldine : vue d'ensemble, empreinte de marque, l'offre, À faire, le carnet (guides et propositions d'articles), les plateformes, les résultats.

- `python3 outils/board.py` écrit `site/board/` depuis `board/contenu.py`, sur le moteur commun `../LCCA-Studio/atelier/tools/board-maison.py`. On ne retouche jamais `site/board/` à la main.
- Le Worker (`worker/index.js`) ne passe en premier que pour `/board` et `/board/*` ; le site public reste servi tel quel. L'API est dans `worker/board.js`.
- **Accès** : application Cloudflare Access « Board Les Piafs » (code par e-mail), créée le 28/10/2026 sur `lespiafsdescollines.com/board` et `www`. Une seule adresse autorisée : geraldinepierrot@life-captures.fr.
- **ClickUp** : liste Roadmap Les Piafs (`1500780000000918`), tâches mères 🌿 Feuille de route, 📝 Le carnet, 🌐 Plateformes, et la mémoire du board. Les identifiants sont dans `wrangler.jsonc`.
- **Le secret** `CLICKUP_API_TOKEN` se pose une fois sur le Worker, au tableau de bord : Workers & Pages › `lespiafs` › Settings › Variables and Secrets › Add › Secret, nom `CLICKUP_API_TOKEN`, valeur du `.env` du vault. Sans lui, les pages vivantes répondent « board non branché ».
- En local : `npx wrangler dev --var MODE:dev --var DEV_EMAIL:{email} --var CLICKUP_API_TOKEN:{jeton}`.

## La location saisonnière est éteinte

Depuis le 23/10/2026, `SAISON_ACTIVE = False` en tête de `outils/build.py` : l'autorisation de location courte durée a expiré le 22/10/2026. Les pages `saisonniere/` restent en ligne mais ne sont ni dans l'accueil, ni dans le pied de page, ni dans le sitemap, et portent un `noindex`. Les anciennes adresses Wix mènent à `/bail-mobilite/`, sauf les mentions légales et la politique de confidentialité.

**Pour tout rallumer** : passer `SAISON_ACTIVE = True`, relancer `python3 outils/build.py`, publier.

## Ce qui reste à faire

- Le formulaire de contact ouvre la messagerie du visiteur (mailto). Pas de traitement côté serveur.
- Les dates et prix de la page Tarifs saisonniers sont ceux de 2025, repris tels quels.
