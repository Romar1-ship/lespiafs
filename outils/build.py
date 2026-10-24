#!/usr/bin/env python3
"""Génère site/ à partir du contenu aspiré du site Wix (_source/) et des pages écrites ici.

Lancer :  python3 outils/build.py
Le contenu saisonnier est repris mot pour mot depuis _source/site_wix_2026-10-23/blocs/*.json.
"""
import json, html, os, re, unicodedata
from pathlib import Path
import i18n

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
BLOCS = RACINE / "_source/site_wix_2026-10-23/blocs"
E = html.escape

# Interrupteur de la location saisonnière. False depuis le 23/10/2026 : la courte durée est fermée
# (autorisation échue le 22/10/2026). Les pages restent en ligne mais ne sont ni promues ni indexées,
# et les anciennes adresses Wix mènent au bail mobilité. Passer à True pour tout rallumer.
SAISON_ACTIVE = False

# Accueil désactivé le 24/10/2026 : le nom de domaine mène directement à la page bail mobilité
# (redirection temporaire, dans chaque langue). Passer à True pour rallumer l'accueil.
ACCUEIL_ACTIF = False

# Guides en relecture : en ligne et accessibles depuis le menu, mais ni indexés ni dans le sitemap.
# Passer à True une fois les articles validés par Géraldine.
GUIDES_VALIDES = False

# Pages anglaises et italiennes : relues par Themis et ouvertes à l'index le 24/10/2026.
LANGUES_VALIDEES = True

# Pages légales réécrites par Themis, complétées avec Géraldine et ouvertes le 24/10/2026.
LEGALES_VALIDEES = True

TEL = "+33 (0)6 11 94 82 35"
TEL_LIEN = "+33611948235"
MAIL = "contact@lespiafsdescollines.com"
ADRESSE = "Colline de Bellet<br>Nice, Côte d'Azur"  # l'adresse exacte n'est publiée nulle part
FACEBOOK = "https://www.facebook.com/lespiafsdescollines"
ENREGISTREMENT = "06088017951MX"

# Polices hébergées sur le site (site/assets/fonts) : Fraunces pour les titres, Sora pour le texte. Aucune requête vers Google.

# Pictos en trait fin (viewBox 32), dessinés pour le site : un <symbol> par picto, appelés par pic().
ICONES = {
    "hopital": '<path d="M4 28h24M7 28V9l9-5 9 5v19"/><path d="M12.5 11v9M19.5 11v9M12.5 15.5h7M14 28v-4h4v4"/>',
    "soleil": '<circle cx="16" cy="13" r="5"/><path d="M16 3v2M6 13H4M28 13h-2M8.9 5.9l1.4 1.4M23.1 5.9l-1.4 1.4M3 23c3-2 5-2 8 0s5 2 8 0 5-2 8 0M3 28c3-2 5-2 8 0s5 2 8 0 5-2 8 0"/>',
    "facture": '<path d="M8 4h16v24l-3-2-2.7 2-2.3-2-2.3 2-2.7-2-3 2z"/><path d="M12 11h8M12 15h8M12 19h5"/>',
    "calendrier": '<rect x="5" y="7" width="22" height="20" rx="2"/><path d="M5 13h22M11 4v6M21 4v6"/>',
    "plan": '<rect x="5" y="5" width="22" height="22"/><path d="M5 17h9v10M14 5v7M19 17h8"/>',
    "energie": '<path d="M11 5c-4 6-6 9-6 12a6 6 0 0012 0c0-3-2-6-6-12z"/><path d="M23 5l-4 9h5l-3 9"/>',
    "cle": '<circle cx="10" cy="16" r="5"/><path d="M15 16h13M24 16v4M28 16v3"/>',
    "plume": '<path d="M26 5C16 6 9 13 7 25M26 5c0 8-6 14-14 15M7 25l-2 3M5 28h22"/>',
    "wifi": '<path d="M4 12a17 17 0 0124 0M8 17a11 11 0 0116 0M12 21.5a5 5 0 018 0"/><circle cx="16" cy="25.5" r="1"/>',
    "lit": '<path d="M4 25V8M4 19h24v6M28 19v-4a3 3 0 00-3-3H14v7M8 16a2 2 0 104 0 2 2 0 10-4 0"/>',
    "valise": '<rect x="5" y="10" width="22" height="16" rx="2"/><path d="M12 10V6h8v4M11 10v16M21 10v16"/>',
    "campus": '<path d="M2 12l14-6 14 6-14 6z"/><path d="M8 15v6c4 3 12 3 16 0v-6M30 12v8"/>',
    "avion": '<path d="M14 4c0-1 4-1 4 0v9l10 6v3l-10-3v6l3 3v2l-5-1.5-5 1.5v-2l3-3v-6L4 22v-3l10-6z"/>',
    "couronne": '<path d="M5 24h22M6 24L4 10l7 6 5-9 5 9 7-6-2 14"/>',
    "puce": '<rect x="9" y="9" width="14" height="14" rx="1"/><path d="M13 9V5M19 9V5M13 27v-4M19 27v-4M9 13H5M9 19H5M27 13h-4M27 19h-4"/>',
    "parasol": '<path d="M4 15a12 9 0 0124 0zM16 15v13M16 6V4M3 28h26"/>',
    "societe": '<path d="M5 28V8h13v20M18 13h9v15M3 28h26M9 12h2M13 12h2M9 17h2M13 17h2M9 22h2M13 22h2M22 18h2M22 23h2"/>',
    "personne": '<circle cx="16" cy="10" r="5"/><path d="M6 28c0-6 4.5-10 10-10s10 4 10 10"/>',
    "repere": '<path d="M16 29s-9-8.5-9-16a9 9 0 0118 0c0 7.5-9 16-9 16z"/><circle cx="16" cy="13" r="3.2"/>',
    "verre": '<path d="M10 4h12l-1 8a5 5 0 01-10 0zM16 17v9M11 28h10M10.6 9h10.8"/>',
    "panier": '<path d="M4 12h24l-3 14H7zM10 12l4-7M22 12l-4-7M12 17v5M16 17v5M20 17v5"/>',
    "scooter": '<circle cx="8" cy="24" r="3"/><circle cx="24" cy="24" r="3"/><path d="M11 24h10l-2-9h-6M19 15l-2-7h-4M24 21l-3-8h4"/>',
    "ordi": '<rect x="6" y="7" width="20" height="13" rx="1"/><path d="M3 25h26l-2-5H5z"/>',
    "parking": '<rect x="5" y="5" width="22" height="22" rx="3"/><path d="M13 23V10h5a4 4 0 010 8h-5"/>',
    "menage": '<path d="M16 4l2.2 5.8L24 12l-5.8 2.2L16 20l-2.2-5.8L8 12l5.8-2.2zM25 19l1 2.6 2.6 1-2.6 1L25 26l-1-2.4-2.6-1 2.6-1zM7 21l.8 2 2 .8-2 .8L7 27l-.8-2.4-2-.8 2-.8z"/>',
    "maison": '<path d="M4 15L16 5l12 10M7 13v14h18V13M13 27v-7h6v7"/>',
    "douche": '<path d="M8 28V8a4 4 0 018 0v1M12 9h8l-1 3h-6zM13 16v1M16 16v2M19 16v1M14 21v1M18 21v1"/>',
    "clim": '<path d="M16 3v26M5 9.5l22 13M5 22.5l22-13M13 5l3 3 3-3M13 27l3-3 3 3"/>',
    "cuisine": '<path d="M5 14h22v4a8 8 0 01-8 8h-6a8 8 0 01-8-8zM2 14h3M27 14h3M11 10c0-2 2-2 2-4M16 10c0-2 2-2 2-4M21 10c0-2 2-2 2-4"/>',
    "machine": '<rect x="6" y="4" width="20" height="24" rx="2"/><circle cx="16" cy="17" r="6"/><path d="M6 9h20M10 6.5h2"/>',
    "piscine": '<path d="M10 22V8a3 3 0 016 0M20 22V8a3 3 0 016 0M10 12h10M10 17h10M3 25c3-2 5-2 8 0s5 2 8 0 5-2 8 0"/>',
    "table": '<path d="M3 10h26M6 10l-1 16M26 10l1 16M10 10v8h12v-8M16 4v6"/>',
    "porte": '<path d="M7 28V4h18v24M3 28h26M20 16v2"/>',
    "equipement": '<path d="M6 28V6h20v22M6 13h20M11 9.5h2M20 18v5"/>',
}
SPRITE = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + "".join(
    f'<symbol id="i-{n}" viewBox="0 0 32 32">{d}</symbol>' for n, d in ICONES.items()) + '</defs></svg>'

def pic(n, cls="pic"):
    return f'<svg class="{cls}" aria-hidden="true"><use href="#i-{n}"/></svg>'

# ---------------------------------------------------------------- contenu source
def blocs(nom):
    return json.load(open(BLOCS / f"{nom}.json", encoding="utf-8"))

def texte(nom, debut):
    """Texte complet du premier bloc de la page `nom` qui commence par `debut`."""
    for t, s, _ in blocs(nom):
        if t != "img" and s.startswith(debut):
            return s
    raise KeyError(f"{nom}: bloc introuvable « {debut} »")

def para(s):
    """Texte source -> paragraphes HTML (les lignes vides séparent les paragraphes)."""
    s = s.replace("​", "").strip()
    parts = [p.strip() for p in re.split(r"\n\s*\n", s) if p.strip()]
    return "".join(f"<p>{E(p).replace(chr(10), '<br>')}</p>" for p in parts)

def ligne(s):
    return E(re.sub(r"\s*\n\s*", " ", s.replace("​", "")).strip())

# ---------------------------------------------------------------- gabarits
NAV_SAISON = [("", "Appartement"), ("hotes", "Hôtes"), ("environs", "Explorez les environs"),
              ("ateliers", "Ateliers"), ("livre-or", "Livre d'or"), ("faq", "F.A.Q."),
              ("tarifs", "Tarifs"), ("contact", "Contact")]
NAV_MOB = [("#logement", "Le logement"), ("#prix", "Prix"), ("#acces", "Accès"),
           ("#contrat", "Contrat"), ("#fiche", "Fiche technique")]

BASE = "https://www.lespiafsdescollines.com"

def url_propre(chemin):
    c = chemin[:-10] if chemin.endswith("index.html") else (chemin[:-5] if chemin.endswith(".html") else chemin)
    return f"{BASE}/{c}"

def tete(titre, description, profondeur, chemin="index.html", jsonld=None, image="terrasse-vue-mer"):
    r = "../" * profondeur
    ld = "".join(f'<script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!doctype html>
<html lang="fr"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{E(titre)}</title>
<meta name="description" content="{E(description)}">
<link rel="icon" type="image/png" href="{r}assets/img/favicon.png">
<!--HREFLANG-->
{'<meta name="robots" content="noindex">' if chemin == "404.html" or (chemin.startswith("saisonniere/") and not SAISON_ACTIVE) or (chemin.startswith("guides/") and not GUIDES_VALIDES) or (chemin[:-5] in {s for s, _ in PAGES_LEGALES} and not LEGALES_VALIDEES) else f'<link rel="canonical" href="{url_propre(chemin)}">'}
<meta property="og:type" content="website"><meta property="og:locale" content="fr_FR"><meta property="og:site_name" content="Les Piafs des Collines">
<meta property="og:url" content="{url_propre(chemin)}">
<meta property="og:title" content="{E(titre)}"><meta property="og:description" content="{E(description)}">
<meta property="og:image" content="{BASE}/assets/img/{image}.jpg"><meta name="twitter:card" content="summary_large_image">
{ld}
<link rel="preload" href="{r}assets/fonts/fraunces-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="preload" href="{r}assets/fonts/sora-normal-latin.woff2" as="font" type="font/woff2" crossorigin>
<link rel="stylesheet" href="{r}assets/fonts/fonts.css">
<link rel="stylesheet" href="{r}assets/style.css">
</head><body>
{SPRITE}
"""

def entete(espace, courant, profondeur):
    r = "../" * profondeur
    if espace == "saison":
        liens = "".join(
            f'<a href="{r}saisonniere/{(slug + ".html") if slug else ""}"{" aria-current=\"page\"" if slug == courant else ""}>{E(lib)}</a>'
            for slug, lib in NAV_SAISON)
        cta = f'<a class="cta" href="{r}saisonniere/contact.html">Réserver</a>'
    else:
        ancre = "" if espace == "mob" else f"{r}bail-mobilite/"
        liens = "".join(f'<a href="{ancre}{a}">{E(l)}</a>' for a, l in NAV_MOB) if espace == "mob" else f'<a href="{r}bail-mobilite/">Bail mobilité</a>'
        liens += f'<a class="lien-guides" href="{r}guides/"{" aria-current=\"page\"" if espace == "guides" else ""}>Guides</a>'
        cta = f'<a class="cta" href="{ancre}#demande">Demander une disponibilité</a>'
    return f"""<header class="entete"><div class="wrap">
<a class="marque" href="{r}{"index.html" if ACCUEIL_ACTIF else "bail-mobilite/"}"><img class="m-oiseau" src="{r}assets/img/logo-oiseau-blanc.svg" alt=""><span class="m-texte"><img class="m-nom" src="{r}assets/img/logo-nom-blanc.svg" alt="Les Piafs des Collines"><span class="m-sous">Location bail mobilité</span></span></a>
<button class="burger" aria-label="Menu" onclick="this.nextElementSibling.classList.toggle('ouvert')">☰</button>
<nav class="nav">{liens}<span class="cta-mobile"><!--LANGUES-->{cta}</span></nav>
<div class="cta-droite"><!--LANGUES-->{cta}</div>
</div></header>
"""

def pied(espace, profondeur):
    r = "../" * profondeur
    s = f"{r}saisonniere/"
    if espace == "saison":
        legal = f"""<h5>Informations</h5><ul>
<li><a href="{s}conditions-generales.html">Conditions générales</a></li>
<li><a href="{s}reglement-interieur.html">Règlement intérieur</a></li>
<li><a href="{s}sante-securite.html">Santé &amp; sécurité</a></li>
<li><a href="{s}conditions-annulation.html">Conditions d'annulation</a></li>
<li><a href="{s}mentions-legales.html">Mentions légales</a></li>
<li><a href="{s}politique-de-confidentialite.html">Politique de confidentialité</a></li>
<li><a href="{s}politique-utilisation.html">Politique d'utilisation</a></li></ul>
<p class="note" style="color:#9d9ab0;margin-top:12px">* En réservant, vous acceptez nos <a href="{s}conditions-generales.html">Conditions Générales</a>, de recevoir des e-mails d'information et vous reconnaissez avoir lu notre <a href="{s}politique-de-confidentialite.html">Politique de confidentialité</a>.</p>"""
    else:
        legal = "<h5>Informations</h5><ul>" + "".join(f'<li><a href="{r}{slug}.html">{E(nom)}</a></li>' for slug, nom in PAGES_LEGALES) + "</ul>"
    return f"""<div class="store" aria-hidden="true"></div><footer class="pied"><div class="wrap"><div class="cols">
<div><h5>Les Piafs des Collines</h5><p>{ADRESSE}</p>
<p><a href="mailto:{MAIL}">{MAIL}</a><br><a href="tel:{TEL_LIEN}">{TEL}</a></p>
<p><a class="reseau" href="{FACEBOOK}" rel="noopener" aria-label="Facebook"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M13.5 21v-7.5h2.6l.4-3h-3V8.6c0-.9.3-1.5 1.5-1.5h1.6V4.4c-.3 0-1.2-.1-2.3-.1-2.3 0-3.9 1.4-3.9 4v2.2H7.8v3h2.6V21z"/></svg></a></p></div>
<div><h5>Nos locations</h5><ul>
{f'<li><a href="{r}index.html">Accueil</a></li>' if ACCUEIL_ACTIF else ""}
{f'<li><a href="{r}saisonniere/">Location saisonnière</a></li>' if SAISON_ACTIVE else ""}
<li><a href="{r}bail-mobilite/">Bail mobilité, 1 à 10 mois</a></li>
<li><a href="{r}guides/">Guides</a></li></ul></div>
<div>{legal}</div>
</div>
<p class="note droit-pied mention-pied">En nous écrivant, vous reconnaissez avoir lu nos conditions de location et notre politique de confidentialité. Vos coordonnées servent uniquement à répondre à votre demande.</p>
<p class="note droit-pied">Le contrat est régi par le droit français et rédigé en français. Les traductions sont fournies à titre d'information.</p>
<div class="bas"><span>© {2026} Les Piafs des Collines</span><span>Site <a href="https://creativeagency-lc.com" rel="noopener">LCCA</a></span></div>
</div></footer>
"""

SCRIPT_REVEAL = """<script>(function(){if(matchMedia('(prefers-reduced-motion: reduce)').matches||!('IntersectionObserver' in window))return;
const el=[...document.querySelectorAll('main section:not(.hero):not(.mob-hero) :is(.wrap,.etroit) > *')];
el.forEach(e=>e.classList.add('reveal'));const o=new IntersectionObserver(es=>es.forEach(x=>{if(x.isIntersecting){x.target.classList.add('vu');o.unobserve(x.target)}}),{rootMargin:'0px 0px -8% 0px'});
el.forEach(e=>o.observe(e))})();</script>
"""

SCRIPT_GALERIE = """<div class="visionneuse" id="vis"><button class="fermer" aria-label="Fermer">×</button><button class="prec" aria-label="Précédente">‹</button><img alt=""><button class="suiv" aria-label="Suivante">›</button></div>
<script>(function(){const L=[...document.querySelectorAll('.galerie a')];if(!L.length)return;const v=document.getElementById('vis'),im=v.querySelector('img');let i=0;
function m(n){i=(n+L.length)%L.length;im.src=L[i].href;im.alt=L[i].querySelector('img').alt;v.classList.add('ouvert')}
L.forEach((a,n)=>a.addEventListener('click',e=>{e.preventDefault();m(n)}));
v.querySelector('.fermer').onclick=()=>v.classList.remove('ouvert');v.querySelector('.prec').onclick=()=>m(i-1);v.querySelector('.suiv').onclick=()=>m(i+1);
v.addEventListener('click',e=>{if(e.target===v)v.classList.remove('ouvert')});
document.addEventListener('keydown',e=>{if(!v.classList.contains('ouvert'))return;if(e.key==='Escape')v.classList.remove('ouvert');if(e.key==='ArrowLeft')m(i-1);if(e.key==='ArrowRight')m(i+1)})})();</script>
"""

def propre(html_txt):
    """Adresses courtes : Cloudflare sert hotes.html sous /hotes et index.html sous le dossier."""
    def f(m):
        u = m.group(2)
        if u.startswith(("http", "mailto:", "tel:", "#", "data:")) or not u.endswith(".html"):
            return m.group(0)
        u = u[:-5]
        if u.endswith("index"):
            u = u[:-5] or "./"
        return f'{m.group(1)}"{u}"'
    return re.sub(r'(href=)"([^"]+)"', f, html_txt)

PAGES = []

# ---------------------------------------------------------------- langues
# Les pages de l'offre existent en français, anglais et italien. Le français est la source :
# l'anglais et l'italien sont produits par outils/i18n.py à partir de contenu/i18n/{langue}.json.
# La location saisonnière reste en français seul.
TRADUITES = {"index.html": "accueil", "bail-mobilite/index.html": "bail", "guides/index.html": "guides"}
ALTS = {}     # clé de page -> {langue: adresse}
ROUTES = {}   # langue -> {adresse française ou locale : adresse dans la langue}

def court(chemin):
    c = chemin[:-5] if chemin.endswith(".html") else chemin
    c = c[:-5] if c.endswith("index") else c
    return "/" + c

def routes():
    for chemin, cle in TRADUITES.items():
        ALTS[cle] = {"fr": court(chemin), **{l: f"/{l}{court(chemin)}" for l in i18n.LANGUES}}
    for f in sorted(GUIDES.glob("*.md")) if GUIDES.exists() else []:
        ALTS["guide:" + f.stem] = {"fr": f"/guides/{lire_md(f)['slug']}"}
        for l in i18n.LANGUES:
            g = GUIDES / l / f.name
            if g.exists():
                ALTS["guide:" + f.stem][l] = f"/{l}/guides/{lire_md(g)['slug']}"
    for l in i18n.LANGUES:
        ROUTES[l] = {}
        for alt in ALTS.values():
            if l in alt:
                ROUTES[l][alt["fr"]] = alt[l]
                ROUTES[l][alt[l][len(l) + 1:]] = alt[l]

def lien_langue(l):
    def f(chemin):
        c = chemin[:-5] if chemin.endswith(".html") else chemin
        c = c[:-5] if c.endswith("/index") else c
        return ROUTES[l].get(c) or ROUTES[l].get(c.rstrip("/") + "/")
    return f

NOMS_LANGUES = {"fr": "FR", "en": "EN", "it": "IT"}

def poser_langues(contenu, cle, l):
    alt = ALTS.get(cle, {})
    if len(alt) < 2:
        return contenu.replace("<!--HREFLANG-->", "").replace("<!--LANGUES-->", "")
    hreflang = "".join(f'<link rel="alternate" hreflang="{x}" href="{BASE}{u}">' for x, u in alt.items()) + f'<link rel="alternate" hreflang="x-default" href="{BASE}{alt["fr"]}">'
    choix = '<span class="langues">' + "".join(
        f'<a href="{u}" hreflang="{x}" lang="{x}"{" aria-current=\"true\"" if x == l else ""}>{NOMS_LANGUES[x]}</a>' for x, u in alt.items()) + "</span>"
    return contenu.replace("<!--HREFLANG-->", hreflang).replace("<!--LANGUES-->", choix)

def ecrire(chemin, contenu, cle=None, langue="fr", ignorer=()):
    """Écrit la page française et, si elle est traduite, ses versions anglaise et italienne."""
    cle = cle or TRADUITES.get(chemin)
    sorties = [] if langue != "fr" else [("fr", chemin, contenu)]
    auto = langue == "fr" and cle in ALTS and not cle.startswith("guide:") and cle != "guides"
    langues = i18n.LANGUES if auto else ((langue,) if langue != "fr" else ())
    for l in langues:
        cible = ALTS[cle][l].lstrip("/")
        cible = (cible + "index.html") if cible.endswith("/") or not cible else cible + ".html"
        t = contenu.replace(url_propre(chemin), BASE + ALTS[cle][l])
        if not LANGUES_VALIDEES:
            t = re.sub(r'<link rel="canonical" href="[^"]*">', '<meta name="robots" content="noindex">', t)
        sorties.append((l, cible, i18n.traduire(t, l, chemin, lien_langue(l), ignorer)))
    for l, c, txt in sorties:
        f = SITE / c
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(poser_langues(txt, cle, l), encoding="utf-8")
        PAGES.append(c)
        print("  ", c)

def page(chemin, titre, description, espace, courant, corps, scripts="", jsonld=None, image="terrasse-vue-mer", cle=None, langue="fr", ignorer=()):
    prof = chemin.count("/")
    contenu = tete(titre, description, prof, chemin, jsonld, image) + entete(espace, courant, prof) + "<main>" + corps + "</main>" + pied(espace, prof) + scripts + SCRIPT_REVEAL + "</body></html>\n"
    contenu = propre(contenu.replace("{R}", "../" * prof))
    ecrire(chemin, contenu, cle, langue, ignorer)

def bandeau(img, titre, sous=""):
    s = f"<p>{E(sous)}</p>" if sous else ""
    return f'<div class="bandeau" style="background-image:url({{R}}assets/img/{img}.jpg)"><div><h1>{E(titre)}</h1>{s}</div></div>'

def img(nom, alt, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{{R}}assets/img/{nom}.jpg" alt="{E(alt)}" loading="lazy">'

# ================================================================ ACCUEIL COMMUN
ADRESSE_LD = {"@type": "PostalAddress",
              "addressLocality": "Nice", "addressRegion": "Provence-Alpes-Côte d'Azur", "addressCountry": "FR"}

CARTE_SAISON = """<a class="carte-choix" href="saisonniere/">
      <span class="k">Vacances à Nice</span>
      <span class="t">Location saisonnière</span>
      <span class="d">L'appartement haut de villa, sa vue panoramique sur la Baie des Anges, sa piscine et ses ateliers.</span>
      <span class="f">Découvrir l'appartement →</span>
    </a>"""
PARA_SAISON = """<p><strong>En <a href="saisonniere/">location saisonnière</a></strong>, il accueille jusqu'à 6 voyageurs avec piscine partagée, parking privé et ateliers.</p>"""

def accueil():
    corps = f"""
<section class="hero" style="background-image:url(assets/img/hero-baie.jpg)">
  <img class="logo-hero" src="assets/img/logo-oiseau.svg" alt="" width="300" height="366">
  <h1 class="titre-hero"><img class="nom-hero" src="assets/img/logo-nom-blanc.svg" alt="Les Piafs des Collines" width="974" height="36"><img class="signature-hero" src="assets/img/logo-signature-blanc.svg" alt="Appartement vue mer panoramique sur les Collines de Bellet" width="710" height="90"><span class="h1-sous">{"Location meublée vue mer à Nice · bail mobilité et location saisonnière" if SAISON_ACTIVE else "Location meublée vue mer à Nice en bail mobilité, de 1 à 10 mois"}</span></h1>
  <div class="choix{"" if SAISON_ACTIVE else " seul"}">
    {CARTE_SAISON if SAISON_ACTIVE else ""}
    <a class="carte-choix mob" href="bail-mobilite/">
      <span class="k">Mission, formation, mutation</span>
      <span class="t">Bail mobilité, 1 à 10 mois</span>
      <span class="d">77,51 m² meublés, tout compris, arrivée autonome. Pour les professionnels en mobilité à Nice.</span>
      <span class="f">Voir l'offre →</span>
    </a>
  </div>
</section>
<div class="store" aria-hidden="true"></div>
<section class="blanc"><div class="wrap"><div class="split">
  <div>
    <span class="sur">Location meublée à Nice</span>
    <h2>{"Un appartement vue mer à Nice, pour quelques mois ou pour les vacances" if SAISON_ACTIVE else "Un appartement vue mer à Nice, pour 1 à 10 mois"}</h2>
    <p>Sur la colline de Bellet, à l'ouest de Nice, Les Piafs des Collines est un appartement entier de 77,51 m² au premier étage d'une villa, avec deux terrasses et une vue totalement dégagée sur la Baie des Anges.</p>
    <p><strong>En <a href="bail-mobilite/">location en bail mobilité à Nice</a></strong>, il loge pour 1 à 10 mois les professionnels en mission, en formation ou en mutation : meublé, tout compris à partir de 2 880 € par mois, avec arrivée autonome. Les centres hospitaliers niçois sont à 12 à 16 minutes en voiture, l'aéroport à 20 minutes, Monaco à 22 minutes et Sophia Antipolis à 28 minutes.</p>
    {PARA_SAISON if SAISON_ACTIVE else '<p>Deux vraies chambres, deux salles d\'eau, fibre, parking privé, linge fourni et ménage de sortie compris : on arrive avec sa valise. <a class="bouton azur" style="margin-top:10px" href="bail-mobilite/">Voir l\'offre bail mobilité</a></p>'}
  </div>
  {img("terrasse-vue-mer", "Terrasse de l'appartement meublé avec vue sur la Baie des Anges à Nice")}
</div></div></section>"""
    jsonld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Les Piafs des Collines", "url": BASE + "/", "inLanguage": "fr-FR"},
        {"@context": "https://schema.org", "@type": "Apartment", "name": "Les Piafs des Collines",
         "description": "Appartement meublé de 77,51 m² avec vue sur la Baie des Anges, à Nice, proposé en bail mobilité de 1 à 10 mois.",
         "url": BASE + "/", "address": ADRESSE_LD,
         "floorSize": {"@type": "QuantitativeValue", "value": 77.51, "unitCode": "MTK"}, "numberOfRooms": 3, "numberOfBedrooms": 2,
         "numberOfBathroomsTotal": 2, "image": [f"{BASE}/assets/img/{n}.jpg" for n in ("terrasse-vue-mer", "vue-baie-de-nice", "sejour-salle-a-manger", "chambre-parentale")],
         "telephone": "+33611948235", "email": MAIL},
    ]
    contenu = (tete("Location bail mobilité à Nice, appartement vue mer | Les Piafs des Collines" if not SAISON_ACTIVE else "Bail mobilité & location saisonnière à Nice, vue mer | Les Piafs des Collines",
                    "Appartement meublé de 77 m² vue Baie des Anges à Nice en bail mobilité de 1 à 10 mois : tout compris dès 2 880 €/mois, arrivée autonome." if not SAISON_ACTIVE else
                    "Appartement meublé de 77 m² vue Baie des Anges à Nice : bail mobilité de 1 à 10 mois, tout compris dès 2 880 €/mois, ou location saisonnière.",
                    0, "index.html", jsonld)
               + "<main>" + corps.replace("{R}", "") + "</main>" + pied("mob", 0) + SCRIPT_REVEAL + "</body></html>\n")
    ecrire("index.html", propre(contenu))
    if not ACCUEIL_ACTIF:
        for l in ("", "en/", "it/"):
            renvoi(f"{l}index.html", f"/{l}bail-mobilite/")

# ================================================================ SAISONNIÈRE
GALERIE = [("terrasse-vue-mer", "La terrasse principale face à la mer", True),
           ("piscine-vue-aerienne", "La piscine et le jardin vus du ciel", False),
           ("vue-baie-de-nice", "La vue sur la Baie de Nice", False),
           ("sejour-salle-a-manger", "Le séjour et la salle à manger", False),
           ("cuisine-sejour", "La cuisine ouverte sur le séjour", False),
           ("cuisine-ilot", "L'îlot de la cuisine", False),
           ("chambre-parentale", "La chambre parentale", False),
           ("chambre-2", "La chambre 2", False),
           ("salon-canape-lit", "Le salon", False),
           ("cuisine-equipee", "La cuisine équipée", False),
           ("jardin", "Le jardin", False),
           ("cuisine-tabourets", "Les tabourets de l'îlot", False),
           ("linge-accueil", "Le linge d'accueil", False)]

EQUIPEMENTS = [
  ("Chauffage & Climatisation", [("climatisation", "Climatisation réversible", "Chambres et salon"), ("chauffage", "Chauffage au sol", "Salle de bain, couloir côté chambres")]),
  ("Chambres & linge", [("draps", "Draps", ""), ("oreillers", "Couettes d'été et couettes d'hiver", ""), ("stores", "Équipements de base", "Serviettes, draps et papier toilette"), ("dressing2", "Espaces de rangement pour les vêtements", "Grands placards dans les chambres et pour le salon"),
                        ("lave-linge", "Lave-linge", ""), ("seche-linge", "Sèche-linge", ""), ("fer-repasser", "Fer à repasser vapeur", ""), ("cintre", "Étendoir à linge et cintres", "")]),
  ("Cuisine & Salle à manger", [("cuisine", "Cuisine", "Espace où les voyageurs peuvent cuisiner"), ("plaques", "Plaques à induction", ""), ("frigo", "Réfrigérateur + congélateur", "Et un mini réfrigérateur"), ("four", "Four", ""), ("four2", "Four à micro-ondes", ""),
                                ("lave-vaisselle", "Lave-vaisselle", ""), ("table", "Table à manger", ""), ("vaisselle", "Équipement de cuisine complet", "Casseroles et poêles, ustensiles, huile, sel, poivre · Bols, tasses, assiettes, couverts"),
                                ("verre", "Verres à vin", ""), ("bouilloire", "Bouilloire électrique", ""), ("cafetiere", "Cafetière", ""), ("grille-pain", "Grille-pain", "")]),
  ("Salle de bain", [("douche", "Douche à l'italienne", ""), ("seche-cheveux", "Sèche cheveux", ""), ("draps", "Serviettes", "Serviettes de bain, serviettes de plage")]),
  ("Famille avec bébé (sur demande)", [("lit-parapluie", "Lit parapluie", ""), ("lit-parapluie", "Cache-prises", ""), ("chaise-haute", "Chaise haute", "")]),
  ("Divertissements", [("wifi", "Connexion Internet Wifi haut débit", ""), ("television", "TV avec abonnement standard", ""), ("ping-pong", "Table de tennis de table", "")]),
  ("Sécurité à la maison", [("detecteur-fumee", "Détecteur de fumée", ""), ("trousse-secours", "Kit de premiers secours", "")]),
  ("Extérieurs", [("terrasse", "2 terrasses privées", ""), ("mobilier", "Espace repas en plein air", "Mobilier d'extérieur"), ("barbecue", "Plancha", "")]),
  ("Parking & Piscine", [("voiture", "Parking privé sécurisé", ""), ("piscine", "Piscine partagée sécurisée", "")]),
  ("Vues", [("panorama", "Vue sur la baie de Nice", ""), ("ville", "Vue sur la ville de Nice", ""), ("montagne", "Vue sur les montagnes de l'arrière-pays niçois", ""), ("jardin", "Vue sur le jardin", "")]),
]

def ico(n): return f'<img src="{{R}}assets/icons/{n}.png" alt="" loading="lazy">'

def saison_appartement():
    gal = "".join(f'<a href="{{R}}assets/img/{n}.jpg"{" class=\"g\"" if g else ""}>{img(n, a)}</a>' for n, a, g in GALERIE)
    equip = "".join(f"<h4>{E(cat)}</h4><ul>" + "".join(f"<li>{ico(i)}<span>{E(t)}{f'<small>{E(s)}</small>' if s else ''}</span></li>" for i, t, s in items) + "</ul>" for cat, items in EQUIPEMENTS)
    intro = texte("index", "Situé sur les collines")
    logement = texte("index", "Bienvenue dans")
    quartier = [s for t, s, _ in blocs("index") if t == "p" and s.startswith(("L’appartement est situé sur les collines de Bellet dans", "A 7 min", "A 2 min", "A 5 min", "La plage"))]
    atouts = [s for t, s, _ in blocs("index") if t == "p" and s.startswith(("L’appartement est situé sur les collines de Bellet où", "Venez découvrir", "Longez", "N’hésitez"))]
    deplacer = [s for t, s, _ in blocs("index") if t == "p" and s.startswith(("Vous avez la possibilité de prendre le bus", "Nous sommes situés à 5 min"))]
    corps = f"""
{bandeau("bandeau-accueil", "Location saisonnière Nice", "Appartement vue mer panoramique sur la Colline de Bellet")}
<section class="blanc"><div class="etroit centre">
  <span class="sur">Nice · Provence-Alpes-Côte d'Azur · France</span>
  <h1>Appartement entier haut de villa à Nice<br>avec vue panoramique sur la Baie des Anges<br>&amp; les montagnes environnantes</h1>
  <div class="chiffres"><span>Logement entier</span><span>6 voyageurs</span><span>2 chambres</span><span>4 lits</span><span>2 salles de bain</span></div>
  <p style="margin-top:18px"><strong>Appartement idéal pour les familles avec ou sans enfants ou entre amis</strong></p>
</div></section>
<section style="padding-top:0" class="blanc"><div class="wrap"><div class="galerie">{gal}</div></div></section>
<section><div class="etroit">
  <div style="font-size:1.12rem;font-weight:600;color:var(--nuit)">{para(intro)}</div>
  <h2 style="margin-top:1.4em">Le logement</h2>{para(logement)}
</div></section>
<section class="blanc"><div class="wrap">
  <span class="sur centre">Les chambres</span><h2 class="centre">Où dormirez-vous ?</h2>
  <div class="grille3" style="margin-top:30px">
    <div class="carte">{img("chambre-parentale", "Chambre 1 parentale")}<div class="corps"><h3>Chambre 1 parentale</h3><ul class="liste-fine"><li>Lit double 160 x 200 cm</li><li>Salle de bain privative avec douche à l'italienne + lavabo</li><li>Double placard</li><li>Climatisation réversible</li><li>Volet roulant électrique</li></ul></div></div>
    <div class="carte">{img("chambre-2", "Chambre 2")}<div class="corps"><h3>Chambre 2</h3><ul class="liste-fine"><li>Au choix 1 Lit double 160 x 200 cm<br>ou 2 lits simples 80 x 200 cm</li><li>Double placard</li><li>Climatisation réversible</li><li>Volet roulant électrique</li></ul></div></div>
    <div class="carte">{img("salon-canape-lit", "Salon")}<div class="corps"><h3>Salon</h3><ul class="liste-fine"><li>1 canapé convertible</li><li>Lit double 140 x 200 cm</li><li>Climatisation réversible</li><li>Volets roulants électriques</li></ul></div></div>
  </div>
</div></section>
<section><div class="wrap">
  <span class="sur centre">La cuisine</span><h2 class="centre">Vous aimez cuisiner ?<br>Profitez d'une cuisine entièrement équipée et conviviale</h2>
  <div class="grille3" style="margin-top:30px">
    <div class="carte">{img("cuisine-ilot", "Îlot de cuisine")}<div class="corps"><h4>Îlot avec plaque à induction + 3 tabourets haut</h4><p class="note">{ligne(texte("index", "Profitez d'un moment convivial"))}</p></div></div>
    <div class="carte">{img("cuisine-electromenager", "Électroménager")}<div class="corps"><h4>Appareils ménagers de dernière génération</h4></div></div>
    <div class="carte">{img("cuisine-ustensiles", "Ustensiles")}<div class="corps"><h4>Ustensiles de cuisine</h4><p class="note">Marmite, casseroles, poêles, écumoire, rouleau à pâtisserie...<br>{ligne(texte("index", "La cuisine est entièrement équipée"))}</p></div></div>
  </div>
  <div class="centre" style="margin-top:34px"><span class="pastille">🚭 Appartement non-fumeur</span><span class="pastille">Animaux non admis</span><span class="pastille">🚲 Stockage des vélos</span></div>
</div></section>
<section class="blanc"><div class="wrap equip">
  <span class="sur centre">Équipements</span><h2 class="centre">Ce que propose l'appartement</h2>{equip}
</div></section>
<section><div class="wrap">
  <div class="grille4">
    <div class="carte"><div class="corps">{ico("communication")}<h4 style="margin-top:10px">Délais de réponse rapide</h4><p class="note">Bonne communication</p></div></div>
    <div class="carte"><div class="corps">{ico("calendrier")}<h4 style="margin-top:10px">Haute Saison · Juillet-Août</h4><p class="note">Location à la semaine du samedi au samedi</p><h4>Moyenne &amp; Basse Saison</h4><p class="note">Location 4 jours minimum</p></div></div>
    <div class="carte"><div class="corps">{ico("cle")}<h4 style="margin-top:10px">Entrée 17h-19h · Sortie 11h</h4><p class="note">Remise des clés en main propre</p></div></div>
    <div class="carte"><div class="corps">{ico("nettoyage")}<h4 style="margin-top:10px">Ménage</h4><p class="note">Partez l'esprit tranquille et prenez l'option ménage fin de séjour</p></div></div>
  </div>
</div></section>
<section class="sable"><div class="wrap">
  <span class="sur centre">Nos plus</span><h2 class="centre">Nos plus</h2>
  <div class="plus" style="margin-top:28px">
    <div><h4>Parking privé</h4><p class="note">Garez-vous dans l'enceinte de la villa, parking privatif et sécurisé</p></div>
    <div><h4>Vue panoramique</h4><p class="note">Admirez la Grande Bleue depuis la terrasse principale avec une vue imprenable</p></div>
    <div><h4>2 Terrasses</h4><p class="note">Profitez de la vue et des espaces extérieurs avec les 2 terrasses exposées Sud Est et Sud Ouest</p></div>
    <div><h4>Piscine</h4><p class="note">Piquez une tête dans la piscine pour vous rafraîchir (Accès partagé avec les propriétaires)</p></div>
    <div><h4>Wifi gratuit</h4><p class="note">Bénéficiez de la fibre et d'un accès internet à très haut débit</p></div>
    <div><h4>Ménage</h4><p class="note">Service de ménage optionnel pendant le séjour ou en fin de séjour</p></div>
    <div><h4>Bébé</h4><p class="note">Équipement bébé disponible à la demande (lit parapluie, chaise haute, cache-prises)</p></div>
    <div><h4>Ateliers Bien être</h4><p class="note">Profitez d'un massage bien être à domicile ou d'une séance de yoga privée, sur demande</p></div>
    <div><h4>Expérience découverte</h4><p class="note">Découvrez les spécialités niçoises et d'autres recettes lors d'un atelier cuisine dédié à notre belle région</p></div>
  </div>
</div></section>
<section class="blanc"><div class="wrap"><div class="split">
  <div><h2>Description du quartier</h2>{"".join(para(q) for q in quartier)}</div>
  {img("vue-baie-de-nice", "La vue depuis l'appartement")}
</div></div></section>
<section><div class="wrap"><div class="split inverse">
  <div><h2>Nice et ses atouts</h2>{"".join(para(q) for q in atouts)}<p><a href="https://vindenice.com" rel="noopener">vindenice.com</a></p></div>
  {img("terrasse-vue-mer", "Apéritif sur la terrasse")}
</div></div></section>
<section class="blanc"><div class="etroit">
  <h2>Se déplacer</h2>{"".join(para(q) for q in deplacer)}
  <h3 style="margin-top:1.5em">Numéro d'enregistrement</h3><p>{ENREGISTREMENT}</p>
  <p style="margin-top:28px"><a class="bouton" href="contact.html">Réserver</a></p>
</div></section>
"""
    page("saisonniere/index.html", "Location saisonnière Nice · Appartement vue mer | Les Piafs des Collines",
         "Appartement entier haut de villa à Nice avec vue panoramique sur la Baie des Anges, 2 chambres, 2 terrasses, piscine et parking.",
         "saison", "", corps, SCRIPT_GALERIE)

def saison_hotes():
    corps = f"""
{bandeau("bandeau-hotes", "Hôtes")}
<section class="blanc"><div class="etroit">
  <h2>Bonjour</h2>
  {para(texte("hôtes", "Nous nous présentons"))}{para(texte("hôtes", "Situé sur les hauteurs"))}{para(texte("hôtes", "Passionnés tous les deux"))}
  <p style="font-family:var(--script);font-size:2rem;color:var(--azur)">Marcelle &amp; Serge</p>
</div></section>
<section><div class="wrap">
  <div class="split" style="margin-bottom:56px">
    <div class="grille2">{img("serge-chef", "Serge")}{img("serge-cuisine", "Serge en cuisine")}</div>
    <div><h2>Serge</h2>{para(texte("hôtes", "Chef cuisinier"))}</div>
  </div>
  <div class="split inverse">
    <div class="grille2">{img("marcelle-bulles", "Marcelle")}{img("marcelle", "Marcelle")}</div>
    <div><h2>Marcelle</h2>{para(texte("hôtes", "Touche à tout"))}</div>
  </div>
</div></section>"""
    page("saisonniere/hotes.html", "Vos hôtes | Les Piafs des Collines", "Marcelle et Serge, vos hôtes sur les collines de Bellet.", "saison", "hotes", corps)

def saison_ateliers():
    def at(image, titre, txt, prix, inverse=False):
        return f"""<div class="split{' inverse' if inverse else ''}" style="margin-bottom:60px">{img(image, titre)}<div><h2>{titre}</h2>{para(txt)}<p class="prix" style="font-size:1.2rem">{E(prix)}</p><p class="note">Pensez à réserver à l'avance</p></div></div>"""
    corps = f"""
{bandeau("bandeau-ateliers", "Ateliers", "Expérience découverte ou atelier de pratique régulière")}
<section class="blanc"><div class="etroit centre"><h2>{ligne(texte("ateliers", "Le temps d'une initiation"))}</h2><p class="sur">Pensez à réserver à l'avance</p></div></section>
<section><div class="wrap">
  {at("atelier-yoga", "Yoga · Sophrologie · Méditation", texte("ateliers", "Les vacances, c'est"), "Forfait à partir de 120€")}
  {at("atelier-massage", "Massage détente", texte("ateliers", "Une ou un masseur"), "À partir de 120€ le massage", True)}
  {at("atelier-cuisine", "Atelier Cuisine", texte("ateliers", "Pour cette expérience"), "Forfait sur demande")}
  {at("atelier-bulles", "Jongle &amp; Bulles", texte("ateliers", "Marcelle, pleine de surprise"), "", True)}
  <p class="centre"><a class="bouton" href="contact.html">Réserver un atelier</a></p>
</div></section>"""
    page("saisonniere/ateliers.html", "Ateliers | Les Piafs des Collines", "Yoga, massage, atelier cuisine niçoise et jongle : des ateliers pour ponctuer vos vacances.", "saison", "ateliers", corps)

def saison_livre_or():
    avis = [("Quel plaisir d'être les premiers voyageurs !\nSuper séjour ! Rien à redire, tout était parfait !\nMerci pour votre accueil et toutes vos attentions !", "Hugo - Nancy (à côté de Malzeville)"),
            (texte("livre-or", "Un grand merci pour votre gentillesse"), "Mélody - Nancy"),
            (texte("livre-or", "Nous avons passé un très agréable") + "\n" + texte("livre-or", "Maolan et Tiloé") + "\n" + texte("livre-or", "Sans oublier la piscine"), "Chantal, Serge, Sabrina & Anthony - Doubs"),
            ("We had a lovely stay at this cute and well equiped apartment.\n" + texte("livre-or", "Everything was perfectly organised"), "Salma & Omar with Maya, Lina, Hannah"),
            (texte("livre-or", "Nous avons passé une agréable") + "\n" + texte("livre-or", "Les hôtes sont d'une gentillesse"), "Anaïs - Nord"),
            ("Thanks to you, we had a really nice vacation here! You have the most beautiful view from the flat and everything you need here!\nThanks you for the loving welcome, it was very nice to meet you and especially the last evening.\nHave a nice time, good to see you until next time.", "Love, Family Traude")]
    corps = f"""
{bandeau("bandeau-livre-or", "Livre d'Or")}
<section><div class="wrap"><div class="avis">
{"".join(f"<blockquote>{E(t.strip()).replace(chr(10), '<br>')}<cite>{E(c)}</cite></blockquote>" for t, c in avis)}
</div></div></section>"""
    page("saisonniere/livre-or.html", "Livre d'or | Les Piafs des Collines", "Ce que nos voyageurs ont écrit.", "saison", "livre-or", corps)

def saison_faq():
    b = blocs("faq"); qr = []; i = 0
    while i < len(b):
        t, s, _ = b[i]
        if t == "h4":
            rep = []; j = i + 1
            while j < len(b) and b[j][0] == "p":
                if b[j][1].strip("​ ").strip(): rep.append(b[j][1])
                j += 1
            qr.append((s, rep)); i = j
        else:
            i += 1
    corps = f"""
{bandeau("bandeau-faq", "F.A.Q.", "Foire aux questions")}
<section><div class="etroit">
<h2 class="centre">Vous avez des questions ?<br>Nous sommes là pour y répondre</h2>
<div style="margin-top:30px">{"".join(f"<details><summary>{ligne(q)}</summary>{''.join(para(r) for r in rs)}</details>" for q, rs in qr)}</div>
<p class="centre" style="margin-top:30px"><a class="bouton" href="contact.html">Nous contacter</a></p>
</div></section>"""
    page("saisonniere/faq.html", "F.A.Q. | Les Piafs des Collines", "Réservation, assurance, accès, équipements : les réponses à vos questions.", "saison", "faq", corps)

def saison_tarifs():
    moy = [("hiver", "Vacances d'Hiver", "8 fév. - 9 mars 2025", "190€ / nuit", "4 nuits minimum"),
           ("printemps", "Vacances Printemps", "5 avril - 4 mai 2025", "180€ / nuit", "4 nuits minimum"),
           ("toussaint", "Vacances Toussaint", "18 oct. - 2 nov. 2025", "190€ / nuit", "4 nuits minimum"),
           ("noel", "Vacances Noël", "20 déc. - 4 janv. 2026", "200€ / nuit", "4 nuits minimum"),
           ("avant-saison", "Avant Saison", "5 avril - 30 mai 2025", "170€ / nuit", "4 nuits minimum"),
           ("ponts", "Pont de l'Ascension · Pentecôte", "29 mai - 1 juin 2025 · 6 - 9 juin 2025", "570€", "3 nuits"),
           ("avant-saison-2", "Avant Saison", "31 mai - 28 juin 2025", "190€ / nuit", "4 nuits minimum"),
           ("apres-saison", "Après Saison", "31 août - 17 oct. 2025", "190€ / nuit", "4 nuits minimum")]
    def carte(im, t, d, p, n):
        return f'<div class="carte">{img("saison-" + im, t)}<div class="corps"><h4>{E(t)}</h4><p class="note">{E(d)}</p><p class="prix">{E(p)}</p><p class="note">{E(n)}</p></div></div>'
    corps = f"""
{bandeau("bandeau-tarifs", "Tarifs", "Tarifs 2025")}
<section class="blanc"><div class="wrap">
  <span class="sur">Juillet - Août</span><h2>Haute Saison</h2>
  <div class="split">{img("saison-ete", "Haute saison")}<div><h3>Vacances d'été · 28 juin - 30 août</h3><p class="prix">1 610€ <span style="font-size:1rem;font-weight:400;color:var(--gris)">· 7 nuits</span></p><p>Tarif 230€ / nuit</p><p class="note">Durant la Haute Saison, du 28 juin au 30 août 2025, locations à la semaine, du samedi 17h au samedi 11h</p></div></div>
</div></section>
<section><div class="wrap">
  <span class="sur">Vacances scolaires · avant et après saison</span><h2>Moyenne Saison</h2>
  <p><strong>Tarif entre 175€ et 200€ / nuit</strong></p>{para(texte("tarifs", "La Moyenne Saison correspond"))}
  <div class="saison" style="margin-top:24px">{"".join(carte(*m) for m in moy)}</div>
</div></section>
<section class="blanc"><div class="wrap">
  <span class="sur">Hors vacances scolaires</span><h2>Basse Saison</h2>
  <div class="split">{img("saison-basse-saison", "Basse saison")}<div><p class="prix">160€ / nuit</p><p>La Basse Saison correspond à la période du 3 novembre 2025 au 5 avril 2026, hors périodes de vacances scolaires.</p><p class="note">Durant la basse saison, nous demandons 4 nuitées de réservation minimum, hors vacances scolaires et jours fériés.</p></div></div>
</div></section>
<section><div class="wrap">
  <span class="sur">Au forfait ou par personne</span><h2>Services associés</h2>
  <div class="split">{img("saison-menage", "Service ménage")}<div><h3>Service Ménage fin de séjour</h3><p>Nettoyage complet de l'appartement</p></div></div>
  <p class="note" style="margin-top:30px">* Les tarifs sont annoncés pour une location pour 4 personnes. Un supplément est à ajouter pour toute personne supplémentaire au-delà de 4, à raison de 18€ par jour / personne pour un maximum de 6 personnes au total.</p>
  <p><a class="bouton" href="contact.html">Réserver</a></p>
</div></section>"""
    page("saisonniere/tarifs.html", "Tarifs | Les Piafs des Collines", "Tarifs de la location saisonnière : haute, moyenne et basse saison.", "saison", "tarifs", corps)

def formulaire(sujet, champs_extra=""):
    return f"""<form class="formulaire-mail" data-to="{MAIL}" data-sujet="{E(sujet)}">
<div class="champs">
<div><label for="prenom">Prénom</label><input id="prenom" name="Prénom" required></div>
<div><label for="nom">Nom</label><input id="nom" name="Nom" required></div>
<div><label for="email">Email</label><input id="email" name="Email" type="email" required></div>
<div><label for="tel">Téléphone</label><input id="tel" name="Téléphone" type="tel"></div>
{champs_extra}
<div class="plein"><label for="msg">Message</label><textarea id="msg" name="Message" required></textarea></div>
</div>
<p style="margin-top:18px"><button class="bouton" type="submit">Envoyer</button></p>
<p class="note">Le bouton ouvre votre messagerie avec le message prérempli, adressé à {MAIL}.</p>
</form>
<script>document.querySelectorAll('.formulaire-mail').forEach(f=>f.addEventListener('submit',e=>{{e.preventDefault();
const l=[...new FormData(f)].filter(([k,v])=>v).map(([k,v])=>k+' : '+v).join('\\n');
location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent(f.dataset.sujet)+'&body='+encodeURIComponent(l);}}));</script>"""

def saison_contact():
    corps = f"""
{bandeau("bandeau-accueil", "Contact")}
<section><div class="wrap"><div class="split" style="align-items:start">
  <div><h2>Nous sommes heureux que vous pensiez à notre appartement pour votre séjour !</h2>
  <p>Si vous avez des questions, c'est avec un grand plaisir que nous y répondrons</p>
  <h4 style="margin-top:1.4em">Adresse</h4><p>{ADRESSE}</p>
  <h4>Email</h4><p><a href="mailto:{MAIL}">{MAIL}</a></p>
  <h4>Téléphone</h4><p><a href="tel:{TEL_LIEN}">{TEL}</a></p>
  <h4>Réseaux sociaux</h4><p><a href="{FACEBOOK}" rel="noopener">Facebook</a></p></div>
  <div class="carte"><div class="corps">{formulaire("Demande de réservation - location saisonnière",
    '<div><label for="arr">Arrivée</label><input id="arr" name="Arrivée" type="date"></div><div><label for="dep">Départ</label><input id="dep" name="Départ" type="date"></div><div class="plein"><label for="pers">Nombre de personnes</label><input id="pers" name="Personnes" type="number" min="1" max="6"></div>')}</div></div>
</div></div></section>"""
    page("saisonniere/contact.html", "Contact | Les Piafs des Collines", "Contactez Marcelle et Serge pour votre séjour.", "saison", "contact", corps)

ARTICLES = [("la-metropole-nice-cote-d-azur", "post_la-métropole-nice-côte-d-azur", "La Métropole Nice Côte d’Azur", "blog-metropole", "10 oct. 2021"),
            ("nissa-la-bella", "post_créez-un-superbe-blog", "Nissa la Bella", "blog-nissa-la-bella", "11 oct. 2021")]

def saison_environs():
    cartes = "".join(f'<a class="carte" style="text-decoration:none;color:inherit" href="environs/{slug}.html">{img(im, t)}<div class="corps"><p class="note">{d}</p><h3>{E(t)}</h3><span class="f" style="color:var(--azur);font-family:var(--titre);font-weight:600">Lire →</span></div></a>' for slug, _, t, im, d in ARTICLES)
    corps = f"""{bandeau("bandeau-environs", "Explorez les environs")}<section><div class="wrap"><div class="grille2">{cartes}</div></div></section>"""
    page("saisonniere/environs.html", "Explorez les environs | Les Piafs des Collines", "Nice, la Métropole, l'arrière-pays : nos coups de cœur autour de l'appartement.", "saison", "environs", corps)
    for slug, src, t, im, d in ARTICLES:
        b = blocs(src); debut = next(i for i, x in enumerate(b) if x[0] == "h1" and x[1] not in ("Explorez les environs",)) if src.startswith("post_cr") else 0
        html_txt = []
        stop = ("Posts récents", "Commentaires", "Mots-clés")
        for tt, s, _ in b[debut:]:
            if s.startswith(stop): break
            if tt in ("li", "img", "a") or s in ("Explorez les environs", t) or s.startswith(("Dernière mise à jour", "10 oct", "2 min")): continue
            if s.startswith(("* En réservant", "CONDITIONS GÉNÉRALES", "©")): continue
            if tt in ("h2", "h3", "h4", "h5", "h6", "h1"): html_txt.append(f"<h3>{ligne(s)}</h3>")
            elif s.strip("​ "): html_txt.append(para(s))
        corps = f"""{bandeau("bandeau-environs", "Explorez les environs")}<section><div class="etroit"><p class="note">{d}</p><h1>{E(t)}</h1>{img(im, t, "")}<div style="margin-top:28px">{''.join(html_txt)}</div><p><a href="../environs.html">← Tous les articles</a></p></div></section>"""
        page(f"saisonniere/environs/{slug}.html", f"{t} | Les Piafs des Collines", t, "saison", "environs", corps)

LEGAL = [("conditions-generales", "copie-de-conditions-d-utilisation", "Conditions générales"),
         ("reglement-interieur", "copie-de-conditions-générales", "Règlement intérieur"),
         ("sante-securite", "copie-de-règlement-intérieur", "Santé & sécurité"),
         ("conditions-annulation", "copie-de-santé-sécurité", "Conditions d'annulation"),
         ("mentions-legales", "mentions-légales", "Mentions légales"),
         ("politique-de-confidentialite", "politique-de-confidentialité", "Politique de confidentialité"),
         ("politique-utilisation", "conditions-d-utilisation", "Politique d'utilisation")]

RENVOIS_LEGAUX = {"conditions-generales": "conditions-de-location", "reglement-interieur": "reglement-interieur", "sante-securite": "reglement-interieur",
                  "conditions-annulation": "conditions-de-location", "mentions-legales": "mentions-legales",
                  "politique-de-confidentialite": "confidentialite", "politique-utilisation": "confidentialite"}

def renvoi(chemin, cible):
    """Page de renvoi vers une nouvelle adresse (sans supprimer l'ancienne)."""
    f = SITE / chemin
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(f'<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="robots" content="noindex">'
                 f'<link rel="canonical" href="{BASE}{cible}"><meta http-equiv="refresh" content="0; url={cible}"><title>Les Piafs des Collines</title></head>'
                 f'<body><p><a href="{cible}">Cette page a changé d\'adresse.</a></p></body></html>\n', encoding="utf-8")
    print("  ", chemin, "->", cible)

def saison_legal():
    if not SAISON_ACTIVE:
        for slug, _, _ in LEGAL:
            renvoi(f"saisonniere/{slug}.html", "/" + RENVOIS_LEGAUX[slug])
        return
    for slug, src, titre in LEGAL:
        out = []; premier = True
        for t, s, _ in blocs(src):
            if t in ("img", "a"): continue
            if s.startswith(("* En réservant", "©")) or s == "CONDITIONS GÉNÉRALES LOCATION SAISONNIÈRE LES PIAFS DES COLLINES NICE" and not premier: continue
            if not s.strip("​ "): continue
            if t in ("h1", "h2") and premier: premier = False; continue
            if t in ("h1", "h2", "h3"): out.append(f"<h3>{ligne(s)}</h3>")
            elif t in ("h4", "h5", "h6"): out.append(f"<h4>{ligne(s)}</h4>")
            elif t == "li": out.append(f"<ul><li>{ligne(s)}</li></ul>")
            else: out.append(para(s))
        corps = f"""{bandeau("bandeau-accueil", titre)}<section><div class="etroit"><div class="texte-legal">{''.join(out).replace('</ul><ul>', '')}</div></div></section>"""
        page(f"saisonniere/{slug}.html", f"{titre} | Les Piafs des Collines", titre, "saison", "", corps)

# ================================================================ BAIL MOBILITÉ
FAQ_MOB = [
 ("Qu'est-ce qu'un bail mobilité ?",
  "C'est un bail de location meublée de 1 à 10 mois, créé par la loi ELAN du 23 novembre 2018 (articles 25-12 et suivants de la loi du 6 juillet 1989). Il n'est ni renouvelable ni reconductible, et le propriétaire ne peut pas demander de dépôt de garantie."),
 ("Qui peut louer en bail mobilité à Nice ?",
  "Une personne en formation professionnelle, en études supérieures, en apprentissage, en stage, en service civique, en mutation professionnelle ou en mission temporaire. Le justificatif du motif est demandé avant la signature du bail."),
 ("Mon employeur peut-il payer le loyer ?",
  "Oui. Quand une société, une agence de relocation, un assureur ou une production paie, le logement se loue par un bail au nom de la structure, à partir de 3 mois, avec une facture à son nom. Aucun justificatif de motif n'est alors demandé."),
 ("Que comprend le loyer ?",
  "Tout : charges, électricité, eau, climatisation, fibre, place de parking privée, accès à la piscine, linge de lit et de toilette, kit d'arrivée et ménage de sortie. Le locataire ne reçoit aucune facture d'énergie."),
 ("Combien coûte le bail mobilité ?",
  "2 880 € par mois pour 7 à 10 mois, 3 200 € par mois pour 3 à 6 mois et 3 600 € par mois pour 1 à 2 mois, tout compris."),
 ("La garantie Visale est-elle acceptée ?",
  "Visale n'est pas mobilisable à ce niveau de loyer. La garantie prend la forme d'une caution de l'employeur ou d'une caution personnelle."),
 ("Peut-on louer moins d'un mois ?",
  "Non. La durée minimale est d'un mois."),
 ("Comment se passe l'arrivée ?",
  "L'arrivée est autonome : le code d'accès est communiqué avant la date d'entrée. Il n'y a pas de rendez-vous de remise des clés, ni de contrainte d'horaire."),
 ("Où se trouve le logement et combien de temps pour rejoindre le centre ?",
  "Sur la colline de Bellet, à l'ouest de Nice. En voiture, hors trafic : Clinique Kantys Centre 12 min, campus Valrose 13 min, CHU Pasteur 2 15 min, Centre Antoine Lacassagne 16 min, aéroport 20 min, Monaco 22 min, Sophia Antipolis 28 min. Le bus 60 s'arrête à 50 m et rejoint le tram ligne 2 à Magnan."),
]

# Livre d'or : seuls les passages sur le logement, sans ce qui touche à l'accueil des hôtes.
AVIS = [("Une vue à couper le souffle, un appartement des plus agréables et d'une propreté irréprochable.", "Mélody, Nancy"),
        ("Un appartement au top, moderne, bien équipé, au goût du jour. Qu'il est agréable de s'asseoir sur la terrasse et de contempler la mer et ses bateaux.", "Chantal, Serge, Sabrina et Anthony, Doubs"),
        ("L'appartement est très bien situé et d'une propreté irréprochable. La vue est magnifique.", "Anaïs, Nord"),
        ("We had a lovely stay at this cute and well equipped apartment. The view is magnificent.", "Salma et Omar"),
        ("You have the most beautiful view from the flat and everything you need here!", "Famille Traude"),
        ("Super séjour ! Rien à redire, tout était parfait !", "Hugo, Nancy")]

def faq_html(qr):
    return "".join(f"<details><summary>{fine(E(q))}</summary><p>{fine(E(r))}</p></details>" for q, r in qr)

# ---------------------------------------------------------------- plan stylisé de Nice
# Plan schématique, façon affiche : pas une carte. Positions composées à la main, ouest à gauche, mer en bas.
def plan_nice():
    cote = "M0 560 C 120 566, 230 572, 318 584 C 350 590, 372 604, 398 606 C 430 604, 470 568, 540 532 C 620 492, 700 462, 780 448 C 820 441, 850 446, 880 440 C 930 428, 1010 408, 1100 398 L 1100 660 L 0 660 Z"
    vagues = "".join(f'<path class="p-vague" d="M{x} {y}q12 -8 24 0t24 0t24 0"/>' for x, y in ((120, 618), (300, 640), (520, 600), (700, 560), (900, 520), (980, 610), (640, 640)))
    collines = ('<path class="p-colline c1" d="M190 430 C 270 330, 370 278, 455 282 C 560 288, 640 360, 705 430 Z"/>'
                '<path class="p-colline c2" d="M300 440 C 370 392, 450 368, 530 378 C 590 388, 630 412, 665 440 Z"/>'
                '<path class="p-colline c3" d="M660 410 C 740 330, 850 300, 960 322 C 1020 336, 1060 358, 1100 372 L 1100 420 Z"/>')
    var = '<path class="p-var" d="M285 0 C 300 160, 270 330, 300 450 C 312 500, 316 545, 324 586"/>'
    ax, ay = 450, 376
    lieux = [("CHU Pasteur 2", "hopital", 905, 300, "15", 1), ("Campus Valrose", "campus", 790, 320, "13", 1),
             ("Centre Lacassagne", "hopital", 590, 392, "16", 1), ("Clinique Kantys", "hopital", 735, 380, "12", 1),
             ("Aéroport", "avion", 400, 590, "20", -1), ("La plage", "parasol", 545, 528, "7", -1)]
    traits, points = "", ""
    for nom, ico, x, y, mn, sens in lieux:
        traits += f'<path class="p-trajet" d="M{ax} {ay} Q {(ax + x) / 2:.0f} {min(ay, y) - 12} {x} {y}"/>'
        ty = 38 if sens > 0 else -50
        points += (f'<g class="p-lieu" transform="translate({x} {y})"><circle r="17"/><use href="#i-{ico}" x="-11" y="-11" width="22" height="22"/>'
                   f'<text class="p-nom" y="{ty}" text-anchor="middle">{E(nom)}</text><text class="p-min" y="{ty + 21}" text-anchor="middle">{mn} min</text></g>')
    bords = ('<g class="p-bord" transform="translate(1030 170)"><use href="#i-couronne" x="-12" y="-38" width="24" height="24"/>'
             '<text text-anchor="middle" class="p-nom">Monaco</text><text y="21" text-anchor="middle" class="p-min">22 min →</text></g>'
             '<g class="p-bord" transform="translate(110 440)"><use href="#i-puce" x="-12" y="-38" width="24" height="24"/>'
             '<text text-anchor="middle" class="p-nom">Sophia Antipolis</text><text y="21" text-anchor="middle" class="p-min">← 28 min</text></g>')
    reperes = ('<g class="p-ville" transform="translate(880 432)"><circle r="7"/><text x="14" y="-12">Centre-ville</text></g>'
               '<text class="p-promenade" x="560" y="560" transform="rotate(-17 560 560)">Promenade des Anglais</text>'
               '<text class="p-baie" x="680" y="625">Baie des Anges</text>'
               '<text class="p-varnom" x="262" y="220" transform="rotate(86 262 220)">le Var</text>')
    maison = (f'<g class="p-piafs" transform="translate({ax} {ay})"><circle r="36"/><image href="{{R}}assets/img/logo-oiseau-blanc.svg" x="-20" y="-24" width="40" height="44"/>'
              '<text class="p-piafs-nom" y="-56" text-anchor="middle">Les Piafs des Collines</text>'
              '<text class="p-piafs-sous" y="-36" text-anchor="middle">sur la colline de Bellet</text></g>')
    return (f'<figure class="plan-nice"><svg viewBox="0 0 1100 660" role="img" aria-label="Plan schématique de Nice : le logement sur la colline de Bellet, à 7 à 28 minutes en voiture des hôpitaux, du campus, de l\'aéroport, de la plage, de Monaco et de Sophia Antipolis">'
            f'<rect class="p-terre" width="1100" height="660"/>{collines}{var}<path class="p-mer" d="{cote}"/>{vagues}{reperes}{traits}{points}{bords}{maison}</svg>'
            '<figcaption>Plan schématique, pas à l\'échelle. Temps en voiture, hors trafic.</figcaption></figure>')

def bail_mobilite():
    gal = "".join(f'<a href="{{R}}assets/img/{n}.jpg"{" class=\"g\"" if g else ""}>{img(n, a)}</a>' for n, a, g in GALERIE[:9])
    fiche = [
        ("Le logement", [("Surface habitable", "77,51 m² (mesurage loi Boutin, 27/09/2026)"), ("Terrasses", "10,58 m² + 15,75 m², Sud-Est et Sud-Ouest"),
                         ("Véranda buanderie", "4,95 m²"), ("Pièces", "3, dont 2 chambres"), ("Chambres", "13,91 m² et 12,88 m²"),
                         ("Salles d'eau", "2, dont 1 privative avec douche à l'italienne"), ("WC", "1 indépendant"),
                         ("Situation", "1er étage d'une villa, logement traversant"), ("Vue", "Baie des Anges, dégagée")]),
        ("Énergie et confort", [("DPE", "C en énergie, A en climat, valable jusqu'au 26/09/2036"), ("Coût énergie estimé", "850 à 1 210 € par an, inclus dans le loyer"),
                                ("Chauffage et climatisation", "Pompe à chaleur, climatisation réversible"), ("Internet", "Fibre")]),
        ("Équipements", [("Cuisine", "Îlot à induction, four, micro-ondes, lave-vaisselle, réfrigérateur-congélateur"),
                         ("Linge", "Lave-linge, sèche-linge, fer à repasser"), ("Literie", "Draps, oreillers, couettes d'été et d'hiver, linge de toilette fournis"),
                         ("Extérieur", "Table à rallonge 6 personnes sous store électrique, plancha"), ("Stationnement", "1 place privée dans l'enceinte"),
                         ("Piscine", "Partagée, selon horaires"), ("Famille", "Chaise haute, lit parapluie, cache-prises sur demande")]),
        ("Contrat", [("Payeur personne morale", "Bail au nom de la société, à partir de 3 mois"), ("Payeur particulier", "Bail mobilité, de 1 à 10 mois"),
                     ("Durée minimale", "1 mois"), ("Pièces", "Justificatif du motif de mobilité avant signature, pour le bail mobilité"),
                     ("Garantie", "Caution de l'employeur ou caution personnelle. Visale non mobilisable à ce niveau de loyer"),
                     ("Facturation", "Exonérée de TVA, au nom du payeur"), ("Arrivée", "Autonome, code d'accès")]),
    ]
    icones = {"Le logement": "plan", "Énergie et confort": "energie", "Équipements": "equipement", "Contrat": "plume"}
    picto_ligne = {"Surface habitable": "plan", "Terrasses": "soleil", "Véranda buanderie": "machine", "Pièces": "porte", "Chambres": "lit",
                   "Salles d'eau": "douche", "WC": "douche", "Situation": "maison", "Vue": "soleil", "DPE": "energie",
                   "Coût énergie estimé": "facture", "Chauffage et climatisation": "clim", "Internet": "wifi", "Cuisine": "cuisine",
                   "Linge": "machine", "Literie": "lit", "Extérieur": "table", "Stationnement": "parking", "Piscine": "piscine",
                   "Famille": "personne", "Payeur personne morale": "societe", "Payeur particulier": "personne", "Durée minimale": "calendrier",
                   "Garantie": "cle", "Facturation": "facture", "Arrivée": "valise"}
    fiche_html = "".join(f'<div class="fiche-bloc"><h3>{pic(icones[t])}{E(t)}</h3><dl>' + "".join(
        f'<dt>{pic(picto_ligne.get(k, "plume" if t == "Contrat" else "plan"), "pic-s")}{E(k)}</dt><dd>{E(v)}</dd>' for k, v in lignes) + "</dl></div>" for t, lignes in fiche)
    def panneau(image, titre, l1, l2, cote="", icone="soleil"):
        return f'''<figure class="panneau {cote}">{img(image, titre.capitalize())}<figcaption><h3>{pic(icone, "pic-s")}{E(titre)}</h3><p>{E(l1)}<br>{E(l2)}</p></figcaption></figure>'''
    corps = f"""
<section class="mob-hero">
  <picture><source media="(max-width:700px)" srcset="{{R}}assets/img/hero-baie-mobile.jpg"><img class="fond" src="{{R}}assets/img/hero-baie.jpg" alt="La Baie des Anges vue depuis l'appartement, sur la colline de Bellet à Nice" fetchpriority="high"></picture>
  <div class="wrap">
    <h1 class="sur">Location en bail mobilité à Nice</h1>
    <p class="legende"><span class="ligne">Sur la colline de Bellet,</span><br><span class="ligne">face à la Baie&nbsp;des&nbsp;Anges,</span><br><em>de 1&nbsp;à 10&nbsp;mois</em></p>
    <a class="bouton" href="#demande">Demander une disponibilité</a>
  </div>
  <div class="timbre" aria-hidden="true"><span class="t-haut">Nice</span><span class="t-nom">Bellet</span><span class="t-bas">Côte d'Azur</span></div>
  <a class="defiler" href="#chiffres" aria-label="Découvrir le logement"><span>Découvrir</span></a>
</section>
<div class="store" aria-hidden="true"></div>

<section class="blanc" id="chiffres"><div class="wrap">
  <div class="geants">
    <div>{pic("hopital")}<b>15<small>min</small></b><span>du CHU Pasteur</span></div>
    <div>{pic("soleil")}<b>26<small>m<sup>2</sup></small></b><span>de terrasses vue mer</span></div>
    <div>{pic("facture")}<b>1</b><span>facture, tout compris</span></div>
  </div>
</div></section>

<section id="logement" class="panneaux"><div class="wrap">
  <h2 class="cache">Un appartement meublé de 77 m² à Nice</h2>
  {panneau("terrasse-vue-mer", "DEUX TERRASSES", "26 m² exposés sud, face à la mer.", "Une table pour six, sous store.", icone="soleil")}
  {panneau("chambre-parentale", "DEUX VRAIES CHAMBRES", "13,91 et 12,88 m², chacune avec son placard.", "Une salle de bain privative, une salle d'eau, un WC indépendant.", "droite", "lit")}
  {panneau("cuisine-sejour", "ARRIVER AVEC SA VALISE", "Lit fait, linge sorti, code d'accès.", "Fibre, parking et ménage de sortie compris.", icone="valise")}
  <div class="galerie" style="margin-top:70px">{gal}</div>
</div></section>

<section class="azur" id="prix"><div class="wrap prix-grille">
  <div><span class="sur">Prix du bail mobilité à Nice, tout compris</span>
  <h2 class="phrase-prix">Plus vous restez, moins vous payez : <em>720&nbsp;€ de moins par mois</em> sur 7&nbsp;à&nbsp;10&nbsp;mois.</h2></div>
  <div><div class="montants">
    <div><span>{pic("calendrier", "pic-s")}1 à 2 mois</span><b>3 600 €<i>/ mois</i></b></div>
    <div><span>{pic("calendrier", "pic-s")}3 à 6 mois</span><b>3 200 €<i>/ mois</i></b></div>
    <div><span>{pic("calendrier", "pic-s")}7 à 10 mois</span><b>2 880 €<i>/ mois</i></b></div>
  </div>
  <p class="note">Par mois. Charges, énergie, fibre, parking, linge et ménage de sortie compris. Facture exonérée de TVA.</p></div>
</div></section>

<section class="sable" id="acces"><div class="wrap">
  <span class="sur">Accès</span><h2>Sur la colline, à un quart d'heure de tout</h2>
  <p class="intro-plan">Ni en bord de mer, ni en centre-ville : sur la colline de Bellet, à l'ouest de Nice, au calme et face à la mer.</p>
  {plan_nice()}
  <div class="carte-trajets">
    <div>{pic("hopital", "pic-s")}<b>12</b><span>Clinique Kantys Centre</span></div><div>{pic("campus", "pic-s")}<b>13</b><span>Campus Valrose</span></div>
    <div>{pic("hopital", "pic-s")}<b>15</b><span>CHU Pasteur 2</span></div><div>{pic("hopital", "pic-s")}<b>16</b><span>Centre Lacassagne</span></div>
    <div>{pic("avion", "pic-s")}<b>20</b><span>Aéroport</span></div><div>{pic("couronne", "pic-s")}<b>22</b><span>Monaco</span></div>
    <div>{pic("puce", "pic-s")}<b>28</b><span>Sophia Antipolis</span></div><div>{pic("parasol", "pic-s")}<b>7</b><span>La plage</span></div>
  </div>
  <p class="note">Minutes en voiture, hors trafic. Bus 60 à 50 m, vers le tram ligne 2.</p>
</div></section>

<section class="blanc" id="contrat"><div class="wrap">
  <span class="sur">Contrat</span><h2>Bail mobilité ou bail société</h2>
  <div class="deux-formules">
    <div>{pic("societe")}<h3>L'employeur paie</h3><p>Bail au nom de la société, dès 3 mois.<br>Aucun justificatif de motif.</p></div>
    <div>{pic("personne")}<h3>Le locataire paie</h3><p>Bail mobilité, de 1 à 10 mois.<br>Justificatif de mobilité, caution employeur ou personnelle.</p></div>
  </div>
  <p class="note droit">Le contrat est régi par le droit français et rédigé en français. Les traductions sont fournies à titre d'information.</p>
</div></section>

<div class="store" aria-hidden="true"></div>
<section class="nuit" id="avis"><div class="etroit centre">
  <span class="sur">Le livre d'or</span>
  <div class="avis-defile" aria-roledescription="carrousel">
    {"".join(f'<blockquote class="citation"><p>« {E(q)} »</p><cite>{E(c)}</cite></blockquote>' for q, c in AVIS)}
  </div>
  <div class="avis-points" aria-hidden="true">{"".join("<span></span>" for _ in AVIS)}</div>
  <p class="note avis-source">Extraits du livre d'or de l'appartement.</p>
</div></section>
<script>(function(){{const d=document.querySelector('.avis-defile');if(!d)return;const p=[...document.querySelectorAll('.avis-points span')];let i=0;
function va(n){{i=(n+p.length)%p.length;d.scrollTo({{left:d.clientWidth*i,behavior:'smooth'}});p.forEach((x,k)=>x.classList.toggle('on',k===i))}}
p.forEach((x,k)=>x.addEventListener('click',()=>va(k)));va(0);
if(!matchMedia('(prefers-reduced-motion: reduce)').matches)setInterval(()=>{{if(!d.matches(':hover'))va(i+1)}},6500)}})();</script>

<section class="blanc" id="fiche"><div class="wrap">
  <span class="sur">Fiche technique</span><h2>Pour valider le dossier</h2>
  <div class="fiche">{fiche_html}</div>
</div></section>

<section id="questions"><div class="etroit">
  <span class="sur">Questions fréquentes</span><h2>Le bail mobilité à Nice, en questions</h2>
  <div style="margin-top:24px">{faq_html(FAQ_MOB)}</div>
</div></section>

<section class="blanc" id="demande"><div class="etroit">
  <span class="sur">Demande</span><h2>Demander une disponibilité</h2>
  <p>Les dates, et qui paie le loyer. Réponse avec une date d'entrée ferme.</p>
  {formulaire("Demande bail mobilité",
    '<div><label for="ent">Date d\'entrée souhaitée</label><input id="ent" name="Entrée" type="date"></div>'
    '<div><label for="duree">Durée</label><select id="duree" name="Durée"><option>1 à 2 mois</option><option>3 à 6 mois</option><option>7 à 10 mois</option></select></div>'
    '<div><label for="payeur">Qui paie le loyer ?</label><select id="payeur" name="Payeur"><option>Mon employeur</option><option>Une agence de relocation</option><option>Un assureur</option><option>Une production</option><option>Moi-même</option></select></div>'
    '<div><label for="motif">Motif du séjour</label><select id="motif" name="Motif"><option>Mission temporaire</option><option>Formation</option><option>Mutation</option><option>Stage</option><option>Études supérieures</option><option>Relogement après sinistre</option><option>Autre</option></select></div>'
    '<div class="plein"><label for="org">Société ou établissement</label><input id="org" name="Société / établissement"></div>')}
  <p class="note" style="margin-top:18px">Ou directement : <a href="mailto:{MAIL}">{MAIL}</a> · <a href="tel:{TEL_LIEN}">{TEL}</a></p>
</div></section>"""
    page("bail-mobilite/index.html", "Location bail mobilité Nice · Meublé 77 m² vue mer | Les Piafs des Collines",
         "Location meublée en bail mobilité à Nice : 77 m² vue Baie des Anges, 2 chambres, parking, fibre. De 1 à 10 mois, tout compris dès 2 880 €/mois.",
         "mob", "", corps, SCRIPT_GALERIE, image="hero-baie", jsonld=[
            {"@context": "https://schema.org", "@type": "Apartment",
             "name": "Location en bail mobilité à Nice, Les Piafs des Collines",
             "description": "Appartement meublé de 77,51 m² avec vue sur la Baie des Anges, loué en bail mobilité de 1 à 10 mois, tout compris à partir de 2 880 € par mois.",
             "url": BASE + "/bail-mobilite/", "address": ADRESSE_LD,
             "floorSize": {"@type": "QuantitativeValue", "value": 77.51, "unitCode": "MTK"}, "numberOfRooms": 3, "numberOfBedrooms": 2, "numberOfBathroomsTotal": 2,
             "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in
                                ("Fibre haut débit", "Parking privé", "Climatisation réversible", "Lave-linge", "Sèche-linge", "Piscine partagée", "Deux terrasses", "Vue mer")],
             "image": [f"{BASE}/assets/img/{n}.jpg" for n in ("terrasse-vue-mer", "vue-baie-de-nice", "sejour-salle-a-manger", "chambre-parentale", "cuisine-ilot")],
             "telephone": "+33611948235", "email": MAIL},
            {"@context": "https://schema.org", "@type": "FAQPage",
             "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": r}} for q, r in FAQ_MOB]},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE + "/"},
             {"@type": "ListItem", "position": 2, "name": "Bail mobilité à Nice", "item": BASE + "/bail-mobilite/"}]}])

# ================================================================ GUIDES
GUIDES = Path(os.environ.get("GUIDES_DIR", RACINE / "contenu/guides"))

def fine(s):
    return re.sub(r" ([?!;»])", "\u202f\\1", s)

def md_ligne(s):
    s = fine(E(s, quote=False))
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    def lien(m):
        bouton = re.search(r"disponibilit|availability", m.group(1), re.I)
        return f'<a class="bouton" href="{m.group(2)}">{m.group(1)}</a>' if bouton else f'<a href="{m.group(2)}">{m.group(1)}</a>'
    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", lien, s)

# Pictos devant les éléments de liste : le premier mot-clé trouvé dans l'élément décide (français, anglais, italien).
PICTO_LISTE = [("linge de lit", "linge"), ("bed linen", "linge"), ("biancheria", "linge"), ("lave-linge", "machine"), ("buanderie", "machine"), ("laundry", "machine"), ("lavanderia", "machine"),
               ("bus ", "repere"), ("bus 60", "repere"), ("tram", "repere"), ("clinique", "hopital"), ("chu", "hopital"), ("hôpital", "hopital"), ("hospital", "hopital"), ("ospedale", "hopital"),
               ("lacassagne", "hopital"), ("valrose", "campus"), ("campus", "campus"), ("aéroport", "avion"), ("airport", "avion"),
               ("aeroporto", "avion"), ("monaco", "couronne"), ("sophia", "puce"), ("plage", "parasol"), ("beach", "parasol"), ("spiaggia", "parasol"),
               ("scooter", "scooter"), ("deux-roues", "scooter"), ("bus", "repere"), ("tram", "repere"), ("train", "repere"), ("ter ", "repere"),
               ("chambre", "lit"), ("bedroom", "lit"), ("camer", "lit"), ("salle", "douche"), ("bathroom", "douche"), ("shower", "douche"),
               ("bagn", "douche"), ("wc", "douche"), ("toilet", "douche"), ("terrasse", "soleil"), ("terrace", "soleil"), ("terrazz", "soleil"),
               ("vue", "soleil"), ("view", "soleil"), ("vista", "soleil"), ("linge", "linge"), ("linen", "linge"), ("biancheria", "linge"),
               ("lave-linge", "machine"), ("washing", "machine"), ("lavatrice", "machine"), ("cuisine", "cuisine"), ("kitchen", "cuisine"),
               ("cucina", "cuisine"), ("fibre", "wifi"), ("fibra", "wifi"), ("internet", "wifi"), ("wifi", "wifi"), ("bureau", "ordi"),
               ("poste de travail", "ordi"), ("desk", "ordi"), ("scrivania", "ordi"), ("parking", "parking"), ("parcheggio", "parking"),
               ("piscine", "piscine"), ("pool", "piscine"), ("piscina", "piscine"), ("climatisation", "clim"), ("air conditioning", "clim"), ("climatizzazione", "clim"), ("clim", "clim"), ("air", "clim"), ("chauffage", "clim"),
               ("villa", "maison"), ("étage", "maison"), ("floor", "maison"), ("piano", "maison"), ("m²", "plan"), ("calme", "soleil"),
               ("pièce d'identité", "personne"), ("identity", "personne"), ("identità", "personne"), ("garantie", "cle"), ("guarant", "cle"),
               ("garanzia", "cle"), ("contrat", "plume"), ("contract", "plume"), ("contratto", "plume"), ("convention", "plume"),
               ("attestation", "plume"), ("certificate", "plume"), ("ordre de mission", "plume"), ("lettre", "plume"), ("letter", "plume"),
               ("vin", "verre"), ("wine", "verre"), ("vino", "verre"), ("courses", "panier"), ("supermarché", "panier"), ("shopping", "panier"),
               ("ménage", "menage"), ("cleaning", "menage"), ("pulizia", "menage"), ("facture", "facture"), ("invoice", "facture"), ("fattura", "facture")]

def picto_liste(texte):
    """Mots entiers seulement : « air » ne doit pas se reconnaître dans « faire »."""
    t = texte.lower()
    return next((n for k, n in PICTO_LISTE if re.search(r"(?<![\w-])" + re.escape(k.strip()) + r"(?![\w-])" if len(k.strip()) <= 5 else re.escape(k), t)), None)

def md_html(texte, pictos=True):
    """Markdown des articles -> HTML : intertitres, paragraphes, listes, tableaux, gras, liens."""
    out, bloc = [], []
    def vider():
        if not bloc: return
        if bloc[0].startswith(("- ", "* ")):
            items = [l[2:] for l in bloc]
            if all(re.match(r"\[[ xX]\] ", i) for i in items):  # liste à cocher
                out.append('<ul class="a-cocher">' + "".join(f'<li><span class="case" aria-hidden="true"></span>{md_ligne(i[4:])}</li>' for i in items) + "</ul>")
            elif pictos and sum(1 for i in items if picto_liste(i)) * 2 >= len(items):  # liste de lieux ou d'équipements : un picto par ligne
                out.append('<ul class="pictos">' + "".join(f'<li>{pic(picto_liste(i) or "repere", "pic-s")}<span>{md_ligne(i)}</span></li>' for i in items) + "</ul>")
            else:
                out.append("<ul>" + "".join(f"<li>{md_ligne(i)}</li>" for i in items) + "</ul>")
        elif re.match(r"\d+\. ", bloc[0]):
            out.append("<ol>" + "".join(f"<li>{md_ligne(l.split('. ', 1)[1])}</li>" for l in bloc) + "</ol>")
        elif bloc[0].startswith("|"):
            rangs = [[c.strip() for c in l.strip("|").split("|")] for l in bloc if not re.match(r"^\|[\s:|-]+\|$", l)]
            out.append('<div class="table"><table><thead><tr>' + "".join(f"<th>{md_ligne(c)}</th>" for c in rangs[0]) + "</tr></thead><tbody>"
                       + "".join("<tr>" + "".join(f"<td>{md_ligne(c)}</td>" for c in r) + "</tr>" for r in rangs[1:]) + "</tbody></table></div>")
        elif bloc[0].startswith("> "):
            out.append("<blockquote>" + md_ligne(" ".join(l[2:] for l in bloc)) + "</blockquote>")
        else:
            out.append(f"<p>{md_ligne(' '.join(bloc))}</p>")
        bloc.clear()
    for l in texte.splitlines():
        l = l.rstrip()
        if not l: vider(); continue
        m = re.match(r"(#{2,3}) (.+)", l)
        if m:
            vider(); n = len(m.group(1)); out.append(f"<h{n}>{md_ligne(m.group(2))}</h{n}>"); continue
        if bloc and (l[:2] in ("- ", "* ") or l.startswith("|") or re.match(r"\d+\. ", l)) != (bloc[0][:2] in ("- ", "* ") or bloc[0].startswith("|") or bool(re.match(r"\d+\. ", bloc[0]))):
            vider()
        bloc.append(l)
    vider()
    return "".join(out)

def lire_md(f):
    tete_md, corps = f.read_text(encoding="utf-8").split("---", 2)[1:]
    meta = dict(l.split(": ", 1) for l in tete_md.strip().splitlines())
    meta["corps"], meta["fichier"] = corps.strip(), f.stem
    return meta

def lire_guides(dossier=None):
    """Articles d'une langue, dans l'ordre des titres français (le guide complet en premier)."""
    dossier = dossier or GUIDES
    fr = sorted((lire_md(f) for f in GUIDES.glob("*.md")), key=lambda a: (a["fichier"] != "bail-mobilite-nice-guide-complet", a["titre"])) if GUIDES.exists() else []
    ordre = [a["fichier"] for a in fr]
    articles = [lire_md(f) for f in dossier.glob("*.md")] if dossier.exists() else []
    return sorted(articles, key=lambda a: ordre.index(a["fichier"]) if a["fichier"] in ordre else 99)

# Images des Guides : aucune photo du logement. Affiches PLM du domaine public et photos libres de Wikimedia Commons.
CREDITS = {
    "affiche-cote-d-azur": ("Affiche PLM « Côte d'Azur », F. Hugo d'Alési", "Domaine public", "https://commons.wikimedia.org/wiki/File:Chemin_de_fer_du_nord_et_de_PLM._C%C3%B4te_d%27Azur._Cannes,_Nice,_Monaco_(...)_-_affiche_-_(F._Hugo_d%27Al%C3%A9si)_;_Ateliers_F._Hugo_d%27Al%C3%A9si,_5_Place_Pigalle,_Paris_-_btv1b9004457q.jpg"),
    "affiche-hiver-a-nice": ("Affiche PLM « L'Hiver à Nice », F. Hugo d'Alési", "Domaine public", "https://commons.wikimedia.org/wiki/File:Chemins_de_fer_P._L._M._L%27Hiver_%C3%A0_Nice_(...)_-_affiche_-_F._Hugo_d%27Al%C3%A9si_-_btv1b90160043.jpg"),
    "affiche-nice-plm": ("Affiche PLM « Nice », F. Hugo d'Alési", "Domaine public", "https://commons.wikimedia.org/wiki/File:Affiche_PLM_Nice.jpg"),
    "affiche-monaco-broders": ("Affiche PLM « Monaco, Monte-Carlo, au pays du soleil », Roger Broders", "Domaine public", "https://commons.wikimedia.org/wiki/File:Flickr_-_%E2%80%A6trialsanderrors_-_Monaco,_Monte-Carlo,_au_pays_du_soleil,_travel_poster_for_PLM,_ca._1920.jpg"),
    "affiche-villefranche": ("Affiche « Villefranche-sur-Mer, port de tourisme », Roger Broders", "Domaine public", "https://commons.wikimedia.org/wiki/File:Edit%C3%A9_par_le_Syndicat_d%27Initiative_-_Villefranche_s-_Mer,_Port_de_tourisme_-_affiche_-_Roger_Broders_-_btv1b9012820q.jpg"),
    "affiche-matisse-nice": ("Affiche « France Côte d'Azur, Nice », Henri Matisse", "Domaine public", "https://commons.wikimedia.org/wiki/File:France._Cote_d%27azur_-_Nice..._-_affiche_-_Henri_Matisse_-_btv1b9005291c.jpg"),
    "affiche-ceria-cote-d-azur": ("Affiche SNCF « Côte d'Azur », Edmond Céria", "Domaine public", "https://commons.wikimedia.org/wiki/File:C%C3%B4te_d%27Azur_-_Soci%C3%A9t%C3%A9_Nationale_des_Chemins_de_Fer_Fran%C3%A7ais_-_affiche_-_C%C3%A9ria_-_btv1b53074563g.jpg"),
    "affiche-cheret-hiver-a-nice": ("Affiche « L'Hiver à Nice », Jules Chéret", "Domaine public", "https://commons.wikimedia.org/wiki/File:L%27Hiver_%C3%A0_Nice_-_affiche_-_Jules_Ch%C3%A9ret_-_btv1b90105736.jpg"),
    "affiche-chanteau-nice-digne": ("Affiche « Nice à Digne par l'autorail », Gabriel Chanteau, 1935", "Domaine public", "https://commons.wikimedia.org/wiki/File:Affiche_publicitaire_Chemins_de_fer_de_la_Provence_%22Nice_%C3%A0_Digne_par_l%27autorail%22,_par_Gabriel_Chanteau_(1874-1955),_1935.jpg"),
    "affiche-broders-montagnes": ("Affiche « La Côte d'Azur, ses montagnes », Roger Broders", "Domaine public", "https://commons.wikimedia.org/wiki/File:La_C%C3%B4te_d%27Azur_ses_montagnes._Edition_de_la_F%C3%A9d%C3%A9ration_des_Essi_C%C3%B4te_d%27Azur_et_Corse_-_affiche_-_Roger_Broders_-_btv1b90039507.jpg"),
    "hopital-pasteur": ("Hôpital Pasteur, Nice. Photo Jesmar", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:H%C3%B4pital_Pasteur_P1010629.JPG"),
    "tram-ligne-2": ("Tramway de Nice, ligne 2. Photo Snoopy 31", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Ligne_2_Tram_de_Nice_07-20.jpg"),
    "chateau-de-bellet": ("Château de Bellet, Nice. Photo Château de Bellet", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:ChateaudeBellet_Boonz-drone2.jpg"),
    "vignoble-saint-jean-bellet": ("Vignoble de Saint-Jean de Bellet. Photo Magnetto", "CC BY-SA 3.0", "https://commons.wikimedia.org/wiki/File:Saint_Jean_Bellet,_le_vignoble.jpg"),
    "baie-des-anges": ("La Baie des Anges, Nice. Photo GFreihalter", "CC BY-SA 4.0", "https://commons.wikimedia.org/wiki/File:Nice_(06)_Baie_des_Anges_773.jpg"),
}
# Par article : couverture, couleur du bloc, photo insérée avant le n-ième intertitre, et trois repères chiffrés.
VISUELS = {
    "bail-mobilite-nice-guide-complet": ("affiche-ceria-cote-d-azur", "azur", ("baie-des-anges", 5),
        [("1 à 10", "mois de bail", "calendrier"), ("0 €", "de dépôt de garantie", "cle"), ("1", "mois de préavis pour le locataire", "plume")]),
    "logement-interne-chu-nice": ("affiche-cheret-hiver-a-nice", "corail", ("hopital-pasteur", 4),
        [("15", "min du CHU Pasteur 2", "hopital"), ("16", "min du Centre Lacassagne", "hopital"), ("3 mai", "2027, changement de semestre", "calendrier")]),
    "logement-monaco-nice": ("affiche-monaco-broders", "nuit", ("baie-des-anges", 4),
        [("22", "min de Monaco en voiture", "couronne"), ("1 sur 4", "salarié du privé de Monaco vit à Nice", "personne"), ("20", "min de l'aéroport", "avion")]),
    "mission-nice-3-a-10-mois": ("affiche-chanteau-nice-digne", "ocre", ("tram-ligne-2", 6),
        [("3 à 10", "mois de mission", "calendrier"), ("28", "min de Sophia Antipolis", "puce"), ("1", "facture, tout compris", "facture")]),
    "vivre-colline-de-bellet-nice": ("affiche-broders-montagnes", "mer", ("vignoble-saint-jean-bellet", 3),
        [("1941", "AOC Bellet, par décret", "verre"), ("26 m²", "de terrasses vue mer", "soleil"), ("13", "min du campus Valrose", "campus")]),
}

def credit(n):
    t, lic, url = CREDITS[n]
    return f'<a href="{url}" rel="noopener">{E(t)}</a> · {E(lic)}'

def gimg(n, alt, cls="", charge="lazy"):
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{{R}}assets/img/guides/{n}.jpg" alt="{E(alt)}" loading="{charge}">'

def mots(texte):
    return len(re.findall(r"\w+", texte))

# Pictos des intertitres : le premier mot-clé trouvé dans le titre décide.
PICTO_TITRE = [("monaco", "couronne"), ("vin", "verre"), ("domaines", "verre"), ("courses", "panier"), ("scooter", "scooter"),
               ("travailler depuis", "ordi"), ("garantie", "cle"), ("dépôt", "cle"), ("visale", "cle"), ("arrivée", "valise"),
               ("employeur", "societe"), ("hôpital ou", "societe"), ("coûte", "facture"), ("comprend", "facture"), ("impôts", "facture"),
               ("ressemble", "plan"), ("transition", "valise"), ("semestre", "calendrier"), ("dure", "calendrier"), ("réserver", "calendrier"),
               ("qui peut", "personne"), ("salariés", "personne"), ("chu", "hopital"), ("minutes", "repere"), ("aller", "repere"),
               ("déplacer", "repere"), ("voiture", "repere"), ("où se", "repere"), ("se trouve", "repere"), ("pièces", "plume"),
               ("démarches", "plume"), ("contrat", "plume"), ("résilier", "plume"), ("dossier", "plume"), ("demande", "plume"),
               ("bail", "plume"), ("logement", "plan")]

def picto_titre(titre):
    t = titre.lower()
    return next((n for k, n in PICTO_TITRE if k in t), "repere")

TRAJETS = [("Clinique Kantys Centre", 12, "hopital"), ("Campus Valrose", 13, "campus"), ("CHU Pasteur 2", 15, "hopital"),
           ("Centre Antoine Lacassagne", 16, "hopital"), ("Aéroport", 20, "avion"), ("Monaco", 22, "couronne"),
           ("Sophia Antipolis", 28, "puce"), ("La plage", 7, "parasol")]

def dg_trajets(focus=()):
    lignes = "".join(f'<li class="{"f" if l in focus else ""}"><span class="l">{pic(i, "pic-s")}{E(l)}</span><span class="barre"><i style="width:{m / 30 * 100:.0f}%"></i></span><b>{m}<small> min</small></b></li>'
                     for l, m, i in sorted(TRAJETS, key=lambda x: x[1]))
    return f'<figure class="dg dg-trajets"><figcaption class="dg-titre">{pic("repere", "pic-s")}Depuis l\'appartement, en voiture</figcaption><ul>{lignes}</ul><p class="dg-note">Minutes hors trafic. Bus 60 vers le tram ligne 2 à Magnan.</p></figure>'

def dg_prix():
    rangs = [("1 à 2 mois", 3600), ("3 à 6 mois", 3200), ("7 à 10 mois", 2880)]
    lignes = "".join(f'<li><span class="l">{pic("calendrier", "pic-s")}{l}</span><span class="barre"><i style="width:{p / 3600 * 100:.0f}%"></i></span><b>{p:,} €</b></li>'.replace(",", " ") for l, p in rangs)
    return f'<figure class="dg dg-prix"><figcaption class="dg-titre">{pic("facture", "pic-s")}Prix par mois, tout compris</figcaption><ul>{lignes}</ul><p class="dg-gain"><b>− 720 €</b> par mois sur 7 à 10 mois, par rapport à 1 à 2 mois.</p></figure>'

def dg_duree():
    case = "".join(f'<span class="c {"a" if m <= 2 else "b" if m <= 6 else "d"}">{m}</span>' for m in range(1, 11))
    return f'''<figure class="dg dg-duree"><figcaption class="dg-titre">{pic("calendrier", "pic-s")}Durée du bail, en mois</figcaption>
<div class="mois">{case}</div>
<div class="legende-dg"><span><i class="a"></i>1 à 2 mois · 3 600 €</span><span><i class="b"></i>3 à 6 mois · 3 200 €</span><span><i class="d"></i>7 à 10 mois · 2 880 €</span></div>
<div class="societe-dg"><span style="margin-left:20%">{pic("societe", "pic-s")}Bail au nom de l\'employeur : à partir de 3 mois</span></div></figure>'''

def dg_semestres():
    mois = ["nov.", "déc.", "janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct."]
    cases = "".join(f'<span class="{"h" if k < 6 else "e"}">{m}</span>' for k, m in enumerate(mois))
    return f'''<figure class="dg dg-semestres"><figcaption class="dg-titre">{pic("calendrier", "pic-s")}L'année d'internat à Nice</figcaption>
<div class="noms"><span>Semestre d'hiver</span><span>Semestre d'été</span></div><div class="mois12">{cases}</div>
<div class="bail6"><span>Un semestre = 6 mois, dans un bail mobilité de 1 à 10 mois</span></div>
<p class="dg-note">Prochain changement de semestre : 3 mai 2027 (ARS Provence-Alpes-Côte d'Azur).</p></figure>'''

def dg_un_sur_quatre():
    gens = "".join(f'<span class="{"f" if k == 0 else ""}">{pic("personne", "pic")}</span>' for k in range(4))
    return f'''<figure class="dg dg-quatre"><div class="gens">{gens}</div><div><b>1 sur 4</b><p>salarié du secteur privé de Monaco vit à Nice : plus de 16 000 personnes.</p><p class="dg-note">Source : IMSEE, Observatoire de l'Emploi 2025.</p></div></figure>'''

def dg_compris():
    items = [("energie", "Eau, électricité, chauffage"), ("wifi", "Fibre"), ("parking", "Place de parking privée"),
             ("linge", "Linge de lit et de toilette, fourni à l'arrivée"), ("menage", "Ménage de sortie"), ("facture", "Une seule facture")]
    tuiles = "".join(f'<div>{pic(i)}<span>{E(l)}</span></div>' for i, l in items)
    return f'<figure class="dg dg-compris"><figcaption class="dg-titre">{pic("facture", "pic-s")}Compris dans le prix mensuel</figcaption><div class="tuiles6">{tuiles}</div></figure>'

def encadre(titre, points, icone="plume"):
    return f'<aside class="encadre"><span class="sur">{pic(icone, "pic-s")}{E(titre)}</span><ul>' + "".join(f"<li>{E(p)}</li>" for p in points) + "</ul></aside>"

# Par article : (avant l'intertitre n, bloc). n = 0 : en tête d'article ; n au-delà du dernier : en fin.
DATAGRAPHIE = {
    "bail-mobilite-nice-guide-complet": [
        (1, encadre("À retenir", ["De 1 à 10 mois, ni renouvelable ni reconductible.", "Aucun dépôt de garantie.", "Le justificatif du motif est demandé avant la signature."])),
        (3, dg_duree()), (9, dg_compris()), (10, dg_prix())],
    "logement-interne-chu-nice": [
        (1, encadre("À retenir", ["Un semestre de 6 mois tient dans un bail mobilité.", "Le bail peut être au nom de l'établissement à partir de 3 mois.", "Aucun dépôt de garantie en bail mobilité."])),
        (2, dg_semestres()), (5, dg_trajets(("CHU Pasteur 2", "Centre Antoine Lacassagne", "Clinique Kantys Centre"))), (7, dg_prix())],
    "logement-monaco-nice": [
        (2, dg_un_sur_quatre()), (3, dg_trajets(("Monaco", "Aéroport"))),
        (6, encadre("À retenir", ["Monaco à 22 minutes en voiture, hors trafic.", "Bail au nom de l'employeur à partir de 3 mois.", "Un prix mensuel tout compris, une facture."]))],
    "mission-nice-3-a-10-mois": [
        (1, encadre("À retenir", ["Bail mobilité de 1 à 10 mois, ou bail au nom de la société à partir de 3 mois.", "Une seule facture, tout compris.", "Facture exonérée de TVA, au nom du payeur."])),
        (2, dg_prix()), (2, dg_compris())],
    "vivre-colline-de-bellet-nice": [
        (2, encadre("À retenir", ["Sur la colline de Bellet, à l'ouest de Nice.", "Vue sur la Baie des Anges depuis deux terrasses.", "AOC Bellet, reconnue par décret en 1941."], "verre")),
        (6, dg_trajets(("La plage", "Campus Valrose", "Aéroport")))],
}

def guides():
    for langue in ("fr",) + i18n.LANGUES:
        guides_langue(langue)

def guides_langue(langue):
    articles = lire_guides(GUIDES if langue == "fr" else GUIDES / langue)
    if not articles: return
    ignorer = set()
    if langue != "fr":  # le texte des articles est déjà dans la langue : il ne passe pas par le dictionnaire
        for a in articles:
            ignorer |= i18n.textes(md_html(a["corps"])) | {i18n.norme(a["titre"]), i18n.norme(a["description"]), i18n.norme(a["title_seo"])}
            ignorer |= {i18n.norme(x) for x in a.get("chapo", "").split("|")}
    for i, a in enumerate(articles):
        couv, couleur, (photo, avant), reperes = VISUELS[a["fichier"]]
        corps_html = md_html(a["corps"])
        titres = re.findall(r"<h2>(.+?)</h2>", corps_html)
        for k, t in enumerate(titres):
            corps_html = corps_html.replace(f"<h2>{t}</h2>", f'<h2 id="s{k + 1}"><span class="num">{pic(picto_titre(t), "pic-s")}{k + 1:02d}</span>{t}</h2>', 1)
        for n, bloc in DATAGRAPHIE.get(a["fichier"], []):
            tableau = re.search(r'<div class="table">(?:(?!</div>).)*3 600 €.*?</div>', corps_html, re.S) if "dg-prix" in bloc else None
            if tableau:  # le graphique des prix remplace le tableau des prix de l'article
                corps_html = corps_html.replace(tableau.group(0), bloc, 1); continue
            cible = f'<h2 id="s{n}"'
            corps_html = corps_html.replace(cible, bloc + cible, 1) if cible in corps_html else corps_html + bloc
        fig = f'<figure class="g-photo">{gimg(photo, CREDITS[photo][0])}<figcaption>{credit(photo)}</figcaption></figure>'
        cible = f'<h2 id="s{avant}"'
        corps_html = corps_html.replace(cible, fig + cible, 1) if cible in corps_html else corps_html + fig
        sommaire = "".join(f'<li><a href="#s{k + 1}">{re.sub("<[^>]+>", "", t)}</a></li>' for k, t in enumerate(titres))
        rep = "".join(f'<div>{pic(i)}<b>{E(c)}</b><span>{E(l)}</span></div>' for c, l, i in reperes)
        autres = [b for b in articles if b is not a][:3]
        suite = "".join(f'<a class="g-tuile {VISUELS[b["fichier"]][1]}" href="{b["slug"]}.html">{gimg(VISUELS[b["fichier"]][0], b["titre"])}<span class="t">{E(b["titre"])}</span></a>' for b in autres)
        corps = f"""
<section class="g-hero {couleur}">
  <div class="g-hero-texte">
    <a class="sur" href="./"><span>Guide n°</span>&nbsp;{i + 1} · <span>Se loger à Nice</span></a>
    <h1>{E(a["titre"])}</h1>
    <p class="chapo">{"<br>".join(E(x.strip()) for x in a.get("chapo", a["description"]).split("|"))}</p>
    <span class="g-meta">{max(1, round(mots(a["corps"]) / 220))}&nbsp;<span>min de lecture</span></span>
  </div>
  <figure class="g-hero-image{" cadre" if couv.startswith("affiche") else ""}" style="--fond:url({{R}}assets/img/guides/{couv}.jpg)"><span class="passe">{gimg(couv, CREDITS[couv][0], charge="eager")}</span><figcaption>{credit(couv)}</figcaption></figure>
</section>
<div class="store" aria-hidden="true"></div>
<section class="g-reperes"><div class="wrap">{rep}</div></section>
<div class="wrap g-corps">
  <aside class="g-sommaire"><span class="sur">Sommaire</span><ol>{sommaire}</ol>
    <a class="bouton" href="../bail-mobilite/#demande">Demander une disponibilité</a></aside>
  <article class="guide">{corps_html}</article>
</div>
<section class="azur guide-fin"><div class="etroit centre">
  <span class="sur">Les Piafs des Collines</span>
  <h2 class="phrase-prix">77 m² sur la colline de Bellet, face à la Baie&nbsp;des&nbsp;Anges,<br><em>de 1&nbsp;à 10&nbsp;mois.</em></h2>
  <a class="bouton" href="../bail-mobilite/">Voir le logement</a>
</div></section>
<section class="g-suite"><div class="wrap"><span class="sur">À lire aussi</span><div class="g-tuiles">{suite}</div></div></section>"""
        page(f"guides/{a['slug']}.html", a["title_seo"], a["description"], "guides", "", corps, image=f"guides/{couv}",
             cle="guide:" + a["fichier"], langue=langue, ignorer=ignorer, jsonld=[
            {"@context": "https://schema.org", "@type": "Article", "headline": a["titre"], "description": a["description"], "inLanguage": {"fr": "fr-FR", "en": "en", "it": "it-IT"}[langue],
             "image": f"{BASE}/assets/img/guides/{couv}.jpg", "url": url_propre(f"guides/{a['slug']}.html"),
             "publisher": {"@type": "Organization", "name": "Les Piafs des Collines", "url": BASE + "/"}},
            {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
             {"@type": "ListItem", "position": 1, "name": "Accueil", "item": BASE + "/"},
             {"@type": "ListItem", "position": 2, "name": "Guides", "item": BASE + "/guides/"},
             {"@type": "ListItem", "position": 3, "name": a["titre"], "item": url_propre(f"guides/{a['slug']}.html")}]}])
    une, reste = articles[0], articles[1:]
    tuiles = "".join(f'<a class="g-tuile {VISUELS[b["fichier"]][1]}" href="{b["slug"]}.html">{gimg(VISUELS[b["fichier"]][0], b["titre"])}<span class="n"><span>Guide n°</span> {k + 2}</span><span class="t">{E(b["titre"])}</span><span class="d">{E(b["description"])}</span></a>' for k, b in enumerate(reste))
    corps = f"""
<section class="g-hero azur g-index">
  <div class="g-hero-texte">
    <span class="sur">Les guides des Piafs</span>
    <h1>Se loger à Nice,<br><em>de 1&nbsp;à 10&nbsp;mois</em></h1>
    <p class="chapo">Bail mobilité, internat, mission, Monaco, vie de quartier<br><span class="chapo-sans">Ce qu'il faut savoir avant de poser sa valise sur la Riviera</span></p>
  </div>
  <figure class="g-hero-image cadre rayee" style="--fond:url({{R}}assets/img/guides/affiche-hiver-a-nice.jpg)"><span class="passe">{gimg("affiche-hiver-a-nice", CREDITS["affiche-hiver-a-nice"][0], charge="eager")}</span><figcaption>{credit("affiche-hiver-a-nice")}</figcaption></figure>
</section>
<div class="store" aria-hidden="true"></div>
<section class="g-une-section"><div class="wrap">
  <a class="g-une" href="{une["slug"]}.html"><span class="g-une-cadre"><span class="passe">{gimg(VISUELS[une["fichier"]][0], une["titre"])}</span></span>
    <div><span class="n"><span>Guide n°</span> 1 · <span>À lire en premier</span></span><span class="t">{E(une["titre"])}</span><span class="d">{E(une["description"])}</span><span class="f">Lire le guide →</span></div></a>
</div></section>
<section class="g-liste"><div class="wrap"><div class="g-tuiles quatre">{tuiles}</div>
  <p class="note g-credits">Affiches anciennes de la Côte d’Azur, domaine public. Photos libres de Wikimedia Commons, créditées sous chaque image.</p></div></section>"""
    page("guides/index.html", "Guides : se loger à Nice en bail mobilité | Les Piafs des Collines",
         "Bail mobilité à Nice, logement près du CHU, travailler à Monaco : nos guides pour se loger à Nice pour 1 à 10 mois.", "guides", "", corps,
         image="guides/affiche-hiver-a-nice", cle="guides", langue=langue, ignorer=ignorer)

# ================================================================ divers
# ---------------------------------------------------------------- pages légales (bail mobilité)
# Textes rédigés par Themis dans contenu/legal/*.md. Elles remplacent les sept pages de l'ancienne location saisonnière.
LEGAL_DIR = RACINE / "contenu/legal"
PAGES_LEGALES = [("mentions-legales", "Mentions légales"), ("conditions-de-location", "Conditions de location"),
                 ("reglement-interieur", "Règlement intérieur"), ("confidentialite", "Confidentialité et cookies")]

def pages_legales():
    for slug, nom in PAGES_LEGALES:
        f = LEGAL_DIR / f"{slug}.md"
        if not f.exists():
            continue
        a = lire_md(f)
        corps_html = md_html(re.sub(r"^# .+\n+", "", a["corps"]), pictos=False)
        corps_html = re.sub(r"\[À COMPLÉTER[^\]]*\]", lambda m: f'<mark class="a-completer">{m.group(0)}</mark>', corps_html)
        titres = re.findall(r"<h2>(.+?)</h2>", corps_html)
        for k, t2 in enumerate(titres):
            corps_html = corps_html.replace(f"<h2>{t2}</h2>", f'<h2 id="s{k + 1}"><span class="num">{k + 1:02d}</span>{t2}</h2>', 1)
        sommaire = "".join(f'<li><a href="#s{k + 1}">{re.sub("<[^>]+>", "", t2)}</a></li>' for k, t2 in enumerate(titres))
        autres = "".join(f'<a href="{s}.html"{" aria-current=\"page\"" if s == slug else ""}>{E(n)}</a>' for s, n in PAGES_LEGALES if (LEGAL_DIR / f"{s}.md").exists())
        corps = f"""
<section class="legal-tete"><div class="wrap">
  <span class="sur">Informations</span>
  <h1>{E(a["titre"])}</h1>
  <p class="chapo">{E(a["description"])}</p>
  <nav class="legal-onglets">{autres}</nav>
</div></section>
<div class="store" aria-hidden="true"></div>
<div class="wrap g-corps legal-corps">
  <aside class="g-sommaire"><span class="sur">Sommaire</span><ol>{sommaire}</ol></aside>
  <article class="guide legal">{corps_html}</article>
</div>"""
        page(f"{slug}.html", f"{a['titre']} | Les Piafs des Collines", a["description"], "info", "", corps)

def page_cookies():
    # fondue dans la page « Confidentialité et cookies » le 24/10/2026
    for c in ("cookies.html", "en/cookies.html", "it/cookies.html"):
        renvoi(c, "/confidentialite")
    return

def ancienne_page_cookies():
    corps = f"""
<section class="guide-tete"><div class="etroit">
  <span class="sur">Informations</span><h1>Cookies</h1>
</div></section>
<article class="etroit guide">
<h2>Ce site ne dépose aucun cookie</h2>
<p>Aucun cookie n'est déposé sur votre appareil, ni pour la mesure d'audience, ni pour la publicité, ni pour le partage sur les réseaux sociaux. Aucun consentement ne vous est donc demandé.</p>
<h2>Ressources techniques</h2>
<p>Le site est hébergé par Cloudflare, qui traite les données techniques de connexion nécessaires à l'affichage des pages. Les polices de caractères sont chargées depuis Google Fonts : votre adresse IP est transmise à Google à cette occasion.</p>
<h2>Formulaire de demande</h2>
<p>Le formulaire de demande ouvre votre logiciel de messagerie. Le site n'enregistre aucune des informations que vous y saisissez.</p>
<h2>Une question ?</h2>
<p>Écrivez à <a href="mailto:{MAIL}">{MAIL}</a>.</p>
</article>"""
    page("cookies.html", "Cookies | Les Piafs des Collines", "Le site Les Piafs des Collines ne dépose aucun cookie.", "info", "", corps)

def page_404():
    corps = f"""{bandeau("bandeau-accueil", "Page introuvable")}<section><div class="etroit centre"><p>Cette page n'existe pas ou a changé d'adresse.</p><p><a class="bouton" href="/">Retour à l'accueil</a></p></div></section>"""
    page("404.html", "Page introuvable | Les Piafs des Collines", "", "saison", "", corps.replace("{R}", "/"))

def redirections():
    """Les anciennes adresses Wix renvoient vers les nouvelles (Cloudflare Pages lit _redirects)."""
    anciennes = {"/accueil": "/saisonniere/", "/hôtes": "/saisonniere/hotes.html", "/blog": "/saisonniere/environs.html",
                 "/ateliers": "/saisonniere/ateliers.html", "/livre-or": "/saisonniere/livre-or.html", "/faq": "/saisonniere/faq.html",
                 "/tarifs": "/saisonniere/tarifs.html", "/contact": "/saisonniere/contact.html", "/copie-de-contact": "/saisonniere/contact.html",
                 "/post/la-métropole-nice-côte-d-azur": "/saisonniere/environs/la-metropole-nice-cote-d-azur.html",
                 "/post/créez-un-superbe-blog": "/saisonniere/environs/nissa-la-bella.html"}
    for slug, src, _ in LEGAL:
        anciennes["/" + src] = f"/saisonniere/{slug}.html"
    if not SAISON_ACTIVE:
        # offre saisonnière éteinte : tout mène au bail mobilité, sauf les pages légales, qui mènent aux nouvelles
        legales = {"/" + src: "/" + RENVOIS_LEGAUX[slug] for slug, src, _ in LEGAL}
        anciennes = {a: legales.get(a, "/bail-mobilite/") for a, n in anciennes.items()}
    lignes = []
    from urllib.parse import quote
    for a, n in anciennes.items():
        n = n[:-5] if n.endswith(".html") else n
        lignes.append(f"{quote(a)} {n} 301")
        if quote(a) != a: lignes.append(f"{a} {n} 301")
    lignes.append("/guides/vivre-collines-de-bellet-nice /guides/vivre-colline-de-bellet-nice 301")
    if not ACCUEIL_ACTIF:
        lignes += ["/ /bail-mobilite/ 302", "/en/ /en/bail-mobilite/ 302", "/it/ /it/bail-mobilite/ 302"]
    lignes.append("/blog/* " + ("/saisonniere/environs" if SAISON_ACTIVE else "/bail-mobilite/") + " 301")
    (SITE / "_redirects").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("   _redirects")

def sitemap():
    import datetime
    jour = datetime.date.today().isoformat()
    prio = {"index.html": "1.0", "bail-mobilite/index.html": "0.9", "saisonniere/index.html": "0.8", "guides/index.html": "0.7"}
    urls = "".join(f"<url><loc>{url_propre(c)}</loc><lastmod>{jour}</lastmod><priority>{prio.get(c, '0.5')}</priority></url>"
                   for c in PAGES if c != "404.html" and (SAISON_ACTIVE or not c.startswith("saisonniere/")) and (GUIDES_VALIDES or "guides/" not in c) and (LANGUES_VALIDEES or not c.startswith(("en/", "it/"))) and (ACCUEIL_ACTIF or c not in ("index.html", "en/index.html", "it/index.html")))
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print("   sitemap.xml, robots.txt")

if __name__ == "__main__":
    print("Génération de site/ :")
    routes()
    accueil(); saison_appartement(); saison_hotes(); saison_ateliers(); saison_livre_or(); saison_faq()
    saison_tarifs(); saison_contact(); saison_environs(); saison_legal(); bail_mobilite(); guides(); pages_legales(); page_cookies(); page_404(); redirections(); sitemap()
    n = i18n.rapport()
    print(f"Textes à traduire : {n} (contenu/i18n/manquants-*.json)" if n else "Traductions complètes.")
    print("Terminé.")
