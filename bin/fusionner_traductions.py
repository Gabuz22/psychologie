#!/usr/bin/env python3
"""FUSIONNE un lot de traductions dans le registre (`traductions/citations_fr.json`).

  python bin/fusionner_traductions.py <fichier_lot_traduit.json> [--scope "Sigmund Freud"]

Le fichier d'entrée est une liste [{"empreinte": ..., "texte_fr": ...}, ...] — le format que je
(Claude) produis après avoir traduit le lot extrait par `bin/extraire_lot_traduction.py`. Valide
chaque entrée avant de fusionner ; un lot mal formé est refusé EN BLOC (voir
`core/traductions.py:enregistrer`), jamais fusionné à moitié.
"""
import argparse
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import traductions            # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Fusionne un lot de traductions dans le registre.")
    ap.add_argument("fichier", help="JSON [{empreinte, texte_fr}] à fusionner")
    ap.add_argument("--scope", help="auteur à déclarer couvert (ajouté à meta.scope)")
    a = ap.parse_args()

    with open(a.fichier, encoding="utf-8") as f:
        entrees = json.load(f)

    lot = {}
    for e in entrees:
        if not e.get("empreinte") or not e.get("texte_fr"):
            raise SystemExit("entrée mal formée (empreinte et texte_fr requis) : %r" % e)
        lot[e["empreinte"]] = e["texte_fr"]

    n = traductions.enregistrer(lot, datetime.date.today().isoformat(), scope_ajoute=a.scope)
    print("-> %d traduction(s) fusionnée(s) dans %s" % (n, traductions.FICHIER))


if __name__ == "__main__":
    main()
