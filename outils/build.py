#!/usr/bin/env python3
"""Génère site/ à partir du contenu aspiré du site Wix (_source/) et des pages écrites ici.

Lancer :  python3 outils/build.py
Le contenu saisonnier est repris mot pour mot depuis _source/site_wix_2026-10-23/blocs/*.json.
"""
import json, html, os, re, unicodedata
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SITE = RACINE / "site"
BLOCS = RACINE / "_source/site_wix_2026-10-23/blocs"
E = html.escape

TEL = "+33 (0)6 11 94 82 35"
TEL_LIEN = "+33611948235"
MAIL = "contact@lespiafsdescollines.com"
ADRESSE = "202 bis, Route de Bellet<br>06200 Nice - France"
FACEBOOK = "https://www.facebook.com/lespiafsdescollines"
ENREGISTREMENT = "06088017951MX"

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
         '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Montserrat:wght@400;600;700&family=Source+Sans+3:wght@400;600&display=swap" rel="stylesheet">')

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
NAV_MOB = [("#logement", "Le logement"), ("#prix", "Prix"), ("#contrat", "Contrat"),
           ("#acces", "Accès"), ("#avis", "Avis"), ("#demande", "Demande")]

BASE = "https://www.lespiafsdescollines.com"
GEO = (43.701472, 7.231682)

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
<link rel="icon" type="image/png" href="{r}assets/img/oiseau.png">
{'<meta name="robots" content="noindex">' if chemin == "404.html" else f'<link rel="canonical" href="{url_propre(chemin)}">'}
<meta property="og:type" content="website"><meta property="og:locale" content="fr_FR"><meta property="og:site_name" content="Les Piafs des Collines">
<meta property="og:url" content="{url_propre(chemin)}">
<meta property="og:title" content="{E(titre)}"><meta property="og:description" content="{E(description)}">
<meta property="og:image" content="{BASE}/assets/img/{image}.jpg"><meta name="twitter:card" content="summary_large_image">
{ld}
{FONTS}
<link rel="stylesheet" href="{r}assets/style.css">
</head><body>
"""

def entete(espace, courant, profondeur):
    r = "../" * profondeur
    if espace == "saison":
        liens = "".join(
            f'<a href="{r}saisonniere/{(slug + ".html") if slug else ""}"{" aria-current=\"page\"" if slug == courant else ""}>{E(lib)}</a>'
            for slug, lib in NAV_SAISON)
        liens += f'<a class="cta" href="{r}saisonniere/contact.html">Réserver</a>'
    else:
        liens = "".join(f'<a href="{a}">{E(l)}</a>' for a, l in NAV_MOB)
        liens += '<a class="cta" href="#demande">Demander une disponibilité</a>'
    return f"""<header class="entete"><div class="wrap">
<a class="marque" href="{r}index.html"><img src="{r}assets/img/oiseau-blanc.png" alt="">Les Piafs des Collines</a>
<button class="burger" aria-label="Menu" onclick="this.nextElementSibling.classList.toggle('ouvert')">☰</button>
<nav class="nav">{liens}</nav>
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
        legal = f"""<h5>Informations</h5><ul>
<li><a href="{s}mentions-legales.html">Mentions légales</a></li>
<li><a href="{s}politique-de-confidentialite.html">Politique de confidentialité</a></li></ul>"""
    return f"""<footer class="pied"><div class="wrap"><div class="cols">
<div><h5>Les Piafs des Collines</h5><p>{ADRESSE}</p>
<p><a href="mailto:{MAIL}">{MAIL}</a><br><a href="tel:{TEL_LIEN}">{TEL}</a></p>
<p><a href="{FACEBOOK}" rel="noopener">Facebook</a></p></div>
<div><h5>Nos locations</h5><ul>
<li><a href="{r}index.html">Accueil</a></li>
<li><a href="{r}saisonniere/">Location saisonnière</a></li>
<li><a href="{r}bail-mobilite/">Bail mobilité, 1 à 10 mois</a></li></ul></div>
<div>{legal}</div>
</div>
<div class="bas"><span>© {2026} Les Piafs des Collines</span><span>Design by <a href="http://www.creative-explorer.fr" rel="noopener">Creative Explorer</a></span></div>
</div></footer>
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

def page(chemin, titre, description, espace, courant, corps, scripts="", jsonld=None, image="terrasse-vue-mer"):
    prof = chemin.count("/")
    PAGES.append(chemin)
    contenu = tete(titre, description, prof, chemin, jsonld, image) + entete(espace, courant, prof) + "<main>" + corps + "</main>" + pied(espace, prof) + scripts + "</body></html>\n"
    contenu = propre(contenu.replace("{R}", "../" * prof))
    f = SITE / chemin
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(contenu, encoding="utf-8")
    print("  ", chemin)

def bandeau(img, titre, sous=""):
    s = f"<p>{E(sous)}</p>" if sous else ""
    return f'<div class="bandeau" style="background-image:url({{R}}assets/img/{img}.jpg)"><div><h1>{E(titre)}</h1>{s}</div></div>'

def img(nom, alt, cls=""):
    c = f' class="{cls}"' if cls else ""
    return f'<img{c} src="{{R}}assets/img/{nom}.jpg" alt="{E(alt)}" loading="lazy">'

# ================================================================ ACCUEIL COMMUN
ADRESSE_LD = {"@type": "PostalAddress", "streetAddress": "202 bis route de Bellet", "postalCode": "06200",
              "addressLocality": "Nice", "addressRegion": "Provence-Alpes-Côte d'Azur", "addressCountry": "FR"}

def accueil():
    corps = f"""
<section class="hero" style="background-image:url(assets/img/bandeau-accueil.jpg)">
  <img class="logo-hero" src="assets/img/oiseau.png" alt="Les Piafs des Collines, location meublée vue mer à Nice" width="298" height="365">
  <h1 class="titre-hero">Les Piafs des Collines<span class="h1-sous">Location meublée vue mer à Nice · bail mobilité et location saisonnière</span></h1>
  <p class="script">Appartement vue mer sur la Colline de Bellet</p>
  <div class="choix">
    <a class="carte-choix" href="saisonniere/">
      <span class="k">Vacances à Nice</span>
      <span class="t">Location saisonnière</span>
      <span class="d">L'appartement haut de villa, sa vue panoramique sur la Baie des Anges, sa piscine et ses ateliers.</span>
      <span class="f">Découvrir l'appartement →</span>
    </a>
    <a class="carte-choix mob" href="bail-mobilite/">
      <span class="k">Mission, formation, mutation</span>
      <span class="t">Bail mobilité, 1 à 10 mois</span>
      <span class="d">77,51 m² meublés, tout compris, arrivée autonome. Pour les professionnels en mobilité à Nice.</span>
      <span class="f">Voir l'offre →</span>
    </a>
  </div>
</section>
<section class="blanc"><div class="wrap"><div class="split">
  <div>
    <span class="sur">Location meublée à Nice</span>
    <h2>Un appartement vue mer à Nice, pour quelques mois ou pour les vacances</h2>
    <p>Sur les collines de Bellet, à l'ouest de Nice, Les Piafs des Collines est un appartement entier de 77,51 m² au premier étage d'une villa, avec deux terrasses et une vue totalement dégagée sur la Baie des Anges.</p>
    <p><strong>En <a href="bail-mobilite/">location en bail mobilité à Nice</a></strong>, il loge pour 1 à 10 mois les professionnels en mission, en formation ou en mutation : meublé, tout compris à partir de 2 880 € par mois, avec arrivée autonome. Les centres hospitaliers niçois sont à 12 à 16 minutes en voiture, l'aéroport à 20 minutes, Monaco à 22 minutes et Sophia Antipolis à 28 minutes.</p>
    <p><strong>En <a href="saisonniere/">location saisonnière</a></strong>, il accueille jusqu'à 6 voyageurs avec piscine partagée, parking privé et ateliers.</p>
  </div>
  {img("terrasse-vue-mer", "Terrasse de l'appartement meublé avec vue sur la Baie des Anges à Nice")}
</div></div></section>"""
    jsonld = [
        {"@context": "https://schema.org", "@type": "WebSite", "name": "Les Piafs des Collines", "url": BASE + "/", "inLanguage": "fr-FR"},
        {"@context": "https://schema.org", "@type": "Apartment", "name": "Les Piafs des Collines",
         "description": "Appartement meublé de 77,51 m² avec vue sur la Baie des Anges, à Nice, proposé en bail mobilité de 1 à 10 mois et en location saisonnière.",
         "url": BASE + "/", "address": ADRESSE_LD, "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
         "floorSize": {"@type": "QuantitativeValue", "value": 77.51, "unitCode": "MTK"}, "numberOfRooms": 3, "numberOfBedrooms": 2,
         "numberOfBathroomsTotal": 2, "image": [f"{BASE}/assets/img/{n}.jpg" for n in ("terrasse-vue-mer", "vue-baie-de-nice", "sejour-salle-a-manger", "chambre-parentale")],
         "telephone": "+33611948235", "email": MAIL},
    ]
    contenu = (tete("Bail mobilité & location saisonnière à Nice, vue mer | Les Piafs des Collines",
                    "Appartement meublé de 77 m² vue Baie des Anges à Nice : bail mobilité de 1 à 10 mois, tout compris dès 2 880 €/mois, ou location saisonnière.",
                    0, "index.html", jsonld)
               + "<main>" + corps.replace("{R}", "") + "</main>" + pied("mob", 0) + "</body></html>\n")
    PAGES.append("index.html")
    (SITE / "index.html").write_text(propre(contenu), encoding="utf-8")
    print("   index.html")

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
  <p style="font-family:var(--script);font-size:2rem;color:var(--prune)">Marcelle &amp; Serge</p>
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
    cartes = "".join(f'<a class="carte" style="text-decoration:none;color:inherit" href="environs/{slug}.html">{img(im, t)}<div class="corps"><p class="note">{d}</p><h3>{E(t)}</h3><span class="f" style="color:var(--prune);font-family:var(--titre);font-weight:600">Lire →</span></div></a>' for slug, _, t, im, d in ARTICLES)
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

def saison_legal():
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
  "Au 202 bis route de Bellet, sur les collines de l'ouest de Nice. En voiture, hors trafic : Clinique Kantys Centre 12 min, campus Valrose 13 min, CHU Pasteur 2 15 min, Centre Antoine Lacassagne 16 min, aéroport 20 min, Monaco 22 min, Sophia Antipolis 28 min. Le bus 60 s'arrête à 50 m et rejoint le tram ligne 2 à Magnan."),
]

def faq_html(qr):
    return "".join(f"<details><summary>{E(q)}</summary><p>{E(r)}</p></details>" for q, r in qr)

def bail_mobilite():
    gal = "".join(f'<a href="{{R}}assets/img/{n}.jpg"{" class=\"g\"" if g else ""}>{img(n, a)}</a>' for n, a, g in GALERIE[:9])
    corps = f"""
<section class="mob-hero" style="background-image:url({{R}}assets/img/terrasse-vue-mer.jpg)"><div class="wrap">
  <span class="sur" style="color:#FFC9A8">Bail mobilité · Nice, collines de Bellet</span>
  <h1>Location en bail mobilité à Nice, avec vue sur la Baie des Anges</h1>
  <p class="lead"><strong>Pour 1 à 10 mois, tout compris.</strong> 77,51 m² meublés au premier étage d'une villa, sur les collines de Bellet. Le locataire arrive avec sa valise, entre avec un code, et travaille le lendemain matin.</p>
  <div class="faits"><span>77,51 m² + 31 m² de terrasses et véranda</span><span>2 chambres · 2 salles d'eau</span><span>Fibre</span><span>Parking privé</span><span>DPE C · A</span><span>À partir de 2 880 €/mois</span></div>
  <a class="bouton" href="#demande">Demander une disponibilité</a> <a class="bouton clair" style="color:#fff;margin-left:8px" href="#prix">Voir les prix</a>
</div></section>

<section class="blanc" id="logement"><div class="wrap">
  <span class="sur">Le logement</span><h2>Un appartement meublé tout équipé : installé sans rien à faire</h2>
  <div class="grille3" style="margin-top:28px">
    <div><h4>Le lit est fait</h4><p>Les draps et les oreillers sont en place, le linge de toilette est sorti. Couettes d'été et d'hiver, cuisine complète, lave-linge et sèche-linge sur place.</p></div>
    <div><h4>Une facture, un prix, un payeur</h4><p>Électricité, eau, climatisation, fibre, parking : déjà dans le loyer. Aucun contrat à ouvrir, aucun compteur à relever, aucune régularisation à la sortie. Le ménage de sortie est compris.</p></div>
    <div><h4>Arrivée autonome</h4><p>Code d'accès communiqué avant la date d'entrée. Aucun rendez-vous de remise de clés, aucune contrainte d'horaire : un locataire qui atterrit à 23 h entre chez lui à 23 h 20.</p></div>
    <div><h4>Une connexion qui tient une visio</h4><p>Fibre haut débit. Trois pièces principales et deux terrasses : on prend un appel sans déranger la personne d'à côté.</p></div>
    <div><h4>Deux professionnels sans se gêner</h4><p>Chambre parentale avec salle de bain privative et douche à l'italienne, seconde chambre avec salle d'eau, WC indépendant. Deux vraies chambres, de 13,91 et 12,88 m².</p></div>
    <div><h4>De quoi recevoir sa famille</h4><p>Canapé-lit, table à rallonge pour 6 sous store électrique, piscine partagée, potager, ping-pong. Chaise haute, lit parapluie et cache-prises sur demande.</p></div>
  </div>
  <div class="galerie" style="margin-top:40px">{gal}</div>
</div></section>

<section><div class="wrap"><div class="split">
  <div><span class="sur">Les surfaces</span><h2>77,51 m² habitables, mesurés</h2>
  <p class="note">Mesurage loi Boutin du 27/09/2026.</p>
  <table class="grille-prix"><tbody>
  <tr><td>Séjour</td><td>25,00 m²</td></tr><tr><td>Chambre 1, avec salle de bain privative</td><td>13,91 m²</td></tr>
  <tr><td>Chambre 2</td><td>12,88 m²</td></tr><tr><td>Cuisine</td><td>12,57 m²</td></tr>
  <tr><td>Salles d'eau, WC, entrée, dégagement</td><td>13,15 m²</td></tr>
  <tr><td><strong>Terrasses</strong>, Sud-Est et Sud-Ouest</td><td><strong>10,58 + 15,75 m²</strong></td></tr>
  <tr><td>Véranda buanderie</td><td>4,95 m²</td></tr></tbody></table></div>
  <div><span class="sur">Le confort, attesté</span><h2>DPE C en énergie, A en climat</h2>
  <p>Le diagnostic du 27/09/2026, valable jusqu'en 2036, relève une bonne inertie, un logement traversant, une toiture isolée, des fenêtres à volets extérieurs et une pompe à chaleur. Le confort d'été est établi par un rapport officiel.</p>
  <p>Le diagnostiqueur estime l'énergie entre <strong>850 et 1 210 € par an</strong>. Ce montant est dans le loyer : le locataire ne reçoit aucune facture, climatisation comprise.</p>
  <p>Vue totalement dégagée sur la Baie des Anges depuis la terrasse principale.</p></div>
</div></div></section>

<section class="blanc" id="prix"><div class="etroit">
  <span class="sur">Prix</span><h2>Prix du bail mobilité à Nice, tout compris</h2>
  <p>Charges, énergie, eau, climatisation, fibre, parking, accès piscine, linge, kit d'arrivée, ménage de sortie.</p>
  <table class="grille-prix" style="margin-top:20px"><thead><tr><th>Durée du séjour</th><th>Loyer mensuel tout compris</th></tr></thead><tbody>
  <tr><td>7 à 10 mois</td><td class="m">2 880 €</td></tr>
  <tr><td>3 à 6 mois</td><td class="m">3 200 €</td></tr>
  <tr><td>1 à 2 mois</td><td class="m">3 600 €</td></tr></tbody></table>
  <p style="margin-top:18px">Pour une mission courte, l'alternative est la résidence de services : un studio de 27 m² y coûte autour de 3 800 € par mois. Ici, le même budget loge dans 77,51 m² avec deux chambres, deux terrasses et la vue.</p>
  <p class="note">Ménage hebdomadaire et poste de travail équipé disponibles en option. Facture exonérée de TVA.</p>
</div></section>

<section id="contrat"><div class="wrap">
  <span class="sur">Contrat</span><h2>Bail mobilité ou bail société : deux formules selon qui paie</h2>
  <div class="regle" style="margin-top:24px">
    <div><h3>L'employeur, une agence, un assureur ou une production paie</h3>
    <p><strong>Bail au nom de la société, à partir de 3 mois.</strong></p>
    <ul><li>Durée adaptée à la mission</li><li>Dépôt de garantie possible</li><li>Aucun justificatif de motif à produire</li><li>Une facture au nom de la structure qui paie</li></ul></div>
    <div class="b"><h3>Le locataire paie en son nom</h3>
    <p><strong>Bail mobilité, de 1 à 10 mois.</strong></p>
    <ul><li>Pour une formation, des études, un stage, une mutation ou une mission temporaire</li><li>Le justificatif du motif est demandé avant la signature</li><li>Visale n'est pas mobilisable à ce niveau de loyer : caution de l'employeur ou caution personnelle</li></ul></div>
  </div>
</div></section>

<section class="blanc" id="acces"><div class="wrap">
  <span class="sur">Accès</span><h2>Sur les hauteurs de Nice Ouest, à un quart d'heure de tout</h2>
  <p>Temps en voiture hors trafic, calculés depuis le 202 bis route de Bellet.</p>
  <div class="trajets" style="margin-top:20px">
    <div><b>12 min</b><span>Clinique Kantys Centre</span></div><div><b>13 min</b><span>Campus Valrose</span></div>
    <div><b>15 min</b><span>CHU Pasteur 2</span></div><div><b>16 min</b><span>Centre Antoine Lacassagne</span></div>
    <div><b>20 min</b><span>Aéroport Nice Côte d'Azur</span></div><div><b>22 min</b><span>Monaco</span></div>
    <div><b>28 min</b><span>Sophia Antipolis</span></div><div><b>7 min</b><span>La plage, 20 min à pied</span></div>
    <div><b>50 m</b><span>Arrêt du bus 60, vers le tram ligne 2 à Magnan</span></div>
  </div>
  <p style="margin-top:22px">Place de parking privée comprise. Pour un séjour de plusieurs mois sans voiture, le scooter est la solution pratique : il se loue au mois et se remise dans l'enceinte de la propriété, comme les vélos.</p>
</div></section>

<section class="sable" id="avis"><div class="wrap">
  <span class="sur">Avis</span><h2>Ce que les locataires ont écrit</h2>
  <div class="avis" style="margin-top:24px">
    <blockquote>Une vue à couper le souffle, un appartement des plus agréables et d'une propreté irréprochable.<cite>Mélody - Nancy</cite></blockquote>
    <blockquote>Un appartement au top, moderne, bien équipé, au goût du jour.<cite>Chantal, Serge, Sabrina &amp; Anthony - Doubs</cite></blockquote>
    <blockquote>Everything was perfectly organised. The view is magnificent.<cite>Salma &amp; Omar</cite></blockquote>
    <blockquote>You have the most beautiful view from the flat and everything you need here!<cite>Family Traude</cite></blockquote>
  </div>
</div></section>

<section id="questions"><div class="etroit">
  <span class="sur">Questions fréquentes</span><h2>Le bail mobilité à Nice, en questions</h2>
  <div style="margin-top:24px">{faq_html(FAQ_MOB)}</div>
</div></section>

<section class="blanc" id="demande"><div class="etroit">
  <span class="sur">Demande</span><h2>Demander une disponibilité</h2>
  <p>Indiquez les dates et qui paie le loyer : nous vous répondons avec la formule adaptée et une date d'entrée ferme.</p>
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
         "mob", "", corps, SCRIPT_GALERIE, jsonld=[
            {"@context": "https://schema.org", "@type": "Apartment",
             "name": "Location en bail mobilité à Nice, Les Piafs des Collines",
             "description": "Appartement meublé de 77,51 m² avec vue sur la Baie des Anges, loué en bail mobilité de 1 à 10 mois, tout compris à partir de 2 880 € par mois.",
             "url": BASE + "/bail-mobilite/", "address": ADRESSE_LD, "geo": {"@type": "GeoCoordinates", "latitude": GEO[0], "longitude": GEO[1]},
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

# ================================================================ divers
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
    lignes = []
    from urllib.parse import quote
    for a, n in anciennes.items():
        n = n[:-5] if n.endswith(".html") else n
        lignes.append(f"{quote(a)} {n} 301")
        if quote(a) != a: lignes.append(f"{a} {n} 301")
    lignes.append("/blog/* /saisonniere/environs 301")
    (SITE / "_redirects").write_text("\n".join(lignes) + "\n", encoding="utf-8")
    print("   _redirects")

def sitemap():
    import datetime
    jour = datetime.date.today().isoformat()
    prio = {"index.html": "1.0", "bail-mobilite/index.html": "0.9", "saisonniere/index.html": "0.8"}
    urls = "".join(f"<url><loc>{url_propre(c)}</loc><lastmod>{jour}</lastmod><priority>{prio.get(c, '0.5')}</priority></url>"
                   for c in PAGES if c != "404.html")
    (SITE / "sitemap.xml").write_text('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + urls + "</urlset>\n", encoding="utf-8")
    (SITE / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {BASE}/sitemap.xml\n", encoding="utf-8")
    print("   sitemap.xml, robots.txt")

if __name__ == "__main__":
    print("Génération de site/ :")
    accueil(); saison_appartement(); saison_hotes(); saison_ateliers(); saison_livre_or(); saison_faq()
    saison_tarifs(); saison_contact(); saison_environs(); saison_legal(); bail_mobilite(); page_404(); redirections(); sitemap()
    print("Terminé.")
