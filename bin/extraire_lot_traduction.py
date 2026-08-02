#!/usr/bin/env python3
"""EXTRAIT un lot d'atomes SANS traduction française encore enregistrée.

  python bin/extraire_lot_traduction.py --auteur "Sigmund Freud" [--oeuvre traumdeutung] [--limite 250]

Le fichier JSON produit est ce que je (Claude) lis pour traduire un lot ;
`bin/fusionner_traductions.py` réinjecte le résultat dans le registre
(`core/traductions.py`, `traductions/citations_fr.json`). Ne recalcule rien : lit le corpus,
retire ce qui est déjà dans le registre (par EMPREINTE, jamais par id positionnel — même
discipline que `core/verification.py`), et écrit le reste dans l'ordre du corpus (œuvre par
œuvre, dans l'ordre du texte) — c'est ce qui rend le travail reprenable à la granularité voulue.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import traductions            # noqa: E402
from core.corpus import Corpus          # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "derive", "traduction", "lot_a_traduire.json")


def main():
    ap = argparse.ArgumentParser(description="Extrait un lot d'atomes à traduire en français.")
    ap.add_argument("--auteur", required=True, help="auteur dont on extrait les atomes")
    ap.add_argument("--oeuvre", help="restreindre à une seule œuvre (clé)")
    ap.add_argument("--limite", type=int, help="nombre maximal d'atomes à extraire")
    a = ap.parse_args()

    corpus = Corpus()
    atomes = corpus.rechercher(auteur=a.auteur, oeuvre=a.oeuvre)
    table = traductions.charger()
    a_traduire = [at for at in atomes if traductions.cle(at) not in table["traductions"]]
    if a.limite:
        a_traduire = a_traduire[:a.limite]

    lot = [{"empreinte": at["empreinte"], "texte": at["texte"], "oeuvre": at["oeuvre"],
            "chapitre": at.get("chapitre")} for at in a_traduire]

    os.makedirs(os.path.dirname(SORTIE), exist_ok=True)
    with open(SORTIE, "w", encoding="utf-8") as f:
        json.dump(lot, f, ensure_ascii=False, indent=1)
    print("-> %s (%d atomes à traduire sur %d au total pour %s%s)"
          % (SORTIE, len(lot), len(atomes), a.auteur, " / " + a.oeuvre if a.oeuvre else ""))


if __name__ == "__main__":
    main()
