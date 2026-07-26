#!/usr/bin/env python3
"""GÉNÈRE documentation/COURANTS_FREUD.md — le dossier de référence des grappes.

  python bin/generer_courants.py

POURQUOI CE SCRIPT EXISTE. Ce document a été tenu à la main jusqu'à l'audit 4 du lexique
(2026-07), qui a fait bouger la partition : ses huit dossiers décrivaient alors des grappes qui
n'existaient plus, sans que rien ne le signale. Un document qui décrit des données CALCULÉES ne
peut pas rester juste s'il est écrit à la main — il dérive au premier changement du lexique.

Le partage est donc net :
  • les CHIFFRES et les CITATIONS viennent de l'agent `courants` et du corpus, à chaque
    exécution — ils ne peuvent pas être faux, seulement à jour ou à régénérer ;
  • la PROSE éditoriale (nom, description, réserve de chaque grappe) vient d'une seule source,
    `bin/exporter_d1.py:EDITORIAL_GRAPPES`, la même qui alimente le site. Il n'y a donc jamais
    deux versions du commentaire d'une grappe.

Si la partition bouge, `nommer_grappes()` fait échouer ce script comme il fait échouer
l'export : on est prévenu, on reprend l'éditorial, on régénère. Jamais de dérive silencieuse.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import agents, sources          # noqa: E402
from core.corpus import Corpus            # noqa: E402
from exporter_d1 import nommer_grappes    # noqa: E402

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SORTIE = os.path.join(RACINE, "documentation", "COURANTS_FREUD.md")

EN_TETE = """# Les courants internes du corpus freudien — dossiers de référence par grappe

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_courants.py` — ne pas éditer à la main : les
> chiffres et les citations viennent du corpus à chaque exécution, la prose éditoriale de
> `bin/exporter_d1.py:EDITORIAL_GRAPPES` (la même source que le site). Régénérer après toute
> modification du lexique.
>
> **Ce que ce document est.** Le dossier de chacune des grappes que l'agent `courants` découpe
> dans le graphe de cooccurrence des concepts (modularité {modularite} sur {relies} concepts
> reliés — le seuil de structure réelle est généralement fixé à 0,30). Chaque dossier donne :
> les concepts membres, le profil chronologique par œuvre, la part **datée avec certitude**
> quand la collation le permet, une citation choisie par l'agent lui-même, et la réserve qui
> limite l'interprétation.
>
> **Ce que ce document n'est pas.** Une classification que Freud revendiquerait. Une grappe est
> un fait de cooccurrence — jamais opposable seul.
>
> Les densités sont en ‰ des atomes de l'œuvre (auteur : Sigmund Freud seul — l'appendice
> d'Otto Rank fausserait la mesure de ce que FREUD pense ensemble). Pour les œuvres
> collationnées, `origine` donne la densité recalculée sur les seuls passages retrouvés dans la
> première édition — la seule comparable d'une œuvre à l'autre sans réserve d'édition.

---
"""

PIED = """
## Ce que les dossiers disent ensemble

1. **Les grappes ne sont pas données d'avance** : leur nombre, leur taille et leur composition
   sont mesurés, et ils BOUGENT quand l'ontologie s'affine. L'audit 4 du lexique (2026-07) a
   recomposé la partition en profondeur — la clinique s'est détachée en grappe propre, la
   différence des sexes a rejoint le roman familial, la seconde topique a cessé d'être isolée.
   Une grappe est donc un état de la mesure, pas une vérité sur Freud.
2. **Certaines grappes sont des faits de corpus autant que de pensée** : la peinture est portée
   par trois analyses d'œuvres, la masse par un seul livre. Le dire est la condition pour
   comparer un jour ces grappes à celles d'un autre auteur sans sur-interpréter.
3. **Les grappes bougent aussi dans le temps** — la mort migre de la famille vers la pulsion, le
   rêve cesse d'absorber la métapsychologie (voir `SYNTHESE_FREUD.md` §3, avec le contrôle qui
   exclut les ajouts datés par collation).

*Reproduire : `python bin/analyser.py --agent courants` · citations : `python
bin/rechercher.py --concept <nom>` · méthode et limites : `INVENTAIRE_ATOMES.md` §4.*
"""


def dossier_grappe(rang, g, edito, corpus):
    nom, description, reserve = edito
    membres = set(g["concepts"])
    lignes = ["## %d. %s — %d concepts, %s atomes\n" % (
        rang, nom, g["taille"], format(g["atomes_concernes"], ",").replace(",", " "))]
    lignes.append("*" + ", ".join(sorted(membres)) + ".*\n")
    if description:
        lignes.append(description + "\n")

    # Densité par œuvre — restreinte à Freud, comme l'agent restreint son propre calcul.
    rangs = []
    for cle, meta in sorted(corpus.oeuvres.items(), key=lambda x: x[1]["annee_oeuvre"]):
        atomes = [a for a in corpus.par_oeuvre(cle)
                  if a.get("auteur", "Sigmund Freud") == "Sigmund Freud"]
        if not atomes:
            continue
        porteurs = [a for a in atomes if {c["concept"] for c in a["concepts"]} & membres]
        base = [a for a in atomes if a["attestation"].get("couche") == "origine"]
        dorig = [a for a in porteurs if a["attestation"].get("couche") == "origine"]
        rangs.append((round(1000 * len(porteurs) / len(atomes)),
                      round(1000 * len(dorig) / len(base)) if base else None,
                      sources.OEUVRES[cle]["titre"], meta["annee_oeuvre"]))
    rangs.sort(reverse=True, key=lambda x: x[0])

    lignes.append("| Œuvre | Densité | Dont d'origine |")
    lignes.append("|---|---:|---:|")
    for dens, orig, titre, annee in rangs[:6]:
        lignes.append("| *%s* (%d) | %d ‰ | %s |" % (
            titre if len(titre) < 46 else titre[:44] + "…", annee, dens,
            "%d ‰" % orig if orig is not None else "—"))
    lignes.append("")

    if g.get("citation"):
        c = corpus.citer(g["citation"]) if isinstance(g["citation"], dict) and "texte" not in g["citation"] else g["citation"]
        texte = " ".join(str(c["texte"]).split())
        lignes.append("Citation choisie par l'agent — le passage qui croise le plus de concepts de "
                      "la grappe, à la longueur la plus proche d'une thèse théorique :\n")
        lignes.append("> « %s »" % (texte[:400] + "…" if len(texte) > 400 else texte))
        lignes.append("> — *%s*, %s\n" % (c["oeuvre"], c["datation"]))

    if reserve:
        lignes.append("**Réserve.** " + reserve + "\n")
    lignes.append("---\n")
    return "\n".join(lignes)


def main():
    corpus = Corpus()
    r = agents.AGENTS["courants"].executer(corpus)
    editorial = nommer_grappes(r["grappes"])      # échoue si la partition a glissé

    parts = [EN_TETE.format(modularite=("%.3f" % r["modularite"]).replace(".", ","),
                            relies=r["concepts_relies"])]
    for rang, g in enumerate(r["grappes"], 1):
        parts.append(dossier_grappe(rang, g, editorial[rang], corpus))
    parts.append(PIED)

    with open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("→ %s (%d grappes, modularité %.3f)" % (SORTIE, len(r["grappes"]), r["modularite"]))


if __name__ == "__main__":
    main()
