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

## Cloudflare Pages

| Réglage | Valeur |
|---|---|
| Build command | *(vide)* |
| Build output directory | `site` |
| Branche de production | `main` |

## Ce qui reste à faire

- Le formulaire de contact ouvre la messagerie du visiteur (mailto). Pas de traitement côté serveur.
- Les dates et prix de la page Tarifs saisonniers sont ceux de 2025, repris tels quels.
