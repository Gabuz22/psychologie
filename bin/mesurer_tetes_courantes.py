#!/usr/bin/env python3
"""COMBIEN DE TÊTES COURANTES RESTENT DANS LE CORPUS — mesurer avant de décider quoi que ce soit.

  python bin/mesurer_tetes_courantes.py                 → toutes les œuvres, vue d'ensemble
  python bin/mesurer_tetes_courantes.py --oeuvre X --lire 30

CE QUE CET OUTIL N'EST PAS : un nettoyeur. Il ne retire rien. Retirer des têtes courantes changerait
le texte de milliers d'atomes, donc leur EMPREINTE, donc l'ancrage de 488 verdicts de lecture. Une
telle opération se décide sur des chiffres, pas sur une intuition — et ces chiffres n'existaient pas.

LE DÉFAUT, ÉTABLI ET NON SUPPOSÉ. `sources.PARATEXTE_FINAL` et `REGIONS_ECARTEES` coupent aux
EXTRÉMITÉS d'un volume. Rien ne traite le MILIEU. Or l'OCR de ces fac-similés soude la tête courante
imprimée en haut de page à la phrase qui commence cette page — et souvent EN PLEIN MILIEU :

    « es gefiel ihr dort ausserordentlich und sie fuhlte BERUFSNEUROSE EINER SANGERIN. 215
      sich sehr wohl. »

Trois conséquences déjà mesurées ailleurs dans le dépôt :
  • `rundfrage` : 87 % de ses occurrences étaient la tête courante d'un volume — sous-concept retiré ;
  • `berufsneurose` : 80 % — retiré ;
  • `angsthysterie` : 43 %, dont 61 atomes ouvrant littéralement par « die angsthysterie. » suivie
    d'un fragment qui ne redémarre pas. Sous-concept GARDÉ, mais son compte brut est faux de moitié.

LA SIGNATURE EST LA PONCTUATION, ET LA PREMIÈRE VERSION DE CET OUTIL S'EST TROMPÉE DESSUS.

Elle prenait pour tête courante tout atome dont les DEUX PREMIERS MOTS se répètent dans l'œuvre.
Résultat : 30,9 % du corpus « touché », et en tête du classement des prétendues têtes courantes —
`ich habe` (91), `es ist` (91), `er war` (70), `in der` (57). Ce sont des OUVERTURES DE PHRASE
ALLEMANDES ORDINAIRES. L'outil ne mesurait pas le paratexte, il mesurait la langue allemande.
C'était la deuxième erreur du même genre dans ce dépôt : le premier détecteur de paratexte du banc
cherchait des atomes répétés à l'identique et ne trouvait RIEN. L'un ne trouvait rien, l'autre
trouvait tout ; les deux étaient faux.

Ce qui distingue une tête courante d'une phrase, c'est qu'elle est un TITRE : elle se termine par
un point IMMÉDIATEMENT, et le texte de la page reprend après. D'où la clé retenue — le texte
jusqu'au PREMIER POINT, s'il fait moins de 40 signes et se répète au moins trois fois en tête
d'atome dans la même œuvre :

    « die angsthysterie. ursachte. »          ← tête courante + fragment de phrase coupée
    « ich habe mich daher entschlossen, … »   ← le premier point est loin : c'est une phrase

ÉTALONNAGE. Deux comptes avaient été établis À LA MAIN par des contradicteurs qui ont lu les atomes
un par un, dans « Nervöse Angstzustände » : 61 atomes ouvrant par « die angsthysterie. » et 46 par
« die angstneurose. » — les titres des deux parties du volume. Le détecteur retrouve **61 et 46**,
exactement. C'est cette concordance qui le rend croyable, pas sa plausibilité.

SECONDE SIGNATURE : un FOLIO QUI OUVRE L'ATOME — un entier de 2 à 4 chiffres suivi d'une minuscule,
en tête. Une phrase ne commence jamais ainsi ; c'est le numéro de page de la tête courante, resté
seul quand le saut de page tombe entre deux phrases :

    « 493 neter, veredelter weise, das kindliche denken beibehalte… »   ← « …[gewin]neter » coupé

CE QUI EST DÉTECTÉ MAIS PAS COMPTÉ, ET POURQUOI. Une tête courante peut aussi atterrir EN PLEIN
MILIEU d'un atome (« …analyse einer angsthysterie mit obsession. 141 gestorben. »). Compter tout
folio nu où qu'il soit ferait passer ce chiffre de 6 % à 31 %, mais la mesure serait fausse : à
cette place, un nombre nu suivi d'une minuscule est INDISCERNABLE d'une référence de page
(« (s. 268 fg.) »), d'un âge (« im alter von 20 jahren »), d'une quantité (« von 23 stichen
durchbohrt ») ou d'une année (« im herbst 1906 vor »). Sur un échantillon lu de l'Inzest-Motiv,
la majorité des captures de milieu de phrase étaient de ce genre. On ne compte donc que ce qu'on
peut établir, et on écrit ici que le reste existe.

CE QUE LE CHIFFRE VAUT. C'est un PLANCHER, jamais un plafond, pour trois raisons cumulées et toutes
mesurées : (1) les têtes courantes de milieu d'atome ne sont pas comptées, voir ci-dessus ; (2) l'OCR
déforme les têtes courantes elles-mêmes — « Todessymbolik » apparaît en 43 orthographes distinctes
dans un seul volume, et une tête trop abîmée pour se répéter à l'identique échappe au seuil ;
(3) une tête courante qui tombe systématiquement en milieu de phrase dans un volume donné n'y est
jamais vue. Le vrai taux est donc PLUS HAUT que ce qui est affiché.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import atomisation, sources                  # noqa: E402
from core.segmentation import replier                  # noqa: E402

TETE_MIN = 3               # répétitions pour qu'un intitulé compte comme tête courante
TETE_SIGNES = 40           # au-delà, ce n'est plus un titre de haut de page

# Le folio est cherché EN TÊTE D'ATOME uniquement, et suivi d'une minuscule. C'est la seule
# position où il soit sans ambiguïté : ailleurs, un entier nu est aussi bien une pagination de
# renvoi, un âge ou une quantité (voir l'en-tête du module). Ancré à gauche, il ne peut être qu'un
# numéro de page laissé par un saut de page.
_FOLIO_EN_TETE = re.compile(r"^\d{2,4}\s+[a-zäöüß]")

# CE QUI N'EST PAS UNE TÊTE COURANTE, bien que court et terminé par un point : la numérotation des
# listes (« 3. »), les ordinaux, et les abréviations usuelles qui ouvrent une phrase (« dr. »,
# « s. », « vgl. »). Les écarter est nécessaire — sans quoi le détecteur compte les listes de
# Stekel, qui numérote ses cas — et suffisant : ce sont des formes closes, pas un jugement.
_PAS_UNE_TETE = re.compile(r"^(?:\(?\d+[a-z]?\.?\)?|[ivxlcdm]+\.|dr\.|s\.|vgl\.|nr\.|bd\.|hrsg\.|"
                           r"z\.|d\.|u\.|a\.|f\.|ff\.|p\.|st\.|prof\.)$")


def _tete(texte):
    """L'intitulé d'un atome : son texte jusqu'au PREMIER POINT, s'il est assez court.

    C'est ce point immédiat qui sépare un titre d'une phrase — voir l'en-tête du module.
    """
    i = texte.find(".")
    if not (0 < i <= TETE_SIGNES):
        return None
    t = texte[:i + 1].strip()
    return None if _PAS_UNE_TETE.match(t) else t


def tetes_courantes(atomes):
    """→ {intitulé répété: nombre d'atomes qu'il ouvre} pour cette œuvre."""
    freq = collections.Counter(x for x in
                               (_tete(replier(a["texte"]).strip()) for a in atomes) if x)
    return {o: k for o, k in freq.items() if k >= TETE_MIN}


def auditer_oeuvre(cle, lire=0):
    r = atomisation.atomiser(cle)
    atomes = r["atomes"]
    if not atomes:
        return None
    replies = [(a, replier(a["texte"]).strip()) for a in atomes]
    ouvertures = tetes_courantes(atomes)

    par_ouverture = collections.Counter()
    n_ouverture = n_folio = 0
    exemples = []
    touches = set()
    for a, t in replies:
        touche = False
        o = _tete(t)
        if o and o in ouvertures:
            n_ouverture += 1
            par_ouverture[o] += 1
            touche = True
        if _FOLIO_EN_TETE.search(t):
            n_folio += 1
            touche = True
        if touche:
            touches.add(a["id"])
            if len(exemples) < lire:
                exemples.append(t)

    return {
        "oeuvre": cle,
        "auteur": sources.OEUVRES[cle].get("auteur", "Sigmund Freud"),
        "atomes": len(atomes),
        "ouverture": n_ouverture,
        "folio": n_folio,
        "touches": len(touches),
        "part": len(touches) / len(atomes),
        "tetes": par_ouverture.most_common(8),
        "exemples": exemples,
    }


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--oeuvre")
    p.add_argument("--lire", type=int, default=0)
    args = p.parse_args()

    cles = [args.oeuvre] if args.oeuvre else list(sources.OEUVRES)
    fiches = [f for f in (auditer_oeuvre(c, args.lire) for c in cles) if f]
    fiches.sort(key=lambda f: -f["part"])

    print("=" * 100)
    print("TÊTES COURANTES RESTANT DANS LE CORPUS — plancher, jamais plafond")
    print("=" * 100)
    print("%-30s %-18s %8s %9s %8s %8s" % ("œuvre", "auteur", "atomes", "ouverture", "folio", "TOUCHÉS"))
    tot_a = tot_t = 0
    for f in fiches:
        tot_a += f["atomes"]
        tot_t += f["touches"]
        print("%-30s %-18s %8d %9d %8d %6d (%.0f %%)"
              % (f["oeuvre"], f["auteur"][:18], f["atomes"], f["ouverture"], f["folio"],
                 f["touches"], 100 * f["part"]))
    print("-" * 100)
    print("%-30s %-18s %8d %9s %8s %6d (%.1f %%)"
          % ("TOTAL", "", tot_a, "", "", tot_t, 100 * tot_t / max(tot_a, 1)))

    if args.oeuvre:
        f = fiches[0]
        print("\nTÊTES COURANTES LES PLUS FRÉQUENTES :")
        for o, k in f["tetes"]:
            print("   %-34s %4d atomes" % (repr(o), k))
        for t in f["exemples"]:
            print("   · %s" % t[:150])


if __name__ == "__main__":
    main()
