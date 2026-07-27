#!/usr/bin/env python3
"""RÉCUPÉRATION d'une œuvre transcrite page par page sur Wikisource allemand.

  python bin/recuperer_wikisource.py "De Studien über Hysterie" 1895_studien_ueber_hysterie.ws.txt

Wikisource transcrit les livres dans l'espace « Seite: », une page de wikitexte par page du
fac-similé, chacune portant un ÉTAT DE RELECTURE. Ce script n'accepte que l'état « Fertig »
(relu deux fois sur le fac-similé) — le même niveau d'exigence que les textes de Project
Gutenberg relus par Distributed Proofreaders, déjà au corpus. Si une seule page est en dessous,
il le DIT et refuse d'écrire : un corpus silencieusement dégradé est pire qu'un corpus absent.

CE QUI EST RETIRÉ, ET POURQUOI :
  • le bandeau <noinclude> de chaque page (état de relecture, en-tête, recommandation de
    citation) : appareil de Wikisource, pas texte de l'auteur ;
  • les GLOSES de contributeurs — reconnaissables à leur lien vers Wikipédia (« [[w:Sopor|… »).
    Utiles au lecteur du site, ce ne sont pas des phrases de l'auteur : atomisées, elles
    produiraient des énoncés du genre « Sopor : sommeil extrêmement profond… » attribués à Freud ;
  • les tableaux de mise en page (table des matières du volume) et le balisage wiki.

CE QUI EST GARDÉ : les notes de bas de page de l'AUTEUR (souvent des développements entiers),
les TITRES DE CHAPITRE — ils portent l'attribution d'auteur dans les œuvres collectives
(« III. Theoretisches (J. Breuer) ») —, l'orthographe d'époque (« einigermaassen »,
« Uebersetzung », antérieure à la réforme de 1901), et les mots coupés en fin de page, recollés.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_DE = os.path.join(RACINE, "sources", "freud", "de")
API = "https://de.wikisource.org/w/api.php"
# Wikimedia exige un User-Agent identifiant l'outil et son dépôt (politique d'accès à l'API).
UA = "corpus-freud/1.0 (https://github.com/Gabuz22/psychologie) python-urllib"


def _api(params):
    url = API + "?" + urllib.parse.urlencode(dict(params, format="json"))
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.load(r)


def _rang(titre):
    """Ordre de lecture réel. Le LIMINAIRE d'abord : les pages du titre et de la préface sont
    nommées « A01 »…« A06 », qu'un tri alphabétique naïf rejetterait APRÈS la page 275 — la
    préface se retrouverait à la fin du livre (défaut constaté, puis corrigé)."""
    m = re.search(r"(A?)(\d+)\.jpg$", titre)
    if not m:
        return (2, 0, titre)
    return (0 if m.group(1) else 1, int(m.group(2)), titre)


def lister_pages(prefixe):
    """Toutes les pages « Seite: » d'une œuvre, dans l'ordre de lecture."""
    titres, suite = [], {}
    while True:
        d = _api(dict({"action": "query", "list": "allpages", "apnamespace": 102,
                       "apprefix": prefixe, "aplimit": 500}, **suite))
        titres += [p["title"] for p in d["query"]["allpages"]]
        if "continue" not in d:
            return sorted(titres, key=_rang)
        suite = d["continue"]


def etats_relecture(titres):
    """État de relecture de chaque page — « Fertig » est le seul accepté."""
    etats = {}
    for i in range(0, len(titres), 50):
        d = _api({"action": "query", "prop": "proofread", "titles": "|".join(titres[i:i + 50])})
        for p in d["query"]["pages"].values():
            etats[p["title"]] = p.get("proofread", {}).get("quality_text", "inconnu")
        time.sleep(0.2)
    return etats


def contenus(titres):
    """Wikitexte de chaque page, indexé par titre."""
    out = {}
    for i in range(0, len(titres), 40):
        d = _api({"action": "query", "prop": "revisions", "rvprop": "content",
                  "rvslots": "main", "titles": "|".join(titres[i:i + 40])})
        for p in d["query"]["pages"].values():
            if "revisions" in p:
                out[p["title"]] = p["revisions"][0]["slots"]["main"]["*"]
        time.sleep(0.2)
    return out


_APOSTROPHES_WIKI = re.compile(r"'{2,}")


def _reduire_gabarits(t):
    """Gabarits wiki : garder le TEXTE qu'ils portent, jeter la mise en page.

    Nécessaire, et pas cosmétique : les titres de chapitre sont enfermés dans des gabarits de
    mise en forme (« LineCenterSize »). Les supprimer en bloc faisait disparaître la structure
    du livre ET l'attribution d'auteur qu'elle porte — « III. Theoretisches (J. Breuer) ». On
    conserve donc le dernier paramètre quand il contient du texte, et on jette le gabarit
    lorsqu'il n'en porte pas (BlockSatzStart, Linie, references…). Du plus imbriqué vers
    l'extérieur, jusqu'à stabilité.
    """
    def remplacer(m):
        params = m.group(1).split("|")
        dernier = params[-1].strip() if len(params) > 1 else ""
        if len(re.findall(r"[A-Za-zÀ-ÿ]", dernier)) >= 2 and "=" not in dernier:
            return " " + dernier + " "
        return " "
    for _ in range(12):
        avant = t
        t = re.sub(r"\{\{([^{}]*)\}\}", remplacer, t)
        if t == avant:
            break
    return t


def nettoyer(wikitexte):
    """Wikitexte d'une page → texte de l'auteur seul."""
    t = wikitexte
    t = re.sub(r"<noinclude>.*?</noinclude>", " ", t, flags=re.S)   # bandeaux d'appareil
    t = re.sub(r"</?noinclude>|<includeonly>|</includeonly>", " ", t)
    # Notes de CONTRIBUTEURS, à retirer. Wikisource les marque lui-même par `group="WS"`
    # (WS = WikiSource) : discriminant sûr, préféré à toute devinette sur le contenu — un
    # premier essai cherchait le mot « Vorlage » et échouait sur « ''Vorlage:'' », mis en
    # italiques. Le lien vers Wikipédia (« [[w:Sopor|… ») sert de filet pour les gloses qui
    # oublient le groupe.
    t = re.sub(r"<ref[^>]*group\s*=\s*[\"']?WS[\"']?[^>]*>.*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"<ref[^>]*>(?=[^<]*\[\[w:).*?</ref>", " ", t, flags=re.S)
    t = re.sub(r"<ref[^>]*/>", " ", t)
    # Les notes de l'AUTEUR sont conservées, mais REJETÉES EN FIN DE PAGE au lieu d'être
    # insérées là où l'appel figure : une note posée au milieu d'une phrase la coupait en deux
    # (« so wird er durch die ) Wenn nicht, so drängt… »), et le découpage en atomes héritait
    # de la coupure. Le texte de la note reste intégralement présent, la phrase reste entière.
    notes = []
    def _mettre_de_cote(m):
        notes.append(" ".join(m.group(1).split()))
        return " "
    t = re.sub(r"<ref[^>]*>(.*?)</ref>", _mettre_de_cote, t, flags=re.S)
    t = re.sub(r"\{\|.*?\|\}", " ", t, flags=re.S)                 # tableaux (table des matières)
    t = _reduire_gabarits(t)
    t = re.sub(r"\[\[[^\]|]*\|([^\]]*)\]\]", r"\1", t)             # [[cible|libellé]] → libellé
    t = re.sub(r"\[\[([^\]]*)\]\]", r"\1", t)                      # [[libellé]] → libellé
    t = _APOSTROPHES_WIKI.sub("", t)                               # gras / italiques wiki
    t = re.sub(r"</?[a-zA-Z][^>]*>", " ", t)                       # balises HTML résiduelles
    t = re.sub(r"^\s*=+\s*(.*?)\s*=+\s*$", r"\1", t, flags=re.M)   # titres : gardés en clair
    t = re.sub(r"^[:*#]+\s*", "", t, flags=re.M)                   # puces et indentations
    if notes:
        t = t.rstrip() + "\n\n" + "\n\n".join(notes)
    return t


def assembler(pages_ordonnees, textes):
    """Colle les pages bout à bout en recollant les mots coupés en fin de page."""
    morceaux = [nettoyer(textes.get(t, "")).strip() for t in pages_ordonnees]
    texte = "\n".join(m for m in morceaux if m)
    texte = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", texte)   # césure de fin de page recollée
    texte = re.sub(r"[ \t]+", " ", texte)
    texte = re.sub(r"\n{3,}", "\n\n", texte)
    return texte.strip()


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        sys.exit(2)
    prefixe, nom_fichier = sys.argv[1], sys.argv[2]

    print("recensement des pages « Seite:%s … »" % prefixe)
    titres = lister_pages(prefixe)
    if not titres:
        sys.exit("aucune page trouvée pour ce préfixe — vérifier l'orthographe exacte")
    print("  %d pages" % len(titres))

    print("contrôle de l'état de relecture…")
    etats = etats_relecture(titres)
    douteuses = {t: e for t, e in etats.items() if e != "Fertig"}
    if douteuses:
        print("  REFUS — %d page(s) ne sont pas en état « Fertig » :" % len(douteuses))
        for t, e in list(douteuses.items())[:10]:
            print("    %s → %s" % (t, e))
        sys.exit("le corpus n'accepte que des transcriptions relues deux fois")
    print("  les %d pages sont en état « Fertig »" % len(titres))

    print("récupération du wikitexte…")
    textes = contenus(titres)
    manquantes = [t for t in titres if t not in textes]
    if manquantes:
        sys.exit("contenu absent pour %d page(s), ex. %s" % (len(manquantes), manquantes[:3]))

    texte = assembler(titres, textes)
    chemin = os.path.join(DOSSIER_DE, nom_fichier)
    with open(chemin, "w", encoding="utf-8", newline="\n") as f:
        f.write(texte)
    print("→ %s (%d signes, %d pages relues « Fertig »)" % (chemin, len(texte), len(titres)))


if __name__ == "__main__":
    main()
