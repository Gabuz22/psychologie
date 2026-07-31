#!/usr/bin/env python3
"""LEXIQUES — un jeu de catégories PAR AUTEUR, construit indépendamment des autres.

RÈGLE FONDATRICE, ET RENVERSEMENT ASSUMÉ D'UNE RÈGLE ANTÉRIEURE.

Le projet a d'abord posé l'inverse : un jeu de concepts COMMUN, au motif qu'on ne peut comparer
deux auteurs qu'à travers la même grille, sans quoi « on ne mesurerait que la différence des
grilles de lecture ». L'objection est réelle, mais elle a un coût que la pratique a rendu
visible : mesurer Rank avec le vocabulaire de Freud, c'est ne voir de Rank que ce qui ressemble
à Freud. Son motif central — l'ENFANT EXPOSÉ, sauvé des eaux, qui revient tuer son père — n'a
aucune case chez Freud, et resterait donc invisible dans le corpus.

La règle est donc : **chaque auteur a ses catégories propres, et se travaille séparément.** Les
rapprochements entre auteurs — socles partagés, divergences, approfondissements, contradictions
— feront l'objet d'une couche EXPLICITE posée par-dessus des graphes construits séparément, avec
des forces de liaison déclarées. Ils ne doivent jamais être un effet de bord du lexique, où ils
seraient invérifiables et indissociables du travail de description.

Conséquence pratique à ne pas perdre : deux auteurs peuvent porter le même NOM de concept sans
désigner la même chose. `geburt` chez Rank est le traumatisme fondateur de toute angoisse ; le
même mot chez Freud n'est qu'un fait biologique parmi d'autres. Aucun code ne doit additionner
deux concepts sous prétexte qu'ils s'écrivent pareil.

CE QU'UN MODULE D'AUTEUR DOIT EXPOSER :
    LANGUE            "de" | "fr"
    CONCEPTS          {groupe: {"label": …, "termes": {concept: [motifs]}}}
    FONCTIONS         [{id, label, aide, marqueurs, fiabilite?}]
    MARQUEURS_STATUT  {niveau: [motifs]}
    NOMS_AUTEURS      [noms cités par cet auteur — sert la fonction « rapport_tiers »]
Tous les motifs sont en forme REPLIÉE (minuscules, sans diacritiques, ß→ss).
"""
from . import abraham, ferenczi, le_bon, rank, stekel

# Freud n'a pas de module ici : ses tables sont restées dans `core/lexique.py`, où elles ont été
# écrites et où sept audits successifs les ont documentées ligne à ligne. Les déplacer n'ajouterait
# rien et ferait perdre l'historique de ces décisions. Le registre les récupère à l'usage
# (`lexique.pour_auteur`), de sorte que Freud est traité par le même chemin que les autres.
PAR_AUTEUR = {
    "Gustave Le Bon": le_bon,
    "Karl Abraham": abraham,
    "Otto Rank": rank,
    "Sándor Ferenczi": ferenczi,
    "Wilhelm Stekel": stekel,
}


def connu(auteur):
    """Cet auteur a-t-il son propre lexique ? Sinon celui de Freud s'applique (voir lexique.py)."""
    return auteur in PAR_AUTEUR
