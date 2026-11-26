#!/usr/bin/env python3
"""Génère la version 2 de la page bail mobilité, à côté de l'ancienne.

Lancer :  python3 outils/build_v2.py
Écrit site/bail-mobilite-v2/index.html. La page /bail-mobilite/ n'est pas touchée.

Textes : brief ClickUp 1amye9cq1n9 du 26/11/2026, repris mot pour mot.
La page reste en noindex, hors sitemap et sans lien depuis le site tant que Géraldine ne l'a pas validée.
Les styles propres à cette page sont dans site/assets/v2.css.
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as b

E, pic, img = b.E, b.pic, b.img
CHEMIN = "bail-mobilite-v2/index.html"

# Bandeau photo/aquarelle : nom du fichier dans assets/img une fois le visuel maître validé (brief, §4).
# Tant qu'il vaut None, le premier écran garde la vraie photo de la baie, sans mention d'aquarelle.
AQUARELLE = None

# Encadré « dernier mois offert » : ses effets en cas de départ anticipé sont à valider par le bailleur
# et le référent juridique avant publication (brief, bloc 6). Passer à False pour l'omettre partout.
OFFRE_10E_MOIS = True

ALT = {n: a for n, a, _ in b.GALERIE}

def insecable(s):
    """Espaces insécables entre un nombre et son unité : « 175 € » ne se coupe pas en fin de ligne."""
    return re.sub(r"(\d) (€|m²|mois|minutes)", "\\1\u00a0\\2", s)

def lignes(t):
    """Un titre de deux phrases s'écrit sur deux lignes, une phrase par ligne (Géraldine, 26/11/2026)."""
    return "".join(f'<span class="v2-ligne">{E(x)}</span>' for x in re.split(r"(?<=[.?!]) (?=[A-ZÀ-Ý])", t))

def paras(*ps):
    return "".join(f"<p>{insecable(b.fine(E(x)))}</p>" for x in ps)

# Bloc 4 · le logement en images : (photo ou None, titre, texte)
PIECES = [
    ("sejour-salle-a-manger", "La pièce de vie", "Un salon et un espace repas ouverts sur la cuisine, avec la mer à l'horizon."),
    ("cuisine-ilot", "La cuisine", "Plaque à induction, four, lave-vaisselle et réfrigérateur-congélateur : de quoi cuisiner au quotidien."),
    ("chambre-parentale", "La première chambre", "13,91 m² et une salle d'eau privative avec douche à l'italienne."),
    ("chambre-2", "La seconde chambre", "12,88 m² et un poste de travail. La fibre est installée dans le logement."),
    (None, "Les salles d'eau", "Deux salles d'eau, dont une privative, et un WC indépendant."),
    ("terrasse-vue-mer", "Les terrasses", "Deux orientations, 26,33 m² au total, une table sous le store et une vue sur la Baie des Anges."),
    (None, "Les détails qui comptent", "Lave-linge, sèche-linge, linge de maison fourni avec rechange, climatisation réversible et une place de parking privée."),
    ("piscine-vue-aerienne", "La piscine", "Une piscine partagée dans le jardin de la villa, accessible selon les horaires prévus."),
]

# Bloc 8 · avis, citations fidèles au livre d'or
AVIS = [("Une vue à couper le souffle, un appartement des plus agréables et d'une propreté irréprochable.", "Mélody, Nancy"),
        ("L'appartement est très bien situé et d'une propreté irréprochable. La vue est magnifique.", "Anaïs, Nord"),
        # Deux avis de plus, déjà publiés sur la page actuelle (Géraldine, 26/11/2026)
        ("Un appartement au top, moderne, bien équipé, au goût du jour. Qu'il est agréable de s'asseoir sur la terrasse et de contempler la mer et ses bateaux.", "Chantal, Serge, Sabrina et Anthony, Doubs"),
        ("You have the most beautiful view from the flat and everything you need here!", "Famille Traude")]

# Bloc 9 · questions utiles
FAQ = [
    ("Qui peut louer ?", "Le bail mobilité s'adresse notamment aux personnes en mission professionnelle temporaire, en mutation, en formation professionnelle, en études supérieures, en apprentissage, en stage ou en service civique. Le motif doit être justifié avant la signature."),
    ("Pour quelle durée ?", "De 1 à 10 mois. Le bail mobilité n'est ni renouvelable ni reconductible. Sa durée peut être modifiée une fois par avenant, sans dépasser 10 mois au total."),
    ("Mon employeur peut-il payer ?", "Oui. Le bail reste signé par la personne logée. Une lettre de prise en charge permet d'organiser le paiement par l'employeur. La quittance est au nom du locataire et mentionne le payeur."),
    ("Faut-il un dépôt de garantie ?", "Non. Le bail mobilité interdit le dépôt de garantie. Une caution peut toutefois être demandée : les garanties sont examinées avec le dossier."),
    ("Qu'est-ce qui reste à ma charge ?", "Le ménage et l'assurance habitation ne sont pas compris. Le prix mensuel de 3 650 € comprend le loyer et le forfait de charges annoncé."),
    ("Puis-je partir avant la fin ?", "Le locataire peut donner congé avec un préavis d'un mois, dans les conditions prévues par la loi."),
    ("Comment se passe l'arrivée ?", "La remise des clés et l'état des lieux sont organisés avec le bailleur."),
    ("La piscine est-elle privée ?", "Non. Elle est partagée, avec des horaires d'accès."),
    ("Peut-on louer pour des vacances ?", "Non. Cette offre concerne exclusivement la location en bail mobilité, avec justificatif d'éligibilité. Elle n'est pas proposée à la nuit."),
]

# Fiche technique repliable : reprise de la page en ligne, alignée sur le socle factuel du brief (§3).
FICHE = [
    ("Le logement", "plan", [("Surface habitable", "77,51 m² (mesurage loi Boutin, 27/09/2026)"), ("Terrasses", "10,58 m² + 15,75 m², soit 26,33 m²"),
                             ("Véranda buanderie", "4,95 m², hors surface habitable"), ("Pièces", "3, dont 2 chambres"), ("Chambres", "13,91 m² et 12,88 m²"),
                             ("Salles d'eau", "2, dont 1 privative avec douche à l'italienne"), ("WC", "1 indépendant"),
                             ("Situation", "1er étage d'une villa, logement traversant"), ("Vue", "Baie des Anges")]),
    ("Énergie et confort", "energie", [("DPE", "C en énergie, A en climat"), ("Chauffage et climatisation", "Climatisation réversible"), ("Internet", "Fibre")]),
    ("Équipements", "equipement", [("Cuisine", "Plaque à induction, four, lave-vaisselle, réfrigérateur-congélateur"),
                                    ("Linge", "Lave-linge, sèche-linge, linge de lit et de toilette fourni avec rechange"),
                                    ("Travail", "Poste de travail dans la seconde chambre"),
                                    ("Extérieur", "Table sous store sur la terrasse"), ("Stationnement", "1 place privée dans l'enceinte de la villa"),
                                    ("Piscine", "Partagée, selon horaires")]),
    ("Contrat", "plume", [("Bail", "Bail mobilité de 1 à 10 mois, signé par la personne logée"), ("Payeur", "Le locataire, ou son employeur avec une lettre de prise en charge"),
                          ("Pièces à fournir", "Justificatif du motif de mobilité avant signature"),
                          ("Garantie", "Aucun dépôt de garantie. Garanties examinées avec le dossier"),
                          ("Quittance", "Au nom du locataire, mentionnant le payeur"), ("Arrivée", "Remise des clés et état des lieux avec le bailleur")]),
]

# Un picto par ligne de la fiche technique, pour la lecture en diagonale (Géraldine, 26/11/2026).
PICTO_LIGNE = {"Surface habitable": "plan", "Terrasses": "soleil", "Véranda buanderie": "machine", "Pièces": "porte", "Chambres": "lit",
               "Salles d'eau": "douche", "WC": "douche", "Situation": "maison", "Vue": "soleil", "DPE": "energie",
               "Chauffage et climatisation": "clim", "Internet": "wifi", "Cuisine": "cuisine", "Linge": "machine", "Travail": "ordi",
               "Extérieur": "table", "Stationnement": "parking", "Piscine": "piscine", "Bail": "plume", "Payeur": "societe",
               "Pièces à fournir": "facture", "Garantie": "cle", "Quittance": "facture", "Arrivée": "valise"}

# Budget : un élément par ligne, avec son picto (Géraldine, 26/11/2026). Texte du brief, bloc 6, découpé en liste.
INCLUS = [("goutte", "Eau"), ("eclair", "Électricité"), ("clim", "Climatisation"), ("wifi", "Fibre"), ("parking", "Parking"),
          ("piscine", "Accès à la piscine partagée selon horaires"), ("lit", "Linge de lit et de toilette fourni avec rechange")]
NON_INCLUS = [("menage", "Le ménage"), ("bouclier", "L'assurance habitation")]

# Pictos propres à cette page, dans le trait des pictos du site (viewBox 32).
PICTOS_V2 = {"goutte": '<path d="M16 4c-5 7-8 11-8 15a8 8 0 0016 0c0-4-3-8-8-15z"/>',
             "eclair": '<path d="M18 3L7 18h8l-2 11 12-16h-8z"/>',
             "bouclier": '<path d="M16 3l11 4v8c0 7-5 12-11 14C10 27 5 22 5 15V7z"/>',
             "details": '<rect x="6" y="4" width="20" height="24" rx="2"/><path d="M10 11l2 2 3.5-3.5M10 19l2 2 3.5-3.5M19 11.5h3M19 19.5h3"/>'}
SPRITE_V2 = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + "".join(
    f'<symbol id="i-{n}" viewBox="0 0 32 32">{d}</symbol>' for n, d in PICTOS_V2.items()) + '</defs></svg>'

ATOUTS = [("wifi", "Fibre"), ("cuisine", "Cuisine équipée"), ("parking", "Parking privé"), ("piscine", "Piscine partagée")]
ATOUTS_HTML = "".join(f'<li>{pic(ic, "pic-s")}<span>{t}</span></li>' for ic, t in ATOUTS)

def liste_pictos(elements):
    return '<ul class="v2-liste">' + "".join(f'<li>{pic(ic, "pic-s")}<span>{E(t)}</span></li>' for ic, t in elements) + "</ul>"

MOTIFS = ["Mission professionnelle temporaire", "Mutation", "Formation professionnelle", "Études supérieures", "Apprentissage", "Stage", "Service civique"]

def photo(n, cls=""):
    return img(n, ALT.get(n, ""), cls)

# Un picto par descriptif du logement (Géraldine, 26/11/2026), pris dans le jeu de pictos du site.
PICTOS = {"La pièce de vie": "table", "La cuisine": "cuisine", "La première chambre": "lit", "La seconde chambre": "ordi",
          "Les salles d'eau": "douche", "Les terrasses": "soleil", "Les détails qui comptent": "details", "La piscine": "piscine"}

def bloc(photo_html, titre_html, contenu, inverse=False, ton="bleu", ident="", picto=""):
    """Bloc image et texte, à la façon de la page « Cannes en hiver » : grand titre en capitales, texte court, photo large."""
    i = f' id="{ident}"' if ident else ""
    pi = pic(picto, f"pic v2-pic {ton}") if picto else ""
    return (f'<div class="v2-bloc{" inverse" if inverse else ""}"{i}><div class="v2-bloc-texte">{pi}{f'<h2 class="v2-t {ton}">{titre_html}</h2>' if titre_html else ""}{contenu}</div>'
            f'<div class="v2-bloc-photo">{photo_html}</div></div>')

def corps():
    fond = AQUARELLE or "hero-baie"
    mention_aqua = '<p class="v2-aqua">Interprétation aquarelle de la vue réelle.</p>' if AQUARELLE else ""
    avec_photo = [(n, t, x) for n, t, x in PIECES if n]
    sans_photo = [(t, x) for n, t, x in PIECES if not n]
    pieces = "".join(bloc(photo(n), E(t), paras(x), inverse=k % 2 == 1, ton="corail" if k % 2 else "bleu", picto=PICTOS[t]).replace('<h2 class="v2-t', '<h3 class="v2-t').replace("</h2>", "</h3>")
                     for k, (n, t, x) in enumerate(avec_photo))
    reperes = "".join(f'<div>{pic(PICTOS[t], "pic v2-pic")}<h3>{E(t)}</h3>{paras(x)}</div>' for t, x in sans_photo)
    gal = "".join(f'<a href="{{R}}assets/img/{n}.jpg"{" class=\"g\"" if g else ""}>{img(n, a)}</a>' for n, a, g in b.GALERIE[:9])
    fiche = "".join(f'<div class="fiche-bloc"><h3>{pic(ic)}{E(t)}</h3><dl>'
                    + "".join(f'<dt>{pic(PICTO_LIGNE.get(k, ic), "pic-s")}{E(k)}</dt><dd>{insecable(E(v))}</dd>' for k, v in lignes) + "</dl></div>" for t, ic, lignes in FICHE)
    faq = "".join(f"<details><summary>{b.fine(E(q))}</summary><p>{b.fine(E(r))}</p></details>" for q, r in FAQ)
    avis = "".join(f'<blockquote class="v2-citation"><p>« {E(q)} »</p><cite>{E(c)}</cite></blockquote>' for q, c in AVIS)
    offre = f"""<aside class="v2-offre"><p class="v2-offre-titre">Vous restez 10 mois ? Le dernier mois de loyer est offert.</p>
    {paras("Une remise de 3 475 €, accordée une fois pour un bail de 10 mois. Le forfait de charges de 175 € reste dû le dernier mois. Les conditions d'application figurent au bail.")}</aside>""" if OFFRE_10E_MOIS else ""
    motifs = "".join(f"<option>{E(m)}</option>" for m in MOTIFS)
    publics = "".join(f'<li>{pic(ic, "pic-s")}<span>{t}</span></li>' for ic, t in
                      (("hopital", "Hôpitaux"), ("societe", "Entreprises"), ("campus", "Universités"), ("valise", "Services de mobilité")))
    PRESCRIPTEUR_FIN = (f'<ul class="v2-publics">{publics}</ul>'
                        + '<p class="v2-reserve">Sous réserve de disponibilités et d' + "'" + 'un dossier éligible</p>'
                        + '<p><a class="bouton" href="#demande" data-pour="tiers">Nous parler d' + "'" + 'une arrivée</a></p>')
    return SPRITE_V2 + f"""<div class="v2">
<section class="v2-hero">
  <div class="v2-cadre">
    <picture><source media="(max-width:700px)" srcset="{{R}}assets/img/hero-baie-mobile.jpg"><img src="{{R}}assets/img/{fond}.jpg" alt="Vue sur la Baie des Anges depuis Les Piafs des Collines, à Nice Bellet." fetchpriority="high"></picture>
    <h1><span class="h1-sur">Location meublée à Nice · Bail mobilité</span>À Nice pour travailler. <span class="v2-h1-2">Bien chez vous pour en profiter.</span></h1>
  </div>
  <div class="v2-l">
    <div class="v2-intro"><p class="v2-intro-1">Votre mission vous amène à Nice.</p><p>Installez-vous dans un appartement meublé de <strong>77 m²</strong>, avec <strong>deux chambres</strong> et <strong>deux terrasses</strong> face à la <strong>Baie des Anges</strong>. Pour <strong>1 à 10 mois</strong>, sur la colline de Bellet.</p></div>
    <p class="v2-prix">3 650 € / mois <span>charges comprises</span></p>
    <p class="v2-actions"><a class="bouton blanc" href="#demande">Vérifier mes dates</a><a class="bouton contour" href="#logement">Voir l'appartement</a></p>
    <p class="v2-micro">Location réservée aux personnes éligibles au bail mobilité</p>
    {mention_aqua}
  </div>
</section>

<section class="v2-bleu v2-chiffres" id="chiffres"><div class="v2-l">
  <div class="v2-geants">
    <div><b>77<small>m²</small></b><span>Un appartement entier</span></div>
    <div><b>2<small>chambres</small></b><span>De la place pour s'installer</span></div>
    <div><b>26<small>m²</small></b><span>Deux terrasses vue mer</span></div>
  </div>
  <ul class="v2-atouts">{ATOUTS_HTML}</ul>
</div></section>
<div class="store" aria-hidden="true"></div>

<section class="v2-blanc" id="habiter"><div class="v2-l">
  <h2 class="v2-t bleu v2-titre-xl">{lignes("Une mission temporaire. Un vrai chez\u2011vous.")}</h2>
  {bloc(photo("cuisine-sejour"), "",
        paras("Une cuisine pour garder vos habitudes. Deux chambres pour ne pas tout faire dans la même pièce. Une terrasse pour prendre le dîner dehors.",
              "Ici, vous louez un appartement entier, meublé et équipé. La vue est un plaisir en plus. Le confort du quotidien est déjà là.")
        + '<p><a class="bouton" href="#demande">Vérifier mes dates</a></p>')}
  <div class="v2-trio">
    <figure>{img("terrasse-vue-mer", "Terrasse de l'appartement avec table et vue sur la mer.")}<figcaption>Le soir, changez d'horizon.</figcaption></figure>
    <figure>{img("sejour-salle-a-manger", "Séjour de l'appartement meublé des Piafs des Collines.")}<figcaption>De la place pour vivre, pas seulement pour dormir.</figcaption></figure>
    <figure>{img("cuisine-ilot", "La cuisine équipée et son îlot.")}<figcaption>Vos habitudes voyagent aussi.</figcaption></figure>
  </div>
</div></section>

<section class="v2-bleu v2-titre-section" id="logement"><div class="v2-l">
  <h2 class="v2-t">{lignes("Entrez. Vous avez de la place.")}</h2>
  <p class="v2-lead">Au premier étage d'une villa, un appartement traversant de 77,51 m² avec deux chambres, deux salles d'eau et deux terrasses.</p>
</div></section>
<section class="v2-blanc v2-pieces"><div class="v2-l">
  {pieces}
  <div class="v2-reperes">{reperes}</div>
  <div class="galerie">{gal}</div>
  <p class="v2-centre"><a class="bouton" href="#demande">Vérifier mes dates</a></p>
</div></section>

<section class="v2-bleu v2-acces" id="acces"><div class="v2-l">
  {bloc(photo("vue-baie-de-nice"), "Nice, côté colline.",
        '<p class="v2-acces-1">Les Piafs se trouvent sur la <strong>colline de Bellet</strong>, à l' + "'" + 'ouest de Nice. Une <strong>place de parking privée</strong> est comprise dans la location.</p>'
        + '<div class="v2-acces-2">' + pic("repere", "pic v2-pic") + '<p class="v2-acces-q">Vous venez pour une mission précise ?</p>'
        + '<p>Indiquez-nous votre lieu de travail : vérifiez votre trajet quotidien avant de choisir vos dates.</p>'
        + '<p><a class="bouton corail" href="#demande">Vérifier mes dates</a></p></div>', inverse=True, ton="")}
</div></section>

<div class="store" aria-hidden="true"></div>
<section class="v2-bleu" id="prix"><div class="v2-l">
  <h2 class="v2-t"><span class="v2-ligne">Un budget clair,</span><span class="v2-ligne">avant de faire vos valises.</span></h2>
  <p class="v2-montant">3 650 €<small>/ mois</small></p>
  <p class="v2-sous-prix">Charges comprises · De 1 à 10 mois</p>
  <p class="v2-detail-prix"><span>Loyer 3 475 €</span><span>+ forfait de charges 175 €</span></p>
  <div class="v2-inclus">
    <div><h3>Inclus</h3>{liste_pictos(INCLUS)}</div>
    <div><h3>Non inclus</h3>{liste_pictos(NON_INCLUS)}<p class="v2-note">À votre charge.</p></div>
  </div>
  {offre}
  <p class="v2-centre"><a class="bouton corail" href="#demande">Demander les disponibilités</a></p>
</div></section>

<section class="v2-blanc" id="prescripteurs"><div class="v2-l">
  {bloc(photo("salon-canape-lit"), "Vous logez un salarié ou un praticien en mobilité ?",
        paras("Transmettez une proposition concrète : un appartement entier à Nice, deux chambres, un tarif mensuel charges comprises et les informations utiles réunies dans une fiche.",
              "Le bail mobilité est signé par la personne logée, si elle remplit les conditions d'éligibilité. Son employeur peut prendre en charge le loyer selon les modalités convenues.")
        + PRESCRIPTEUR_FIN)}
</div></section>

<section class="v2-marine" id="avis"><div class="v2-l">
  <h2 class="v2-t">{lignes("Ils ont habité ici. Ils en parlent mieux que nous.")}</h2>
  <div class="v2-avis">{avis}</div>
  <p class="v2-note">Extraits du livre d'or de l'appartement.</p>
</div></section>

<section class="v2-blanc" id="questions"><div class="v2-l v2-etroit">
  <h2 class="v2-t bleu">Questions utiles</h2>
  {faq}
  <details class="v2-fiche" id="fiche"><summary>Fiche technique détaillée</summary><div class="fiche">{fiche}</div></details>
</div></section>

<div class="store" aria-hidden="true"></div>
<section class="v2-bleu" id="demande"><div class="v2-l v2-etroit">
  <h2 class="v2-t">Votre mission commence quand ?</h2>
  <p class="v2-lead">Indiquez vos dates, le nombre de personnes et votre lieu de travail ou de formation. Nous vous répondrons avec les disponibilités et les éléments nécessaires à votre dossier.</p>
  <form class="v2-form" data-to="{b.MAIL}" data-sujet="Demande bail mobilité">
  <fieldset class="v2-pour"><legend>Je contacte</legend>
    <label><input type="radio" name="Je contacte" value="Pour moi" checked> Pour moi</label>
    <label><input type="radio" name="Je contacte" value="Pour un salarié ou un praticien"> Pour un salarié ou un praticien</label>
  </fieldset>
  <div class="champs">
    <div><label for="nom">Nom</label><input id="nom" name="Nom" autocomplete="name" required></div>
    <div><label for="email">Email</label><input id="email" name="Email" type="email" autocomplete="email" required></div>
    <div><label for="tel">Téléphone (facultatif)</label><input id="tel" name="Téléphone" type="tel" autocomplete="tel"></div>
    <div><label for="occ">Nombre d'occupants</label><input id="occ" name="Nombre d'occupants" type="number" min="1" inputmode="numeric"></div>
    <div><label for="arr">Date d'arrivée souhaitée</label><input id="arr" name="Arrivée souhaitée" type="date"></div>
    <div><label for="dep">Date de départ souhaitée</label><input id="dep" name="Départ souhaité" type="date"></div>
    <div><label for="lieu">Lieu de travail ou de formation</label><input id="lieu" name="Lieu de travail ou de formation"></div>
    <div><label for="motif">Motif de mobilité</label><select id="motif" name="Motif de mobilité">{motifs}</select></div>
    <div class="v2-tiers" hidden><label for="org">Organisme</label><input id="org" name="Organisme"></div>
    <div class="v2-tiers" hidden><label for="mailpro">Email professionnel</label><input id="mailpro" name="Email professionnel" type="email"></div>
    <div class="plein"><label for="msg">Message (facultatif)</label><textarea id="msg" name="Message"></textarea></div>
  </div>
  <p class="v2-envoi"><button class="bouton corail" type="submit">Envoyer ma demande</button></p>
  <p class="v2-note">Le bouton ouvre votre messagerie avec votre demande préremplie, adressée à {b.MAIL}.</p>
  <p class="v2-note">Les informations transmises servent à traiter votre demande de logement. N'envoyez pas de pièce d'identité ni de document confidentiel dans ce formulaire.</p>
  </form>
  <p class="v2-contact"><a href="mailto:{b.MAIL}">{b.MAIL}</a> · <a href="tel:{b.TEL_LIEN}">{b.TEL}</a></p>
</div></section>
</div>"""

SCRIPT_FORM = """<script>(function(){const f=document.querySelector('.v2-form');if(!f)return;
const tiers=[...f.querySelectorAll('.v2-tiers')];
function maj(){const t=f.querySelector('input[name="Je contacte"]:checked').value!=='Pour moi';tiers.forEach(d=>d.hidden=!t)}
f.querySelectorAll('input[name="Je contacte"]').forEach(r=>r.addEventListener('change',maj));
document.querySelectorAll('a[data-pour="tiers"]').forEach(a=>a.addEventListener('click',()=>{f.querySelectorAll('input[name="Je contacte"]')[1].checked=true;maj()}));
f.addEventListener('submit',e=>{e.preventDefault();
const l=[...new FormData(f)].filter(([k,v])=>v&&!(tiers[0].hidden&&(k==='Organisme'||k==='Email professionnel'))).map(([k,v])=>k+' : '+v).join('\\n');
location.href='mailto:'+f.dataset.to+'?subject='+encodeURIComponent(f.dataset.sujet)+'&body='+encodeURIComponent(l)});maj()})();</script>
"""

def generer():
    prof = CHEMIN.count("/")
    tete = b.tete("Bail mobilité à Nice : 77 m² vue mer | Les Piafs des Collines",
                  "À Nice Bellet, appartement meublé de 77 m², 2 chambres, terrasses vue mer et parking. Bail mobilité de 1 à 10 mois. 3 650 €/mois charges comprises.",
                  prof, CHEMIN, image="hero-baie")
    # Page en relecture : ni canonique ni index, et la feuille v2 après la feuille commune.
    tete = tete.replace(f'<link rel="canonical" href="{b.url_propre(CHEMIN)}">', '<meta name="robots" content="noindex">')
    tete = tete.replace('href="{R}assets/style.css">', 'href="{R}assets/style.css">\n<link rel="stylesheet" href="{R}assets/v2.css">')
    tete = tete.replace(f'href="{"../" * prof}assets/style.css">', f'href="{"../" * prof}assets/style.css">\n<link rel="stylesheet" href="{"../" * prof}assets/v2.css">')
    tete = tete.replace("<body>", '<body class="v2-page">', 1)
    contenu = tete + b.entete("mob", "", prof) + "<main>" + corps() + "</main>" + b.pied("mob", prof) + b.SCRIPT_GALERIE + SCRIPT_FORM + b.SCRIPT_REVEAL + "</body></html>\n"
    contenu = b.propre(contenu.replace("{R}", "../" * prof))
    contenu = b.poser_langues(contenu, None, "fr")
    f = b.SITE / CHEMIN
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(contenu, encoding="utf-8")
    print("  ", CHEMIN)

if __name__ == "__main__":
    generer()
