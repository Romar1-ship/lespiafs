"""Traduction des pages générées : le HTML français est réécrit en anglais ou en italien.

Chaque texte visible, chaque attribut lisible (alt, aria-label, placeholder, description) et chaque
chaîne des données structurées passe par le dictionnaire contenu/i18n/{langue}.json, dont les clés
sont les textes français. Un texte absent du dictionnaire reste en français et est signalé.
Les liens internes sont rendus absolus et basculés vers la version de la langue quand elle existe.
"""
import html, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin

RACINE = Path(__file__).resolve().parent.parent
DICO = RACINE / "contenu/i18n"
LANGUES = ("en", "it")
ATTRS = {"alt", "aria-label", "placeholder", "title", "data-sujet"}
META = {"description", "og:title", "og:description", "twitter:title"}
MANQUANTS = {l: {} for l in LANGUES}

def norme(s):
    return re.sub(r"\s+", " ", s.replace("\xa0", " ").replace(" ", " ")).strip()

_dicos = {}
def dico(l):
    if l not in _dicos:
        f = DICO / f"{l}.json"
        brut = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
        _dicos[l] = {norme(k): v for k, v in brut.items()}
    return _dicos[l]

def tr(s, l, ignorer=()):
    """Traduit un texte ; garde les espaces autour. Les textes sans lettre ne se traduisent pas."""
    cle = norme(s)
    if not cle or not re.search(r"[A-Za-zÀ-ÿ]", cle):
        return s
    t = dico(l).get(cle)
    if t is None:
        if cle not in ignorer:
            MANQUANTS[l][cle] = ""
        return s
    debut, fin = s[:len(s) - len(s.lstrip())], s[len(s.rstrip()):]
    return debut + t + fin

def tr_json(o, l, ignorer):
    if isinstance(o, dict):
        return {k: (v if k in ("@type", "@context", "url", "item", "email", "telephone", "unitCode", "image", "addressCountry", "inLanguage")
                    else tr_json(v, l, ignorer)) for k, v in o.items()}
    if isinstance(o, list):
        return [tr_json(v, l, ignorer) for v in o]
    if isinstance(o, str):
        return tr(o, l, ignorer)
    return o

class _Traducteur(HTMLParser):
    def __init__(self, l, chemin, liens, ignorer):
        super().__init__(convert_charrefs=True)
        self.l, self.chemin, self.liens, self.ignorer = l, chemin, liens, ignorer
        self.out, self.pile, self.jsonld = [], [], False

    def lien(self, u):
        if not u or u.startswith(("http", "mailto:", "tel:", "#", "data:", "javascript:")):
            return u
        absolu = urljoin("/" + self.chemin, u)
        chemin, _, ancre = absolu.partition("#")
        cible = self.liens(chemin)
        return (cible or chemin) + (("#" + ancre) if ancre else "")

    def balise(self, tag, attrs, fermee=False):
        a = dict(attrs)
        if tag == "html":
            a["lang"] = self.l
        for k, v in list(a.items()):
            if v is None:
                continue
            if k in ("href", "src") or (k == "srcset" and "," not in v):
                a[k] = self.lien(v)
            elif k == "style" and "url(" in v:
                a[k] = re.sub(r"url\(([^)]+)\)", lambda m: f"url({self.lien(m.group(1))})", v)
            elif k in ATTRS:
                a[k] = tr(v, self.l, self.ignorer)
        if tag == "meta" and (a.get("name") in META or a.get("property") in META) and a.get("content"):
            a["content"] = tr(a["content"], self.l, self.ignorer)
        if tag == "meta" and a.get("property") == "og:locale":
            a["content"] = {"en": "en_GB", "it": "it_IT"}[self.l]
        txt = "".join(f" {k}" if v is None else f' {k}="{html.escape(v)}"' for k, v in a.items())
        return f"<{tag}{txt}{' /' if fermee else ''}>"

    def handle_decl(self, d): self.out.append(f"<!{d}>")
    def handle_comment(self, d): self.out.append(f"<!--{d}-->")
    def handle_starttag(self, tag, attrs):
        self.pile.append(tag)
        self.jsonld = tag == "script" and ("type", "application/ld+json") in attrs
        self.out.append(self.balise(tag, attrs))
    def handle_startendtag(self, tag, attrs): self.out.append(self.balise(tag, attrs, True))
    def handle_endtag(self, tag):
        if self.pile and self.pile[-1] == tag: self.pile.pop()
        self.jsonld = False
        self.out.append(f"</{tag}>")
    def handle_data(self, d):
        dans = self.pile[-1] if self.pile else ""
        if dans == "script":
            self.out.append(json.dumps(tr_json(json.loads(d), self.l, self.ignorer), ensure_ascii=False) if self.jsonld and d.strip() else d)
        elif dans == "style":
            self.out.append(d)
        else:
            self.out.append(html.escape(tr(d, self.l, self.ignorer), quote=False))

def traduire(page_html, l, chemin, liens, ignorer=()):
    """page_html : la page française ; chemin : son chemin dans site/ ; liens(chemin_absolu) -> chemin traduit ou None."""
    t = _Traducteur(l, chemin, liens, set(ignorer))
    t.feed(page_html); t.close()
    return "".join(t.out)

class _Textes(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True); self.t = set()
    def handle_data(self, d):
        if norme(d): self.t.add(norme(d))

def textes(fragment):
    """Les textes d'un fragment HTML, normalisés : sert à ne pas signaler ce qui est déjà traduit."""
    p = _Textes(); p.feed(fragment); p.close()
    return p.t

def rapport():
    """Écrit les textes manquants dans contenu/i18n/manquants-{langue}.json et renvoie leur nombre."""
    n = 0
    for l, m in MANQUANTS.items():
        f = DICO / f"manquants-{l}.json"
        DICO.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(m, ensure_ascii=False, indent=1), encoding="utf-8")
        n += len(m)
    return n
