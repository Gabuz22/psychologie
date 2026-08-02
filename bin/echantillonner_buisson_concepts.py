#!/usr/bin/env python3
"""ÉCHANTILLONNE le buisson des concepts pour une lecture de plausibilité, un auteur à la fois.

  python bin/echantillonner_buisson_concepts.py

Avant de publier `concept_liens` pour un auteur, on doit pouvoir lire quelques-unes de ses
paires les plus fortes et reconnaître un lien réel, pas un artefact du seuil ou du lexique — la
même discipline que la lecture qui a validé `socle_par_couple` avant son export. Ce script reste
dans bin/ pour être rejoué après tout audit de lexique, exactement comme `generer_courants.py`.

Imprime, pour chaque auteur qui n'est pas Freud (déjà lu à la main pendant la Phase A), les 5
paires de plus fort poids avec UNE citation chacune — un atome qui porte les deux concepts à la
fois, choisi comme dans AgentCourants._decrire_grappe (prose théorique, ni vers, ni trop long).
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import agents, lexiques         # noqa: E402
from core.agents import _est_vers, _ecart_longueur_ideale   # noqa: E402
from core.corpus import Corpus            # noqa: E402

MINIMUM_BRUT = 8
SOMMET = 5


def citation_pour(atomes, x, y):
    croises = [a for a in atomes
               if {c["concept"] for c in a["concepts"]} >= {x, y}
               and a["statut"] == "affirme" and not _est_vers(a["texte"])]
    return min(croises, key=_ecart_longueur_ideale) if croises else None


def main():
    corpus = Corpus()
    auteurs = sorted(lexiques.AUTEURS_AVEC_LEXIQUE_PROPRE - {"Sigmund Freud"})
    for nom_auteur in auteurs:
        atomes = [a for a in corpus.atomes if a.get("auteur", "Sigmund Freud") == nom_auteur]
        r = agents.AGENTS["buisson_concepts"].executer(
            corpus, auteur=nom_auteur, minimum_brut=MINIMUM_BRUT)
        print("\n=== %s — %d atomes, %d liens au seuil %d ==="
              % (nom_auteur, len(atomes), len(r["liens"]), MINIMUM_BRUT))
        if not r["liens"]:
            print("  (aucun lien à ce seuil)")
            continue
        for lien in r["liens"][:SOMMET]:
            x, y = lien["concepts"]
            print("\n  %s <-> %s  (brut=%d, poids=%.4f)"
                  % (x, y, lien["occurrences_brutes"], lien["poids"]))
            citation = citation_pour(atomes, x, y)
            if citation:
                c = corpus.citer(citation)
                texte = " ".join(c["texte"].split())
                print("    « %s »" % (texte[:300] + "…" if len(texte) > 300 else texte))
                print("    — %s, %s" % (c["oeuvre"], c["datation"]))
            else:
                print("    (aucune citation croisée trouvée — atome porteur des deux, "
                      "mais ni affirmé ni en prose)")


if __name__ == "__main__":
    main()
