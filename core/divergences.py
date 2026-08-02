#!/usr/bin/env python3
"""CANDIDATS DE DIVERGENCE — où chercher, jamais ce qu'il faut y trouver.

CE MODULE N'EST PAS UN QUATRIÈME DÉTECTEUR AUTOMATIQUE. Trois l'ont précédé sur ce terrain précis
et ont tous échoué, mesurés : `ecart_freud` (marqueur lexical de première personne — 0 confirmé
sur 5, les cinq étaient des renvois d'accord), l'appariement de concepts par voisinage (1 confirmé
sur 16 — voir `documentation/APPARIEMENT_ECARTE.md`), la signature lexicale inter-auteurs de
`core/branches.py` (0 sur 35 après contrôle du lexicographe et de la taille de corpus). Un point
commun aux trois : chacun prétendait qu'un CALCUL puisse trancher la NATURE d'un rapport. Ce
module ne le prétend pas — il ne rend aucun verdict, seulement une liste d'endroits où LIRE,
exactement comme le seuil de contenance 0,30 pour les reprises ou le nom trouvé pour les
mentions : un repère, jamais un jugement.

LA RECETTE, ET D'OÙ ELLE VIENT. Les quatre oppositions déjà documentées à la main dans
`documentation/COMPARAISON_INTER_AUTEURS.md` §4 (rupture de Rank 1924, Freud contre Le Bon,
non-rupture d'Abraham, convergence Ferenczi/Rank 1924) partagent toutes DEUX INGRÉDIENTS :
  1. un lien VÉRIFIÉ entre les deux auteurs sur CE concept précis — un acte de citation confirmé,
     une mention confirmée : la preuve que l'un a réellement lu l'autre sur ce point, pas
     seulement qu'ils emploient le même mot ;
  2. une TRAJECTOIRE RÉELLE chez l'un des deux — un vocabulaire qui apparaît ou disparaît dans son
     œuvre (`core/branches.trajectoire`), jamais un simple contraste de fréquence entre auteurs
     (c'est exactement ce que la signature lexicale a mesuré et n'a jamais tenu).
Personne n'avait systématisé ce croisement avant ce module — les quatre cas connus avaient été
trouvés à la main, par lecture large du corpus. `candidats()` le fait mécaniquement, et c'est tout
ce qu'il fait : il ne remplace pas la lecture qui a produit ces quatre cas, il en généralise le
POINT DE DÉPART.

Le premier ingrédient couvre les actes de citation et les mentions, PAS les « lectures déclarées »
(un chapitre qui annonce dans son titre traiter d'un autre auteur, table `lectures_declarees`,
gardée séparée dans `bin/exporter_d1.py`) — or c'est précisément ce troisième type de lien qui
fait le cas Freud contre Le Bon (§4.2 : « une lecture déclarée… le seul qu'une reprise de mots ne
pourrait pas trouver »). `touches` (ci-dessous) n'interroge donc que deux des trois types de lien
établis par le projet ; en pratique Le Bon apparaît quand même dans quelques `lie_a` via le canal
« mention », mais le mécanisme reste aveugle à un lien qui ne se déclare que par le canal
« lecture déclarée » seul.

`touches` (le premier ingrédient) N'EST PAS CALCULÉ ICI : il vit déjà dans D1 (`carte_actes` pour
les actes confirmés, `mentions` pour les mentions confirmées), et `bin/generer_candidats_divergences.py`
le lit directement — le recalculer en Python aurait recréé une troisième source de vérité pour un
fait déjà établi, exactement ce que `carte.liens_juges` évite déjà en étant partagé entre
`bin/exporter_d1.py` et `bin/generer_socle.py`.

SONDÉ AVANT D'ÉCRIRE LA MOINDRE LIGNE DE CAMPAGNE DE LECTURE, avec un dédoublonnage encore fondé
sur le NOM : ce croisement donnait 76 candidats — ni zéro (un quatrième échec à documenter), ni des
centaines (un critère trop lâche pour être lu sérieusement). Et il retrouvait, sans qu'on les lui
ait donnés, des faits historiques réels : le grand article d'Abraham sur les stades du
développement de la libido (1924) en ressortait avec plusieurs concepts qui « apparaissent »
exactement dans ce texte-là. C'est ce contrôle qui a autorisé à investir dans la lecture — le même
genre de contrôle que la validation « oedipus » a fourni à `densite_comparee` avant qu'elle ne
serve à quoi que ce soit.

LE CHIFFRE RÉEL, PRODUIT PAR `bin/generer_candidats_divergences.py` avec le dédoublonnage sur la
VALEUR décrit plus bas, est **98** (55 apparitions, 43 disparitions). L'écart avec le sondage
(76) n'est pas une erreur : le sondage dédoublonnait par NOM de concept, qui fusionnait à tort des
candidats au nom identique mais à la trajectoire réellement différente — exactement le défaut que
le dédoublonnage par valeur corrige (voir `test_deux_concepts_qui_se_ressemblent_mais_diffèrent_
vraiment_restent_distincts`). Le chiffre juste est donc le plus élevé des deux, et c'est celui que
la campagne de lecture a effectivement reçu.

LA CAMPAGNE DE LECTURE EST FAITE — voir `documentation/COMPARAISON_INTER_AUTEURS.md` § 7. Les 98
candidats ont été lus deux fois chacun (un lecteur, puis un second qui ne voit que les mêmes pièces,
jamais le jugement du premier). Résultat : 85 lectures confirmées par les deux passages. Sur ces 85,
**une seule montre un désaccord nommé et textuellement confirmé** — Stekel contestant Ferenczi sur
la nosologie de l'homosexualité masculine, ajouté au § 4 comme cinquième opposition (§4.5), la
première trouvée par ce mécanisme plutôt que par une lecture large. Les 84 autres montrent des
convergences documentées (citation à l'appui) ou des liens réels mais topiquement étrangers au
concept mesuré — jamais d'opposition. C'est un QUATRIÈME résultat qui nuance, sans le contredire,
le zéro des trois échecs cités plus haut : obtenu par un mécanisme systématique plutôt que par une
lecture large, il montre que la divergence intellectuelle laisse RAREMENT ce genre de trace
lexicale (1 candidat sur 98, un taux comparable au 1 sur 16 de l'appariement) — mais pas jamais.
"""
import collections
import re

DIVERGENCES_VERSION = "1.0.0"


def candidats(trajectoires_par_auteur, touches):
    """Croise trajectoires et liens vérifiés → liste de candidats à LIRE, triés par concentration.

    `trajectoires_par_auteur` : {auteur: [(sous_concept, trajectoire), …]} — `trajectoire` est le
        dict rendu par `branches.trajectoire()` pour ce (auteur, sous_concept).
    `touches` : {(auteur, sous_concept): {autres_auteurs liés}} — construit à partir des actes de
        citation CONFIRMÉS et des mentions CONFIRMÉES touchant ce concept (voir docstring du
        module : c'est le premier des deux ingrédients).

    Ne retient QUE les trajectoires « apparait » ou « disparait » — jamais « constant » (rien ne
    bouge, rien à lire) ni « livre_unique » seul (le vocabulaire d'un livre, sans direction : voir
    `branches.trajectoire`, qui distingue déjà ce cas d'une vraie apparition ou disparition selon
    la POSITION de l'œuvre dominante dans la série).

    Chaque candidat porte AVEC QUOI il est lié — le lecteur doit savoir, avant d'ouvrir le texte,
    quels auteurs ont un rapport vérifié avec celui dont la trajectoire bouge. Rien de plus : ni
    verdict, ni direction du rapport, ni nature.
    """
    out = []
    for auteur, paires in trajectoires_par_auteur.items():
        for sous, traj in paires:
            if traj is None or traj["classe"] not in ("apparait", "disparait"):
                continue
            lies = touches.get((auteur, sous))
            if not lies:
                continue
            out.append({
                "auteur": auteur, "concept": sous, "classe": traj["classe"],
                "lie_a": sorted(lies),
                "oeuvre_dominante": traj["oeuvre_dominante"],
                "annee_dominante": traj["annee_dominante"],
                "part_dominante": traj["part_dominante"],
                "pour_mille_avant": traj["pour_mille_avant"],
                "pour_mille_apres": traj["pour_mille_apres"],
                "occurrences": traj["occurrences"],
            })
    # DÉDOUBLONNAGE SUR LA VALEUR, PAS SUR LE NOM — même discipline que `branches.dedoublonner`,
    # avec la même clé (auteur, œuvre dominante, part dominante, pour-mille avant/après,
    # OCCURRENCES — ce dernier champ, un entier non arrondi, écarte les collisions par coïncidence
    # d'arrondi que les champs en pour-mille, arrondis, laisseraient sinon passer) PLUS `classe`,
    # gardée par prudence : rien ne garantit formellement que deux trajectoires partageant tout le
    # reste partagent aussi leur classe. La raison mesurée reste celle de `branches.dedoublonner` :
    # « identifizier » et « identifizierung » sont deux CHAÎNES différentes qui retiennent les
    # mêmes phrases. Dédupliquer par (auteur, nom du concept) laisserait passer les deux comme
    # s'ils étaient deux candidats distincts, alors qu'ils décrivent la même trajectoire.
    vus, uniques = set(), []
    for c in sorted(out, key=lambda x: (x["auteur"], len(x["concept"]), x["concept"])):
        cle = (c["auteur"], c["classe"], c["oeuvre_dominante"], c["part_dominante"],
               c["pour_mille_avant"], c["pour_mille_apres"], c["occurrences"])
        if cle in vus:
            continue
        vus.add(cle)
        uniques.append(c)
    uniques.sort(key=lambda x: -x["part_dominante"])
    return uniques


def resume(liste):
    """Combien de candidats, par classe et par auteur — avant même d'en lire un seul."""
    return {
        "total": len(liste),
        "par_classe": dict(collections.Counter(c["classe"] for c in liste)),
        "par_auteur": dict(collections.Counter(c["auteur"] for c in liste)),
    }


def reserve():
    """Ce qu'un candidat n'est pas — porté avec la liste, jamais séparé d'elle."""
    return (
        "Cette liste ne contient AUCUN verdict de divergence — seulement des endroits où un "
        "vocabulaire bouge réellement chez un auteur (apparaît ou disparaît, jamais un simple "
        "contraste de fréquence entre auteurs, méthode déjà mesurée et écartée) ALORS QU'un lien "
        "vérifié le rattache à un autre auteur sur ce même concept. Un candidat peut se lire, "
        "après lecture, comme une divergence réelle, une convergence, un développement "
        "indépendant, ou un artefact — les quatre se sont produits dans les cas déjà connus de ce "
        "corpus. La lecture tranche ; cette liste ne fait que désigner où regarder, exactement "
        "comme un seuil de contenance désigne une reprise à vérifier sans en préjuger le "
        "verdict. Une réserve supplémentaire, propre à `annee_dominante` et `classe` : ces deux "
        "champs viennent de `branches.trajectoire()`, dont la datation peut reposer sur une "
        "fenêtre d'édition peu fiable (une réédition sans mention des ajouts, par exemple) — un "
        "risque que `branches.py` documente sans le porter jusqu'ici, faute d'un signal de "
        "fiabilité dans le dict qu'il renvoie. Une année dominante inattendue mérite donc d'être "
        "vérifiée à la lecture, pas seulement prise au mot."
    )
