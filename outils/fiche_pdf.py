#!/usr/bin/env python3
"""Génère le PDF A4 de la fiche logement RH depuis contenu/kit-rh/fiche-logement.html (Chrome via Playwright).

Lancer :  python3 outils/fiche_pdf.py
Sortie :  site/assets/docs/fiche-logement-les-piafs-des-collines.pdf (non liée depuis le site tant qu'elle n'est pas validée).
"""
import subprocess
from pathlib import Path

RACINE = Path(__file__).resolve().parent.parent
SOURCE = RACINE / "contenu/kit-rh/fiche-logement.html"
SORTIE = RACINE / "site/assets/docs/fiche-logement-les-piafs-des-collines.pdf"   # pour le bouton de téléchargement de la page
# Ce qui se partage va dans MEDIA/OUT, pas dans le dépôt (Géraldine, 26/11/2026)
PARTAGE = RACINE.parent.parent / "MEDIA/OUT/LCCA/Clients/PIAFS/Location Bail Mobilité/Kit RH"
PLAYWRIGHT = "/opt/homebrew/lib/node_modules/playwright"

SCRIPT = f"""
const {{ chromium }} = require('{PLAYWRIGHT}');
(async () => {{
  const b = await chromium.launch({{ channel: 'chrome' }});
  const p = await b.newPage();
  await p.goto('file://{SOURCE}', {{ waitUntil: 'networkidle' }});
  await p.evaluate(() => document.fonts.ready);
  await p.pdf({{ path: '{SORTIE}', format: 'A4', printBackground: true, margin: {{ top: 0, right: 0, bottom: 0, left: 0 }}, preferCSSPageSize: true }});
  await b.close();
}})();
"""

if __name__ == "__main__":
    SORTIE.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["node", "-e", SCRIPT], check=True)
    print("  ", SORTIE.relative_to(RACINE))
    import shutil
    PARTAGE.mkdir(parents=True, exist_ok=True)
    shutil.copy2(SORTIE, PARTAGE / SORTIE.name)
    shutil.copy2(RACINE / "contenu/kit-rh/emails.md", PARTAGE / "emails-kit-rh.md")
    shutil.copy2(RACINE / "contenu/kit-rh/premiers-envois.md", PARTAGE / "premiers-envois.md")
    print("   partage :", PARTAGE)
