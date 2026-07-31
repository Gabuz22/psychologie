#!/usr/bin/env python3
"""BANC D'ÉPREUVE D'UN SOUS-CONCEPT — mesurer ce qu'un motif capte VRAIMENT, avant de le croire.

  python bin/eprouver_sous_concept.py "Wilhelm Stekel"                    → tout le lexique
  python bin/eprouver_sous_concept.py "Wilhelm Stekel" --groupe neurose   → un groupe
  python bin/eprouver_sous_concept.py "Wilhelm Stekel" --sous sterben --lire 20

POURQUOI CET OUTIL EXISTE, ET POURQUOI IL EST VERSIONNÉ.

L'audit contradictoire du lexique de Stekel (2026-07-31) a mesuré autre chose que ce qu'il croyait
DEUX FOIS, et les deux fois il INVENTAIT des défauts. Un banc écrit à la main dans un bac à sable
se réécrit à chaque audit, et refait les mêmes deux fautes :

  1. IL FAUT REPLIER AVEC `segmentation.replier`, PAS avec `collation.normaliser`. Le second est
     fait pour comparer deux éditions, donc agressif : Mutter → muter, Pollution → polution,
     Phantasie → fantasie. Cinq sous-concepts étaient sortis à ZÉRO atome, purs artefacts du banc.
  2. IL FAUT BORDER CHAQUE MOTIF À GAUCHE. Le moteur compile `re.compile(r"\\b" + m)` ; un banc qui
     ne borde pas fait attraper natur/kultur/lekture à « tur », gleiche/vergleiche à « leiche »,
     konstatieren à « tier » — des centaines de faux positifs imaginaires.

Le banc importe donc la MÊME fonction de repli et le MÊME bordage que le moteur, au lieu de les
réécrire. Un banc de mesure qui ne partage pas le code mesuré ne mesure pas ce qu'on croit.

CE QU'IL MESURE, ET POURQUOI CHAQUE COLONNE A ÉTÉ AJOUTÉE PAR UN DÉFAUT RÉEL :

  atomes        combien d'atomes de cet auteur le sous-concept touche.
  propres       combien il est SEUL à qualifier — son coût réel. Le retirer les déqualifie.
                (« madchen » : 606 atomes, 597 propres. C'est ce chiffre qui condamne, pas le 1er.)
  formes        LES FORMES RÉELLEMENT CAPTÉES, comptées. La règle d'or du projet : `traum` captait
                Trauma, `see` captait Seele 255 fois pour 19 lacs. On ne juge JAMAIS un motif sur
                son intention, toujours sur la liste de ce qu'il ramène.
  paratexte     part des atomes où le motif est porté par une TÊTE COURANTE ou une ligne de
                sommaire. Ce piège a pris le projet DEUX FOIS (`genitaltheorie` chez Ferenczi,
                50 occurrences sur 83 ; `rundfrage` et `berufsneurose` chez Stekel, 87 % et 80 %)
                — et les deux fois il ressemblait à une signature d'auteur, parce qu'un titre de
                chapitre imprimé en haut de chaque page compte beaucoup chez lui et ZÉRO chez les
                autres. Un piège qui a pris deux fois doit être détecté par la machine, pas par la
                vigilance du lecteur. Voir `part_paratexte` ci-dessous pour ce qu'il fallait
                mesurer exactement — la première version de ce banc s'est trompée de signature.
  rapport       fréquence relative contre les autres auteurs de la même langue. < 1 = ce n'est pas
                son mot ; le lexique d'un auteur ne doit pas lui prêter le vocabulaire commun.
  concentre     part des atomes venant d'UN SEUL volume — voir `part_concentree` plus bas. C'est la
                forme GÉNÉRALE du piège que `paratexte` n'attrape que sous une de ses formes.

Le banc ne DÉCIDE pas. Il donne les chiffres et les contextes ; le verdict se rend en lisant.
"""
import argparse
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import atomisation, lexique, sources          # noqa: E402
from core.segmentation import replier                   # noqa: E402

# ------------------------------------------------------------------------------------------
# DÉTECTION DU PARATEXTE IMPRIMÉ — et pourquoi la première version de ce banc s'est trompée.
#
# La tête courante N'EST PAS un atome répété. Le premier détecteur cherchait des atomes identiques
# et n'en trouvait AUCUN, sur des motifs dont on savait qu'ils étaient à 80 % du paratexte. La
# raison, lue dans le texte : l'OCR SOUDE la tête courante à la phrase de la page, et souvent EN
# PLEIN MILIEU. Chaque occurrence est donc textuellement unique.
#
#     « es gefiel ihr dort ausserordentlich und sie fuhlte BERUFSNEUROSE EINER SANGERIN. 215
#       sich sehr wohl. »
#
# Deux signatures mécaniques valent mieux qu'une, parce que le paratexte a deux formes :
#
#   1. OUVERTURE RÉPÉTÉE — la tête est soudée au DÉBUT et le motif est dedans. Attrape `rundfrage`
#      (60 % de ses atomes) ; manque `berufsneurose` (10 %).
#   2. NUMÉRO DE PAGE NU À PROXIMITÉ — un entier isolé de 2 à 4 chiffres près du motif : c'est le
#      folio imprimé, qui suit la tête courante partout où elle atterrit. Attrape `berufsneurose`
#      (70 %) ; complète `rundfrage` (18 %).
#
# Étalonnage sur les deux cas connus et six témoins négatifs : les deux motifs condamnés par
# l'audit ressortent ≥ 70 %, les concepts réels restent ≤ 10 %. C'est un signal d'alerte, pas une
# mesure exacte — il dit « va lire ces atomes-là », et c'est tout ce qu'on lui demande.
#
# CE CHIFFRE EST UN PLANCHER, JAMAIS UN PLAFOND, et la raison est mesurée. `_ouvertures_repetees`
# exige au moins trois ouvertures IDENTIQUES ; or quand l'OCR massacre une tête courante, elle
# n'est plus identique à elle-même. Cas relevé : « Todessymbolik », tête courante de « Die Sprache
# des Traumes », apparaît en 43 ORTHOGRAPHES DISTINCTES (todeeaymlxdik, todmajmbolik,
# todeoajmbolik…), dont 17 soudées en tête d'un atome sans rapport — « todeeaymlxdik. Stock die
# Brust der Amme! ». Aucun seuil de répétition n'est atteint, et le banc n'en signale que 2 sur
# ~23. Un « 7 % de paratexte » ne dit donc PAS « il n'y en a pas plus » ; il dit « au moins 7 % ».
PARATEXTE_OUVERTURE_MIN = 3        # occurrences pour qu'une ouverture compte comme répétée
PARATEXTE_OUVERTURE_SIGNES = 28    # au-delà, ce n'est plus une tête courante
PARATEXTE_FENETRE = 70             # distance motif ↔ numéro de page

_PAGE_NUE = re.compile(r"(?<![\w,.])\d{2,4}(?![\w,.\d])")
_SEUIL_ALERTE_PARATEXTE = 0.30

# ------------------------------------------------------------------------------------------
# CONCENTRATION DANS UN SEUL VOLUME — la forme GÉNÉRALE d'un piège qui a pris le projet TROIS fois.
#
# Les trois cas sont mécaniquement le même, sous trois déguisements différents :
#
#   genitaltheorie (Ferenczi)  50 des 83 occurrences = la tête courante d'UN volume
#   rundfrage / berufsneurose  87 % et 80 % = la tête courante et le sommaire d'UN volume
#   keller (celui-ci)          36 des 54 = Gottfried et Paul KELLER, les écrivains, dont 25 dans
#                              le seul « Die Träume der Dichter »
#
# Le troisième n'est PAS du paratexte : c'est un nom propre en pleine prose, et le détecteur de
# tête courante ne le voit pas (5 %). Ce qu'ils partagent tous les trois, c'est autre chose — le
# compte est porté par UN SEUL LIVRE, et paraît d'autant plus convaincant qu'il est nul chez les
# autres auteurs, puisque personne d'autre n'a écrit ce livre-là.
#
# La concentration ne condamne pas : `traumsprache` se concentre légitimement dans « Die Sprache
# des Traumes ». Elle dit où regarder — et sur les trois cas connus, elle regarde au bon endroit.
_SEUIL_ALERTE_CONCENTRATION = 0.60


def atomes_par_auteur():
    """{auteur: [atomes]} pour tout le corpus, une seule atomisation."""
    out = collections.defaultdict(list)
    for cle in sources.OEUVRES:
        for a in atomisation.atomiser(cle)["atomes"]:
            out[a.get("auteur", "Sigmund Freud")].append(a)
    return out


def _ouverture(texte):
    return " ".join(texte.split()[:2])


def _ouvertures_repetees(textes):
    """Les deux premiers mots qui reviennent assez souvent pour être une tête courante soudée."""
    freq = collections.Counter(_ouverture(t) for t in textes)
    return {o for o, k in freq.items()
            if k >= PARATEXTE_OUVERTURE_MIN and len(o) <= PARATEXTE_OUVERTURE_SIGNES}


def _est_paratexte(texte, position, ouvertures):
    """Ce motif, à cette position, est-il porté par du paratexte imprimé plutôt que par la prose ?"""
    ouv = _ouverture(texte)
    if ouv in ouvertures and position <= len(ouv) + 2:
        return True
    return any(abs(m.start() - position) <= PARATEXTE_FENETRE for m in _PAGE_NUE.finditer(texte))


def eprouver(auteur, tous, groupe_filtre=None, sous_filtre=None, lire=0):
    """Mesure chaque sous-concept du lexique de cet auteur → liste de fiches."""
    table = lexique.pour_auteur(auteur)
    mes_atomes = tous[auteur]

    # Témoin : les autres auteurs de la MÊME LANGUE. Comparer un motif allemand à un corpus
    # français donnerait un rapport infini qui ne veut rien dire.
    temoin = []
    for autre, atomes in tous.items():
        if autre != auteur and lexique.pour_auteur(autre).LANGUE == table.LANGUE:
            temoin.extend(atomes)
    signes_moi = sum(len(a["texte"]) for a in mes_atomes) or 1
    signes_temoin = sum(len(a["texte"]) for a in temoin) or 1

    # Repli mémorisé : le corpus fait plusieurs millions de signes, et chaque sous-concept le
    # reparcourt. Sans cela le banc est inutilisable.
    replie_moi = [(a, replier(a["texte"]).strip()) for a in mes_atomes]
    replie_temoin = [replier(a["texte"]) for a in temoin]
    ouvertures = _ouvertures_repetees([t for _, t in replie_moi])

    fiches = []
    for groupe, meta in table.CONCEPTS.items():
        if groupe_filtre and groupe != groupe_filtre:
            continue
        for sous, motifs in meta["termes"].items():
            if sous_filtre and sous != sous_filtre:
                continue
            res = [re.compile(r"\b" + m) for m in motifs]

            touches, formes, n_paratexte = [], collections.Counter(), 0
            for a, t in replie_moi:
                # On relit la forme ENTIÈRE du mot autour de chaque correspondance : `findall`
                # rendrait '' pour un motif sans groupe capturant, et la colonne « formes » doit
                # montrer ce qui est VRAIMENT capté — c'est toute la règle d'or du lexique.
                #
                # UNE OCCURRENCE EST UNE POSITION DANS LE TEXTE, PAS UNE CORRESPONDANCE DE MOTIF.
                # Défaut réel, trouvé par un contradicteur : quand deux motifs d'un même
                # sous-concept se recouvrent — `tod` et `todes`, `sterbe` et `sterben` — le même
                # mot était compté une fois PAR MOTIF. Le banc affichait « sterben 692 » pour 346
                # occurrences réelles et « todes 162 » pour 81 : 33 % du compte de `sterben` était
                # fictif, et le doublon se lisait dans la colonne « formes » sans qu'on le voie,
                # tous les chiffres y étant exactement le double du réel.
                # La clé est la position de départ : un mot capté par trois motifs reste un mot.
                par_position = {}
                for r in res:
                    for m in r.finditer(t):
                        fin = m.end()
                        while fin < len(t) and (t[fin].isalpha() or t[fin] == "-"):
                            fin += 1
                        par_position[m.start()] = t[m.start():fin]
                if not par_position:
                    continue
                positions = sorted(par_position)
                touches.append(a)
                formes.update(par_position.values())
                if all(_est_paratexte(t, p, ouvertures) for p in positions):
                    n_paratexte += 1

            # Coût propre : atomes que CE sous-concept est SEUL à qualifier — ce que son retrait
            # ferait basculer en « non qualifié ». C'est le chiffre qui condamne ou qui sauve.
            #
            # DÉFAUT RÉEL, trouvé par un contradicteur et corrigé ici. La version précédente lisait
            # `c.get("sous_concepts", [])` — une clé qui N'EXISTE PAS sur un atome. Les clés réelles
            # sont `groupe` et `concept`. L'ensemble `autres` était donc TOUJOURS vide, et la
            # colonne ne mesurait pas ce qu'elle annonçait : elle comptait « atomes sans fonction ».
            # Comme 16 % des atomes de Stekel portent au moins deux sous-concepts, le coût propre
            # était surestimé d'un facteur ~2,3 (neurose : 747 affichés contre 307 réels).
            #
            # Un `.get()` avec valeur par défaut sur une clé absente échoue EN SILENCE : il rend une
            # colonne plausible et fausse. C'est exactement ce qu'un banc de mesure ne doit pas
            # faire — d'où le test qui vérifie désormais que la clé lue existe bien sur les atomes.
            propres = 0
            for a in touches:
                autres = {c["concept"] for c in a["concepts"]} - {sous}
                if not autres and not a["fonctions"]:
                    propres += 1

            # D'où viennent ces atomes ? Un sous-concept porté par un seul volume décrit ce livre,
            # pas cet auteur — que ce soit par une tête courante ou par un nom propre.
            par_oeuvre = collections.Counter(a["oeuvre"] for a in touches)
            oeuvre_dominante, n_dominante = (par_oeuvre.most_common(1) or [(None, 0)])[0]

            occ_moi = sum(formes.values())
            # Le témoin se compte de la MÊME façon — par position, jamais par correspondance de
            # motif. Compté par motif des deux côtés, le doublon se compensait en partie et
            # masquait sa propre ampleur : le rapport de `sterben` passait pour ×2,88 au lieu
            # de ×2,67.
            occ_temoin = 0
            for t in replie_temoin:
                occ_temoin += len({m.start() for r in res for m in r.finditer(t)})
            d_moi = occ_moi / signes_moi
            d_temoin = occ_temoin / signes_temoin
            rapport = (d_moi / d_temoin) if d_temoin else (float("inf") if occ_moi else 0.0)

            fiches.append({
                "groupe": groupe, "sous": sous, "motifs": motifs,
                "atomes": len(touches), "propres": propres,
                "occurrences": occ_moi, "occurrences_temoin": occ_temoin,
                "rapport": rapport,
                "paratexte": n_paratexte,
                "part_paratexte": (n_paratexte / len(touches)) if touches else 0.0,
                "oeuvre_dominante": oeuvre_dominante,
                "part_concentree": (n_dominante / len(touches)) if touches else 0.0,
                "par_oeuvre": par_oeuvre.most_common(),
                "formes": formes.most_common(25),
                "exemples": [a["texte"] for a in touches[:: max(1, len(touches) // max(lire, 1))]
                             ][:lire] if lire else [],
            })
    return fiches


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("auteur")
    p.add_argument("--groupe")
    p.add_argument("--sous")
    p.add_argument("--lire", type=int, default=0)
    args = p.parse_args()

    tous = atomes_par_auteur()
    if args.auteur not in tous:
        raise SystemExit("auteur inconnu — connus : %s" % ", ".join(sorted(tous)))
    fiches = eprouver(args.auteur, tous, args.groupe, args.sous, args.lire)

    print("=" * 96)
    print("%s — %d atomes" % (args.auteur, len(tous[args.auteur])))
    print("=" * 96)
    print("%-16s %-22s %6s %7s %8s %9s   %s"
          % ("groupe", "sous-concept", "atomes", "propres", "rapport", "paratexte", "alerte"))
    for f in sorted(fiches, key=lambda f: (f["groupe"], f["sous"])):
        alertes = []
        if f["atomes"] == 0:
            alertes.append("MOTIF MORT")
        if f["part_paratexte"] >= _SEUIL_ALERTE_PARATEXTE:
            alertes.append("PARATEXTE %d %%" % round(100 * f["part_paratexte"]))
        if f["part_concentree"] >= _SEUIL_ALERTE_CONCENTRATION:
            alertes.append("UN SEUL VOLUME %d %% (%s)"
                           % (round(100 * f["part_concentree"]), f["oeuvre_dominante"]))
        if f["rapport"] < 1.0 and f["atomes"]:
            alertes.append("PAS SON MOT")
        print("%-16s %-22s %6d %7d %8s %6d %2s   %s"
              % (f["groupe"], f["sous"], f["atomes"], f["propres"],
                 ("%.2f" % f["rapport"]) if f["rapport"] != float("inf") else "inf",
                 f["paratexte"], "", " · ".join(alertes)))

    if args.sous or args.groupe:
        for f in fiches:
            print("\n" + "-" * 96)
            print("%s / %s   motifs = %r" % (f["groupe"], f["sous"], f["motifs"]))
            print("  %d atomes (%d propres), %d occurrences chez lui contre %d au témoin → ×%.2f"
                  % (f["atomes"], f["propres"], f["occurrences"], f["occurrences_temoin"],
                     f["rapport"]))
            print("  paratexte : %d atomes (%.0f %%)" % (f["paratexte"], 100 * f["part_paratexte"]))
            print("  RÉPARTITION PAR VOLUME (un seul volume = ce sous-concept décrit un livre) :")
            for oeuvre, k in f["par_oeuvre"]:
                print("      %-34s %5d  (%.0f %%)" % (oeuvre, k, 100 * k / max(f["atomes"], 1)))
            print("  FORMES RÉELLEMENT CAPTÉES :")
            for forme, k in f["formes"]:
                print("      %-34s %5d" % (forme, k))
            for texte in f["exemples"]:
                print("   · %s" % repr(texte[:150].replace("\n", " ")))


if __name__ == "__main__":
    main()
