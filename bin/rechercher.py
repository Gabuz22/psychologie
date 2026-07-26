#!/usr/bin/env python3
"""RECHERCHER — interroge et exporte le corpus sans relancer un script à la main.

  python bin/rechercher.py --concept trieb --annee-max 1905
  python bin/rechercher.py --auteur "Otto Rank"
  python bin/rechercher.py --mot-cle Schmetterling
  python bin/rechercher.py --oeuvre traumdeutung --groupe reve --csv > citations.csv
  python bin/rechercher.py --groupe pulsion --json

Chaque filtre fourni est un ET logique ; aucun n'est requis (sans filtre : tout le corpus).
Chaque résultat est une CITATION complète (texte allemand + repère + réserve de datation) —
jamais un chiffre nu, jamais un extrait qu'on ne pourrait pas revérifier dans la source.
"""
import argparse
import csv
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core.corpus import Corpus     # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Recherche multicritère et export de citations.")
    ap.add_argument("--concept")
    ap.add_argument("--groupe")
    ap.add_argument("--sous-concept")
    ap.add_argument("--auteur", help='ex. "Sigmund Freud", "Otto Rank"')
    ap.add_argument("--oeuvre", help="clé du registre core/sources.py (ex. traumdeutung)")
    ap.add_argument("--statut", choices=["affirme", "modalise", "interrogatif", "rapporte"])
    ap.add_argument("--fonction", help="ex. hypothese, objection, auto_citation, revision")
    ap.add_argument("--mot-cle", help="sous-chaîne allemande cherchée dans le texte (insensible à la casse)")
    ap.add_argument("--annee-min", type=int, help="borne basse de la fenêtre de datation de l'atome")
    ap.add_argument("--annee-max", type=int, help="borne haute de la fenêtre de datation de l'atome")
    ap.add_argument("--limite", type=int, default=50, help="nombre de citations rendues (0 = tout)")
    ap.add_argument("--longueur", type=int, default=300, help="longueur du texte cité, en caractères")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--csv", action="store_true")
    a = ap.parse_args()

    corpus = Corpus()
    atomes = corpus.rechercher(concept=a.concept, groupe=a.groupe, sous_concept=a.sous_concept,
                               auteur=a.auteur, oeuvre=a.oeuvre, statut=a.statut,
                               fonction=a.fonction, mot_cle=a.mot_cle,
                               annee_min=a.annee_min, annee_max=a.annee_max)
    # Ordre de lecture naturel : chronologique par œuvre, puis position dans le texte.
    atomes.sort(key=lambda x: (corpus.oeuvres[x["oeuvre"]]["annee_oeuvre"], x["debut"]))
    rendus = atomes if a.limite == 0 else atomes[:a.limite]
    citations = [corpus.citer(at, longueur=a.longueur) for at in rendus]

    if a.json:
        print(json.dumps({"total_trouve": len(atomes), "rendus": len(citations),
                          "citations": citations}, ensure_ascii=False, indent=1))
    elif a.csv:
        w = csv.writer(sys.stdout)
        w.writerow(["id", "auteur", "oeuvre", "chapitre", "position_debut", "position_fin",
                   "edition_lue", "datation", "texte"])
        for c in citations:
            w.writerow([c["id"], c["auteur"], c["oeuvre"], c["chapitre"] or "",
                       c["position"][0], c["position"][1], c["edition_lue"], c["datation"],
                       " ".join(c["texte"].split())])
    else:
        print("%d atome(s) trouvé(s) — %d affiché(s)\n" % (len(atomes), len(citations)))
        for c in citations:
            print("« %s »" % " ".join(c["texte"].split()))
            print("  → %s (%s) · %s · %s\n" % (c["oeuvre"], c["auteur"], c["chapitre"] or "—",
                                                c["datation"]))
        if not citations:
            print("Aucun résultat — vérifiez le nom exact du concept/groupe (core/lexique.py) "
                  "ou de l'œuvre (core/sources.py).")


if __name__ == "__main__":
    main()
