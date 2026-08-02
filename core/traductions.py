#!/usr/bin/env python3
"""TRADUCTIONS — la mémoire des lectures françaises des citations, atome par atome.

Même doctrine que `core/verification.py`, une unité de plus : SÉPARÉE du corpus (les atomes se
recalculent, les traductions ne se recalculent pas), versionnée et cumulative dans `traductions/`,
jamais dans `derive/`.

Ceci renverse une doctrine plus ancienne du projet (README.md « Pourquoi la langue originale » :
« Aucune phrase n'est jamais traduite ») — décision assumée de Gabriel, pas un oubli. Les deux
raisons d'origine restent honorées : la citation reste vérifiable (le texte original demeure la
référence, la traduction n'est qu'un confort de lecture affiché À CÔTÉ, jamais à sa place), et les
querelles de traduction ne sont pas héritées au hasard (le glossaire imposé à la génération vient de
`core/traduction.py:TERMES`, déjà tranché et documenté par ce projet — *Trieb* → pulsion, jamais
instinct).

Chaque traduction est produite directement depuis le texte source, jamais recopiée ou reconstruite
à partir du souvenir d'une édition publiée existante : c'est autant une garantie de fidélité qu'une
protection contre la reprise d'une traduction protégée.
"""
import json
import os

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FICHIER = os.path.join(RACINE, "traductions", "citations_fr.json")


def charger():
    """Traductions connues → {empreinte: {texte_fr, genere_le, ...}}. Absent = rien encore généré."""
    if not os.path.exists(FICHIER):
        return {"meta": {"scope": []}, "traductions": {}}
    with open(FICHIER, encoding="utf-8") as f:
        return json.load(f)


def cle(atome):
    """Clé d'une traduction : l'EMPREINTE de l'atome, jamais son id positionnel — même raison que
    `verification.cle()` : un identifiant positionnel dérive dès que la segmentation bouge en
    amont, une traduction déjà produite se retrouverait alors accrochée au mauvais atome."""
    return atome["empreinte"] if isinstance(atome, dict) else atome


def traduction(atome, table=None):
    """Le texte français de cet atome, ou None s'il n'a pas encore été traduit."""
    entree = (table or charger())["traductions"].get(cle(atome))
    return entree["texte_fr"] if entree else None


def valider(table=None):
    """Contrôle d'intégrité du registre (appelé par les tests)."""
    t = table or charger()
    erreurs = []
    for empreinte, entree in t["traductions"].items():
        if not entree.get("texte_fr", "").strip():
            erreurs.append("traduction vide pour %s" % empreinte)
        if not entree.get("genere_le"):
            erreurs.append("traduction sans date de génération pour %s" % empreinte)
    return {"ok": not erreurs, "erreurs": erreurs, "traduites": len(t["traductions"])}


def enregistrer(lot, genere_le, scope_ajoute=None, chemin=FICHIER):
    """Fusionne un LOT {empreinte: texte_fr} dans le registre, SANS jamais écraser ce qui y est
    déjà — une interruption en cours de fusion ne doit perdre que le lot en cours, jamais le
    travail déjà acquis. `scope_ajoute` étend `meta.scope` (les auteurs déclarés couverts) sans
    dupliquer une entrée déjà présente.
    """
    # Lire depuis CE chemin, jamais via charger() (qui lit toujours le fichier par défaut) — sinon
    # fusionner sur un chemin autre que celui par défaut relirait le mauvais registre et écraserait
    # ce qui existe déjà à `chemin` avec une copie tronquée du registre par défaut.
    if os.path.exists(chemin):
        with open(chemin, encoding="utf-8") as f:
            t = json.load(f)
    else:
        t = {"meta": {"scope": []}, "traductions": {}}
    for empreinte, texte_fr in lot.items():
        if not texte_fr.strip():
            raise ValueError("traduction vide refusée pour %s" % empreinte)
        t["traductions"][empreinte] = {"texte_fr": texte_fr, "genere_le": genere_le}
    if scope_ajoute:
        portee = set(t["meta"].get("scope", []))
        portee.add(scope_ajoute)
        t["meta"]["scope"] = sorted(portee)
    os.makedirs(os.path.dirname(chemin), exist_ok=True)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(t, f, ensure_ascii=False, indent=1)
        f.write("\n")
    return len(lot)


def couverture(atomes, table=None):
    """Part des ATOMES DONNÉS déjà traduits — sert de garde-fou à l'export : la couverture ne se
    mesure JAMAIS sur le corpus entier, seulement sur la portée qu'on prétend avoir traitée
    (`meta.scope`), sans quoi un auteur pas encore commencé ferait échouer l'export à tort."""
    t = table or charger()
    trad = t["traductions"]
    total = len(atomes)
    traduits = sum(1 for a in atomes if cle(a) in trad)
    return {"total": total, "traduits": traduits,
            "part": round(traduits / total, 4) if total else None}
