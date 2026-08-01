#!/usr/bin/env python3
"""ACCUEIL D'UN AUTEUR — ce qu'il faut déclarer pour qu'un huitième auteur entre sans rien casser.

CE MODULE N'EST PAS UNE INTENTION, C'EST UN CONTRÔLE. Le dépôt affirme depuis longtemps qu'ajouter
un auteur revient à « ajouter des concepts et des groupes, sans toucher au moteur ». L'affirmation
a été vérifiée ici plutôt que répétée, et elle tient — mais pas entièrement, et ce module dit où.

CE QU'ON A MESURÉ EN L'ÉCRIVANT.

  • UN SEUL branchement par auteur subsiste dans le code de production hors registres :
    `bin/generer_courants.py` restreint les grappes à Freud, et c'est délibéré et documenté.
    Aucune couche de comparaison, aucun export, aucune route ne teste un nom d'auteur.

  • QUARANTE occurrences de `atome.get("auteur", "Sigmund Freud")` dans vingt et un fichiers. Ce
    défaut n'est JAMAIS nécessaire : `atomisation` pose `auteur` sur chaque atome qu'il produit.
    Il ne peut donc se déclencher que si quelque chose est cassé — et il attribue alors
    silencieusement du texte à Freud. C'est exactement le mode de panne qui a rendu Ferenczi
    invisible pendant des semaines : entré avec 16,8 % des atomes, sans jeton de nom, aucun auteur
    ne pouvait être enregistré comme le nommant. D'où `auteur_de()`, qui échoue au lieu de deviner.

  • UNE EXCEPTION SILENCIEUSE à la règle fondatrice « chaque auteur a ses catégories propres » :
    Josef Breuer, 885 atomes, définit ZÉRO motif. Ses pages sont décrites avec le lexique de Freud,
    parce qu'elles sont imprimées dans un volume de Freud. C'est défendable, et c'est documenté
    dans `atomisation` — mais la conséquence ne l'était pas : plusieurs mesures deviennent vides
    de sens pour un tel auteur, et l'une d'elles l'était sans que personne le voie (voir
    `mesures_non_applicables`).

CE QUE LE CONTRAT NE PROMET PAS. Qu'un auteur entré selon ces règles soit COMPARABLE aux autres.
Il sera décrit, cité, daté, et ses reprises seront trouvées ; mais s'il écrit dans une autre
langue, la reprise textuelle est aveugle par construction, et s'il n'a pas de lexique propre, une
partie des mesures ne s'applique pas à lui. Le contrat garantit l'ACCUEIL, jamais la comparabilité.
"""
import collections

ACCUEIL_VERSION = "1.0.0"

# LES POINTS DE DÉCLARATION, dans l'ordre où on les remplit. Chacun a été payé au moins une fois :
# le jeton de nom par l'oubli de Ferenczi, la biographie par le courant de Stekel qu'il a fallu
# déclarer à part pour ne pas mêler deux doctrines dans les mesures.
POINTS = [
    {
        "cle": "oeuvres",
        "ou": "core/sources.py : OEUVRES",
        "obligatoire": True,
        "donne": "au moins une œuvre, avec sa langue, son édition lue et ses années",
        "sinon": "l'auteur n'existe pas — il n'a aucun atome",
    },
    {
        "cle": "jeton_de_nom",
        "ou": "core/comparaison.py : NOMS",
        "obligatoire": True,
        "donne": "les formes sous lesquelles son nom s'écrit, génitif et adjectif compris",
        # LE POINT LE PLUS COÛTEUX À OUBLIER, et il a été oublié. Sans jeton, la couche des
        # mentions ne peut enregistrer PERSONNE le nommant : l'auteur paraît isolé, et cet
        # isolement se lit comme un fait de texte alors que c'est un trou de configuration.
        "sinon": "aucun auteur ne peut être enregistré comme le nommant — il paraît isolé, et "
                 "ce silence se lit comme un fait de corpus (mesuré sur Ferenczi : 16,8 % des "
                 "atomes, 80 mentions invisibles)",
    },
    {
        "cle": "biographie",
        "ou": "bin/exporter_d1.py : AUTEURS",
        "obligatoire": True,
        "donne": "naissance, mort, et le COURANT sous lequel il est compté",
        "sinon": "l'export échoue à la clé manquante — panne bruyante, donc sans danger",
    },
    {
        "cle": "lexique",
        "ou": "core/lexiques/__init__.py : PAR_AUTEUR",
        # NON OBLIGATOIRE, ET C'EST LA SEULE CASE OÙ LE DÉFAUT EST SILENCIEUX. Un auteur sans
        # lexique est décrit avec celui de Freud. Le corpus en compte un — Breuer — et personne
        # n'avait mesuré ce que cela invalide.
        "obligatoire": False,
        "donne": "ses propres catégories : LANGUE, CONCEPTS, FONCTIONS, MARQUEURS_STATUT",
        "sinon": "il est décrit avec le lexique de Freud, donc on ne voit de lui que ce qui "
                 "ressemble à Freud — et plusieurs mesures cessent d'avoir un sens pour lui "
                 "(voir `mesures_non_applicables`)",
    },
    {
        "cle": "langue",
        # LE SEUL POINT QUI NE SE DÉCLARE PAS, et la distinction compte : il est DÉRIVÉ des
        # atomes. Le déclarer serait offrir un endroit où se tromper — une œuvre en français
        # rangée sous un auteur annoncé germanophone passerait sans bruit. Il n'y a rien à
        # écrire, mais il y a quelque chose à vérifier : que la langue soit RÉSOLUBLE.
        "derive": True,
        "ou": "core/comparaison.py : langues_par_auteur",
        "obligatoire": True,
        "donne": "rien à écrire — la langue vient des œuvres, mais elle doit être UNIQUE",
        "sinon": "un auteur à cheval sur deux langues rend None, et aucune densité n'est mesurée "
                 "sur lui : le silence vaut mieux qu'un zéro faux, mais il est alors déclaré",
    },
]


def auteur_de(atome):
    """L'auteur d'un atome — ÉCHOUE plutôt que de deviner.

    POURQUOI CETTE FONCTION EXISTE. Le dépôt écrit quarante fois `atome.get("auteur", "Sigmund
    Freud")`. Ce défaut n'est jamais nécessaire — `atomisation` pose `auteur` sur chaque atome
    qu'il produit — et il ne peut donc se déclencher que si quelque chose est cassé. Ce jour-là,
    il n'annonce rien : il attribue le texte à Freud, et la mesure fausse traverse toutes les
    couches sans un mot. Un auteur nouveau dont un chemin oublierait de poser le nom verrait ses
    pages comptées comme freudiennes.

    Une panne bruyante vaut mieux qu'une attribution silencieuse. C'est la même règle que le
    corpus applique déjà à la datation (INDÉCIDABLE plutôt qu'une date devinée) et aux langues
    (non mesurable plutôt qu'un zéro faux).
    """
    auteur = atome.get("auteur")
    if not auteur:
        raise ValueError(
            "ATOME SANS AUTEUR : %r. Aucun défaut n'est appliqué — attribuer ce texte à Freud "
            "parce qu'il est le premier auteur du corpus serait une mesure fausse traversant "
            "toutes les couches en silence. Vérifier `atomisation.atomiser`, qui pose ce champ "
            "sur chaque atome qu'il produit." % atome.get("id", "?"))
    return auteur


def verifier(auteurs_du_corpus, jetons, biographies, lexiques, langues):
    """Chaque auteur AYANT DES ATOMES satisfait-il le contrat ? → fiche par auteur.

    Les registres sont INJECTÉS et non importés : `core` ne doit pas dépendre de `bin`, et un
    contrôle qui va chercher lui-même ses données ne peut pas être éprouvé sur un cas fabriqué.

    Le contrôle porte sur les auteurs PRÉSENTS DANS LE CORPUS, jamais sur les registres : un nom
    déclaré sans œuvre n'est pas un problème, un auteur qui écrit sans être déclaré en est un.
    C'est le sens exact de l'oubli de Ferenczi.
    """
    fiches = []
    for auteur in sorted(auteurs_du_corpus):
        manque, reserves = [], []
        if auteur not in jetons:
            manque.append("jeton_de_nom")
        if auteur not in biographies:
            manque.append("biographie")
        if langues.get(auteur) is None:
            manque.append("langue")
        if auteur not in lexiques:
            # Ce n'est pas un manquement — c'est une réserve, et elle doit voyager avec l'auteur.
            reserves.append("lexique")
        fiches.append({
            "auteur": auteur,
            "conforme": not manque,
            "manque": manque,
            "reserves": reserves,
            "langue": langues.get(auteur),
            "lexique_propre": auteur in lexiques,
            "non_applicables": mesures_non_applicables(auteur in lexiques),
        })
    return {
        "auteurs": fiches,
        "conformes": sum(1 for f in fiches if f["conforme"]),
        "total": len(fiches),
        "avec_reserve": sum(1 for f in fiches if f["reserves"]),
    }


def mesures_non_applicables(a_un_lexique_propre):
    """Ce qui cesse d'avoir un sens pour un auteur DÉCRIT AVEC LE LEXIQUE D'UN AUTRE.

    TROUVÉ EN ÉCRIVANT CE MODULE, ET CELA CORRIGE UNE MESURE DÉJÀ PUBLIÉE.

    La couche des branches écarte les « signatures lexicales » d'un auteur quand le motif vient de
    SON PROPRE lexique : le motif ayant été écrit pour lui, sa domination est vraie par
    construction. Ce contrôle est le plus sévère des deux — il élimine 31 des 35 signatures du
    corpus.

    Or il est VIDE pour un auteur qui ne possède aucun motif : il ne peut jamais le déclencher.
    Les quatre signatures qui « survivaient » au premier contrôle étaient toutes de Josef Breuer,
    et ce n'était pas une coïncidence — c'est la seule chose qui pouvait arriver. Elles ne
    survivaient pas au contrôle : elles ne le rencontraient pas.

    La conclusion publiée ne change pas (zéro signature après les deux contrôles), mais la raison
    change, et elle vaut mieux : le contrôle par provenance du lexique ne protège que les auteurs
    qui en ont un.
    """
    if a_un_lexique_propre:
        return []
    return [{
        "mesure": "signature lexicale (branches, §1)",
        "pourquoi": "le contrôle par provenance du motif est VIDE pour lui — ne possédant aucun "
                    "motif, il ne peut jamais dominer sur le sien. Toute signature qu'il produit "
                    "passe le contrôle sans être éprouvée par lui.",
    }, {
        "mesure": "densité de ses concepts propres (usages)",
        "pourquoi": "aucun motif n'a été écrit pour lui : on ne voit de lui que ce qui ressemble "
                    "à l'auteur dont on emprunte le lexique.",
    }]


def points_manquants(fiches):
    """Quels points du contrat manquent, et à qui — pour un message d'erreur utile."""
    par_point = collections.defaultdict(list)
    for f in fiches:
        for p in f["manque"]:
            par_point[p].append(f["auteur"])
    return dict(par_point)


def reserve():
    """Ce que le contrat garantit, et ce qu'il ne garantit pas."""
    return (
        "Ce contrat garantit l'ACCUEIL d'un auteur, jamais sa COMPARABILITÉ. Un auteur entré "
        "selon ces règles sera décrit, cité, daté, et ses reprises textuelles seront trouvées. "
        "Mais s'il écrit dans une autre langue, la reprise textuelle est aveugle par construction "
        "— les corpus français et allemand du projet partagent UN seul groupe de six mots. Et "
        "s'il n'a pas de lexique propre, il est décrit avec celui d'un autre : on ne voit alors "
        "de lui que ce qui ressemble à cet autre, et certaines mesures cessent d'avoir un sens "
        "pour lui sans que rien ne le signale. "
        "LE CONTRAT NE SE VÉRIFIE PAS TOUT SEUL : il est éprouvé par un test sur les auteurs "
        "réellement présents dans le corpus. Un nom déclaré sans œuvre n'est pas un problème ; "
        "un auteur qui écrit sans être déclaré en est un, et c'est arrivé — Ferenczi est entré "
        "avec 16,8 % des atomes du corpus et sans jeton de nom, si bien qu'aucun auteur ne "
        "pouvait être enregistré comme le nommant."
    )
