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

**Le Worker n'est pas encore relié à GitHub** : un push ne publie rien. On publie avec :

```
CLOUDFLARE_API_TOKEN=$CLOUDFLARE_LCCA_API_TOKEN CLOUDFLARE_ACCOUNT_ID=319ca0bc4d9526bc7655c49937e301a9 npx wrangler deploy
```

Pour que chaque push publie, relier le Worker au dépôt `Romar1-ship/lespiafs` dans le tableau de bord (Workers Builds, autorisation GitHub), avec les réglages ci-dessous.

| Réglage Workers Builds | Valeur |
|---|---|
| Build command | *(vide)* |
| Deploy command | `npx wrangler deploy` |
| Root directory | *(racine)* |

**Domaines.** `lespiafsdescollines.com` et `www.` sont rattachés au Worker (custom domains, déclarés dans `wrangler.jsonc`). Les anciens enregistrements Wix ont été supprimés le 23/10/2026. Les adresses sont courtes : Cloudflare sert `hotes.html` sous `/saisonniere/hotes`, et le générateur écrit directement ces adresses. **Ne jamais toucher aux MX, SPF et SRV : c'est la messagerie OVH.**

## La location saisonnière est éteinte

Depuis le 23/10/2026, `SAISON_ACTIVE = False` en tête de `outils/build.py` : l'autorisation de location courte durée a expiré le 22/10/2026. Les pages `saisonniere/` restent en ligne mais ne sont ni dans l'accueil, ni dans le pied de page, ni dans le sitemap, et portent un `noindex`. Les anciennes adresses Wix mènent à `/bail-mobilite/`, sauf les mentions légales et la politique de confidentialité.

**Pour tout rallumer** : passer `SAISON_ACTIVE = True`, relancer `python3 outils/build.py`, publier.

## Ce qui reste à faire

- Le formulaire de contact ouvre la messagerie du visiteur (mailto). Pas de traitement côté serveur.
- Les dates et prix de la page Tarifs saisonniers sont ceux de 2025, repris tels quels.
