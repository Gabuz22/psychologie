#!/usr/bin/env python3
"""CLI d'analyse — interroge le corpus par les agents déterministes.

  python bin/analyser.py                     état des lieux (profils, co-occurrences, signaux)
  python bin/analyser.py trieb               dossier d'un concept (+ chronologie, tensions)
  python bin/analyser.py --agent cooccurrence
  python bin/analyser.py --agent signaux --json

Sortie lisible par défaut, `--json` pour chaîner avec un autre outil. Toute affirmation affichée
renvoie à des atomes, et tout atome renvoie au texte allemand : rien n'est à croire sur parole.
"""
import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import agents          # noqa: E402
from core.corpus import Corpus   # noqa: E402


def humain(dossier):
    c = dossier["corpus"]
    print("CORPUS : %d œuvres · %d atomes · %d qualifiés · %d à confirmer"
          % (c["oeuvres"], c["atomes"], c["qualifies"], c["a_confirmer"]))
    if dossier["concept"]:
        print("CONCEPT : %s" % dossier["concept"])
    for nom, r in dossier["resultats"].items():
        print("\n" + "=" * 78)
        print("AGENT « %s » — %s" % (nom, r["question"]))
        if r.get("statut") == "a_confirmer":
            print("  ⚠ résultats À CONFIRMER — pistes de lecture, pas des faits établis")
        _rendre(nom, r)
    for nom, err in dossier["erreurs"].items():
        print("\n⚠ agent « %s » en échec : %s" % (nom, err))


def _rendre(nom, r):
    if nom == "profil":
        for p in r["profils"].values():
            print("\n  %s (%d atomes)" % (p["titre"], p["atomes"]))
            print("    ce qui la DISTINGUE : %s" % (p.get("signature") or "—"))
            print("    concepts dominants  : %s"
                  % ", ".join("%s(%d)" % kv for kv in list(p["concepts_dominants"].items())[:6]))
    elif nom == "cooccurrence":
        print("  Concepts que Freud pense ensemble (Jaccard, seuil n≥%d) :" % r["seuil_minimum"])
        for l in r["liens"][:15]:
            print("    %-18s + %-18s  %.3f   (n=%d)"
                  % (l["concepts"][0], l["concepts"][1], l["jaccard"], l["ensemble"]))
        print("  %s" % r["note"])
    elif nom == "concept":
        if not r.get("atomes"):
            print("  %s" % r.get("note", "aucun atome"))
            return
        print("  %d atomes · par œuvre %s" % (r["atomes"], r["par_oeuvre"]))
        print("  statuts %s" % r["par_statut"])
        if r["sous_concepts"]:
            print("  sous-concepts %s" % r["sous_concepts"])
        for cit in r["citations"][:3]:
            print("\n    « %s »" % " ".join(cit["texte"].split())[:190])
            print("      → %s · %s" % (cit["oeuvre"], cit["chapitre"] or "—"))
    elif nom == "chronologie":
        for e in r["etapes"]:
            print("    %-34s %d (éd. %d, ±%d ans) : %4d atomes = %d‰"
                  % (e["oeuvre"][:34], e["annee_oeuvre"], e["annee_edition"],
                     e["incertitude_annees"], e["atomes_du_concept"], e["pour_mille"]))
        print("\n  RÉSERVE : %s" % r["reserve"])
    elif nom == "tension":
        for c in r["candidats"][:5]:
            print("\n    concept « %s » — %d affirmations sans négation, %d avec%s"
                  % (c["concept"], c["affirmes_sans_negation"], c["affirmes_avec_negation"],
                     " (même œuvre)" if c["meme_oeuvre"] else ""))
            for cit in c["paire"]:
                print("      · %s" % " ".join(cit["texte"].split())[:150])
        print("\n  %s" % r["note"])
    elif nom == "signaux":
        print("  %d passages à vérifier · %s" % (r["total"], r["par_signal"]))
        for p in r["passages"][:6]:
            print("    [%s] %s" % (",".join(p["signaux"]), " ".join(p["texte"].split())[:140]))
        print("\n  %s" % r["note"])


def main():
    ap = argparse.ArgumentParser(description="Analyse déterministe du corpus freudien.")
    ap.add_argument("concept", nargs="?", help="concept à instruire (ex. trieb, traum, angst)")
    ap.add_argument("--agent", help="n'exécuter qu'un agent : %s" % ", ".join(agents.AGENTS))
    ap.add_argument("--oeuvres", nargs="*", help="restreindre le corpus à ces œuvres")
    ap.add_argument("--json", action="store_true", help="sortie JSON brute")
    a = ap.parse_args()

    corpus = Corpus(a.oeuvres or None)
    if a.agent:
        if a.agent not in agents.AGENTS:
            ap.error("agent inconnu « %s » (connus : %s)" % (a.agent, ", ".join(agents.AGENTS)))
        r = agents.AGENTS[a.agent].executer(corpus, concept=a.concept)
        dossier = {"corpus": corpus.resume(), "plan": [a.agent], "concept": a.concept,
                   "resultats": {a.agent: r}, "erreurs": {}}
    else:
        dossier = agents.orchestrer(corpus, a.concept)

    if a.json:
        print(json.dumps(dossier, ensure_ascii=False, indent=1))
    else:
        humain(dossier)


if __name__ == "__main__":
    main()
