#!/usr/bin/env python3
"""GÉNÈRE documentation/TRADUCTION.md — ce qu'un mot français doit porter, mesuré.

    python bin/generer_traduction.py

POURQUOI CE SCRIPT EXISTE. Un tableau de correspondances allemand↔français tenu à la main est
exactement le genre de document qui devient faux sans qu'on le voie : les comptes de formes
changent à chaque œuvre ajoutée, et un faux ami non mesuré se lit comme une précaution de style
plutôt que comme un fait. Ici les deux chiffres qui portent tout — la CHARGE (combien de formes
allemandes un mot français doit couvrir) et la CONTAMINATION (ce qu'une recherche par radical
ramasse en trop) — sont recalculés à chaque exécution.

Le partage :
  • les CHIFFRES viennent du corpus ;
  • le rendu français COURANT et les notes viennent de `core/traduction.TERMES`, et ils sont
    déclarés EXTÉRIEURS au corpus — le corpus ne peut ni les valider ni les infirmer.
"""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import comparaison, traduction        # noqa: E402
from core.corpus import Corpus                  # noqa: E402
from generer_socle import _nombre, _virgule     # noqa: E402

SORTIE = os.path.join(RACINE, "documentation", "TRADUCTION.md")

EN_TETE = """# Traduire depuis l'allemand — ce qu'un seul mot français doit porter

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_traduction.py` — ne pas éditer à la main : la charge
> et la contamination sont recalculées sur le corpus à chaque exécution. Régénérer après tout
> ajout d'œuvre.
>
> **Ce que ce document est.** Pour chaque terme canonique allemand, la mesure de ce qu'un mot
> français unique doit couvrir : le nombre de formes distinctes de la famille, la part qui vit
> à l'intérieur d'un composé, et les faux amis que le radical attrape.
>
> **{verdict}**
>
> **Ce que ce document n'est PAS, et c'est le point le plus important.** Il ne juge aucune
> traduction. Décider que « pulsion » rend bien *Trieb* demande une compétence de traducteur et
> une histoire des traductions ; ce corpus n'a ni l'une ni l'autre. La colonne **français
> courant** est une donnée EXTÉRIEURE, donnée pour être confrontée, jamais validée.
>
> **Le corpus n'a qu'une ancre bilingue** : Gustave Le Bon, {atomes_fr} atomes, 1895 — et il n'est
> pas psychanalyste. Le seul énoncé solide qu'on puisse en tirer sur une traduction est un
> **refus** de correspondance, pas une validation. Ils sont en §3.

---
"""


def section_charge(familles):
    L = ["## 1. La charge de traduction — l'allemand compose, le français juxtapose\n"]
    L.append("Un terme canonique n'apparaît presque jamais seul. La **charge** est le nombre de "
             "formes allemandes distinctes qu'il faut couvrir pour atteindre %s %% des "
             "occurrences : c'est ce qu'un mot français unique doit porter.\n"
             % _virgule(100 * traduction.COUVERTURE_CIBLE, 0))
    L.append("| Terme | Français courant | Formes | Occurrences | **Charge** | Radical interne |")
    L.append("|---|---|---:|---:|---:|---:|")
    for f in sorted(familles, key=lambda f: -f["charge"]):
        # Un radical déclaré inutilisable garde sa ligne — l'effacer cacherait le cas le plus
        # instructif — mais sa charge est marquée comme non interprétable.
        L.append("| *%s*%s | %s | %s | %s | %s | %s %% |"
                 % (f["allemand"], "" if f["radical_utilisable"] else " ⚠",
                    f["francais_courant"], _nombre(f["formes"]),
                    _nombre(f["occurrences"]),
                    "**%d**" % f["charge"] if f["radical_utilisable"] else "(%d)" % f["charge"],
                    _virgule(100 * (f["part_interne"] or 0), 0)))
    L.append("")
    L.append("⚠ *Radical déclaré inutilisable : la charge entre parenthèses mesure l'échec de la "
             "recherche par radical, pas le terme. Voir §2.*")
    L.append("")
    L.append("**Les deux extrêmes disent la même chose sous deux formes.** *Verdrängung* est le "
             "terme le plus propre du corpus — le radical ouvre presque toujours le mot, la "
             "famille est courte, et « refoulement » tient sans réserve. *Besetzung* est "
             "l'inverse : plus de la moitié de ses occurrences sont dans un composé "
             "(Objektbesetzung, Gegenbesetzung, Überbesetzung), et le mot français doit survivre "
             "à la composition — ce qu'il fait mal.\n")
    return "\n".join(L)


def section_faux_amis(familles):
    L = ["## 2. Les faux amis — mesurés, déclarés, jamais devinés\n"]
    L.append("Chercher un terme par son radical attrape des mots qui n'ont rien à voir. C'est le "
             "défaut que le lexique du projet a déjà payé : `\\bschwan` attrapait **`schwanger`** "
             "— enceinte — 65 fois chez l'auteur dont la thèse centrale est la naissance, soit "
             "28 % de captures fausses. Les faux amis sont donc DÉCLARÉS et comptés.\n")
    L.append("| Terme | Ce que le radical attrape en trop | Occurrences | Contamination |")
    L.append("|---|---|---:|---:|")
    for f in sorted(familles, key=lambda f: -(f["contamination"] or 0)):
        if not f["faux_amis"] or not f["radical_utilisable"]:
            continue
        L.append("| *%s* | %s | %s | **%s %%** |"
                 % (f["allemand"],
                    ", ".join("`%s`" % m for m, _ in f["faux_amis"][:4]),
                    _nombre(f["occurrences_faux_amis"]),
                    _virgule(100 * f["contamination"])))
    L.append("")
    propres = [f for f in familles if not f["faux_amis"]]
    if propres:
        L.append("Deux termes n'ont **aucun** faux ami mesuré : %s. Quand un terme se comporte "
                 "ainsi, la charge de traduction est celle de la composition seule.\n"
                 % ", ".join("*%s*" % f["allemand"] for f in propres))
    L.append("### Le cas qui montre la limite de la méthode\n")
    ich = next((f for f in familles if f["id"] == "ich"), None)
    if ich:
        L.append("Le radical `ich` est **inutilisable**, et il est le seul du tableau à être "
                 "déclaré tel. Douze faux amis suffisent à en écarter **%s %%** — `sich`, "
                 "`nicht`, `mich`, `nichts`, `vielleicht` — et il en resterait des centaines : "
                 "ce chiffre est un plancher, pas un total. C'est pourquoi il ne figure dans "
                 "aucun classement de ce document : il mesurerait l'échec de la recherche par "
                 "radical, pas le terme *Ich*.\n" % _virgule(100 * ich["contamination"]))
        L.append("Le lexique du projet ne s'y risque pas — `lexique._RE_ICH_MOI` cherche "
                 "« das Ich », « Ich-Ideal », « Ichs », « des Ichs », jamais le radical nu. "
                 "Certains termes ne se cherchent pas par leur radical du tout, et aucune mesure "
                 "de charge ne le dirait : il faut le savoir avant de mesurer.\n")
    return "\n".join(L)


def section_notes(familles):
    L = ["## 3. Terme par terme — et les refus\n"]
    for f in sorted(familles, key=lambda f: f["allemand"]):
        L.append("### *%s* → « %s »\n" % (f["allemand"], f["francais_courant"]))
        L.append("%s formes, %s occurrences, charge **%d**. Formes principales : %s.\n"
                 % (_nombre(f["formes"]), _nombre(f["occurrences"]), f["charge"],
                    ", ".join("`%s` (%s)" % (m, _nombre(n)) for m, n in f["principales"][:8])))
        if f["internes_principales"]:
            L.append("Composés où le radical n'ouvre pas le mot : %s.\n"
                     % ", ".join("`%s` (%s)" % (m, _nombre(n))
                                 for m, n in f["internes_principales"][:6]))
        L.append("**Note.** %s\n" % f["note"])
    L.append("### Les correspondances REFUSÉES\n")
    L.append("Un refus argumenté est le seul énoncé qu'un corpus de 1 485 atomes français puisse "
             "produire sur une traduction — et il vaut mieux qu'une correspondance plausible. "
             "Ceux-ci vivent dans `lexique.MOTIFS_FR` et gouvernent réellement la mesure : le "
             "concept correspondant n'est pas mesuré sur le texte français, il reste non qualifié "
             "plutôt qu'approximé.\n")
    L.append("| Français | ≠ Allemand | Pourquoi |")
    L.append("|---|---|---|")
    for r in traduction.refus_documentes():
        L.append("| « %s » | *%s* | %s |" % (r["francais"], r["allemand"], r["motif"]))
    L.append("")
    return "\n".join(L)


def main(corpus=None):
    corpus = corpus or Corpus()          # partageable entre générateurs — voir `generer_socle`
    langues = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)
    allemands = [comparaison.replier_comparaison(a["texte"]) for a in corpus.atomes
                 if langues.get(a.get("auteur", "Sigmund Freud")) == "de"]
    atomes_fr = sum(1 for a in corpus.atomes
                    if langues.get(a.get("auteur", "Sigmund Freud")) == "fr")

    vocab = traduction.vocabulaire(allemands)
    familles = traduction.familles(vocab)

    # LES SUPERLATIFS EXCLUENT LES RADICAUX DÉCLARÉS INUTILISABLES. `Ich` sort en tête de tous les
    # classements — 902 de charge, 40 % de contamination — mais ces deux chiffres mesurent l'échec
    # du radical, pas le terme : la liste de ses faux amis en écarte douze là où il y en a des
    # centaines. Le prendre comme exemple de tête ferait passer un artefact de méthode pour le
    # résultat principal du document. Il a sa section, en §2, où il dit ce qu'il dit vraiment.
    mesurables = [f for f in familles if f["radical_utilisable"]]
    pire = max(mesurables, key=lambda f: f["contamination"] or 0)
    lourd = max(mesurables, key=lambda f: f["charge"])
    inutilisables = [f for f in familles if not f["radical_utilisable"]]
    verdict = ("RÉSULTAT À LIRE AVANT LES TABLEAUX. Aucun de ces mots n'est un mot : *%s* demande "
               "**%d formes allemandes distinctes** pour couvrir %s %% de ses emplois, et une "
               "recherche par radical sur *%s* ramasse **%s %% de faux amis** — c'est-à-dire du "
               "texte qui n'a rien à voir avec le terme. Traduire par un mot unique est une "
               "décision, pas une évidence. %s"
               % (lourd["allemand"], lourd["charge"],
                  _virgule(100 * traduction.COUVERTURE_CIBLE, 0),
                  pire["allemand"], _virgule(100 * pire["contamination"]),
                  ("Un terme est pire encore et ne figure dans aucun de ces deux classements : "
                   "%s, dont le radical est déclaré INUTILISABLE — ses chiffres mesureraient "
                   "l'échec de la méthode, pas le mot. Voir §2."
                   % ", ".join("*%s*" % f["allemand"] for f in inutilisables))
                  if inutilisables else ""))

    parts = [EN_TETE.format(verdict=verdict, atomes_fr=_nombre(atomes_fr)),
             section_charge(familles), "---\n",
             section_faux_amis(familles), "---\n",
             section_notes(familles), "---\n",
             "## 4. Ce que ce document ne dit pas\n",
             traduction.reserve() + "\n",
             "*Reproduire : `python bin/generer_traduction.py` · la table des motifs français : "
             "`core/lexique.py:MOTIFS_FR` · l'usage comparé des mots : `SOCLE_COMMUN.md` §2.*\n"]

    with open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("→ %s (%d termes, charge max %d sur %s, contamination max %s %% sur %s)"
          % (SORTIE, len(familles), lourd["charge"], lourd["allemand"],
             _virgule(100 * pire["contamination"]), pire["allemand"]))


if __name__ == "__main__":
    main()
