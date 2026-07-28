#!/usr/bin/env python3
"""AUDIT D'UN LEXIQUE — trouver les domaines qu'il ne voit pas, en interrogeant le texte.

  python bin/auditer_lexique.py                       →  tous les auteurs, vue d'ensemble
  python bin/auditer_lexique.py "Otto Rank"           →  le détail d'un auteur
  python bin/auditer_lexique.py "Otto Rank" --lire 12 →  + douze atomes non qualifiés, à lire

MÉTHODE, ET POURQUOI ELLE EST DEVENUE UN OUTIL.

Le lexique de Freud a été construit en sept passes successives, celui de Rank en deux, ceux
d'Abraham et de Le Bon en deux chacun. À chaque fois la même démarche : prendre les atomes que le
lexique ne qualifie PAS, relever leur vocabulaire fréquent, et y chercher un domaine entier
absent de l'ontologie. À chaque fois elle a trouvé quelque chose — le vocabulaire de la mort chez
Rank (1 310 occurrences), les idées chez Le Bon (142, alors qu'un chapitre entier s'intitule
« Les idées des foules »), la topique chez Abraham. Une méthode qui a payé treize fois mérite
d'être un outil du dépôt plutôt qu'un script réécrit chaque fois.

CE QUE L'OUTIL NE FAIT PAS : décider. Il propose des mots ; c'est à un humain de dire si un mot
fréquent désigne un domaine de pensée ou n'est qu'un mot fréquent. La différence est exactement
celle qui sépare un corpus utile d'un corpus dont le taux de qualification a été gonflé.

LE PLAFOND EST NORMAL. Un corpus n'atteint pas 100 %, et ne doit pas chercher à l'atteindre :
il reste toujours des phrases de liaison (« Dieser Einwand ist leicht zu widerlegen. »), des
fragments d'apparat critique et des noms propres. Les taguer ferait monter un chiffre sans rien
ajouter à l'analyse — c'est la doctrine du projet : ce qui n'est pas qualifié est AFFICHÉ,
jamais comblé.
"""
import collections
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import atomisation, lexique, sources          # noqa: E402
from core.segmentation import replier                   # noqa: E402

# Mots-outils : grammaire pure, jamais un domaine de pensée. Les laisser noierait le signal sous
# les auxiliaires et les adverbes, qui sont par construction les plus fréquents.
OUTILS_DE = set("""aber alle allen aller alles also andere anderen auch bereits diese diesem
diesen dieser dieses durch einem einen einer eines etwas haben immer jeder jener kann konnen
mehr muss nicht noch oder ohne schon sehr sein seine seinem seinen seiner selbst sind solche
sondern uber unter viele wenn werden wieder wird wohl worden wurde wurden zwei zwischen lassen
lasst machen sagen sehen stelle steht kommt kommen finden findet geben gibt bleibt weise ersten
zweiten letzten ganzen ganze gerade eigentlich naturlich ebenso ahnlich bloss handelt scheint
erscheint zeigt zeigen weiter weniger meist bekannt allerdings freilich vielmehr namlich daher
darauf daraus dabei damit dadurch dagegen einerseits anderseits hatte andern gegen wollen mochte
durfte sollte konnte mussen wissen kennen halten stellen setzen bringen nehmen geht gehen liegt
liegen sieht denken glauben meinen heisst bedeutet folgt nichts einmal jedoch endlich eigenen
jetzt wollte waren keine wahrend beiden beide welche indem unser unserer schliesslich zuruck
fuhrt ihrer ihren ihnen ihrem meine seines daruber denen weiss leicht wegen seite gleichen
besonders gewisse gewissen bedeutung teil sinne form dessen deren solchen zunachst folgenden
hervor spater damals werde anderer einige musste""".split())
OUTILS_FR = set("""alors aucun aucune aussi autre autres avait avaient avant avec beaucoup
bientot cependant chaque comme comment dans depuis derniere deux doivent donne donner elles
encore entre etaient etait etant sont sera seraient etre faire fait faut jamais leurs lorsque
meme memes moins notre nous parce parfois peuvent plus plusieurs pouvait presque puis quand
quelque quelques sans seul seule seulement souvent sous suffit surtout tandis toujours tous
toute toutes trop vers vient voir ainsi cette celui ceux dont elle leur mais pour quelle etat
autrement generalement rapidement facilement completement absolument nullement egalement guere
ailleurs pourtant avoir avons ayant devant apres facon moment premier premiers certaines
aujourd effet choses""".split())


def atomes_de(auteur):
    """Tous les atomes des œuvres SIGNÉES par cet auteur."""
    out = []
    for cle, meta in sources.OEUVRES.items():
        if meta.get("auteur", "Sigmund Freud") != auteur:
            continue
        out.extend(atomisation.atomiser(cle)["atomes"])
    return out


def auditer(auteur, combien=40, seuil=12):
    """→ {taux, non_qualifies, candidats} — les mots fréquents que le lexique ne voit pas."""
    atomes = atomes_de(auteur)
    if not atomes:
        return None
    nq = [a for a in atomes if a["non_qualifie"]]
    langue = lexique.pour_auteur(auteur).LANGUE
    outils = OUTILS_FR if langue == "fr" else OUTILS_DE
    motif = r"[a-zà-ÿ]{5,}" if langue == "fr" else r"[a-zäöüß]{5,}"
    freq = collections.Counter()
    for a in nq:
        freq.update(re.findall(motif, replier(a["texte"])))
    candidats = [(m, k) for m, k in freq.most_common(600) if m not in outils and k >= seuil]
    return {
        "auteur": auteur,
        "atomes": len(atomes),
        "non_qualifies": len(nq),
        "taux_qualifie": round(100 * (len(atomes) - len(nq)) / len(atomes)),
        "candidats": candidats[:combien],
        "exemples": [a["texte"] for a in nq],
    }


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    lire = 0
    if "--lire" in sys.argv:
        i = sys.argv.index("--lire")
        lire = int(sys.argv[i + 1]) if i + 1 < len(sys.argv) else 8

    auteurs = args or sorted({m.get("auteur", "Sigmund Freud") for m in sources.OEUVRES.values()})
    for auteur in auteurs:
        r = auditer(auteur)
        if not r:
            print("aucune œuvre signée par %r" % auteur)
            continue
        print("=" * 78)
        print("%s — %d atomes, %d qualifiés (%d %%), %d non qualifiés"
              % (auteur, r["atomes"], r["atomes"] - r["non_qualifies"],
                 r["taux_qualifie"], r["non_qualifies"]))
        if not r["candidats"]:
            print("  aucun mot fréquent hors lexique : le rendement du scan est atteint.")
        for mot, k in r["candidats"]:
            print("  %-26s %4d" % (mot, k))
        for texte in r["exemples"][:: max(1, len(r["exemples"]) // max(lire, 1))][:lire]:
            print("   · %s" % repr(texte[:130].replace("\n", " ")))


if __name__ == "__main__":
    main()
