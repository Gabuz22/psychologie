#!/usr/bin/env python3
"""CLI — atomise le corpus et écrit les résultats dans derive/.

  python bin/atomiser.py              # tout le corpus
  python bin/atomiser.py traumdeutung # une œuvre

`derive/` est REGÉNÉRABLE : rien d'irremplaçable n'y vit (les sources, elles, ne sont jamais
modifiées). Le rapport affiché est volontairement chiffré et vérifiable — pas un « ça marche ».
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import atomisation, sources     # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DERIVE = os.path.join(RACINE, "derive")


def main(cles):
    os.makedirs(DERIVE, exist_ok=True)
    with open(os.path.join(DERIVE, "manifeste_sources.json"), "w", encoding="utf-8") as f:
        json.dump(sources.manifeste(), f, ensure_ascii=False, indent=1)

    for cle in cles:
        r = atomisation.atomiser(cle)
        c, m = r["controles"], r["meta"]
        sortie = {k: r[k] for k in ("meta", "atomes", "controles")}
        sortie["index"] = {k: v for k, v in r["index"].items() if not k.startswith("_")}
        chemin = os.path.join(DERIVE, "atomes_%s.json" % cle)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(sortie, f, ensure_ascii=False, indent=1)

        print("=" * 74)
        print("%s (%s) — éd. lue %s, %d" % (m["oeuvre"], m["oeuvre_fr"], m["edition_lue"], m["annee_edition"]))
        print("  atomes            : %d" % c["total_atomes"])
        print("  recomposition     : %s" % ("OK" if c["recomposition_ordre_ok"] else "ÉCHEC"))
        print("  localisation      : %d/%d (%s)" % (c["localisation_exacte"], c["total_atomes"],
              "toutes vérifiables" if c["localisation_complete"] else "INCOMPLÈTE"))
        print("  qualifiés         : %d (%.0f %%) · non qualifiés : %d"
              % (c["qualifies"], 100 * c["qualifies"] / max(1, c["total_atomes"]), c["non_qualifies"]))
        print("  fonctions établies: %s" % json.dumps(r["index"]["par_fonction"], ensure_ascii=False))
        print("  À CONFIRMER       : %d atome(s) — %s" % (c["a_confirmer"],
              json.dumps(r["index"]["par_signal_a_confirmer"], ensure_ascii=False)))
        print("  statuts           : %s" % json.dumps(r["index"]["par_statut"], ensure_ascii=False))
        print("  groupes concepts  : %s" % json.dumps(r["index"]["par_groupe"], ensure_ascii=False))
        print("  → %s" % os.path.relpath(chemin, RACINE))


if __name__ == "__main__":
    main(sys.argv[1:] or list(sources.OEUVRES))
