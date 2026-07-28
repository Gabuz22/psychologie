#!/usr/bin/env python3
"""SEGMENTATION — découpe un texte en PHRASES, de façon déterministe.

Multilingue depuis l'entrée de Le Bon (1895, français) : la mécanique (masquage par sentinelle,
offsets exacts, recomposition prouvable) est commune à toutes les langues ; seules varient les
DONNÉES — abréviations et classe des débuts de phrase — choisies par le paramètre `langue`.
Le comportement allemand est inchangé au signe près : c'est la langue par défaut, et ses tables
n'ont pas bougé (leçon du corpus : un correctif ne doit pas déplacer le défaut vers une autre
œuvre — a fortiori vers une autre langue).

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
    # APPARAT BIBLIOGRAPHIQUE (ajouté 2026-07-28, audit des atomes courts).
    # Les volumes savants de Rank et d'Abraham sont truffés de notes en abrégé, et chaque point
    # non déclaré y coupait une phrase : « Zeitschr. f. PsA. » produisait trois atomes de deux
    # mots. Mesuré avant correction : 1 086 atomes de quatre mots ou moins chez Rank, dont 943
    # non qualifiés — c'est-à-dire un cinquième de ses non-qualifiés, imputables à la seule
    # segmentation et non au lexique.
    # Chaque forme ci-dessous a été RELEVÉE dans le corpus par comptage des mots abrégés en fin
    # d'atome court, jamais devinée.
    "Vgl", "vgl", "Lit", "Gesch", "Schr", "Jahrb", "Jahrg", "Zentralbl", "Intern", "Internat",
    "Zschr", "Zeitschr", "PsA", "psychoanalyt", "aerztl", "Ges", "Phil", "Kl", "Th", "Chr",
    "Anmkg", "Ausg", "Bd", "Abt", "Beitr", "Forsch", "Sitzungsber", "Arch", "Ann", "Mitt",
    "Frl", "Fam", "Sex", "ed", "Ed", "Verl", "Aufl",
    # LES CHIFFRES ROMAINS ONT ÉTÉ ESSAYÉS PUIS RETIRÉS. Ils apparaissent bien comme numéros de
    # tome en fin de référence (« Bd. III. », 77 occurrences), mais ils ouvrent AUSSI les titres
    # de section — « II. Krankengeschichten. » — et les déclarer soudait le titre à la phrase
    # suivante. Dans les « Studien über Hysterie », l'atome ainsi formé enjambait la frontière de
    # la contribution de Breuer et repassait à Freud : un test l'a signalé.
    # Le gain était mince, le dégât structurel. On préfère quelques références coupées à des
    # titres avalés — et l'attribution d'auteur a par ailleurs été rendue robuste (voir
    # `atomisation._auteur_de`).
)

# Abréviations attestées dans « Psychologie des foules » (Gutenberg #24007) — le texte de 1895 est
# sobre : « M. Taine », « MM. », « vol. III », « p. 12 », plus quelques usuels ajoutés par prudence.
ABBREVIATIONS_FR = (
    "p. ex",
    "MM", "Mme", "Mlle", "vol", "chap", "fig", "art", "etc", "cf", "sq", "St", "Dr",
    "II", "III", "IV", "VI", "VII", "VIII",       # « vol. III. de… » : renvois en chiffres romains
    "t", "p",
)

_ABREVIATIONS_PAR_LANGUE = {"de": ABBREVIATIONS, "fr": ABBREVIATIONS_FR}

# Classe des MAJUSCULES pouvant ouvrir une phrase — par langue. Le français commence volontiers
# une phrase par « À » ou « Étant » ; l'allemand garde sa classe historique, intacte.
_MAJUSCULES = {"de": "A-ZÄÖÜ", "fr": "A-ZÀÂÆÇÉÈÊËÎÏÔŒÙÛÜ"}


def _masquer(texte, langue="de"):
    """Remplace par la sentinelle les points qui NE terminent PAS une phrase."""
    t = texte
    # 1. Abréviations connues. On masque TOUS les points de l'abréviation, pas seulement le
    #    dernier : « z. B. » en contient deux, et laisser le premier ferait couper après « z. »
    #    (point + espace + majuscule = frontière parfaitement plausible pour le découpeur).
    for a in sorted(_ABREVIATIONS_PAR_LANGUE[langue], key=len, reverse=True):
        motif = re.escape(a).replace("\\ ", r"\s*")     # « z. B » tolère « z.B »
        t = re.sub(r"\b" + motif + r"\.", lambda m: m.group(0).replace(".", _S), t)
    # 2. Initiale isolée : une seule majuscule suivie d'un point (« Dr. M. », « Otto R. »).
    t = re.sub(r"\b([%s])\." % _MAJUSCULES[langue], r"\1" + _S, t)
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


def segmenter(texte, langue="de"):
    """texte → [{index, texte, debut, fin, nb_mots}] — phrases dans l'ordre, offsets d'origine.

    Les offsets pointent dans le TEXTE REÇU (non modifié) : une phrase est toujours re-localisable
    dans la source, ce qui rend chaque citation vérifiable. Garantie testée : recomposition exacte.
    """
    if not texte or not texte.strip():
        return []
    masque = _masquer(texte, langue)
    maj = _MAJUSCULES[langue]
    # Le guillemet ouvrant français « peut précéder la majuscule de reprise ; il n'entre PAS dans
    # la classe allemande (où » est ouvrant, à l'ancienne : »Wort«) pour ne rien y déplacer.
    ouvrants = r"[»«\"„_~#(\[]?" if langue == "fr" else r"[»\"„_~#(\[]?"
    # Deux sortes de frontières :
    #   (a) fin de phrase = ponctuation forte + espace(s) + début plausible (majuscule, guillemet,
    #       souligné de mise en relief Gutenberg) ;
    #   (b) ITEM DE LISTE = un numéro en tête de ligne (« 1. Ich mache einen Besuch… »). Sans elle,
    #       toute une énumération de rêves se soudait en un seul atome de 250 mots ; avec une
    #       coupure « après le point », le numéro se serait retrouvé collé à l'atome précédent.
    frontiere = re.compile(
        r"(?<=[.!?])[ \t]*(?:\n(?!\s*\n))?[ \t]*(?=" + ouvrants + "[" + maj + r"0-9])"
        r"|(?<=\n)(?=[ \t]*\d{1,2}[.\x00][ \t]+[" + maj + r"])")
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
    """Forme repliée pour comparaison : minuscules, sans diacritiques, ß→ss, blancs normalisés.

    Le ß devient « ss » à dessein : l'orthographe de 1900 et l'actuelle divergent (« Unbewußte »
    / « Unbewusste »), et un lexique qui les distinguerait manquerait la moitié des occurrences.

    Les BLANCS sont réduits à une espace simple : le texte d'origine est retourné à la ligne, et
    un motif contextuel (« , dem es » pour écarter une relative) ne voit pas « ,\\ndem es » sans
    cela — quatre relatives sur dix-neuf survivaient au correctif du concept « es » par ce seul
    biais. Aucun motif du lexique ne s'appuie sur la structure en lignes (vérifié : zéro re.M).
    """
    s = (s or "").replace("ß", "ss")
    s = unicodedata.normalize("NFD", s)
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return " ".join(s.split())


def replier_esszett(s):
    """Même repliement, mais le ß est CONSERVÉ — pour les mots que seul le ß distingue.

    Cas réel : « Masse » (la foule) et « Maße » (les mesures) deviennent identiques après le
    repliement ordinaire, ce qui rattachait une vingtaine de « in hohem Maße » à la psychologie
    des foules. L'allemand, lui, les sépare nettement : on lui laisse trancher.
    """
    s = unicodedata.normalize("NFD", s or "")
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return " ".join(s.split())
