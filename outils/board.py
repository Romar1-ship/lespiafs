#!/usr/bin/env python3
"""Le board des Piafs, sur le gabarit commun des boards LCCA (Géraldine, 28/10/2026).
Le moteur est celui de LCCA-Studio/atelier/tools/board-maison.py ; le contenu est dans board/contenu.py.
Écrit site/board/ : le Worker le sert sous /board, derrière Cloudflare Access, en noindex.
Lancer depuis la racine du dépôt : python3 outils/board.py"""
import importlib.util
import os
import shutil
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ATELIER = os.path.join(RACINE, "..", "LCCA-Studio", "atelier")
LCCA = os.path.join(ATELIER, "..", "board", "site")
SITE = os.path.join(RACINE, "site", "board")
OUTILS = os.path.join(RACINE, "board")

spec = importlib.util.spec_from_file_location("board_maison", os.path.join(ATELIER, "tools", "board-maison.py"))
BM = importlib.util.module_from_spec(spec)
spec.loader.exec_module(BM)
sys.path.insert(0, OUTILS)
import contenu as C  # noqa: E402

os.makedirs(os.path.join(SITE, "assets", "fonts"), exist_ok=True)
os.makedirs(os.path.join(SITE, "assets", "icones"), exist_ok=True)
shutil.copy(os.path.join(LCCA, "lcca.css"), os.path.join(SITE, "atelier.css"))
shutil.copy(os.path.join(LCCA, "base-tokens.css"), os.path.join(SITE, "base-tokens.css"))
shutil.copy(os.path.join(LCCA, "assets", "fonts", "Ezalor.otf"), os.path.join(SITE, "assets", "fonts", "Ezalor.otf"))
shutil.copytree(os.path.join(LCCA, "assets", "textures"), os.path.join(SITE, "assets", "textures"), dirs_exist_ok=True)
shutil.copytree(os.path.join(ATELIER, "site", "_moteur"), os.path.join(SITE, "_moteur"), dirs_exist_ok=True)
shutil.copy(os.path.join(OUTILS, "outil.js"), os.path.join(SITE, "outil.js"))
shutil.copy(os.path.join(ATELIER, "tools", "cloche.js"), os.path.join(SITE, "cloche.js"))

# l'emblème du menu : le nom des Piafs, en blanc, repris du site
shutil.copy(os.path.join(RACINE, "site", "assets", "img", "logo-nom-blanc.svg"), os.path.join(SITE, "assets", "nom.svg"))
# les icônes de l'application, depuis l'oiseau du site
from PIL import Image  # noqa: E402
ico = Image.open(os.path.join(RACINE, "site", "assets", "img", "favicon.png")).convert("RGBA")
for s in (180, 192, 512):
    ico.resize((s, s), Image.LANCZOS).save(os.path.join(SITE, "assets", "icones", f"icone-{s}.png"))

open(os.path.join(SITE, "theme.css"), "w", encoding="utf-8").write(BM.theme(C.MAISON))
sys.path.insert(0, os.path.join(ATELIER, "tools"))
import verifier_formes  # noqa: E402  le verrou des formes communes
verifier_formes.verifier(C.MAISON.get("css", ""), C.MAISON["nom"])
open(os.path.join(SITE, "avis.js"), "w", encoding="utf-8").write(BM.AVIS_JS)
open(os.path.join(SITE, "manifest.webmanifest"), "w", encoding="utf-8").write(BM.manifeste(C.MAISON))
open(os.path.join(SITE, "sw.js"), "w", encoding="utf-8").write(BM.SW)
open(os.path.join(SITE, "plan.js"), "w", encoding="utf-8").write(BM.plan(C.MAISON))
for chemin, (titre, corps) in BM.construire(C).items():
    f = os.path.join(SITE, chemin)
    os.makedirs(os.path.dirname(f), exist_ok=True)
    # les polices du site, hébergées : Fraunces et Sora (le moteur appelle aussi Google Fonts pour ses polices de secours)
    html = BM.page(C, chemin, titre, corps).replace('<link rel="stylesheet" href="', '<link rel="stylesheet" href="/assets/fonts/fonts.css">\n<link rel="stylesheet" href="', 1)
    open(f, "w", encoding="utf-8").write(html)
    print("écrite :", chemin)
