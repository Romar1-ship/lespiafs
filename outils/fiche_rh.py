#!/usr/bin/env python3
"""Génère la fiche logement RH, une seule page A4 (recto, Géraldine 26/11/2026), dans contenu/kit-rh/fiche-logement.html, puis le PDF.

Lancer :  python3 outils/fiche_rh.py
Textes : sous-tâche ClickUp 1amye9cq1q8, relecture Themis du 26/11/2026, retours de Géraldine du 26/11/2026
(pictos à la place des puces, titres de rubrique en capitales, texte plus grand, capacité 4 personnes,
grande salle d'eau avec WC et WC indépendant).
"""
import subprocess, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as b
import build_v2 as v

RACINE = Path(__file__).resolve().parent.parent
SORTIE = RACINE / "contenu/kit-rh/fiche-logement.html"

ICONES = {**b.ICONES, **v.PICTOS_V2}
def ic(n, cls="ic"):
    return f'<svg class="{cls}" viewBox="0 0 32 32" aria-hidden="true">{ICONES[n]}</svg>'

def liste(elements):
    return '<ul class="pl">' + "".join(f"<li>{ic(i)}<span>{t}</span></li>" for i, t in elements) + "</ul>"

REPERES = [("plan", "77 m²", "Appartement entier"), ("lit", "2", "Chambres"), ("douche", "2", "Salles d'eau"),
           ("soleil", "2", "Terrasses vue mer"), ("personne", "4", "Personnes")]

VIVRE = [("cuisine", "Une cuisine équipée pour garder ses habitudes"),
         ("machine", "Lave-linge et sèche-linge"),
         ("ordi", "Fibre et poste de travail"),
         ("clim", "Climatisation, chauffage"),
         ("linge", "Linge de maison fourni avec rechange"),
         ("parking", "Une place de parking privée"),
         ("piscine", "Piscine partagée selon horaires")]

CONFIG = [("lit", "<b>Chambre 1</b> · lit double et salle d'eau privative"),
          ("lit", "<b>Chambre 2</b> · deux lits simples de 80 × 200 cm ou un lit double de 160 cm"),
          ("canape", "<b>Salon</b> · canapé-lit"),
          ("douche", "<b>Grande salle d'eau</b> avec WC"),
          ("porte", "<b>WC indépendant</b>"),
          ("machine", "<b>Véranda d'entrée</b> · buanderie avec lave-linge, sèche-linge et petit réfrigérateur"),
          ("personne", "<b>Jusqu'à 4 personnes</b> · couple, colocation ou famille avec deux enfants")]

INCLUS = [("goutte", "Eau"), ("eclair", "Électricité"), ("clim", "Climatisation, chauffage"), ("wifi", "Fibre"),
          ("parking", "Parking"), ("piscine", "Piscine partagée")]

CONTRAT = [("plume", "Bail mobilité de 1 à 10 mois, signé par l'occupant éligible"),
           ("societe", "Prise en charge du loyer par l'employeur possible, avec lettre de prise en charge"),
           ("cle", "Aucun dépôt de garantie · garanties examinées avec le dossier"),
           ("valise", "Remise des clés et état des lieux avec le bailleur"),
           ("repere", "Nice, colline de Bellet · trajet selon le lieu d'affectation")]

# Retour de Brain du 26/11/2026, transmis par Géraldine : une photo intérieure, chaque information à un seul endroit,
# l'argument employeur traduit, un contrat en 4 lignes, une sortie avec lien et QR code.
EMPLOYEUR = [("maison", "Un appartement déjà équipé"), ("facture", "Un budget connu à l'avance"),
             ("personne", "Pour venir seul ou accompagné")]
PLACE = [("lit", "Deux chambres, dont une avec salle d'eau privative"),
         ("lit", "Seconde chambre : deux lits simples ou un lit double"),
         ("douche", "Deux salles d'eau et un WC indépendant"),
         ("cuisine", "Cuisine équipée, buanderie et espace de travail")]
CONTRAT_COURT = [("calendrier", "De 1 à 10 mois en bail mobilité"), ("plume", "Contrat signé par l'occupant éligible"),
                 ("societe", "Prise en charge employeur possible"), ("cle", "Aucun dépôt de garantie")]
INCLUS2 = [("goutte", "Eau"), ("eclair", "Électricité"), ("clim", "Climatisation, chauffage"), ("wifi", "Fibre · Wi-Fi<br>540 Mb/s mesurés*"),
           ("parking", "Parking"), ("piscine", "Piscine partagée"), ("linge", "Linge de maison avec rechange")]

CSS = """
@font-face{font-family:"Outfit";font-weight:100 900;src:url(../../site/assets/fonts/outfit-latin-wght.woff2) format("woff2")}
@font-face{font-family:"Outfit";font-weight:100 900;src:url(../../site/assets/fonts/outfit-latin-ext-wght.woff2) format("woff2");unicode-range:U+0100-02BA,U+1E00-1EFF,U+20A0-20C0}
@page{size:A4;margin:0}
:root{--bleu:#0041B9;--marine:#1C2B45;--corail:#F2735F;--dore:#F6D9A8;--pale:#F1F5FC;--gris:#56627c}
*{box-sizing:border-box}
html,body{margin:0;padding:0}
body{font-family:"Outfit",system-ui,sans-serif;color:var(--marine);font-size:11pt;line-height:1.4;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.page{width:210mm;height:297mm;position:relative;overflow:hidden;background:#fff;page-break-after:always}
.page:last-child{page-break-after:auto}
a{color:var(--bleu);text-decoration:none}
b{font-weight:600}
.ic{width:7mm;height:7mm;flex:none;fill:none;stroke:var(--bleu);stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round}
/* bandeau bleu fin et liseré */
.bande{background:var(--bleu);color:#fff;height:15mm;padding:0 12mm;display:flex;align-items:center;justify-content:space-between}
.marque{display:flex;align-items:center;gap:2.6mm}
.marque .oiseau{height:8.5mm}
.marque .nom{height:2.8mm}
.bande .lieu{font-size:8.6pt;font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--dore)}
.liseret{height:2.4mm;background:repeating-linear-gradient(90deg,var(--bleu) 0 6mm,#fff 6mm 12mm)}
/* photo d'ouverture, titre dans l'image */
.hero{position:relative;height:92mm}
.hero img{width:100%;height:100%;object-fit:cover;display:block}
.hero::after{content:"";position:absolute;inset:0;background:linear-gradient(180deg,transparent 40%,rgba(0,30,90,.62) 100%)}
.hero h1{position:absolute;z-index:1;left:12mm;right:12mm;bottom:8mm;margin:0;color:#fff;font-weight:600;font-size:27pt;line-height:1.05;letter-spacing:-.015em}
.hero h1 span{display:block;color:var(--dore)}
.corps{padding:7mm 12mm 0}
.accroche{font-size:17pt;line-height:1.2;font-weight:600;color:var(--bleu);margin:0 0 6mm;letter-spacing:-.01em}
.accroche span{display:block;color:var(--corail)}
.reperes{display:grid;grid-template-columns:repeat(5,1fr);border-top:.5mm solid var(--bleu);border-bottom:.5mm solid var(--bleu);margin:0 0 7mm}
.reperes div{padding:3.4mm 1mm;text-align:center;display:flex;flex-direction:column;align-items:center;gap:1.2mm}
.reperes div+div{border-left:.3mm solid #cfd9ee}
.reperes .ic{width:8mm;height:8mm;stroke:var(--corail)}
.reperes b{font-size:18pt;font-weight:700;color:var(--bleu);line-height:1}
.reperes span{font-size:7.6pt;text-transform:uppercase;letter-spacing:.1em;font-weight:600;color:var(--gris)}
h2{font-size:11pt;font-weight:700;text-transform:uppercase;letter-spacing:.12em;color:var(--bleu);margin:0 0 3.4mm}
.pl{list-style:none;margin:0;padding:0;display:grid;gap:2.6mm}
.pl li{display:flex;align-items:center;gap:3.4mm;font-size:11.4pt;line-height:1.3}
.deux{display:grid;grid-template-columns:1fr 1fr;gap:9mm}
.photos3{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;position:absolute;left:12mm;right:12mm;bottom:14mm}
.photos3 img{width:100%;height:54mm;object-fit:cover;display:block}
.photos3 figcaption{font-size:8.6pt;color:var(--gris);margin-top:1.4mm}
.suite{position:absolute;right:12mm;bottom:5mm;font-size:8.4pt;color:var(--gris);font-style:italic}
/* page 2 */
.capacite{display:flex;align-items:center;gap:4mm;background:var(--pale);border-left:1.4mm solid var(--corail);padding:4mm 5mm;margin:0 0 7mm}
.capacite .ic{width:11mm;height:11mm;stroke:var(--corail)}
.capacite p{margin:0;font-size:12pt;line-height:1.3}
.capacite b{color:var(--bleu);font-size:14pt;display:block;font-weight:700}
.budget{background:var(--bleu);color:#fff;padding:6mm 7mm;margin:0 0 7mm;display:grid;grid-template-columns:1fr 1.25fr;gap:7mm;align-items:start}
.budget h2{color:var(--dore)}
.prix{font-size:30pt;font-weight:700;line-height:1;margin:0;letter-spacing:-.015em}
.prix small{font-size:12pt;font-weight:500;color:var(--dore)}
.cc{font-size:8.6pt;text-transform:uppercase;letter-spacing:.14em;font-weight:700;color:var(--dore);margin:2mm 0 3mm}
.detail{margin:0;font-size:11pt}
.detail span{display:block}
.tuiles{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(3,1fr);gap:2.4mm}
.tuiles li{background:rgba(255,255,255,.12);padding:2.6mm 2mm;display:flex;flex-direction:column;align-items:flex-start;gap:1.4mm;font-size:9.8pt;line-height:1.2}
.tuiles .ic{stroke:var(--dore);width:6.5mm;height:6.5mm}
.budget .plus{margin:3mm 0 0;font-size:10pt;line-height:1.35}
.budget .plus b{color:var(--dore)}
.loc{display:grid;grid-template-columns:1fr 1fr;gap:9mm;align-items:center;margin-top:7mm}
.loc img{width:100%;height:38mm;object-fit:cover;display:block}
.loc p{margin:0;font-size:11.4pt}
.action{position:absolute;left:12mm;right:12mm;bottom:17mm;background:var(--pale);padding:5mm 6mm;display:grid;grid-template-columns:1.3fr 1fr;gap:6mm;align-items:center;border-top:1.4mm solid var(--bleu)}
.action p.q{font-size:13pt;font-weight:600;color:var(--bleu);line-height:1.25;margin:0}
.action .liens{display:grid;gap:2mm}
.action .liens a{display:flex;align-items:center;gap:2.6mm;font-size:11pt;font-weight:600}
.pied{position:absolute;left:12mm;right:12mm;bottom:6mm;font-size:8pt;color:var(--gris);font-style:italic}

/* recto seul */
.une .bande{height:13mm}
.une .hero{height:49mm}
.une .hero img{object-position:50% 50%}
.une .hero::after{content:none}
.une .hero h1{top:6mm;bottom:auto;font-size:24pt;text-shadow:0 1px 10px rgba(0,40,120,.3)}
.une .corps{padding:5mm 12mm 0}
.une .accroche{font-size:14.5pt;margin:0 0 3.6mm}
.une .reperes{margin:0 0 4mm}
.une .reperes div{padding:2mm 1mm;gap:.8mm}
.une .reperes b{font-size:16pt}
.une .reperes .ic{width:7mm;height:7mm}
.une h2{font-size:10pt;margin:0 0 2.4mm;letter-spacing:.08em}
.une .pl{gap:1.7mm}
.une .pl li{font-size:10.6pt;line-height:1.25;gap:2.8mm}
.une .pl .ic{width:6mm;height:6mm}
.une .cols{display:grid;grid-template-columns:1fr 1fr;gap:4.6mm 8mm}
.une .budget{margin:0;padding:4.4mm 5mm;display:block}
.une .prix{font-size:24pt}
.une .cc{margin:1.2mm 0 1.6mm}
.une .detail{font-size:10.4pt;margin:0 0 2.6mm}
.une .tuiles{gap:1.8mm}
.une .tuiles li{padding:1.8mm 1.8mm;font-size:9.4pt;gap:1mm}
.une .tuiles .ic{width:5.6mm;height:5.6mm}
.une .budget .plus{font-size:9.6pt;margin-top:2.2mm}
.une .action{bottom:13mm;padding:3.2mm 5mm}
.une .action p.q{font-size:11.6pt}
.une .action .liens a{font-size:10.6pt}
.une .action .ic{width:5.6mm;height:5.6mm}
/* tous les pictos des listes : plus petits, en corail (Géraldine, 26/11/2026) */
.une .pl .ic{width:5mm;height:5mm;stroke:var(--corail)}
.une .pied{bottom:5mm;font-size:7.6pt}

/* version resserrée (retour de Brain, 26/11/2026) */
.r .hero{height:46mm}
.r .accroche{margin:0 0 3mm}
.r .atouts{display:grid;grid-template-columns:repeat(3,1fr);gap:3mm;margin:0 0 4mm}
.r .atouts div{display:flex;align-items:center;gap:2.6mm;background:var(--pale);padding:2.6mm 3mm;font-size:10.6pt;font-weight:600;color:var(--bleu);line-height:1.2}
.r .atouts .ic{width:6.5mm;height:6.5mm;stroke:var(--corail)}
.r .duo{display:grid;grid-template-columns:1.08fr 1fr;gap:6mm;align-items:stretch;margin:0 0 4.4mm}
.r .duo figure{margin:0;display:flex;flex-direction:column}
.r .duo img{width:100%;flex:1;min-height:0;object-fit:cover;display:block}
.r .duo figcaption{font-size:8.6pt;color:var(--gris);margin-top:1.2mm}
.r .budget{margin:0}
.r .tuiles{grid-template-columns:repeat(2,1fr)}
.r .tuiles li{flex-direction:row;align-items:center;gap:2mm;padding:1.6mm 2mm;font-size:9.6pt}
.r .tuiles li:last-child{grid-column:1/-1}
.r .sortie{position:absolute;left:12mm;right:12mm;bottom:16mm;background:var(--pale);border-top:1.4mm solid var(--bleu);padding:4mm 5mm;display:grid;grid-template-columns:1fr auto;gap:5mm;align-items:center}
.r .sortie p.q{font-size:12.6pt;font-weight:600;color:var(--bleu);line-height:1.22;margin:0 0 2.4mm}
.r .sortie p.q span{display:block;font-weight:400;color:var(--marine);font-size:11pt}
.r .sortie .cta{display:inline-block;background:var(--corail);color:#fff;font-weight:700;font-size:10pt;letter-spacing:.04em;padding:2.4mm 4mm;margin:0 0 2.4mm}
.r .sortie .mail{display:flex;align-items:center;gap:2.4mm;font-size:10.6pt;font-weight:600}
.r .sortie .mail .ic{width:5.4mm;height:5.4mm}
.r .qr{text-align:center;font-size:7.6pt;color:var(--gris)}
.r .qr img{width:24mm;height:24mm;display:block;margin:0 auto 1mm;background:#fff;padding:1.6mm}
.r .hero{height:44mm}
.r .atouts{margin:0 0 3.4mm}
.r .atouts div{padding:2mm 3mm}
.r .reperes{margin:0 0 3.6mm}
.r .duo{align-items:start}
.r .duo img{height:64mm;flex:none}
.r .budget{padding:3.6mm 4.4mm}
.r .budget .prix{font-size:22pt}
.r .tuiles{grid-template-columns:repeat(3,1fr);gap:1.6mm}
.r .tuiles li{padding:1.4mm 1.6mm;font-size:9pt;gap:1.4mm}
.r .tuiles .ic{width:4.8mm;height:4.8mm}
.r .tuiles li:last-child{grid-column:1/-1}
.r .sortie{padding:3mm 5mm}
.r .sortie p.q{margin:0 0 1.8mm}
.r .sortie .cta{margin:0 3mm 0 0}
.r .sortie .liens{display:flex;align-items:center;flex-wrap:wrap;gap:2mm}
.r .qr img{width:21mm;height:21mm}
.r .tuiles li:nth-child(4){grid-column:span 2}
.r .tuiles li:last-child{grid-column:span 2}
"""

def page1():
    reperes = "".join(f"<div>{ic(i)}<b>{n}</b><span>{t}</span></div>" for i, n, t in REPERES)
    return f"""
<div class="page">
  <div class="bande"><div class="marque"><img class="oiseau" src="img/logo-oiseau-blanc.svg" alt=""><img class="nom" src="img/logo-nom-blanc.svg" alt="Les Piafs des Collines"></div>
  <span class="lieu">Location meublée · Bail mobilité · Nice Bellet</span></div>
  <div class="liseret"></div>
  <div class="hero"><img src="img/vue-bateaux.jpg" alt="La Baie des Anges vue depuis l'appartement, à Nice Bellet">
    <h1>Un vrai chez-soi<span>pour une mission à Nice.</span></h1></div>
  <main class="corps">
    <p class="accroche">Votre collaborateur vient pour plusieurs mois.<span>Proposez-lui un endroit où vivre.</span></p>
    <div class="reperes">{reperes}</div>
    <h2>Pour vivre, pas seulement pour dormir</h2>
    <div class="deux">{liste(VIVRE[:4])}{liste(VIVRE[4:])}</div>
  </main>
  <div class="photos3">
    <figure style="margin:0"><img src="img/sejour.jpg" alt="Le séjour, le canapé et la table"><figcaption>Le séjour</figcaption></figure>
    <figure style="margin:0"><img src="img/cuisine.jpg" alt="La cuisine équipée et son îlot"><figcaption>La cuisine</figcaption></figure>
    <figure style="margin:0"><img src="img/chambre1.jpg" alt="La première chambre"><figcaption>La première chambre</figcaption></figure>
  </div>
  <p class="suite">Configuration, budget et contrat au verso</p>
</div>"""

def page2():
    tuiles = "".join(f"<li>{ic(i)}<span>{t}</span></li>" for i, t in INCLUS)
    return f"""
<div class="page">
  <div class="bande"><div class="marque"><img class="oiseau" src="img/logo-oiseau-blanc.svg" alt=""><img class="nom" src="img/logo-nom-blanc.svg" alt="Les Piafs des Collines"></div>
  <span class="lieu">Fiche logement · Nice Bellet</span></div>
  <div class="liseret"></div>
  <main class="corps">
    <div class="capacite">{ic("personne")}<p><b>Jusqu'à 4 personnes</b>Un couple, une colocation ou une famille avec deux enfants. Nombre d'occupants confirmé pour chaque demande, avant le bail.</p></div>
    <div class="deux">
      <section><h2>Configuration</h2>{liste(CONFIG)}</section>
      <section><h2>Contrat</h2>{liste(CONTRAT)}</section>
    </div>
    <div class="budget" style="margin-top:7mm">
      <div><h2>Budget</h2><p class="prix">3 650 €<small> / mois</small></p><p class="cc">Charges comprises</p>
        <p class="detail"><span>Loyer 3 475 €</span><span>+ forfait de charges 175 €</span></p></div>
      <div><h2>Compris dans le prix mensuel</h2><ul class="tuiles">{tuiles}</ul>
        <p class="plus"><b>Aussi compris :</b> linge de maison avec rechange.<br><b>Non compris :</b> ménage et assurance habitation.</p></div>
    </div>
    <div class="loc"><div><h2>Localisation</h2><p>Nice, colline de Bellet. Trajet quotidien à vérifier selon le lieu d'affectation et les horaires.</p></div>
      <img src="img/terrasse.jpg" alt="La terrasse face à la mer"></div>
  </main>
  <div class="action">
    <p class="q">Une arrivée à préparer ? Envoyez-nous les dates, le nombre d'occupants et le lieu d'affectation.</p>
    <div class="liens">
      <a href="mailto:contact@lespiafsdescollines.com">{ic("enveloppe")}contact@lespiafsdescollines.com</a>
      <a href="https://lespiafsdescollines.com/">{ic("maison")}lespiafsdescollines.com</a>
    </div>
  </div>
  <footer class="pied">Sous réserve de disponibilités et de dossier accepté. Surface exacte : 77,51 m². DPE C · Climat A. Location meublée en bail mobilité (loi n° 89-462 du 6 juillet 1989, titre I<sup>er</sup> ter).</footer>
</div>"""

def page_unique():
    reperes = "".join(f"<div>{ic(i)}<b>{n}</b><span>{t}</span></div>" for i, n, t in REPERES)
    tuiles = "".join(f"<li>{ic(i)}<span>{t}</span></li>" for i, t in INCLUS)
    return f"""
<div class="page une">
  <div class="bande"><div class="marque"><img class="oiseau" src="img/logo-oiseau-blanc.svg" alt=""><img class="nom" src="img/logo-nom-blanc.svg" alt="Les Piafs des Collines"></div>
  <span class="lieu">Location meublée · Bail mobilité · Nice Bellet</span></div>
  <div class="liseret"></div>
  <div class="hero"><img src="img/vue-bateaux.jpg" alt="La Baie des Anges vue depuis l'appartement, à Nice Bellet">
    <h1>Un vrai chez-soi<span>pour une mission à Nice.</span></h1></div>
  <main class="corps">
    <p class="accroche">Votre collaborateur vient pour plusieurs mois.<span>Proposez-lui un endroit où vivre.</span></p>
    <div class="reperes">{reperes}</div>
    <div class="cols">
      <div><section class="vivre"><h2>Pour vivre, pas seulement pour dormir</h2>{liste(VIVRE)}</section>
        <section style="margin-top:4.4mm"><h2>Configuration</h2>{liste(CONFIG)}</section></div>
      <div><section class="budget"><h2>Budget</h2><p class="prix">3 650 €<small> / mois</small></p><p class="cc">Charges comprises</p>
        <p class="detail"><span>Loyer 3 475 € + forfait de charges 175 €</span></p>
        <ul class="tuiles">{tuiles}</ul>
        <p class="plus"><b>Aussi compris :</b> linge de maison avec rechange<br><b>Non compris :</b> ménage et assurance habitation</p></section>
        <section style="margin-top:4.4mm"><h2>Contrat</h2>{liste(CONTRAT)}</section></div>
    </div>
  </main>
  <div class="action">
    <p class="q">Une arrivée à préparer ? Envoyez-nous les dates, le nombre d'occupants et le lieu d'affectation.</p>
    <div class="liens">
      <a href="mailto:contact@lespiafsdescollines.com">{ic("enveloppe")}contact@lespiafsdescollines.com</a>
      <a href="https://lespiafsdescollines.com/">{ic("maison")}lespiafsdescollines.com</a>
    </div>
  </div>
  <footer class="pied">Sous réserve de disponibilités et de dossier accepté. Nombre d'occupants confirmé pour chaque demande, avant le bail. Surface exacte : 77,51 m². DPE C · Climat A. Location meublée en bail mobilité (loi n° 89-462 du 6 juillet 1989, titre I<sup>er</sup> ter).</footer>
</div>"""

def page_resserree():
    reperes = "".join(f"<div>{ic(i)}<b>{n}</b><span>{t}</span></div>" for i, n, t in REPERES)
    tuiles = "".join(f"<li>{ic(i)}<span>{t}</span></li>" for i, t in INCLUS2)
    atouts = "".join(f"<div>{ic(i)}<span>{t}</span></div>" for i, t in EMPLOYEUR)
    return f"""
<div class="page une r">
  <div class="bande"><div class="marque"><img class="oiseau" src="img/logo-oiseau-blanc.svg" alt=""><img class="nom" src="img/logo-nom-blanc.svg" alt="Les Piafs des Collines"></div>
  <span class="lieu">Location meublée · Bail mobilité · Nice Bellet</span></div>
  <div class="liseret"></div>
  <div class="hero"><img src="img/vue-bateaux.jpg" alt="La Baie des Anges vue depuis l'appartement, à Nice Bellet">
    <h1>Un vrai chez-soi<span>pour une mission à Nice.</span></h1></div>
  <main class="corps">
    <p class="accroche">Votre collaborateur vient pour plusieurs mois.<span>Proposez-lui un endroit où vivre.</span></p>
    <div class="atouts">{atouts}</div>
    <div class="reperes">{reperes}</div>
    <div class="duo">
      <figure><img src="img/sejour-terrasse.jpg" alt="Le séjour, le canapé et la table, ouverts sur la terrasse"><figcaption>Le séjour, ouvert sur la terrasse et la mer</figcaption></figure>
      <section class="budget"><h2>Budget</h2><p class="prix">3 650 €<small> / mois</small></p><p class="cc">Charges comprises</p>
        <p class="detail"><span>Loyer 3 475 € + forfait de charges 175 €</span></p>
        <ul class="tuiles">{tuiles}</ul>
        <p class="plus"><b>Non compris :</b> ménage et assurance habitation</p></section>
    </div>
    <div class="cols">
      <section><h2>De la place pour venir accompagné</h2>{liste(PLACE)}</section>
      <section><h2>Contrat</h2>{liste(CONTRAT_COURT)}</section>
    </div>
  </main>
  <div class="sortie">
    <div>
      <p class="q">Votre collaborateur arrive à Nice ?<span>Envoyez-nous ses dates et le nombre d'occupants.</span></p>
      <div class="liens"><a class="cta" href="https://www.lespiafsdescollines.com/">Découvrir l'appartement</a>
      <a class="mail" href="mailto:contact@lespiafsdescollines.com">{ic("enveloppe")}contact@lespiafsdescollines.com</a></div>
    </div>
    <div class="qr"><img src="img/qr-site.svg" alt="QR code vers lespiafsdescollines.com">lespiafsdescollines.com</div>
  </div>
  <footer class="pied">Sous réserve de disponibilités et de dossier accepté. Nombre d'occupants confirmé pour chaque demande, avant le bail. Surface exacte : 77,51 m². DPE C · Climat A. Location meublée en bail mobilité (loi n° 89-462 du 6 juillet 1989, titre I<sup>er</sup> ter).<br>*Débit mesuré ponctuellement en Wi-Fi, variable selon les conditions d'utilisation.</footer>
</div>"""

if __name__ == "__main__":
    html = f"""<!doctype html>
<!-- Généré par outils/fiche_rh.py : modifier le script, pas ce fichier. -->
<html lang="fr"><head><meta charset="utf-8"><title>Les Piafs des Collines · Fiche logement · Bail mobilité à Nice</title>
<style>{CSS}</style></head><body>{page_resserree()}</body></html>
"""
    SORTIE.write_text(html, encoding="utf-8")
    print("  ", SORTIE.relative_to(RACINE))
    subprocess.run([sys.executable, str(RACINE / "outils/fiche_pdf.py")], check=True)
