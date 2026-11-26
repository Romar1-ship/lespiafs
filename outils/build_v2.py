#!/usr/bin/env python3
"""Génère la version 2 de la page bail mobilité, à côté de l'ancienne.

Lancer :  python3 outils/build_v2.py
Écrit site/bail-mobilite-v2/index.html. La page /bail-mobilite/ n'est pas touchée.

Textes : brief ClickUp 1amye9cq1n9 du 26/11/2026, repris mot pour mot.
Depuis le 26/11/2026 (Géraldine) : la page est l'adresse principale du site, https://www.lespiafsdescollines.com/.
L'ancienne page bail mobilité est gardée telle quelle sous /bail-mobilite-v1/ (copie statique, noindex).
Les styles propres à cette page sont dans site/assets/v2.css.
"""
import re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as b

E, pic, img = b.E, b.pic, b.img
CHEMIN = "index.html"   # la racine du site

# Bandeau photo/aquarelle : nom du fichier dans assets/img une fois le visuel maître validé (brief, §4).
# Tant qu'il vaut None, le premier écran garde la vraie photo de la baie, sans mention d'aquarelle.
AQUARELLE = None

# Encadré « dernier mois offert » : ses effets en cas de départ anticipé sont à valider par le bailleur
# et le référent juridique avant publication (brief, bloc 6). Passer à False pour l'omettre partout.
OFFRE_10E_MOIS = True
# Formulation de Themis, 26/11/2026 (art. 25-15 et 25-17 de la loi 89-462, art. 18, L121-3 c. conso.)
OFFRE_TITRE = "Bail de 10 mois mené à son terme : le 10e loyer est offert"
OFFRE_TEXTE = "Si vous réglez les 9 premiers loyers de 3 475 € et restez jusqu'au terme du bail de 10 mois, le loyer du 10e mois (3 475 €) est offert, une seule fois. Le loyer reste de 3 475 € par mois sur toute la durée, le forfait de charges de 175 € reste dû chaque mois, le 10e compris, et un départ avant le terme ne donne pas droit à cette remise."

ALT = {n: a for n, a, _ in b.GALERIE}

def insecable(s):
    """Espaces insécables entre un nombre et son unité : « 175 € » ne se coupe pas en fin de ligne."""
    return re.sub(r"(\d) (€|m²|mois|minutes)", "\\1\u00a0\\2", s)

def lignes(t):
    """Un titre de deux phrases s'écrit sur deux lignes, une phrase par ligne (Géraldine, 26/11/2026)."""
    return "".join(f'<span class="v2-ligne">{E(x)}</span>' for x in re.split(r"(?<=[.?!]) (?=[A-ZÀ-Ý])", t))

def paras(*ps):
    return "".join(f"<p>{insecable(b.fine(E(x)))}</p>" for x in ps)

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
    ("Puis-je partir avant la fin ?", "Oui. Vous pouvez quitter le logement à tout moment en donnant congé au bailleur avec un préavis d'un mois, par lettre recommandée avec avis de réception, par acte de commissaire de justice ou par remise en main propre contre récépissé. Le loyer et le forfait de charges restent dus jusqu'à la fin du préavis. Aucune indemnité de départ n'est demandée. Seule la remise du 10e loyer, réservée aux baux menés jusqu'à leur terme de 10 mois, n'est pas accordée."),
    ("Comment se passe l'arrivée ?", "La remise des clés et l'état des lieux sont organisés avec le bailleur."),
    ("La piscine est-elle privée ?", "Non. Elle est partagée, avec des horaires d'accès."),
    ("Peut-on louer pour des vacances ?", "Non. Cette offre concerne exclusivement la location en bail mobilité, avec justificatif d'éligibilité. Elle n'est pas proposée à la nuit."),
]

# Fiche technique repliable : reprise de la page en ligne, alignée sur le socle factuel du brief (§3).
FICHE = [
    ("Le logement", "plan", [("Surface habitable", "77,51 m² (mesurage loi Boutin, 27/09/2026)"), ("Terrasses", "10,58 m² + 15,75 m², soit 26,33 m²"),
                             ("Véranda buanderie", "4,95 m², hors surface habitable"), ("Pièces", "3, dont 2 chambres"), ("Chambres", "13,91 m² et 12,88 m²"),
                             ("Couchages", "Chambre 1 : lit double. Chambre 2 : deux lits simples de 80 × 200 cm ou un lit double de 160 cm. Salon : canapé-lit"),
                             ("Capacité", "Jusqu'à 4 personnes : couple, colocation ou famille avec deux enfants"),
                             ("Salles d'eau", "2, dont 1 privative avec douche à l'italienne"), ("WC", "2, dont 1 indépendant"),
                             ("Situation", "1er étage d'une villa, logement traversant"), ("Vue", "Baie des Anges")]),
    ("Énergie et confort", "energie", [("DPE", "C en énergie, A en climat"), ("Chauffage et climatisation", "Climatisation réversible"), ("Internet", "Fibre")]),
    ("Équipements", "equipement", [("Cuisine", "Plaque à induction, four, micro-ondes, lave-vaisselle, réfrigérateur-congélateur"),
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
PICTO_LIGNE = {"Surface habitable": "plan", "Terrasses": "soleil", "Véranda buanderie": "machine", "Pièces": "porte", "Chambres": "lit", "Couchages": "lit", "Capacité": "personne",
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
             "enveloppe": '<rect x="4" y="7" width="24" height="18" rx="2"/><path d="M4 9l12 9 12-9"/>',
             "telephone": '<path d="M8 4h5l2 6-3 2c1.5 3.5 4.5 6.5 8 8l2-3 6 2v5c0 1-1 2-2 2C14 26 6 18 6 6c0-1 1-2 2-2z"/>',
             "bus": '<rect x="6" y="4" width="20" height="21" rx="3"/><path d="M6 15h20M6 10h20M10 25v3M22 25v3"/><circle cx="11" cy="20" r="1.2"/><circle cx="21" cy="20" r="1.2"/>',
             "seche": '<rect x="6" y="4" width="20" height="24" rx="2"/><path d="M6 9h20"/><circle cx="16" cy="18" r="6"/><path d="M13 16.5c1 1 2-1 3 0s2 1 3 0M13 19.5c1 1 2-1 3 0s2 1 3 0"/>',
             "linge": '<path d="M5 12h22v5H5zM7 17h18v5H7zM5 22h22v5H5z"/><path d="M9 8c2-3 4-3 7 0s5 3 7 0"/>',
             "pieton": '<circle cx="17" cy="5" r="2.5"/><path d="M16 10l-5 5 1 5M16 10l3 5 5 2M16 10l-2 9 5 4 1 6M14 19l-4 5-3 4"/>',
             "lune": '<path d="M20 4a12 12 0 1 0 8 18A10 10 0 0 1 20 4z"/>',
             "canape": '<path d="M4 14v10h24V14M4 14a2 2 0 0 1 4 0v4h16v-4a2 2 0 0 1 4 0M8 18v-8h16v8M7 24v3M25 24v3"/>',
             "tram": '<rect x="8" y="6" width="16" height="18" rx="3"/><path d="M8 16h16M12 3h8M16 3v3M11 24l-3 5M21 24l3 5M7 29h18"/><circle cx="12" cy="20" r="1.1"/><circle cx="20" cy="20" r="1.1"/>',
             "details": '<rect x="6" y="4" width="20" height="24" rx="2"/><path d="M10 11l2 2 3.5-3.5M10 19l2 2 3.5-3.5M19 11.5h3M19 19.5h3"/>'}
SPRITE_V2 = '<svg width="0" height="0" style="position:absolute" aria-hidden="true"><defs>' + "".join(
    f'<symbol id="i-{n}" viewBox="0 0 32 32">{d}</symbol>' for n, d in PICTOS_V2.items()) + '</defs></svg>'

ATOUTS = [("wifi", "Fibre"), ("cuisine", "Cuisine équipée"), ("parking", "Parking privé"), ("piscine", "Piscine partagée")]
ATOUTS_HTML = "".join(f'<li>{pic(ic, "pic-s")}<span>{t}</span></li>' for ic, t in ATOUTS)

# « Les détails qui comptent » : un élément par ligne avec son picto (Géraldine, 26/11/2026).
DETAILS = [("machine", "Lave-linge"), ("seche", "Sèche-linge"), ("linge", "Linge de maison fourni avec rechange"),
           ("clim", "Climatisation réversible"), ("parking", "Une place de parking privée")]

def paras_pictos(*elements):
    """Paragraphes précédés chacun de leur picto (Géraldine, 26/11/2026)."""
    return '<div class="v2-pparas">' + "".join(f'<div>{pic(ic, "pic-s")}<p>{insecable(b.fine(E(t)))}</p></div>' for ic, t in elements) + "</div>"

def tuiles(elements):
    """Une tuile par élément : picto en grand, libellé dessous (budget, Géraldine, 26/11/2026)."""
    return "".join(f'<li>{pic(ic, "pic")}<span>{E(t)}</span></li>' for ic, t in elements)

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

# Visite resserrée (retour de Brain validé par Géraldine, 26/11/2026) : chambres, salles d'eau, salon, piscine, équipement.
# Le séjour, la cuisine et les terrasses sont déjà dans le trio : ils ne reviennent pas ici.
CARTES = [
    ("visite/salon-ferme", "canape", "Le salon", "Un canapé-lit dans la pièce de vie."),
    ("visite/carte-cuisine", "cuisine", "La cuisine", "Plaque à induction, four, micro-ondes, lave-vaisselle et réfrigérateur-congélateur : de quoi cuisiner au quotidien."),
    ("chambre-1-fenetre", "lit", "La première chambre", "13,91 m², un lit double et une salle d'eau privative avec douche à l'italienne."),
    ("chambre-2-lits", "ordi", "La seconde chambre", "12,88 m², deux lits simples de 80 × 200 cm ou un lit double de 160 cm, et un poste de travail. La fibre est installée dans le logement."),
    ("salle-eau-douche", "douche", "Les salles d'eau", "Deux salles d'eau, dont une privative, la grande avec WC, et un WC indépendant."),
    ("visite/piscine-3", "piscine", "La piscine", "Une piscine partagée dans le jardin de la villa, accessible selon les horaires prévus."),
]
# Toutes les photos, dans l'ordre de la visite, regroupées par pièce (Géraldine, 26/11/2026). Fichiers dans assets/img/visite/.
GALERIE_GROUPES = [
    ("Le séjour", [("salon-ferme", "Le coin salon, canapé-lit replié"), ("salon-1", "Le coin salon, canapé-lit déplié")]),
    ("La cuisine", [("cuisine-1", "La cuisine ouverte et son îlot, face au séjour"), ("cuisine-2", "La cuisine : plan de travail, four, micro-ondes, réfrigérateur"),
                    ("cuisine-3", "L'îlot de la cuisine"), ("cuisine-4", "La cuisine et l'entrée"), ("cuisine-5", "Four, micro-ondes et réfrigérateur-congélateur"),
                    ("cuisine-6", "Plaque à induction et ustensiles"), ("cuisine-7", "Préparer le dîner dans la cuisine")]),
    ("La première chambre et sa salle d'eau privative", [("chambre1-1", "La première chambre, son lit double et sa fenêtre"), ("chambre1-2", "La première chambre et ses rangements"),
                                                          ("sde-privative", "La salle d'eau privative, douche à l'italienne")]),
    ("La seconde chambre", [("chambre2-2", "La seconde chambre côté fenêtre"), ("chambre2-3", "La seconde chambre, côté mur")]),
    ("La grande salle d'eau et le WC", [("sde-grande", "La grande salle d'eau"), ("wc", "Le WC indépendant")]),
    ("Les terrasses", [("terrasse-2", "La terrasse face à la mer"), ("terrasse-3", "La table de la terrasse"), ("apero-3", "La terrasse et la mer"),
                       ("apero-4", "Les tables de la terrasse vues d'en haut"), ("vue", "La vue sur la Baie des Anges")]),
    ("Le jardin et la piscine partagée", [("piscine-3", "La piscine partagée et le jardin"), ("piscine-ciel", "La piscine et le jardin vus du ciel")]),
]
NB_PHOTOS = sum(len(g) for _, g in GALERIE_GROUPES)
GALERIE_TOUT = []
ALT.update({n: a for n, a, _ in GALERIE_TOUT})
ALT.update({"visite/carte-cuisine": "La cuisine équipée : plan de travail, four, micro-ondes et réfrigérateur", "visite/salon-ferme": "Le salon et son canapé replié, contre le mur orange", "visite/piscine-3": "La piscine partagée et le jardin de la villa", "chambre-1-fenetre": "La première chambre, son lit double et sa fenêtre", "salon-vue": "Le salon et son canapé-lit, ouvert sur la terrasse", "chambre-1-lit": "La première chambre et son lit double", "chambre-2-lits": "La seconde chambre et ses deux lits simples",
            "salle-eau-douche": "La grande salle d'eau"})

# Repères de localisation gardés (Géraldine : trajets vérifiés depuis le logement, hors trafic, 26/11/2026).
REPERES_ACCES = [("bus", "Le bus 60 passe à 50 mètres de la villa"), ("tram", "Moins de 10 minutes de la porte au quai du tram"),
                 ("parasol", "La plage à 300 mètres du bas de la colline"), ("parking", "Une place de parking privée comprise")]

# Entrée employeur (retour de Brain validé par Géraldine, 26/11/2026) : espace, équipement, budget identifié, prise en charge.
EMPLOYEUR = [("plan", "Un appartement entier de 77 m², deux chambres, deux salles d'eau"),
             ("equipement", "Cuisine équipée, fibre, poste de travail, linge fourni"),
             ("facture", "Un budget identifié : 3 650 € par mois charges comprises, de 1 à 10 mois"),
             ("societe", "Prise en charge du loyer par l'employeur possible, bail au nom de l'occupant éligible")]

def plan_nice():
    """Plan schématique de Nice, repris de la page du 09/11 : pas une carte, positions composées à la main, ouest à gauche, mer en bas.
    Monaco et Sophia Antipolis sont indiqués en direction, sans temps (retour de Brain, 26/11/2026)."""
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
             '<text text-anchor="middle" class="p-nom">Monaco →</text></g>'
             '<g class="p-bord" transform="translate(110 440)"><use href="#i-puce" x="-12" y="-38" width="24" height="24"/>'
             '<text text-anchor="middle" class="p-nom">← Sophia Antipolis</text></g>')
    reperes = ('<g class="p-ville" transform="translate(880 432)"><circle r="7"/><text x="14" y="-12">Centre-ville</text></g>'
               '<text class="p-promenade" x="560" y="560" transform="rotate(-17 560 560)">Promenade des Anglais</text>'
               '<text class="p-baie" x="680" y="625">Baie des Anges</text>'
               '<text class="p-varnom" x="262" y="220" transform="rotate(86 262 220)">le Var</text>')
    maison = (f'<g class="p-piafs" transform="translate({ax} {ay})"><circle r="36"/><image href="{{R}}assets/img/logo-oiseau-blanc.svg" x="-20" y="-24" width="40" height="44"/>'
              '<text class="p-piafs-nom" y="-56" text-anchor="middle">Les Piafs des Collines</text>'
              '<text class="p-piafs-sous" y="-36" text-anchor="middle">sur la colline de Bellet</text></g>')
    return (f'<figure class="plan-nice"><svg viewBox="0 0 1100 660" role="img" aria-label="Plan schématique de Nice : le logement sur la colline de Bellet, à 7 à 20 minutes en voiture de la plage, des hôpitaux, du campus et de l' + "'" + 'aéroport">'
            f'<rect class="p-terre" width="1100" height="660"/>{collines}{var}<path class="p-mer" d="{cote}"/>{vagues}{reperes}{traits}{points}{bords}{maison}</svg>'
            '<figcaption>Temps en voiture hors trafic, depuis le logement</figcaption></figure>')

def carte(n, ic, t, x):
    return f'<figure class="v2-carte">{photo(n)}<figcaption>{pic(ic, "pic v2-pic")}<h3>{E(t)}</h3>{paras(x)}</figcaption></figure>'

def corps():
    fond = AQUARELLE or "hero-vue-v2"   # vue retouchée, ciel bleu et bateaux (Géraldine, 26/11/2026)
    mention_aqua = '<p class="v2-aqua">Interprétation aquarelle de la vue réelle.</p>' if AQUARELLE else ""
    cartes = "".join(carte(*c) for c in CARTES)
    details = f'<div class="v2-carte v2-carte-bleue">{pic("details", "pic v2-pic")}<h3>Les détails qui comptent</h3>{liste_pictos(DETAILS)}</div>'
    gal = "".join(f'<div class="v2-galerie-groupe"><h3>{E(t)}</h3><div class="galerie v2-gg">'
                  + "".join(f'<a href="{{R}}assets/img/visite/{n}.jpg"><img src="{{R}}assets/img/visite/{n}-m.jpg" alt="{E(a)}" loading="lazy"></a>' for n, a in photos)
                  + "</div></div>" for t, photos in GALERIE_GROUPES)
    fiche = "".join(f'<div class="fiche-bloc"><h3>{pic(ic)}{E(t)}</h3><dl>'
                    + "".join(f'<dt>{pic(PICTO_LIGNE.get(k, ic), "pic-s")}{E(k)}</dt><dd>{insecable(E(v))}</dd>' for k, v in lignes) + "</dl></div>" for t, ic, lignes in FICHE)
    faq = "".join(f"<details><summary>{b.fine(E(q))}</summary><p>{b.fine(E(r))}</p></details>" for q, r in FAQ)
    avis = "".join(f'<blockquote class="v2-citation"><p>« {E(q)} »</p><cite>{E(c)}</cite></blockquote>' for q, c in AVIS)
    # Encadré réhiérarchisé (Géraldine, 26/11/2026) : mots de Themis inchangés, découpés pour la lecture.
    offre = f"""<aside class="v2-offre">
      <p class="v2-offre-sur">Bail de 10 mois mené à son terme :</p>
      <p class="v2-offre-titre">le 10<sup>e</sup> loyer est offert</p>
      <p class="v2-offre-cle">Si vous réglez les 9 premiers loyers de 3 475 € et restez jusqu'au terme du bail de 10 mois, le loyer du 10<sup>e</sup> mois (3 475 €) est offert, une seule fois.</p>
      <ul class="v2-offre-conditions">
        <li>Le loyer reste de 3 475 € par mois sur toute la durée</li>
        <li>Le forfait de charges de 175 € reste dû chaque mois, le 10<sup>e</sup> compris</li>
        <li>Un départ avant le terme ne donne pas droit à cette remise</li>
      </ul></aside>""" if OFFRE_10E_MOIS else ""
    motifs = "".join(f"<option>{E(m)}</option>" for m in MOTIFS)
    publics = "".join(f'<li>{pic(ic, "pic-s")}<span>{t}</span></li>' for ic, t in
                      (("hopital", "Hôpitaux"), ("societe", "Entreprises"), ("campus", "Universités"), ("valise", "Services de mobilité")))
    reserve = "Sous réserve de disponibilités et d'un dossier éligible"
    parler = "Nous parler d'une arrivée"
    acces_texte = "Les Piafs se trouvent sur la <strong>colline de Bellet</strong>, à l'ouest de Nice."
    return SPRITE_V2 + f"""<div class="v2">
<section class="v2-hero">
  <div class="v2-cadre">
    <picture><source media="(max-width:700px)" srcset="{{R}}assets/img/hero-vue-v2-mobile.jpg"><img src="{{R}}assets/img/{fond}.jpg" alt="Vue sur la Baie des Anges depuis Les Piafs des Collines, à Nice Bellet." fetchpriority="high"></picture>
    <h1><span class="h1-sur">Location meublée à Nice · Bail mobilité</span>À Nice pour travailler. <span class="v2-h1-2">Bien chez vous pour en profiter.</span></h1>
  </div>
  <div class="v2-l v2-hero-info">
    <div class="v2-hero-faits">
      <p>77 m² · 2 chambres · Terrasses vue mer</p>
      <p>Nice Bellet · De 1 à 10 mois</p>
    </div>
    <div class="v2-hero-action">
      <p class="v2-prix">3 650 €/mois <span>Charges comprises</span></p>
      <p class="v2-actions"><a class="bouton blanc" href="#demande">Vérifier mes dates</a></p>
      <p class="v2-micro">Prise en charge employeur possible</p>
    </div>
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
  <p class="v2-eligible">Location réservée aux personnes éligibles au bail mobilité</p>
</div></section>
<div class="store" aria-hidden="true"></div>

<section class="v2-blanc" id="habiter"><div class="v2-l">
  <h2 class="v2-t bleu v2-titre-xl">{lignes("Une mission temporaire. Un vrai chez‑vous.")}</h2>
  <div class="v2-habiter-texte">{paras("Une cuisine pour garder vos habitudes. Deux chambres pour ne pas tout faire dans la même pièce. Une terrasse pour prendre le dîner dehors.",
        "Ici, vous louez un appartement entier, meublé et équipé. La vue est un plaisir en plus. Le confort du quotidien est déjà là.")}</div>
  <div class="v2-trio v2-bandeau">
    <figure>{img("terrasse-vue-mer", "Terrasse de l'appartement avec table et vue sur la mer.")}<figcaption>Le soir, changez d'horizon</figcaption></figure>
    <figure><img src="{{R}}assets/img/visite/trio-sejour.jpg" alt="Le séjour : le canapé et la table à manger, ouverts sur la terrasse" loading="lazy"><figcaption>De la place pour vivre, pas seulement pour dormir</figcaption></figure>
    <figure><img src="{{R}}assets/img/visite/trio-cuisine.jpg" alt="La cuisine équipée : îlot et tabourets, four, micro-ondes et réfrigérateur" loading="lazy"><figcaption>Vos habitudes voyagent aussi</figcaption></figure>
  </div>
  <p class="v2-centre"><a class="bouton" href="#demande">Vérifier mes dates</a></p>
</div></section>

<section class="v2-bleu v2-titre-section" id="logement"><div class="v2-l">
  <h2 class="v2-t v2-titre-xl">{lignes("Entrez. Vous avez de la place.")}</h2>
  <p class="v2-lead v2-une-ligne">Au premier étage d'une villa, un appartement traversant de 77,51 m² avec deux chambres, deux salles d'eau et deux terrasses.</p>
</div></section>
<section class="v2-blanc v2-visite"><div class="v2-l">
  <div class="v2-cartes">{cartes}{details}</div>
  <details class="v2-galerie-tout"><summary>Voir toutes les photos ({NB_PHOTOS})</summary><div class="v2-galerie-visite">{gal}</div></details>
</div></section>

<section class="v2-bleu v2-acces" id="acces"><div class="v2-l">
  <h2 class="v2-t">Nice, côté colline.</h2>
  <p class="v2-acces-1">{acces_texte}</p>
  <div class="v2-acces-grille">
    {plan_nice()}
    <div>
      {liste_pictos(REPERES_ACCES)}
      <div class="v2-acces-2">{pic("repere", "pic v2-pic")}<p class="v2-acces-q">Vous venez pour une mission précise ?</p>
      <p>Indiquez-nous votre lieu de travail : vérifiez votre trajet quotidien avant de choisir vos dates.</p>
      <p><a class="bouton corail" href="#demande">Vérifier mes dates</a></p></div>
    </div>
  </div>
</div></section>

<div class="store" aria-hidden="true"></div>
<section class="v2-bleu" id="prix"><div class="v2-l">
  <h2 class="v2-t"><span class="v2-ligne">Un budget clair,</span><span class="v2-ligne">avant de faire vos valises.</span></h2>
  <p class="v2-montant">3 650 €<small>/ mois</small></p>
  <p class="v2-sous-prix">Charges comprises · De 1 à 10 mois</p>
  <p class="v2-detail-prix"><span>Loyer 3 475 €</span><span>+ forfait de charges 175 €</span></p>
  <div class="v2-budget">
    <div class="v2-budget-col"><h3>Ce qui est inclus</h3><ul class="v2-tuiles">{tuiles(INCLUS)}</ul></div>
    <div class="v2-budget-col v2-budget-charge"><h3>Ce qui n'est pas inclus, à votre charge</h3><ul class="v2-tuiles">{tuiles(NON_INCLUS)}</ul></div>
  </div>
  {offre}
  <p class="v2-centre"><a class="bouton corail" href="#demande">Demander les disponibilités</a></p>
</div></section>

<section class="v2-bleu v2-employeur" id="prescripteurs"><div class="v2-l">
  <h2 class="v2-t v2-titre-employeur"><span class="v2-ligne">Votre collaborateur vient pour plusieurs mois.</span><span class="v2-ligne v2-dore">Proposez-lui un endroit où vivre.</span></h2>
  <div class="v2-employeur-grille">
    <div>
      {liste_pictos(EMPLOYEUR)}
      <ul class="v2-publics">{publics}</ul><p class="v2-reserve">{E(reserve)}</p>
      <p><a class="bouton corail" href="#demande" data-pour="tiers">{E(parler)}</a></p>
    </div>
    <div class="v2-employeur-photo"><img src="{{R}}assets/img/visite/cuisine-1.jpg" alt="La pièce de vie : cuisine ouverte, îlot et séjour face à la terrasse" loading="lazy"></div>
  </div>
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
  <div class="v2-contact">
    <a class="v2-encadre-contact v2-tel" href="mailto:{b.MAIL}">{pic("enveloppe", "pic-s")}<span>{b.MAIL}</span></a>
  </div>
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
    tete = tete.replace('href="{R}assets/style.css">', 'href="{R}assets/style.css">\n<link rel="stylesheet" href="{R}assets/v2.css">')
    tete = tete.replace(f'href="{"../" * prof}assets/style.css">', f'href="{"../" * prof}assets/style.css">\n<link rel="stylesheet" href="{"../" * prof}assets/v2.css">')
    tete = tete.replace("<body>", '<body class="v2-page">', 1)
    contenu = tete + b.entete("mob", "", prof) + "<main>" + corps() + "</main>" + b.pied("mob", prof) + b.SCRIPT_GALERIE + SCRIPT_FORM + b.SCRIPT_REVEAL + "</body></html>\n"
    # Contact par email uniquement sur cette page (Géraldine, 26/11/2026) : le téléphone du pied de page commun est retiré ici.
    contenu = contenu.replace(f'<br><a href="tel:{b.TEL_LIEN}">{b.TEL}</a>', "")
    contenu = b.propre(contenu.replace("{R}", "../" * prof))
    contenu = b.poser_langues(contenu, None, "fr")
    f = b.SITE / CHEMIN
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(contenu, encoding="utf-8")
    print("  ", CHEMIN)

def lancement():
    """La v2 devient la page d'accueil (Géraldine, 26/11/2026). Idempotent : se relance après outils/build.py."""
    generer()
    # Redirections : la racine ne renvoie plus vers /bail-mobilite/ ; l'ancienne adresse et celle de la v2 mènent à la racine.
    f = b.SITE / "_redirects"
    lignes = [l for l in f.read_text(encoding="utf-8").splitlines() if l.strip()]
    garde = ("/bail-mobilite/ / 301", "/bail-mobilite / 301", "/bail-mobilite-v2/ / 301", "/bail-mobilite-v2 / 301")
    lignes = [l for l in lignes if l != "/ /bail-mobilite/ 302" and l not in garde]
    lignes = [l.replace(" /bail-mobilite/ ", " / ") for l in lignes]
    f.write_text("\n".join(list(garde) + lignes) + "\n", encoding="utf-8")
    # Plan du site : la racine remplace /bail-mobilite/.
    m = b.SITE / "sitemap.xml"
    t = m.read_text(encoding="utf-8").replace(f"<loc>{b.BASE}/bail-mobilite/</loc>", f"<loc>{b.BASE}/</loc>")
    m.write_text(t, encoding="utf-8")
    print("   _redirects, sitemap.xml : racine = page v2")

if __name__ == "__main__":
    lancement()
