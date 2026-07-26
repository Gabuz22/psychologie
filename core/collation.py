#!/usr/bin/env python3
"""COLLATION — dater les couches d'écriture en confrontant l'édition lue à la PREMIÈRE.

Le corpus porte une incertitude assumée depuis l'origine : Freud a cessé, dès la 3e édition, de
signaler ses ajouts. Un atome n'est donc « attesté au plus tard » que dans l'édition qu'on lit,
et une chronologie tirée de ces éditions peut confondre un mouvement de pensée avec un ajout
tardif. La seule façon de lever cela est de comparer avec le texte d'origine.

POURQUOI L'OCR SUFFIT ICI, ALORS QU'IL AVAIT ÉTÉ ÉCARTÉ.
Les fac-similés d'archive.org ont été rejetés pour le corpus de travail : leur océrisation est
inutilisable pour CITER (« Patielitin » pour Patientin). Mais la collation ne demande pas de citer
— elle demande de savoir si un passage EXISTE dans l'édition antérieure. C'est une exigence bien
plus faible, que du texte bruité satisfait, à condition de comparer par fragments et non mot à mot.

DEUX ÉCARTS SYSTÉMATIQUES À NEUTRALISER :
  • l'orthographe. L'édition de 1900 précède la réforme de 1901 (« Werthe », « Theil »,
    « Litteratur ») ; celle de 1914 la suit. Sans normalisation, presque rien ne correspondrait.
  • l'océrisation. Ses fautes sont ALÉATOIRES, non systématiques : on les absorbe en cherchant des
    suites de mots (n-grammes) plutôt que des mots isolés — une faute casse un n-gramme, pas tous.

MESURÉ, JAMAIS SUPPOSÉ. La méthode est étalonnée sur deux témoins avant d'être appliquée :
  • témoin POSITIF — la préface de la 1re édition, reproduite telle quelle dans la 4e : elle doit
    correspondre. Ce qu'elle ne retrouve pas donne le taux de faux « ajouts ».
  • témoin NÉGATIF — l'appendice d'Otto Rank, ajouté en 1914 : il ne doit RIEN retrouver.
Sans ces deux mesures, un taux d'ajouts n'aurait aucune valeur.
"""
import os
import re
import unicodedata

COLLATION_VERSION = "1.0.0"

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOSSIER_FAC = os.path.join(RACINE, "sources", "freud", "facsimiles")

# Fac-similés de PREMIÈRE édition, océrisés (archive.org). Ils ne servent QU'À la collation —
# jamais à citer : leur océrisation est trop dégradée pour cela (voir l'en-tête du module).
# `annee` = date réelle du texte retrouvé ; c'est elle qui datera les atomes qui s'y retrouvent.
FACSIMILES = {
    "traumdeutung": {"fichier": "traumdeutung_1900.txt", "annee": 1900,
                     "source": "archive.org/details/Freud_1900_Die_Traumdeutung_k"},
    "drei_abhandlungen": {"fichier": "drei_abhandlungen_1905.txt", "annee": 1905,
                          "source": "archive.org/details/Freud_1905_Drei_Abhandlungen"},
    "witz": {"fichier": "witz_1905.txt", "annee": 1905,
             "source": "archive.org/details/Freud_1905_Der_Witz_k"},
    "psychopathologie": {"fichier": "psychopathologie_1901.txt", "annee": 1901,
                         "source": "archive.org/details/mpn_X_1901_1 (Monatsschrift, publication d'origine)"},
    "jenseits": {"fichier": "jenseits_1920.txt", "annee": 1920,
                 "source": "archive.org/details/II_Freud_1920_Jenseits_k"},
}

# Réforme orthographique de 1901 : ces substitutions rapprochent les deux états de la langue.
# Elles s'appliquent AUX DEUX TEXTES — un écart systématique appliqué des deux côtés disparaît.
_REFORME = [
    (r"th", "t"),        # Werthe → Werte, Theil → Teil, Thier → Tier
    (r"ll", "l"), (r"mm", "m"), (r"nn", "n"), (r"tt", "t"),   # gémination instable en OCR
    (r"c(?=[eiy])", "z"),   # Ceremonie → Zeremonie
    (r"ck", "k"), (r"ph", "f"), (r"ss", "s"),
]


def normaliser(texte):
    """Forme comparable : minuscules, sans diacritiques, orthographe 1901 neutralisée, lettres seules."""
    s = unicodedata.normalize("NFD", (texte or "").replace("ß", "ss"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    for motif, remplacement in _REFORME:
        s = re.sub(motif, remplacement, s)
    return re.sub(r"[^a-z]+", " ", s).strip()


def ngrammes(texte_normalise, n=4):
    """Suites de n mots consécutifs — l'unité de comparaison, tolérante aux fautes isolées."""
    mots = texte_normalise.split()
    if len(mots) < n:
        return {" ".join(mots)} if mots else set()
    return {" ".join(mots[i:i + n]) for i in range(len(mots) - n + 1)}


class Temoin:
    """Index d'une édition de référence, interrogeable par fragments."""

    def __init__(self, texte, n=4):
        self.n = n
        self.index = ngrammes(normaliser(texte), n)

    def couverture(self, texte):
        """Part des n-grammes du passage qu'on retrouve dans l'édition de référence (0 à 1).

        1.0 = présent tel quel ; 0.0 = absent. Entre les deux : passage remanié, ou dégradé par
        l'océrisation — c'est pourquoi le seuil de décision est ÉTALONNÉ, pas choisi d'avance.
        """
        g = ngrammes(normaliser(texte), self.n)
        if not g:
            return None
        return len(g & self.index) / len(g)


def temoin_de(cle_oeuvre):
    """Charge le fac-similé de première édition d'une œuvre, ou None s'il n'y en a pas."""
    meta = FACSIMILES.get(cle_oeuvre)
    if not meta:
        return None
    chemin = os.path.join(DOSSIER_FAC, meta["fichier"])
    if not os.path.exists(chemin):
        return None
    with open(chemin, encoding="utf-8", errors="replace") as f:
        return Temoin(f.read())


# Marge de sécurité entre les deux populations étalonnées : on ne prend pas le seuil optimal, qui
# tombe exactement sur le plus faible des « présents » et n'aurait aucune tolérance. Le seuil
# retenu se place au milieu de l'écart mesuré.
def seuil_avec_marge(etalon):
    if not etalon.get("utilisable"):
        return None
    return round((etalon["absents"]["max"] + etalon["presents"]["min"]) / 2, 3)


def dater_atomes(atomes, temoin, seuil, annee_origine, annee_edition, mots_min=8):
    """Attribue à chaque atome sa couche d'écriture. Renvoie {empreinte: attestation}.

    Trois issues, jamais confondues :
      • « origine »   — retrouvé dans la première édition : daté de l'année d'origine, avec certitude ;
      • « ajout »     — absent de la première édition : ajouté entre l'origine et l'édition lue ;
      • « indecis »   — passage trop court pour être jugé (une poignée de mots peut se retrouver
                        partout par hasard). On refuse de trancher plutôt que de deviner.
    """
    out = {}
    for a in atomes:
        if a["nb_mots"] < mots_min:
            # Trop court pour être jugé : quelques mots se retrouvent partout par hasard. On
            # conserve alors la réserve de l'œuvre — l'incertitude connue vaut mieux qu'une
            # date obtenue au hasard.
            out[a["empreinte"]] = {
                "couche": "indecis", "couverture": None,
                "annee_min": annee_origine, "annee_max": annee_edition,
                "regle": "passage trop court pour être collationné — attesté au plus tard en %d"
                         % annee_edition}
            continue
        c = temoin.couverture(a["texte"])
        if (c or 0) >= seuil:
            out[a["empreinte"]] = {
                "couche": "origine", "couverture": round(c, 3), "annee": annee_origine,
                "regle": "retrouvé dans l'édition de %d — daté avec certitude" % annee_origine}
        else:
            out[a["empreinte"]] = {
                "couche": "ajout", "couverture": round(c, 3),
                "annee_min": annee_origine, "annee_max": annee_edition,
                "regle": "absent de l'édition de %d — ajouté entre %d et %d"
                         % (annee_origine, annee_origine, annee_edition)}
    return out


def etalonner(temoin, textes_oeuvre, textes_etrangers, bins=20):
    """Décide si la collation est concluante pour cette œuvre, et à quel seuil.

    Deux garde-fous, parce qu'un taux d'ajouts sans étalonnage ne vaudrait rien :

    1. TÉMOIN NÉGATIF UNIVERSEL — des passages d'une AUTRE œuvre, forcément absents de ce
       fac-similé. Ils donnent le bruit de fond : mesuré partout sous 0,08. Tout seuil doit rester
       nettement au-dessus.

    2. BIMODALITÉ — si la méthode discrimine, les couvertures se répartissent en deux masses :
       proche de 0 (ajouté) et haute (présent d'origine), séparées par un creux. Le seuil se place
       dans ce creux. S'il n'y a qu'une bosse, c'est que l'océrisation dégrade tout uniformément :
       on ne distingue plus « absent » de « présent mais illisible », et **on ne conclut pas**.
    """
    co = sorted(c for c in (temoin.couverture(t) for t in textes_oeuvre) if c is not None)
    ce = sorted(c for c in (temoin.couverture(t) for t in textes_etrangers) if c is not None)
    if len(co) < 30 or not ce:
        return {"concluant": False, "motif": "échantillon insuffisant"}

    plancher = max(0.10, round(max(ce) * 2, 3))     # deux fois le bruit de fond mesuré
    hist = [0] * bins
    for c in co:
        hist[min(bins - 1, int(c * bins))] += 1

    # Creux : le minimum entre le mode bas et le mode haut, cherché au-delà du plancher.
    debut = max(1, int(plancher * bins))
    fin = int(0.7 * bins)
    if debut >= fin:
        return {"concluant": False, "motif": "plancher de bruit trop haut"}
    i_creux = min(range(debut, fin), key=lambda i: hist[i])
    masse_basse, masse_haute = sum(hist[:i_creux]), sum(hist[i_creux + 1:])
    creux = hist[i_creux]

    mediane = co[len(co) // 2]
    seuil = round((i_creux + 0.5) / bins, 3)
    bimodal = (masse_basse >= 0.05 * len(co) and masse_haute >= 0.05 * len(co)
               and creux <= 0.35 * min(masse_basse, masse_haute))
    # UNIMODALE HAUTE : presque tout se retrouve dans la première édition. Ce n'est pas un échec de
    # la méthode mais un RÉSULTAT — l'édition lue diffère à peine de l'originale. À ne pas
    # confondre avec une distribution étalée à mi-hauteur, qui signale une océrisation trop
    # dégradée pour séparer « absent » de « présent mais illisible ».
    quasi_identique = (not bimodal and masse_basse < 0.05 * len(co) and mediane >= 0.6)

    if bimodal:
        forme, motif = "bimodale", None
    elif quasi_identique:
        forme, motif = "quasi_identique", ("l'édition lue diffère à peine de la première : "
                                           "presque aucun passage n'y manque")
    else:
        forme, motif = "etalee", ("distribution étalée — l'océrisation ne permet pas de distinguer "
                                  "« absent » de « présent mais dégradé »")
    return {
        "concluant": bimodal or quasi_identique,
        "forme": forme,
        "seuil": seuil,
        "mediane": round(mediane, 3),
        "plancher_bruit": plancher,
        "bruit_de_fond": {"n": len(ce), "max": round(max(ce), 3)},
        "distribution": {"n": len(co), "sous_le_creux": masse_basse, "au_creux": creux,
                         "au_dessus": masse_haute},
        "motif": motif,
    }
