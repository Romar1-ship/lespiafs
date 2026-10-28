"""Le contenu du board Les Piafs, sur le gabarit commun des boards LCCA (LCCA-Studio/atelier/tools/board-maison.py).
Généré par : python3 outils/board.py (depuis la racine du dépôt piafs), écrit dans site/board/.
Rubriques : Vue d'ensemble · Empreinte de Marque · L'offre · À faire · Le carnet · Plateformes · Résultats (Géraldine, 28/10/2026).
À faire, le carnet, les plateformes et les résultats sont vivants : ils lisent ClickUp, liste Roadmap Les Piafs, par /board/api/."""
import os

ICI = os.path.dirname(os.path.abspath(__file__))

MAISON = dict(
    nom="Les Piafs des Collines", court="Les Piafs", espace="Le board des Piafs", fondatrice="Géraldine",
    # la palette Riviera du site : la nuit pour la barre, le sable derrière le bandeau, l'azur pour les titres, le corail en filet
    couleurs=dict(bandeau="#0B5FA5", fond_bandeau="#F7F1E7", survol="#1C2B45", menu="#1C2B45", fond="#FBF8F2", encre="#24324D", accent="#F2735F",
                  titre="#1C2B45", titre_em="#0B5FA5", boussole_em="#F6D9A8", avis_fond="#FCE3DC"),
    emblème="assets/nom.svg", emblème_h="34px",
    voile=".94",
)

# ---------------------------------------------------------------- LA FEUILLE DE ROUTE
ROUTE = [
    ("fait", "globe", "23 oct. 2026", "Le site sur Cloudflare", "Sans Wix, sur la page bail mobilité."),
    ("fait", "plume", "Octobre 2026", "Trois langues, les guides", "Français, anglais, italien ; 5 guides en ligne."),
    ("fait", "cle", "Octobre 2026", "Le cadre légal", "Les pages légales du bail mobilité, relues par Themis."),
    ("ici", "plan", "28 oct. 2026", "Les fondations", "Les guides validés, le médiateur, les plateformes."),
    ("cible", "maison", "15 nov. 2026", "Le premier bail signé", "L'entrée dans les lieux au plus tard le 15 novembre."),
    ("cible", "calendrier", "À dater", "Loué 12 mois sur 12", "Sans vacance entre deux baux."),
]

# ---------------------------------------------------------------- LES TROIS ÉTATS
ETATS = dict(
    retour=[
        "<b>Publier les corrections du 28 octobre</b> : l'arrivée accompagnée, la colline. Il suffit de dire « push ».",
        "<b>Valider les 5 guides</b> dans Le carnet : ils s'ouvrent alors à Google.",
        "<b>Choisir les articles à écrire</b> parmi les 8 propositions du carnet.",
        "<b>Le médiateur de la consommation</b> : adhérer, puis envoyer son nom, son adresse et son site.",
        "<b>La photo du hero</b> : la choisir avant de l'agrandir.",
    ],
    atelier=[
        "<b>Les plateformes</b> : 15 relais à ouvrir, un par un, dans Plateformes.",
        "<b>Le board</b> : l'accès par code e-mail et le lien avec ClickUp.",
    ],
    foi=[
        ("23 oct.", "<b>Le bail mobilité</b>, de 1 à 10 mois, et <b>le bail société</b>, à partir de 3 mois. Plus aucune nuit touristique."),
        ("24 oct.", "<b>On publie par le dépôt</b> : un push sur GitHub, Cloudflare déploie."),
        ("25 oct.", "<b>Le domaine</b> arrive sur la page bail mobilité."),
        ("28 oct.", "<b>L'arrivée est accompagnée</b> : accueil sur place, remise des clés et état des lieux d'entrée ensemble."),
    ],
)

# ---------------------------------------------------------------- L'EMPREINTE, EN LÉGER
S_SITE = "Source : lespiafsdescollines.com, validé par Géraldine du 23 au 28 octobre 2026."
_COUL = [("Azur", "#0B5FA5", "Titres, liens, boutons", True), ("Mer", "#0A4F8A", "Survol", True), ("Corail", "#F2735F", "Guides, langues, filets", True),
         ("Orange", "#E2A94B", "Rayures, accents", False), ("Doré", "#F6D9A8", "Fonds clairs", False), ("Nuit", "#1C2B45", "Titres, pied de page", True),
         ("Ivoire", "#FBF8F2", "Fond", False), ("Sable", "#F7F1E7", "Fonds de blocs", False)]
ESTH_COULEURS = '<div class="pi-charte">' + "".join(
    f'<figure><span style="background:{h}"></span><figcaption><b>{n}</b><code>{h}</code><small>{r}</small></figcaption></figure>' for n, h, r, _f in _COUL) + "</div>"
ESTH_TYPOS = ('<div class="pi-typos"><div><p class="pi-k">Les titres</p><p class="pi-fraunces">Fraunces <em>italique</em></p><small>Graisse 500 pour le hero, 400 ailleurs</small></div>'
              '<div><p class="pi-k">Le texte</p><p class="pi-sora">Sora, lisible et chaleureuse.</p><small>Le texte courant, les menus, les boutons</small></div></div>')
ESTH_IMAGES = ('<div class="pi-affiches">' + "".join(
    f'<figure><img src="/assets/img/guides/{f}.jpg" alt="{t}" loading="lazy"><figcaption>{t}</figcaption></figure>'
    for f, t in [("affiche-hiver-a-nice", "L'Hiver à Nice"), ("affiche-cote-d-azur", "Côte d'Azur"), ("affiche-monaco-broders", "Monaco"), ("affiche-villefranche", "Villefranche")]) + "</div>")

EMPREINTE = [
    ("fondations", "Les fondations", "Les <em>fondations</em>", "Volume II · La Marque", "Qu'est-ce que <em>l'on offre, et à qui ?</em>", [
        ("promesse", "La promesse", dict(forme="frappe", etat="foi", source=S_SITE,
            essentiel="Sur la colline de Bellet, face à la Baie des Anges, <em>de 1 à 10 mois.</em>",
            sous="Un appartement entier de 77,51 m², meublé, tout compris : on arrive avec sa valise.")),
        ("public", "Le public", dict(forme="cartes", etat="foi", source=S_SITE,
            essentiel="Les professionnels <em>en mobilité à Nice.</em>",
            tuiles=[("", "En mission", "Salariés, consultants, chercheurs. Le bail mobilité, de 1 à 10 mois."),
                    ("", "En formation ou en internat", "Internes, fellows, adultes en formation. Les hôpitaux à 12 à 16 minutes."),
                    ("", "Logés par leur employeur", "Le bail au nom de la société, à partir de 3 mois, facturé au payeur.")])),
        ("difference", "La différence", dict(etat="foi", source=S_SITE,
            essentiel="Ni en bord de mer, ni en centre-ville : <em>au calme, face à la mer.</em>",
            tuiles=[("", "Une vraie maison", "Deux chambres, deux salles d'eau, deux terrasses, le jardin, la piscine partagée."),
                    ("", "Tout compris", "Fibre, parking privé, linge fourni, ménage de sortie : un seul montant par mois."),
                    ("", "Un accueil", "Le jour de l'entrée, on vous accueille sur place : les clés, l'état des lieux, ensemble.")])),
        ("territoire", "Le territoire", dict(etat="foi", source=S_SITE,
            essentiel="La colline de Bellet, <em>à l'ouest de Nice.</em>",
            sous="En voiture, hors trafic : Clinique Kantys Centre 12 min, campus Valrose 13 min, CHU Pasteur 2 15 min, aéroport 20 min, Monaco 22 min, Sophia Antipolis 28 min. Le bus 60 à 50 m, vers le tram ligne 2. L'adresse n'apparaît que dans les mentions légales.")),
    ]),
    ("esthetique", "L'esthétique", "L'<em>esthétique</em>", "Volume II · La Marque", "Comment la Riviera <em>se voit-elle ?</em>", [
        ("couleurs", "Les couleurs", dict(etat="foi", source=S_SITE,
            essentiel="L'azur porte, <em>le corail signale.</em>",
            sous="L'esprit des affiches de la Côte d'Azur : l'azur et la nuit pour lire, le corail pour ce qui se clique, les rayures orange en rappel.",
            html=ESTH_COULEURS)),
        ("typographies", "Les typographies", dict(etat="foi", source="Source : le couple de colineperrot.fr, retenu par Géraldine en octobre 2026.",
            essentiel="Fraunces pour les titres, <em>Sora pour le texte.</em>", html=ESTH_TYPOS)),
        ("images", "Les images", dict(etat="foi", source="Source : affiches du domaine public, recadrées et encadrées ; rien de généré.",
            essentiel="Les affiches de la Riviera, <em>pas nos photos.</em>",
            sous="Dans les guides : des affiches anciennes du domaine public, chacune dans son cadre, et des photos sous licence libre. Les photos de l'appartement restent sur la page de l'offre.",
            html=ESTH_IMAGES)),
    ]),
    ("outils", "Les outils", "Les <em>outils</em>", "Volume II · La Marque", "Avec quoi <em>la marque vit-elle ?</em>", [
        ("supports", "Les supports", dict(etat="foi", source=S_SITE,
            essentiel="Le site, les guides, <em>et bientôt les plateformes.</em>",
            fiche=[("Le site", "lespiafsdescollines.com · la page bail mobilité, en FR, EN et IT"),
                   ("Les guides", "5 articles, en ligne, à valider avant Google"),
                   ("Les plateformes", "15 relais à ouvrir : voir Plateformes"),
                   ("Ce board", "lespiafsdescollines.com/board · réservé à Géraldine")])),
        ("qui-valide", "Qui valide", dict(etat="foi", source="Source : Géraldine, 28 octobre 2026.",
            essentiel="Géraldine valide, <em>le site publie.</em>",
            sous="Un article validé dans Le carnet est relu par Themis s'il touche au bail, traduit en anglais et en italien, puis mis en ligne par le dépôt.")),
    ]),
]

# ---------------------------------------------------------------- L'OFFRE
OFFRES = [
    ("bail-mobilite", "Payeur particulier · 1 à 10 mois", "Le bail mobilité", "Le bail <em>mobilité</em>",
     "Pour une mission, une formation, une mutation ou des études : de 1 à 10 mois, meublé et tout compris.", "foi",
     [("Durée", "1 à 10 mois, sans renouvellement"), ("Prix", "Tout compris, à partir de 2 880 € par mois"), ("Pièces", "Le justificatif du motif de mobilité, avant la signature"),
      ("Garantie", "Caution de l'employeur ou caution personnelle ; Visale non mobilisable à ce niveau de loyer")],
     dict(etat="foi", source="Source : lespiafsdescollines.com/bail-mobilite/, 28 octobre 2026.",
          essentiel="De 1 à 10 mois, <em>on arrive avec sa valise.</em>",
          fiche=[("Le logement", "77,51 m², 2 chambres, 2 salles d'eau, 2 terrasses vue mer"), ("Compris", "Charges, fibre, parking privé, linge, ménage de sortie"),
                 ("L'arrivée", "Accueil sur place, remise des clés et état des lieux d'entrée ensemble"), ("Facturation", "Exonérée de TVA")],
          liens=[("https://www.lespiafsdescollines.com/bail-mobilite/", "Voir la page du site")])),
    ("bail-societe", "Payeur personne morale · dès 3 mois", "Le bail société", "Le bail <em>société</em>",
     "L'entreprise loge son collaborateur : le bail et la facture à son nom, à partir de 3 mois.", "foi",
     [("Durée", "À partir de 3 mois"), ("Payeur", "La société, au nom de laquelle le bail est signé"), ("Facturation", "Au nom du payeur, exonérée de TVA")],
     dict(etat="foi", source="Source : lespiafsdescollines.com/bail-mobilite/, 28 octobre 2026.",
          essentiel="Un seul montant à budgéter, <em>une facture au payeur.</em>",
          liens=[("https://www.lespiafsdescollines.com/bail-mobilite/", "Voir la page du site")])),
]
EXPERIENCES = []
OFFRES_NOM = ("L'offre", "L'<em>offre</em>")
COLLABORATION = None


# ---------------------------------------------------------------- LES RUBRIQUES VIVANTES (lues dans ClickUp par /board/api/)
def _vois(liste, ici):
    liens = "".join((f'<a class="est-ici" href="@/{h}">{t}</a>' if h == ici else f'<a href="@/{h}">{t}</a>') for h, t in liste)
    return f'    <nav class="voisines" aria-label="Les pages"><div class="container">{liens}</div></nav>\n'


def _cadre(id_, k, ess, html):
    return (f'    <div class="section paper pt pt--texte" id="{id_}" data-etat="foi"><div class="container"><div class="pt__tete"><p class="pt__k"><span>§N§</span>{k}</p></div>\n'
            f'<p class="pt__ess">{ess}</p>\n<div class="pt__html">{html}</div></div></div>\n<script src="@/outil.js" defer></script>')


A_FAIRE = [("a-faire/", "Les étapes"), ("a-faire/ajouter/", "Ajouter une étape")]
ROADMAP = _vois(A_FAIRE, "a-faire/") + _cadre("etapes", "Les étapes", "Une étape à la fois. <em>Quand c'est fait, on la coche.</em>",
    '<div class="pi-outil" id="pi-etapes"><p class="pi-vide">Un instant…</p></div>')
AJOUT = _vois(A_FAIRE, "a-faire/ajouter/") + _cadre("ajouter", "Ajouter une étape", "Une étape, un article ou une plateforme : <em>elle arrive dans ClickUp.</em>",
    '<form class="pi-form" id="pi-ajout">'
    '<div class="pi-choix"><label><input type="radio" name="type" value="etape" checked> Une étape</label><label><input type="radio" name="type" value="article"> Un article à proposer</label><label><input type="radio" name="type" value="plateforme"> Une plateforme</label></div>'
    '<label for="a-nom">Titre</label><input type="text" id="a-nom" name="nom" required maxlength="160">'
    '<label for="a-note">Consigne ou détail <small>(facultatif)</small></label><textarea id="a-note" name="consigne" rows="6"></textarea>'
    '<button class="pi-btn pi-btn--plein" type="submit">Ajouter</button></form>')
CARNET = _cadre("articles", "Les articles", "Les guides en ligne, <em>les propositions à choisir.</em>",
    '<div class="pi-outil" id="pi-articles"><p class="pi-vide">Un instant…</p></div>'
    '<p class="pi-aide">Un guide validé s\'ouvre à Google à la prochaine publication du site. Une proposition retenue est écrite, relue par Themis si elle touche au bail, traduite, puis mise en ligne.</p>')
PLATEFORMES = _cadre("plateformes", "Les plateformes", "Là où la demande de moyenne durée se trouve déjà : <em>où en est chacune.</em>",
    '<div class="pi-outil" id="pi-plateformes"><p class="pi-vide">Un instant…</p></div>'
    '<p class="pi-aide">À chaque mise en ligne : la durée minimale d\'un mois verrouillée, le calendrier tenu à jour partout en même temps.</p>')

RUBRIQUES_PROPRES = [
    dict(id="a-faire", chemin="a-faire/index.html", menu="À faire", titre="À <em>faire</em>", corps=ROADMAP,
         pages=[("a-faire/ajouter/index.html", "Ajouter une étape", AJOUT)],
         groupes=[("À faire", [("a-faire/index.html", "Les étapes"), ("a-faire/ajouter/index.html", "Ajouter une étape")], "")]),
    dict(id="carnet", chemin="carnet/index.html", menu="Le carnet", titre="Le <em>carnet</em>", corps=CARNET,
         groupes=[("Le carnet", [("carnet/index.html", "Les articles")], "")]),
    dict(id="plateformes", chemin="plateformes/index.html", menu="Plateformes", titre="Les <em>plateformes</em>", corps=PLATEFORMES,
         groupes=[("Plateformes", [("plateformes/index.html", "Où en est chacune")], "")]),
]

RESULTATS_CORPS = _cadre("score", "Le score", "Du site <em>au premier bail signé.</em>",
    '<div class="pi-outil" id="pi-score"><p class="pi-vide">Un instant…</p></div>'
    '<h3 class="pi-h">Saisir un chiffre</h3><form class="pi-form" id="pi-releve"><div class="pi-ligne">'
    '<div><label for="c-ind">Ce que tu mesures</label><input type="text" id="c-ind" name="indicateur" list="c-liste" required placeholder="Demandes reçues">'
    '<datalist id="c-liste"><option value="Demandes reçues"><option value="Visites organisées"><option value="Baux signés"><option value="Mois loués"><option value="Avis Google"><option value="Clics Search Console"></datalist></div>'
    '<div><label for="c-val">Le chiffre</label><input type="text" inputmode="decimal" id="c-val" name="valeur" required></div>'
    '<div><label for="c-date">Date</label><input type="date" id="c-date" name="date"></div></div>'
    '<label for="c-note">Note <small>(facultatif)</small></label><input type="text" id="c-note" name="note" maxlength="200">'
    '<button class="pi-btn pi-btn--plein" type="submit">Enregistrer le chiffre</button></form>'
    '<div class="pi-outil" id="pi-releves"></div>')
RESULTATS = dict(cible="Le premier bail signé, entrée au plus tard le 15 novembre 2026 ; puis loué 12 mois sur 12.", mesures=[], corps=RESULTATS_CORPS,
                 menu=[("resultats/index.html", "Le score")])

# Le style propre au board des Piafs (classes pi-) et ses polices, hébergées sur le site.
MAISON["css"] = open(os.path.join(ICI, "outil.css"), encoding="utf-8").read()
