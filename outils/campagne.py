#!/usr/bin/env python3
"""Visuels de campagne des Piafs des Collines (sous-tâche ClickUp 1amye9cq1q7), composés en HTML puis exportés en PNG.

Lancer :  python3 outils/campagne.py [A B C D E]
Sources : contenu/campagne/ (HTML éditable, une page par visuel et par format).
Exports : MEDIA/OUT/LCCA/Clients/PIAFS/Location Bail Mobilité/Campagne/ (sRGB).
Pas d'aquarelle (Géraldine, 26/11/2026) : chaque visuel est une vraie photo du logement, dans l'identité bleue du site.
Visuel maître A validé par Géraldine le 26/11/2026, avec le cartouche « Location en bail mobilité ».
"""
import subprocess, sys
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SRC = RACINE / "contenu/campagne"
OUT = RACINE.parent.parent / "MEDIA/OUT/LCCA/Clients/PIAFS/Location Bail Mobilité/Campagne"
PLAYWRIGHT = "/opt/homebrew/lib/node_modules/playwright"
FONTS = "../../site/assets/fonts"
ACCROCHE = "Location en bail mobilité"
MENTION = "Bail mobilité sous conditions d'éligibilité et de disponibilité"
EXCLUS = "Ménage et assurance habitation non compris"

# Textes de la sous-tâche, section « Visuels et textes à produire ».
# ciel : le titre se pose dans le ciel de la photo ; sinon il ouvre le panneau bleu.
VISUELS = {
 "A": {"nom": "signature", "photo": "vue.jpg", "pos": "50% 45%", "ciel": True,
       "titre": ["À Nice pour travailler.", "Bien chez vous pour en profiter."],
       "preuve": "77 m² · 2 chambres · Terrasses vue mer",
       "repere": "De 1 à 10 mois · 3 650 €/mois charges comprises",
       "action": "Vérifiez vos dates", "rh": False, "prix": True},
 "B": {"nom": "connivence", "photo": "terrasse.jpg", "pos": "50% 45%", "ciel": False,
       "titre": ["Votre journée était chargée.", "La vue est dégagée."],
       "preuve": "Votre appartement meublé à Nice, pour 1 à 10 mois",
       "repere": "2 chambres · Fibre · Parking privé",
       "action": "Découvrez Les Piafs des Collines", "rh": False, "prix": False},
 "C": {"nom": "installation", "photo": "sejour.jpg", "pos": "50% 50%", "ciel": False,
       "titre": ["En déplacement.", "Pas entre deux valises."],
       "preuve": "Un appartement entier, meublé et équipé, à Nice Bellet",
       "repere": "77 m² · De 1 à 10 mois",
       "action": "Vérifiez vos dates", "rh": False, "prix": False},
 "D": {"nom": "hopitaux", "photo": "chambre.jpg", "pos": "50% 55%", "ciel": False,
       "titre": ["Une mission à Nice.", "Un vrai chez-soi à l'arrivée."],
       "preuve": "Appartement meublé · 2 chambres · 2 salles d'eau",
       "repere": "De 1 à 10 mois · 3 650 €/mois charges comprises",
       "action": "Demandez la fiche logement", "rh": True, "prix": True},
 "E": {"nom": "entreprises", "photo": "cuisine.jpg", "pos": "50% 60%", "ciel": False,
       "titre": ["Votre collaborateur vient pour plusieurs mois.", "Proposez-lui un endroit où vivre."],
       "preuve": "Nice Bellet · Appartement entier · 77 m² · 2 chambres",
       "repere": "3 650 €/mois charges comprises · De 1 à 10 mois",
       "action": "Recevez la fiche logement", "rh": True, "prix": True},
}
FORMATS = {"A": [(1080, 1350), (1080, 1920)], "B": [(1080, 1350), (1080, 1920)], "C": [(1080, 1350), (1080, 1920)],
           "D": [(1200, 1500), (1200, 628)], "E": [(1200, 1500), (1200, 628)]}

def html(v, w, h):
    t1, t2 = v["titre"]
    paysage, story = w > h, h / w > 1.6
    u = (h / 628) if paysage else (w / 1080)
    titre = f'<h1><small>{ACCROCHE}</small><br>{t1}<span>{t2}</span></h1>'
    rh = '<p class="rh">Prise en charge employeur possible</p>' if v["rh"] else ""
    mention = (EXCLUS + "<br>" if v["prix"] else "") + MENTION
    dans_ciel = v["ciel"] and not paysage
    corps = f"""<div class="photo"><img src="img/{v["photo"]}" alt="">{titre if dans_ciel else ""}</div>
<div class="texte">
  {"" if dans_ciel else titre}
  <p class="preuve">{v["preuve"]}</p>
  <p class="repere">{v["repere"]}</p>
  {rh}
  <div class="bas"><span class="action">{v["action"]}</span><span class="site">lespiafsdescollines.com</span></div>
  <p class="mention">{mention}</p>
</div>"""
    return f"""<!doctype html><html lang="fr"><head><meta charset="utf-8"><style>
@font-face{{font-family:"Outfit";font-weight:100 900;src:url({FONTS}/outfit-latin-wght.woff2) format("woff2")}}
@font-face{{font-family:"Outfit";font-weight:100 900;src:url({FONTS}/outfit-latin-ext-wght.woff2) format("woff2");unicode-range:U+0100-02BA,U+1E00-1EFF,U+20A0-20C0}}
:root{{--bleu:#0041B9;--dore:#F6D9A8;--corail:#F2735F;--u:{u}px}}
*{{box-sizing:border-box;margin:0}}
body{{width:{w}px;height:{h}px;overflow:hidden;font-family:"Outfit",sans-serif;background:var(--bleu);color:#fff;display:flex;flex-direction:column{";padding:calc(150*var(--u)) 0 calc(230*var(--u))" if story else ""}}}
.bande{{flex:none;height:calc({"64" if paysage else "96"}*var(--u));display:flex;align-items:center;justify-content:space-between;padding:0 calc(56*var(--u))}}
.marque{{display:flex;align-items:center;gap:calc(16*var(--u))}}
.marque .o{{height:calc({"36" if paysage else "52"}*var(--u))}} .marque .n{{height:calc({"13" if paysage else "17"}*var(--u))}}
.bande .lieu{{font-size:calc({"14" if paysage else "19"}*var(--u));font-weight:700;letter-spacing:.16em;text-transform:uppercase;color:var(--dore)}}
.liseret{{flex:none;height:calc({"10" if paysage else "14"}*var(--u));background:repeating-linear-gradient(90deg,var(--bleu) 0 calc(34*var(--u)),#fff calc(34*var(--u)) calc(68*var(--u)))}}
.scene{{flex:1 1 auto;min-height:0;display:flex;flex-direction:{"row" if paysage else "column"}}}
.photo{{position:relative;flex:1 1 auto;min-height:0;min-width:0}}
.photo img{{position:absolute;inset:0;width:100%;height:100%;object-fit:cover;object-position:{v["pos"]};display:block}}
h1{{font-weight:600;font-size:calc({"34" if paysage else "64"}*var(--u));line-height:1.05;letter-spacing:-.02em;text-wrap:balance}}
.photo h1{{position:absolute;left:calc(56*var(--u));right:calc(56*var(--u));top:calc(46*var(--u));text-shadow:0 calc(2*var(--u)) calc(18*var(--u)) rgba(0,40,120,.35)}}
.texte h1{{margin-bottom:calc({"16" if paysage else "30"}*var(--u))}}
h1 span{{display:block;color:var(--dore)}}
h1 small{{display:inline-block;font-size:calc({"16" if paysage else "26"}*var(--u));font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:#fff;background:var(--bleu);padding:calc(10*var(--u)) calc(18*var(--u));margin-bottom:calc({"12" if paysage else "22"}*var(--u));text-shadow:none}}
.texte h1 small{{background:var(--corail)}}
.texte{{flex:none;{"width:54%;display:flex;flex-direction:column;justify-content:center;padding:calc(30*var(--u)) calc(44*var(--u))" if paysage else "padding:calc(44*var(--u)) calc(56*var(--u)) calc(40*var(--u))"}}}
.preuve{{font-size:calc({"21" if paysage else "38"}*var(--u));font-weight:600;line-height:1.15;text-wrap:balance;margin-bottom:calc(10*var(--u))}}
.repere{{font-size:calc({"18" if paysage else "34"}*var(--u));font-weight:500;color:var(--dore);margin-bottom:calc({"14" if paysage else "24"}*var(--u))}}
.rh{{font-size:calc({"16" if paysage else "28"}*var(--u));font-weight:600;margin:calc(-4*var(--u)) 0 calc({"14" if paysage else "24"}*var(--u))}}
.bas{{display:flex;align-items:center;justify-content:space-between;gap:calc(24*var(--u))}}
.action{{background:var(--corail);color:#fff;font-weight:700;font-size:calc({"15" if paysage else "28"}*var(--u));letter-spacing:.04em;text-transform:uppercase;white-space:nowrap;padding:calc({"12" if paysage else "18"}*var(--u)) calc({"20" if paysage else "30"}*var(--u))}}
.site{{font-size:calc({"15" if paysage else "28"}*var(--u));font-weight:600;text-align:right}}
.mention{{margin-top:calc({"12" if paysage else "20"}*var(--u));font-size:calc({"12" if paysage else "21"}*var(--u));line-height:1.35;opacity:.85}}
</style></head><body>
<div class="bande"><div class="marque"><img class="o" src="img/logo-oiseau-blanc.svg" alt=""><img class="n" src="img/logo-nom-blanc.svg" alt="Les Piafs des Collines"></div><span class="lieu">Nice Bellet</span></div>
<div class="liseret"></div>
<div class="scene">{corps}</div>
</body></html>"""

def exporter(lettres):
    OUT.mkdir(parents=True, exist_ok=True)
    taches = []
    for L in lettres:
        v = VISUELS[L]
        for w, h in FORMATS[L]:
            f = SRC / f"{L}-{v['nom']}-{w}x{h}.html"
            f.write_text(html(v, w, h), encoding="utf-8")
            taches.append((f, OUT / f"{L}-{v['nom']}-{w}x{h}.png", w, h))
    js = f"""const {{ chromium }} = require('{PLAYWRIGHT}');
(async () => {{ const b = await chromium.launch({{ channel: 'chrome' }});
for (const [src, out, w, h] of {[[str(a), str(o), w, h] for a, o, w, h in taches]}) {{
  const p = await b.newPage({{ viewport: {{ width: w, height: h }}, deviceScaleFactor: 1 }});
  await p.goto('file://' + src, {{ waitUntil: 'networkidle' }}); await p.evaluate(() => document.fonts.ready);
  await p.screenshot({{ path: out }}); await p.close(); }}
await b.close(); }})();"""
    subprocess.run(["node", "-e", js], check=True)
    for _, o, _, _ in taches:
        print("  ", o.name)

if __name__ == "__main__":
    exporter(sys.argv[1:] or list(VISUELS))
