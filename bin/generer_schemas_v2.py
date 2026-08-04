#!/usr/bin/env python3
"""Écrit les schémas v2 canoniques depuis le module qui les exécute."""
import json
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)

from core import relations_v2  # noqa: E402


def main():
    dossier = os.path.join(RACINE, "schemas")
    os.makedirs(dossier, exist_ok=True)
    sorties = {
        "relations_v2.schema.json": json.dumps(
            relations_v2.JSON_SCHEMA, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        "relations_v2.sql": relations_v2.SQL_SCHEMA.strip() + "\n",
        "relations_v2_rollback.sql": relations_v2.SQL_ROLLBACK.strip() + "\n",
    }
    for nom, contenu in sorties.items():
        chemin = os.path.join(dossier, nom)
        with open(chemin, "w", encoding="utf-8", newline="\n") as f:
            f.write(contenu)
        print("ÉCRIT : %s" % chemin)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
