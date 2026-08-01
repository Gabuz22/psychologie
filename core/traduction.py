#!/usr/bin/env python3
"""TRADUCTION — ce qu'un seul mot français doit porter quand l'allemand compose.

CE QUE CE MODULE NE FAIT PAS, ET IL FAUT LE DIRE D'ABORD : il ne juge aucune traduction. Décider
que « pulsion » rend bien `Trieb` demande une compétence de traducteur et une histoire des
traductions ; le corpus n'a ni l'une ni l'autre, et prétendre trancher serait exactement la faute
que ce projet documente ailleurs — nommer une nature que la mesure ne prouve pas.

CE QU'IL FAIT, ET QUI EST MESURABLE. L'allemand COMPOSE. Un terme canonique n'apparaît presque
jamais seul : le radical `trieb` touche 426 formes distinctes du corpus AVANT tout seuil, `traum`
en touche 1 039 — l'essentiel étant une queue de hapax et de coquilles d'OCR que `famille()`
écarte. Un mot français qui prétend traduire le terme doit couvrir la famille qui reste, et c'est
un fait de texte, comptable, qu'aucune décision de traducteur ne modifie. Le module rend donc la
CHARGE : combien de formes il faut couvrir pour atteindre l'essentiel des emplois, et lesquelles.
Les comptes après seuil sont dans `documentation/TRADUCTION.md`, qui est régénéré ; ils ne sont
pas recopiés ici, où ils dériveraient.

LE PIÈGE, MESURÉ AVANT D'ÉCRIRE UNE LIGNE, ET IL EST LE MÊME QUE CELUI DU LEXIQUE. Chercher un
terme par son radical attrape des mots qui n'ont rien à voir (chiffres de la dernière
régénération de `documentation/TRADUCTION.md`, qui fait foi) :
    `lust`  attrape `Verlust` (« la perte ») et `lustig` (« drôle ») — 394 occurrences, 11,1 % ;
    `angst` attrape `längst` (« depuis longtemps ») — 373 occurrences, 6,1 % du radical ;
    `trieb` attrape `übertrieben`, `Betrieb` — 208, soit 5,3 % ;
    `traum` attrape `Trauma` et `traumatisch` — 868, soit 4,4 %, et c'est le plus coûteux des
            quatre : il confond les DEUX termes centraux du corpus, le rêve et le traumatisme ;
    `ich`   attrape `sich`, `nicht`, `mich`, `nichts`, `vielleicht`, `dichter` — 72 715
            occurrences, 40,4 % du radical, et ce chiffre est un PLANCHER : douze faux amis
            seulement ont été déclarés là où il y en a des centaines. Le radical est donc marqué
            inutilisable, et le lexique le savait déjà : `lexique._RE_ICH_MOI` cherche
            « das Ich », « Ich-Ideal », « Ichs », jamais `ich`.
C'est le même défaut que `\\bschwan` attrapant `schwanger` (« enceinte ») dans le lexique de Rank,
mesuré à 28 % de captures fausses. Les faux amis sont donc DÉCLARÉS et COMPTÉS, jamais devinés.

LA SEULE ANCRE BILINGUE DU CORPUS est Gustave Le Bon, 1 485 atomes en français, 1895 — et Freud le
lit en traduction allemande. `lexique.MOTIFS_FR` en tire déjà quatre REFUS documentés (`instinct`
n'est pas `Trieb`, `rêve` n'est pas `Traum` chez Le Bon, `illusion` n'est pas `Wahn`, `état` n'est
pas `Staat`). Ce module les prolonge : un refus argumenté vaut mieux qu'une correspondance
plausible, et c'est la seule chose que ce corpus permet d'affirmer sur une traduction.
"""
import collections
import re

TRADUCTION_VERSION = "1.0.0"

# Un mot doit peser au moins cela pour figurer dans la famille rendue : sous ce seuil, on décrit
# des coquilles d'OCR plutôt que du vocabulaire — le corpus est majoritairement océrisé sans
# relecture. Mesuré sur `traum` : le radical touche plus de mille formes distinctes, dont l'immense
# majorité n'apparaît qu'une ou deux fois.
OCCURRENCES_MINIMUM = 3

# Part des occurrences qu'on cherche à couvrir pour dire « voilà la famille utile ».
COUVERTURE_CIBLE = 0.90


# LES TERMES CANONIQUES, avec leur rendu français COURANT — et ce rendu est une donnée EXTÉRIEURE
# au corpus, pas une mesure. Il est là pour être confronté, jamais pour être validé : le corpus ne
# peut ni le confirmer ni l'infirmer, il peut seulement dire ce que le mot allemand fait chez ces
# auteurs-là. La colonne qui informe est `faux_amis`, qui est mesurée.
TERMES = [
    {"id": "trieb", "allemand": "Trieb", "francais_courant": "pulsion", "radical": "trieb",
     "faux_amis": ["betrieb", "ubertrieben", "ubertriebene", "ubertriebenen", "vertrieben"],
     "note": "« Instinkt » et « Trieb » sont deux mots distincts en allemand, et Le Bon écrit "
             "« instinct » en 1895 sans rien devoir à Freud : `lexique.MOTIFS_FR` REFUSE "
             "explicitement de les apparier. Les formes verbales de `treiben` (getrieben, "
             "Antrieb) sont laissées dans la famille — elles sont de la même racine, et les "
             "retirer serait trancher une question de morphologie que le corpus ne pose pas."},
    {"id": "traum", "allemand": "Traum", "francais_courant": "rêve", "radical": "traum",
     "faux_amis": ["trauma", "traumas", "traumatisch", "traumatische", "traumatischen",
                   "traumatischer", "traumatismus", "geburtstrauma", "geburtstraumas"],
     "note": "LE FAUX AMI LE PLUS COÛTEUX DU CORPUS : chercher `traum` attrape `Trauma`, "
             "c'est-à-dire que le rêve avale le traumatisme — et donc tout le vocabulaire du "
             "livre de 1924 de Rank. Chez Le Bon, « rêve » est métaphorique (« les rêves de nos "
             "pères ») et `MOTIFS_FR` refuse de le rattacher à `Traum`."},
    {"id": "angst", "allemand": "Angst", "francais_courant": "angoisse", "radical": "angst",
     "faux_amis": ["langst", "unlangst"],
     "note": "« Angst » se rend tantôt par « angoisse », tantôt par « peur », et le corpus ne "
             "peut pas trancher entre les deux — il peut seulement montrer les contextes. Le faux "
             "ami `längst` (« depuis longtemps ») n'a aucun rapport avec le terme et n'est séparé "
             "de lui par aucune frontière de mot : seule une déclaration explicite l'écarte."},
    {"id": "lust", "allemand": "Lust", "francais_courant": "plaisir", "radical": "lust",
     "faux_amis": ["verlust", "verluste", "verlustes", "verlusten", "lustig", "lustige",
                   "lustigen", "geluste", "gelust", "lustiger"],
     "note": "`Verlust` est LA PERTE, exactement le contraire du plaisir, et le radical l'attrape. "
             "`Unlust` en revanche appartient bien à la famille — c'est le déplaisir freudien, "
             "second terme du couple Lust/Unlust."},
    {"id": "verdrangung", "allemand": "Verdrängung", "francais_courant": "refoulement",
     "radical": "verdrang", "faux_amis": [],
     # AUCUN CHIFFRE ICI : la charge et la part interne sont dans le tableau généré, deux lignes
     # plus haut. Une note qui les recopie diverge à la première régénération — c'est arrivé dès
     # la première version, qui annonçait « 14 formes » quand le calcul en donnait 9.
     "note": "Le terme le plus PROPRE du corpus : le radical ouvre presque toujours le mot, la "
             "famille est courte, et aucun faux ami n'a été trouvé. Quand un terme se comporte "
             "ainsi, la charge de traduction est faible et le mot français unique tient sans "
             "réserve particulière."},
    {"id": "besetzung", "allemand": "Besetzung", "francais_courant": "investissement",
     "radical": "besetzung", "faux_amis": [],
     "note": "CAS INVERSE ET LE PLUS INSTRUCTIF : c'est le terme dont la plus grande part des "
             "emplois a le radical À L'INTÉRIEUR d'un composé (Objektbesetzung, Gegenbesetzung, "
             "Libidobesetzung, Überbesetzung) — voir la colonne « radical interne ». Le mot "
             "français doit donc survivre à la composition, ce qu'il fait mal : "
             "« contre-investissement » passe, « investissement d'objet » s'alourdit."},
    {"id": "ubertragung", "allemand": "Übertragung", "francais_courant": "transfert",
     "radical": "ubertragung", "faux_amis": ["gedankenubertragung"],
     "note": "`Gedankenübertragung` est la TRANSMISSION DE PENSÉE — la télépathie, sujet réel "
             "chez Freud et Ferenczi — et non le transfert analytique. Le composé est déclaré "
             "faux ami parce que le français emploie deux mots là où l'allemand en emploie un."},
    {"id": "ich", "allemand": "Ich", "francais_courant": "moi", "radical": "ich",
     # LE SEUL TERME DONT LE RADICAL EST DÉCLARÉ INUTILISABLE, et ce drapeau n'est pas décoratif :
     # ses chiffres de charge et de contamination sont des ARTEFACTS de la méthode, pas des
     # mesures du terme. La liste de faux amis ci-dessous en écarte douze là où il y en a des
     # centaines — la contamination résiduelle de 40 % est donc un plancher, pas un total. Le
     # publier comme le pire cas du tableau ferait passer un échec de méthode pour un résultat.
     "radical_utilisable": False,
     "faux_amis": ["sich", "nicht", "nichts", "mich", "vielleicht", "dichter", "dichtung",
                   "gleich", "leicht", "reich", "wirklich", "eigentlich"],
     "note": "LE RADICAL EST INUTILISABLE : la contamination mesurée dans le tableau ci-dessus "
             "est un PLANCHER, obtenu en ne déclarant que douze faux amis là où il y en a des "
             "centaines. Le lexique du projet ne s'y risque pas — `lexique._RE_ICH_MOI` cherche "
             "« das Ich », « Ich-Ideal », « Ichs », « des Ichs ». C'est le cas qui montre que la "
             "charge de traduction n'est pas seulement lexicale : certains termes ne se "
             "cherchent pas par leur radical du tout."},
]


def vocabulaire(atomes):
    """{forme repliée: occurrences} sur des atomes déjà repliés — la matière des familles."""
    mot = re.compile(r"[a-zäöüß]{3,}")
    v = collections.Counter()
    for a in atomes:
        for m in mot.findall(a):
            v[m] += 1
    return v


def famille(terme, vocab):
    """La famille d'un terme canonique dans le corpus → dict, avec sa charge et ses faux amis.

    Trois ensembles, séparés MÉCANIQUEMENT par la position du radical, parce que c'est la seule
    séparation qu'on puisse faire sans morphologie allemande :
      `initiales` — le radical ouvre le mot (Trieb, Triebregung, Triebleben). Presque toujours du
          vocabulaire du terme.
      `internes`  — le radical est à l'intérieur (Sexualtrieb, mais aussi Verlust pour `lust`).
          C'est là que vit toute l'ambiguïté, et le module ne tranche pas : il compte et il liste.
      `faux_amis` — les formes DÉCLARÉES sans rapport, avec leur poids réel. Déclarées, jamais
          devinées : le corpus a déjà payé une détection automatique de ce genre.

    `charge` est le chiffre à retenir : le nombre de formes distinctes qu'il faut couvrir pour
    atteindre 90 % des occurrences. C'est ce qu'un mot français unique doit porter.
    """
    radical = terme["radical"]
    exclus = set(terme.get("faux_amis") or ())
    toutes = {f: n for f, n in vocab.items() if radical in f and n >= OCCURRENCES_MINIMUM}
    bruit = {f: n for f, n in toutes.items() if f in exclus}
    retenues = {f: n for f, n in toutes.items() if f not in exclus}

    total_brut = sum(toutes.values())
    total = sum(retenues.values())
    ordonnees = sorted(retenues.items(), key=lambda x: -x[1])
    cumul, charge = 0, 0
    for _, n in ordonnees:
        cumul += n
        charge += 1
        if cumul >= COUVERTURE_CIBLE * total:
            break

    initiales = {f: n for f, n in retenues.items() if f.startswith(radical)}
    internes = {f: n for f, n in retenues.items() if not f.startswith(radical)}
    return {
        "id": terme["id"],
        "allemand": terme["allemand"],
        "francais_courant": terme["francais_courant"],
        "radical": radical,
        # Quand il est faux, `charge` et `contamination` mesurent l'échec du radical, pas le
        # terme : ils ne doivent jamais servir de superlatif dans un classement.
        "radical_utilisable": terme.get("radical_utilisable", True),
        "formes": len(retenues),
        "occurrences": total,
        "charge": charge,
        "part_initiale": round(sum(initiales.values()) / total, 3) if total else None,
        "part_interne": round(sum(internes.values()) / total, 3) if total else None,
        "principales": ordonnees[:12],
        "internes_principales": sorted(internes.items(), key=lambda x: -x[1])[:8],
        "faux_amis": sorted(bruit.items(), key=lambda x: -x[1]),
        "occurrences_faux_amis": sum(bruit.values()),
        # LE CHIFFRE QUI JUSTIFIE LA DÉCLARATION : ce qu'une recherche naïve par radical aurait
        # ramassé en trop. C'est lui qui transforme « attention aux faux amis » en fait mesuré.
        "contamination": round(sum(bruit.values()) / total_brut, 3) if total_brut else None,
        "note": terme.get("note"),
    }


def familles(vocab, termes=None):
    return [famille(t, vocab) for t in (termes or TERMES)]


def refus_documentes():
    """Les correspondances français↔allemand EXPLICITEMENT REFUSÉES, et pourquoi.

    Elles viennent de `lexique.MOTIFS_FR`, où elles sont écrites en fin de table. Les rendre ici
    n'est pas de la redondance : un refus argumenté est le seul énoncé qu'un corpus de 1 485 atomes
    français puisse produire sur une traduction, et c'est donc le résultat le plus solide de cette
    couche. Une correspondance plausible et fausse coûte plus cher qu'un refus.
    """
    return [
        {"francais": "instinct", "allemand": "Trieb", "refuse": True,
         "motif": "La distinction Trieb/Instinkt est un débat de traduction connu, et « l'instinct "
                  "des foules » de Le Bon en 1895 n'est pas la pulsion freudienne."},
        {"francais": "rêve", "allemand": "Traum", "refuse": True,
         "motif": "Chez Le Bon le mot est métaphorique (« les rêves de nos pères »), jamais "
                  "l'objet théorique de la Traumdeutung."},
        {"francais": "illusion", "allemand": "Wahn", "refuse": True,
         "motif": "Le délire n'est pas l'illusion. Le chapitre « Les illusions » de Le Bon traite "
                  "des croyances collectives, pas de la psychose."},
        {"francais": "état", "allemand": "Staat", "refuse": True,
         "motif": "Replié sans majuscule, « l'État » se confond avec « l'état mental » — "
                  "l'ambiguïté est créée par le pliage, pas par la langue."},
    ]


def reserve():
    """Ce que cette couche ne dit pas — portée avec elle."""
    return (
        "Ce document NE JUGE AUCUNE TRADUCTION. Décider que « pulsion » rend bien Trieb demande "
        "une compétence de traducteur et une histoire des traductions ; le corpus n'a ni l'une ni "
        "l'autre. La colonne « français courant » est une donnée EXTÉRIEURE au corpus, donnée pour "
        "être confrontée et non validée. "
        "Ce qui est mesuré, c'est la CHARGE : le nombre de formes allemandes distinctes qu'un mot "
        "français unique doit couvrir, l'allemand composant là où le français juxtapose. "
        "Les FAUX AMIS sont déclarés et comptés, jamais détectés : chercher un terme par son "
        "radical attrape `Verlust` pour `Lust`, `längst` pour `Angst`, `Trauma` pour `Traum` — et "
        "pour `ich`, 40,4 % des occurrences sont `sich`, `nicht`, `mich`. C'est le même défaut que "
        "`\\bschwan` attrapant `schwanger` dans le lexique de Rank, mesuré à 28 % de captures "
        "fausses. "
        "Enfin, LE CORPUS N'A QU'UNE ANCRE BILINGUE — Gustave Le Bon, 1 485 atomes, 1895, et il "
        "n'est pas psychanalyste. Les seuls énoncés solides qu'on puisse en tirer sont des REFUS "
        "de correspondance, pas des validations."
    )
