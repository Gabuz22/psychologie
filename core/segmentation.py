#!/usr/bin/env python3
"""SEGMENTATION — découpe un texte allemand en PHRASES, de façon déterministe.

Première brique de l'atomisation : sans découpage fiable, tout ce qui suit est faux. L'allemand
de Freud (1900-1920) pose trois pièges concrets, mesurés sur le corpus réel — chacun ferait
éclater une phrase au mauvais endroit et produirait des atomes tronqués :

  1. ABRÉVIATIONS à point (« z. B. », « d. h. », « u. dgl. », « vgl. », « S. 12 », « Bd. II »)
     — très fréquentes chez Freud, souvent AVEC espace interne (« z. B. » = deux jetons).
  2. INITIALES de noms propres (« Dr. M. », « Otto R. ») — l'anonymisation des patients par
     initiale est constante dans les récits de cas.
  3. ORDINAUX (« 3. Auflage », « 1. Kapitel ») — le point ne clôt rien.

Méthode : on masque ces cas par un caractère sentinelle AVANT de couper, puis on démasque. Aucun
modèle, aucune heuristique probabiliste : même entrée → même sortie, toujours. Le texte n'est
jamais modifié (les phrases rendues sont des tranches du texte d'origine, offsets à l'appui).
"""
import re
import unicodedata

# Sentinelle : caractère de contrôle absent des textes imprimés (masquage réversible sans perte).
_S = "\x00"

# Abréviations attestées dans le corpus (repérées sur Die Traumdeutung / Drei Abhandlungen).
# Écrites SANS le point final ; le motif ajoute le point. Ordre : les plus longues d'abord.
ABBREVIATIONS = (
    "z. B", "d. h", "u. a", "u. dgl", "z. T", "a. a. O", "u. zw", "d. i",
    "usw", "usf", "vgl", "bzw", "ca", "etc", "evtl", "ggf", "inkl", "resp", "ebd",
    "Nr", "Bd", "Abb", "Kap", "Anm", "Aufl", "Jh", "Jhdt", "Hrsg", "Verf",
    "Dr", "Prof", "Hr", "Fr", "St", "Sr",
    "ff", "f", "S", "p", "cf",
)


def _masquer(texte):
    """Remplace par la sentinelle les points qui NE terminent PAS une phrase."""
    t = texte
    # 1. Abréviations connues. On masque TOUS les points de l'abréviation, pas seulement le
    #    dernier : « z. B. » en contient deux, et laisser le premier ferait couper après « z. »
    #    (point + espace + majuscule = frontière parfaitement plausible pour le découpeur).
    for a in sorted(ABBREVIATIONS, key=len, reverse=True):
        motif = re.escape(a).replace("\\ ", r"\s*")     # « z. B » tolère « z.B »
        t = re.sub(r"\b" + motif + r"\.", lambda m: m.group(0).replace(".", _S), t)
    # 2. Initiale isolée : une seule majuscule suivie d'un point (« Dr. M. », « Otto R. »).
    t = re.sub(r"\b([A-ZÄÖÜ])\.", r"\1" + _S, t)
    # 3. Ordinal : « 3. Auflage », « 1. Kapitel ». Le mot suivant est le plus souvent un NOM, donc
    #    capitalisé en allemand — on accepte donc les deux casses. Limité à 1-2 chiffres : cela
    #    exclut volontairement les millésimes à 4 chiffres (« Er starb 1939. Seine Werke… »), où le
    #    point termine réellement la phrase. Compromis assumé et testé.
    #
    #    Le point d'un numéro EN DÉBUT DE LIGNE est masqué lui aussi, mais pour une autre raison :
    #    c'est un item de liste (Freud énumère beaucoup de rêves ainsi), et la coupure doit se
    #    faire AVANT le numéro, pas après — sinon « 1. » se retrouve collé à la fin de l'atome
    #    précédent. La frontière correspondante est posée dans `segmenter`.
    t = re.sub(r"\b(\d{1,2})\.(?=\s+[A-ZÄÖÜa-zäöüß])", r"\1" + _S, t)
    return t


def _demasquer(texte):
    return texte.replace(_S, ".")


def segmenter(texte):
    """texte → [{index, texte, debut, fin, nb_mots}] — phrases dans l'ordre, offsets d'origine.

    Les offsets pointent dans le TEXTE REÇU (non modifié) : une phrase est toujours re-localisable
    dans la source, ce qui rend chaque citation vérifiable. Garantie testée : recomposition exacte.
    """
    if not texte or not texte.strip():
        return []
    masque = _masquer(texte)
    # Deux sortes de frontières :
    #   (a) fin de phrase = ponctuation forte + espace(s) + début plausible (majuscule, guillemet,
    #       souligné de mise en relief Gutenberg) ;
    #   (b) ITEM DE LISTE = un numéro en tête de ligne (« 1. Ich mache einen Besuch… »). Sans elle,
    #       toute une énumération de rêves se soudait en un seul atome de 250 mots ; avec une
    #       coupure « après le point », le numéro se serait retrouvé collé à l'atome précédent.
    frontiere = re.compile(
        r"(?<=[.!?])[ \t]*(?:\n(?!\s*\n))?[ \t]*(?=[»\"„_~#(\[]?[A-ZÄÖÜ0-9])"
        r"|(?<=\n)(?=[ \t]*\d{1,2}[.\x00][ \t]+[A-ZÄÖÜ])")
    phrases, debut, index = [], 0, 0
    for m in frontiere.finditer(masque):
        brut = texte[debut:m.start()]
        if brut.strip():
            phrases.append(_phrase(index, brut, debut, texte))
            index += 1
        debut = m.start()
    reste = texte[debut:]
    if reste.strip():
        phrases.append(_phrase(index, reste, debut, texte))
    return phrases


def _phrase(index, brut, debut, source):
    """Construit une phrase en conservant ses offsets RÉELS dans la source (bornes resserrées)."""
    gauche = len(brut) - len(brut.lstrip())
    net = brut.strip()
    d = debut + gauche
    return {
        "index": index,
        "texte": net,
        "debut": d,
        "fin": d + len(net),
        "nb_mots": len(re.findall(r"[\wÄÖÜäöüß]+", net)),
    }


def recomposable(phrases, source):
    """Vérifie que chaque phrase est bien la tranche annoncée de la source (preuve d'intégrité)."""
    return all(source[p["debut"]:p["fin"]] == p["texte"] for p in phrases)


def replier(s):
    """Forme repliée pour comparaison : minuscules, sans diacritiques, ß→ss (allemand).

    Le ß devient « ss » à dessein : l'orthographe de 1900 et l'actuelle divergent (« Unbewußte »
    / « Unbewusste »), et un lexique qui les distinguerait manquerait la moitié des occurrences.
    """
    s = (s or "").replace("ß", "ss")
    s = unicodedata.normalize("NFD", s)
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def replier_esszett(s):
    """Même repliement, mais le ß est CONSERVÉ — pour les mots que seul le ß distingue.

    Cas réel : « Masse » (la foule) et « Maße » (les mesures) deviennent identiques après le
    repliement ordinaire, ce qui rattachait une vingtaine de « in hohem Maße » à la psychologie
    des foules. L'allemand, lui, les sépare nettement : on lui laisse trancher.
    """
    s = unicodedata.normalize("NFD", s or "")
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
