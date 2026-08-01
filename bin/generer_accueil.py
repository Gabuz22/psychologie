#!/usr/bin/env python3
"""GÉNÈRE documentation/ACCUEIL_D_UN_AUTEUR.md — le contrat d'entrée, vérifié sur le corpus réel.

    python bin/generer_accueil.py

POURQUOI CE SCRIPT EXISTE. Le dépôt affirme depuis longtemps qu'ajouter un auteur revient à
« ajouter des concepts et des groupes, sans toucher au moteur ». Une affirmation de ce genre ne
coûte rien tant que rien ne la vérifie — et c'est précisément parce que personne ne la vérifiait
que Sándor Ferenczi a pu entrer avec 16,8 % des atomes du corpus SANS jeton de nom, rendant
invisibles quatre-vingts mentions de lui.

Le document ne décrit donc pas une intention : il rend l'ÉTAT MESURÉ des sept auteurs présents,
point de contrat par point de contrat, à chaque exécution. S'il devient faux, c'est qu'un auteur
est entré sans être déclaré — et c'est exactement ce qu'on veut voir.
"""
import os
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import accueil, comparaison, lexiques        # noqa: E402
from core.corpus import Corpus                         # noqa: E402
from exporter_d1 import AUTEURS                        # noqa: E402
from generer_socle import _nombre                      # noqa: E402

SORTIE = os.path.join(RACINE, "documentation", "ACCUEIL_D_UN_AUTEUR.md")

EN_TETE = """# Accueillir un huitième auteur — le contrat, et ce qu'il ne promet pas

> **DOCUMENT GÉNÉRÉ** par `python bin/generer_accueil.py` — ne pas éditer à la main : l'état des
> auteurs présents est recalculé sur le corpus à chaque exécution. Régénérer après toute entrée
> d'auteur ou d'œuvre.
>
> **Ce que ce document est.** La liste des points à déclarer pour qu'un auteur entre dans le
> corpus sans rien casser, et l'état vérifié des **{n_auteurs}** auteurs déjà présents.
>
> **{verdict}**
>
> **Ce que ce contrat ne promet PAS.** Que l'auteur entré soit *comparable* aux autres. Il sera
> décrit, cité, daté, et ses reprises textuelles seront trouvées. Mais s'il écrit dans une autre
> langue, la reprise textuelle est aveugle par construction — les corpus français et allemand du
> projet partagent UN seul groupe de six mots. Et s'il n'a pas de lexique propre, il est décrit
> avec celui d'un autre : on ne voit alors de lui que ce qui ressemble à cet autre.

---
"""


def section_points():
    L = ["## 1. Les points à déclarer\n"]
    L.append("Chacun a été payé au moins une fois. La colonne **si on l'oublie** n'est pas une "
             "précaution de style : c'est ce qui est réellement arrivé, ou ce que le code fait "
             "réellement.\n")
    L.append("| Point | Où | Obligatoire | Si on l'oublie |")
    L.append("|---|---|---|---|")
    for p in accueil.POINTS:
        L.append("| **%s** | `%s` | %s | %s |"
                 % (p["cle"], p["ou"],
                    "oui" if p["obligatoire"] else "non — mais réserve",
                    p["sinon"]))
    L.append("")
    derive = [p for p in accueil.POINTS if p.get("derive")]
    if derive:
        L.append("**Un seul point ne se déclare pas** : la *langue*, dérivée des œuvres de "
                 "l'auteur. La distinction n'est pas cosmétique — offrir un endroit où déclarer "
                 "la langue serait offrir un endroit où se tromper : une œuvre française rangée "
                 "sous un auteur annoncé germanophone passerait sans bruit. Il n'y a rien à "
                 "écrire, seulement à vérifier qu'elle est résoluble.\n")
    return "\n".join(L)


def section_etat(r, atomes_par_auteur):
    L = ["## 2. L'état des auteurs présents, vérifié\n"]
    L.append("Le contrôle porte sur les auteurs **ayant des atomes**, jamais sur les registres : "
             "un nom déclaré sans œuvre n'est pas un problème, un auteur qui écrit sans être "
             "déclaré en est un. C'est le sens exact de l'oubli de Ferenczi, et l'inverse ne "
             "s'est jamais produit.\n")
    L.append("| Auteur | Atomes | Langue | Lexique propre | Conforme |")
    L.append("|---|---:|---|---|---|")
    for f in sorted(r["auteurs"], key=lambda f: -atomes_par_auteur.get(f["auteur"], 0)):
        L.append("| %s | %s | %s | %s | %s |"
                 % (f["auteur"], _nombre(atomes_par_auteur.get(f["auteur"], 0)),
                    f["langue"] or "**irrésoluble**",
                    "oui" if f["lexique_propre"] else "**non**",
                    "oui" if f["conforme"] else "**NON — %s**" % ", ".join(f["manque"])))
    L.append("")
    return "\n".join(L)


def section_reserve_lexique(r):
    sans = [f for f in r["auteurs"] if not f["lexique_propre"]]
    L = ["## 3. L'exception, et ce qu'elle invalide\n"]
    if not sans:
        L.append("Aucun auteur du corpus n'est décrit avec le lexique d'un autre. La règle "
                 "fondatrice — chaque auteur a ses catégories propres — est tenue sans "
                 "exception.\n")
        return "\n".join(L)
    L.append("**%s** est décrit avec le lexique de Freud, et c'est le seul cas. Ce n'est pas un "
             "manquement : ses pages sont imprimées dans un volume de Freud, et les catégories "
             "sont celles de l'auteur du volume — décision documentée dans `core/atomisation.py`. "
             "Mais la CONSÉQUENCE ne l'était pas, et elle a fait passer un artefact pour un "
             "résultat.\n" % ", ".join(f["auteur"] for f in sans))
    L.append("| Mesure qui cesse d'avoir un sens | Pourquoi |")
    L.append("|---|---|")
    for m in sans[0]["non_applicables"]:
        L.append("| %s | %s |" % (m["mesure"], m["pourquoi"]))
    L.append("")
    L.append("**Le cas mesuré.** La couche des branches écarte une signature lexicale quand le "
             "motif vient du PROPRE lexique de l'auteur qui domine — contrôle qui élimine 31 des "
             "35 signatures du corpus. Les 4 restantes étaient toutes de Breuer, et l'on a "
             "d'abord écrit qu'elles *survivaient* à ce contrôle. C'est faux : ne possédant aucun "
             "motif, il ne peut jamais dominer sur le sien, donc le contrôle est **vide pour lui**. "
             "Elles ne survivaient pas, elles ne le rencontraient pas. Le résultat publié ne "
             "change pas — zéro signature après les deux contrôles — mais il repose désormais sur "
             "le bon motif.\n")
    return "\n".join(L)


def section_defaut():
    return """## 4. Le défaut qui attendait le huitième auteur

Le dépôt écrit **quarante fois** `atome.get("auteur", "Sigmund Freud")`, dans vingt et un
fichiers. Ce défaut n'est **jamais** nécessaire : `core/atomisation.py` pose le champ `auteur` sur
chaque atome qu'il produit. Il ne peut donc se déclencher que si quelque chose est cassé — et ce
jour-là, il n'annonce rien : il attribue le texte à Freud, et la mesure fausse traverse toutes les
couches en silence.

C'est le mode de panne exact qui a rendu Ferenczi invisible : entré avec **16,8 %** des atomes du
corpus et sans jeton de nom, aucun auteur ne pouvait être enregistré comme le nommant, et le
couple Freud ↔ Ferenczi paraissait unidirectionnel — un accident de configuration présenté comme
un fait de texte.

`accueil.auteur_de()` échoue au lieu de deviner, et un test l'appelle sur les **116 545** atomes du
corpus sans qu'il lève une seule fois. Le défaut est donc prouvé mort : il ne protège rien, il ne
peut que mentir. C'est la même règle que le corpus applique déjà à la datation (INDÉCIDABLE plutôt
qu'une date devinée) et aux langues (non mesurable plutôt qu'un zéro faux).

---
"""


def main(corpus=None):
    corpus = corpus or Corpus()
    atomes_par_auteur = {}
    for a in corpus.atomes:
        auteur = accueil.auteur_de(a)
        atomes_par_auteur[auteur] = atomes_par_auteur.get(auteur, 0) + 1

    r = accueil.verifier(
        set(atomes_par_auteur),
        jetons=comparaison.NOMS,
        biographies=AUTEURS,
        # PAS `PAR_AUTEUR` : Freud n'y figure pas, ses tables vivant dans `core/lexique.py`.
        # La première version de ce script concluait donc que Freud était décrit avec le lexique
        # d'un autre — le document l'aurait imprimé.
        lexiques=lexiques.AUTEURS_AVEC_LEXIQUE_PROPRE,
        langues=comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres))

    # LE VERDICT EST CALCULÉ, jamais laissé au lecteur — même règle que les autres générateurs.
    if r["conformes"] < r["total"]:
        verdict = ("ALERTE : %d auteur(s) sur %d ne satisfont pas le contrat — %s. Un auteur qui "
                   "écrit sans être déclaré devient invisible dans les couches de comparaison, et "
                   "cette invisibilité se lit comme un fait de corpus."
                   % (r["total"] - r["conformes"], r["total"],
                      accueil.points_manquants(r["auteurs"])))
    elif r["avec_reserve"]:
        n = r["avec_reserve"]
        verdict = ("ÉTAT : les %d auteurs du corpus satisfont le contrat, et %s une réserve — "
                   "décrit%s avec le lexique d'un autre, ce qui rend certaines mesures "
                   "inapplicables. Voir §3."
                   % (r["total"],
                      "un seul porte" if n == 1 else "%d portent" % n,
                      "" if n == 1 else "s"))
    else:
        verdict = ("ÉTAT : les %d auteurs du corpus satisfont le contrat, sans réserve."
                   % r["total"])

    parts = [EN_TETE.format(n_auteurs=r["total"], verdict=verdict),
             section_points(), "---\n",
             section_etat(r, atomes_par_auteur), "---\n",
             section_reserve_lexique(r), "---\n",
             section_defaut(),
             "## 5. Ce que ce contrat ne dit pas\n",
             accueil.reserve() + "\n",
             "*Reproduire : `python bin/generer_accueil.py` · la règle du lexique par auteur : "
             "`core/lexiques/__init__.py` · ce que la comparaison entre auteurs ne donne pas : "
             "`BRANCHES_ET_DERIVATIONS.md` §1.*\n"]

    with open(SORTIE, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(parts))
    print("→ %s (%d auteurs, %d conformes, %d avec réserve)"
          % (SORTIE, r["total"], r["conformes"], r["avec_reserve"]))


if __name__ == "__main__":
    main()
