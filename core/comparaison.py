#!/usr/bin/env python3
"""COMPARAISON INTER-AUTEURS — la couche qui relie des graphes construits SÉPARÉMENT.

POURQUOI CETTE COUCHE EXISTE, ET POURQUOI ELLE EST SÉPARÉE.

Chaque auteur du corpus est décrit avec SON propre lexique (voir `core/lexiques/`). Cette règle
a un coût qu'il faut assumer : rien, dans les données, ne dit spontanément que la `verdraengung`
de Rank et celle de Freud sont la même chose — ni qu'elles ne le sont pas. Les rapprochements
doivent donc être POSÉS, explicitement, avec la mesure qui les fonde. C'est l'objet de ce module.

Il ne fusionne jamais deux concepts. Il pose des ARÊTES entre des couples (auteur, objet) qui
restent distincts, et chaque arête porte la preuve qui l'établit.

CE QUI EST ÉTABLI ICI, ET CE QUI NE L'EST PAS.

Trois dimensions seulement, retenues parce que chacune se vérifie à l'œil sur le texte :

  1. REPRISE TEXTUELLE — deux passages partagent des suites de mots. Fait de texte.
  2. MENTION NOMINALE — un auteur écrit le nom d'un autre. Fait de texte.
  3. LECTURE DÉCLARÉE — un chapitre annonce dans son TITRE qu'il traite d'un autre auteur.
     Fait d'édition, le plus fort des trois, et le seul qui traverse la barrière des langues.

Ce qui a été ESSAYÉ PUIS ÉCARTÉ, DEUX FOIS : l'appariement de concepts par similarité de
voisinage. Le premier refus (2026-07-28) tenait à l'absence de témoin positif valide — le seul
disponible, « un concept comparé à lui-même coupé en deux moitiés », mesure la stabilité d'un
échantillon et non la correspondance entre deux auteurs.

CE VERROU-LÀ A ÉTÉ LEVÉ le lendemain, et le diagnostic était donc le mauvais. La couche « usage
des mots » fournit un vrai témoin inter-auteurs : le même motif appliqué à deux corpus distincts.
Il fonctionne — AUC 0,893, R-précision cent fois le hasard, et le signal survit au retrait des
mots qui le portent le plus.

LA MÉTHODE A ÉCHOUÉ AILLEURS, et il fallait la construire pour le voir. Sur la tâche réelle — tous
les concepts de A contre tous ceux de B — la précision est de 6 % au seuil courant. Elle ne
distingue un mot ni de son synonyme (`behandlung`/`kur` : 0,32) ni de son CONTRAIRE
(`männlichkeit`/`weiblichkeit` : 0,29, autant que deux occurrences du même mot). Ses plus hauts
scores sont portés par l'autre moitié du terme (`erogene` validé à 72 % par `zone`). Et la lecture
des divergences qu'elle produit n'en a confirmé QU'UNE SUR SEIZE : sept étaient des artefacts
d'œuvre unique, six le même sens appliqué à une autre matière.

Le module de mesure est conservé dans `core/appariement.py`, avec ses témoins ; il n'alimente ni la
base ni le site. Les chiffres, les cas lus et les quatre conditions pour rouvrir le chantier sont
dans `documentation/APPARIEMENT_ECARTE.md`. Y revenir sans les lire serait refaire le travail.

LE PIÈGE CENTRAL, MESURÉ AVANT D'ÉCRIRE UNE LIGNE.

Le motif de nom le plus évident est faux, et de deux façons indépendantes :
  • « \\bfreud » attrape « Freude », « Freuden », « freudig » — la JOIE, 82 atomes ;
  • « \\ble ?bon\\b » ne trouve qu'UN atome de Freud citant Le Bon, là où il y en a 31 : la
    transcription Gutenberg met les noms en relief avec des soulignés (« _Le Bon_ »), et « _ »
    est un caractère de mot pour « \\b », qui ne voit donc aucune frontière.
    Ces 30 atomes invisibles comprenaient tout le chapitre « II. Le Bon's Schilderung der
    Massenseele » — c'est-à-dire la relation inter-auteurs la mieux documentée de tout le corpus.
D'où `aplatir()` : on réduit le texte à des lettres et des espaces AVANT de chercher, et on
cherche un jeton exact. Les deux défauts disparaissent ensemble.
"""
import re
import unicodedata

from . import collation

COMPARAISON_VERSION = "1.0.0"

# Longueur des suites de mots comparées. Quatre suffit pour la collation (qui demande seulement
# si un passage EXISTE dans une autre édition) ; ici on demande si deux auteurs partagent une
# formulation, question plus exigeante — d'où six, mesuré comme le meilleur compromis entre
# rappel et bruit sur ce corpus (voir `documentation/COMPARAISON.md`).
N_GRAMME = 6

# Un atome plus court ne porte pas assez de matière pour qu'un partage signifie quelque chose.
# Mesuré : sous ce seuil, la bande haute des scores est envahie de titres d'ouvrage et d'en-têtes
# de page océrisés, qui se ressemblent entre eux sans qu'aucun auteur n'en cite un autre.
MOTS_MINIMUM = 20

# Un n-gramme présent dans beaucoup d'atomes n'est pas une reprise, c'est de la langue courante.
# Le corpus en compte très peu à six mots — 3 sur 1 102 842 : la contrainte coûte presque rien et
# protège du cas où un auteur reprendrait une formule figée de l'époque.
DOCUMENTS_MAXIMUM = 12

# SEUILS FIXÉS PAR LECTURE, PAS PAR HISTOGRAMME. Cette précision compte : la première version de
# ce module calait le seuil sur `collation.etalonner`, qui cherche un creux dans la distribution.
# Cette fonction a été écrite pour un autre problème — la couverture d'un texte par rapport à UN
# témoin — et ici son verdict de bimodalité est un artefact du nombre de classes de l'histogramme :
# il répond « oui » quel que soit le découpage. Elle est donc INAPPLICABLE ici, et ne doit pas
# être réutilisée hors de son domaine.
#
# Les deux seuils ci-dessous viennent d'une lecture réelle, bande par bande, des 281 paires
# candidates du corpus :
#   • au-dessus de 0,70 : reprise manifeste — texte quasi mot pour mot, souvent entre guillemets.
#     Lues : citation du cas d'Anna O. par Freud, du résumé d'Œdipe par Rank, des « Drei
#     Abhandlungen » par Rank et par Abraham. Aucune fausse dans l'échantillon lu.
#   • entre 0,30 et 0,70 : reprise partielle — l'emprunt est réel mais reformulé, abrégé, ou
#     enchâssé. Souvent attribué en toutes lettres (« Freud fügt eine Bemerkung hinzu: », « In der
#     Traumdeutung heißt es: »). Une part notable relève d'une SOURCE TIERCE partagée (voir
#     `SOURCES_TIERCES`) — ces cas sont signalés, jamais orientés.
#   • en dessous de 0,30 : l'apparat bibliographique domine (deux notes de bas de page citant le
#     même titre de revue), et la lecture n'y trouve plus de reprise de pensée.
#
# UN RÉSULTAT NÉGATIF, mesuré et conservé parce qu'il a écarté une fausse piste : on a cherché à
# discriminer le vrai du faux par l'ATTRIBUTION NOMINALE (le texte nomme-t-il l'auteur repris ?).
# Le taux est PLAT — 40 % dans la bande haute comme dans la bande basse — parce que les notes
# bibliographiques nomment les auteurs autant que les vraies citations. L'attribution est donc un
# attribut utile à afficher, jamais un critère de tri.
SEUIL_PUBLICATION = 0.30
SEUIL_MANIFESTE = 0.70

# Sources que DEUX auteurs peuvent citer indépendamment l'un de l'autre. Quand les deux passages
# les nomment, le partage de mots ne prouve plus un emprunt entre eux : Rank et Abraham racontent
# tous deux Œdipe d'après Sophocle, Abraham et Freud citent tous deux Sancho Pança. Le lien reste
# affiché — c'est un vrai voisinage — mais il n'est jamais ORIENTÉ d'un auteur vers l'autre.
SOURCES_TIERCES = re.compile(
    r"\b(sophokles|odipus|oedipus|jokaste|laios|hamlet|shakespeare|sancho|quijote|"
    r"goethe|schiller|nietzsche|homer|ovid)\b", re.I)


def aplatir(texte):
    """Texte réduit à des lettres, des chiffres et des espaces, bordé d'espaces.

    Sert à chercher un NOM PROPRE comme jeton exact. Le bordage permet d'écrire « le bon »
    entouré d'espaces sans se soucier du début ni de la fin de la chaîne, et l'écrasement de
    toute la ponctuation fait tomber les soulignés de mise en relief de Gutenberg — sans quoi
    trente atomes de Freud citant Le Bon restent invisibles (voir l'en-tête du module).
    """
    s = unicodedata.normalize("NFD", (texte or "").replace("ß", "ss"))
    s = "".join(c for c in s if unicodedata.category(c) != "Mn").lower()
    return " " + re.sub(r"[^a-z0-9]+", " ", s).strip() + " "


# Jetons de nom, par auteur du corpus. Écrits comme des ALTERNATIVES EXACTES bordées d'espaces :
# c'est ce qui écarte « Freude » sans avoir à énumérer ses formes. Le génitif allemand (« Freuds »)
# et l'adjectif (« Freudsche », « Freudschen ») sont des mentions et doivent compter.
NOMS = {
    "Sigmund Freud": [r" freud ", r" freuds ", r" freudsch\w* "],
    "Otto Rank": [r" rank ", r" ranks ", r" ranksch\w* "],
    "Karl Abraham": [r" abraham ", r" abrahams "],
    "Josef Breuer": [r" breuer ", r" breuers ", r" breuersch\w* "],
    "Gustave Le Bon": [r" le bon ", r" le bons "],
    # OUBLI RÉEL, trouvé en auditant la carte des citations et corrigé le 2026-07-29. Sándor
    # Ferenczi est entré dans le corpus sans que son nom entre dans cette table : il pesait 16,8 %
    # des atomes et AUCUN auteur ne pouvait être enregistré comme le nommant. Mesuré après
    # correction : 80 atomes le nomment (Freud 32, Rank 30, Abraham 18). Le couple
    # Freud ↔ Ferenczi paraissait donc unidirectionnel — un accident de configuration présenté
    # comme un fait de texte, ce que ce projet doit précisément éviter.
    "Sándor Ferenczi": [r" ferenczi ", r" ferenczis ", r" ferenczisch\w* ",
                        # L'OCR des Bausteine lit régulièrement « Ferenezi » (n pour n, c pour c) :
                        # relevé dans le texte, non supposé.
                        r" ferenezi ", r" ferenezis "],
}

# HOMOGRAPHES CONNUS — un nom d'auteur qui est aussi autre chose. Ils ne sont PAS filtrés
# automatiquement : on ne saurait pas le faire sans se tromper. Ils sont DÉCLARÉS, pour que la
# mention porte l'avertissement et que la lecture tranche.
# Mesuré : « Abraham » apparaît 62 fois chez Rank, et une partie est le patriarche biblique
# (« von der Geburt des Stammvaters der hebräischen Nation, von Abraham »), pas le collègue.
HOMOGRAPHES = {
    "Karl Abraham": ("« Abraham » est aussi le patriarche biblique, que Rank et Freud citent "
                     "abondamment dans leurs travaux sur le mythe. Toute mention de cet auteur "
                     "demande une lecture avant d'être comptée comme un renvoi au collègue."),
}


def mentions(atomes, auteur_atome):
    """Atomes où cet auteur nomme un AUTRE auteur du corpus → [{auteur_nomme, atome, homographe}].

    Fait de texte, vérifiable à l'œil : le nom est là ou il n'est pas là. Ce que la mention
    n'établit PAS, et qu'il ne faut jamais lui faire dire : la NATURE du rapport. Nommer n'est
    ni suivre, ni approuver, ni contredire. Le précédent du projet est net — le signal
    « ecart_freud » construit pour Rank a donné 0 confirmé sur 5 candidats : les cinq passages
    étaient des renvois d'ACCORD. Un motif localise, il ne qualifie pas.
    """
    out = []
    for a in atomes:
        plat = aplatir(a["texte"])
        for nomme, jetons in NOMS.items():
            if nomme == auteur_atome:
                continue                      # se nommer soi-même n'est pas une mention d'autrui
            if any(re.search(j, plat) for j in jetons):
                out.append({
                    "auteur_nomme": nomme,
                    "atome": a,
                    "homographe": HOMOGRAPHES.get(nomme),
                })
    return out


# Un vrai INTITULÉ de chapitre est COMPLET : il se termine par une ponctuation de fin.
# Cette condition n'est pas cosmétique, elle corrige un défaut mesuré. Le repérage de chapitre
# (`atomisation._CHAPITRE`) prend la ligne qui suit le chiffre romain et la tronque à 90 signes ;
# pour les œuvres dépourvues d'intitulé de section, cette ligne est la PREMIÈRE PHRASE du
# chapitre, coupée en plein mot. Sans ce filtre, « II. Ich knüpfe nun an meine früheren
# Bemerkungen an, bei meinen Versuchen, die Breuer'sche Meth » passait pour un chapitre que Freud
# consacrerait à Breuer : le fait est réel — il y parle bien de la méthode de Breuer — mais le
# présenter comme une déclaration d'édition le surinterprète.
# Mesuré alors : 57 intitulés complets retenus, 52 amorces de texte écartées. Le contrôle qui
# comptait : « II. Le Bon's Schilderung der Massenseele. » était conservé.
#
# CE FILTRE NE S'APPLIQUE PLUS QU'AU DÉTECTEUR COMMUN, et la nuance a été payée cher. Seize œuvres
# déclarent désormais leur propre motif de chapitre (`sources.MOTIFS_CHAPITRE`), relevé dans le
# texte et rejoué : leurs titres sont de VRAIS intitulés, et beaucoup ne se terminent par aucune
# ponctuation. Leur imposer ce filtre écartait des lectures bien réelles — « Zur Kritik der
# Rankschen ›Technik der Psychoanalyse‹ » de Ferenczi, qui est sa rupture avec Rank, ou « Die
# wissenschaftliche Bedeutung von Freuds ›Drei Abhandlungen zur Sexualtheorie‹ ». Le corpus n'en
# comptait qu'UNE alors qu'il en porte plusieurs.
_INTITULE_COMPLET = re.compile(r"[.!?»]\s*$")


def lectures_declarees(atomes, auteur_atome):
    """Chapitres dont le TITRE annonce qu'ils traitent d'un autre auteur → liens de chapitre.

    LA DIMENSION LA PLUS FORTE, et la moins chère. Quand Freud intitule un chapitre « II. Le
    Bon's Schilderung der Massenseele », il déclare lui-même, en tête de section, qu'il va rendre
    compte d'un autre auteur. Ce n'est pas une inférence : c'est l'édition qui le dit.

    C'est aussi le SEUL signal qui traverse la barrière des langues. Freud lit Le Bon en
    traduction allemande ; aucune reprise textuelle ne peut relier les deux corpus, puisqu'ils
    ne sont pas écrits dans la même langue. Sans cette dimension, la relation inter-auteurs la
    mieux documentée du corpus — 105 atomes — serait absente de la couche.
    """
    par_chapitre, declares = {}, set()
    for a in atomes:
        ch = a.get("chapitre")
        if not ch:
            continue
        if isinstance(ch, str):
            cle = ch
        else:
            cle = ("%s. %s" % (ch["numero"], ch["titre"])) if ch.get("numero") else ch["titre"]
            if ch.get("declare"):
                declares.add(cle)
        par_chapitre.setdefault(cle, []).append(a)

    out = []
    for titre, groupe in sorted(par_chapitre.items()):
        # Le filtre de complétude ne vaut que pour le détecteur COMMUN, qui peut prendre une
        # amorce de texte pour un titre. Un motif déclaré extrait un vrai intitulé.
        if titre not in declares and not _INTITULE_COMPLET.search(titre):
            continue
        plat = aplatir(titre)
        for nomme, jetons in NOMS.items():
            if nomme == auteur_atome:
                continue
            if any(re.search(j, plat) for j in jetons):
                out.append({
                    "auteur_lu": nomme,
                    "chapitre": titre,
                    # L'œuvre où se trouve le chapitre. Elle dit aussi d'où vient le repère —
                    # motif déclaré ou détecteur commun — ce dont dépend la confiance à lui
                    # accorder, le second pouvant prendre une amorce de texte pour un titre.
                    "oeuvre": groupe[0]["oeuvre"],
                    "atomes": groupe,
                    "portee": len(groupe),
                    "homographe": HOMOGRAPHES.get(nomme),
                })
    return out


def _n_grammes_utiles(atomes, frequences):
    """Index {atome_id: ensemble de n-grammes}, en écartant les atomes trop courts."""
    index = {}
    for a in atomes:
        if a["nb_mots"] < MOTS_MINIMUM:
            continue
        g = collation.ngrammes(collation.normaliser(a["texte"]), N_GRAMME)
        if g:
            index[a["id"]] = g
    return index


def frequences_documentaires(groupes):
    """Combien d'atomes portent chaque n-gramme, TOUS auteurs confondus.

    Sert à écarter la langue courante : une suite de six mots qu'on retrouve partout n'est pas
    une reprise. Calculée sur le corpus entier, donc identique quel que soit le couple d'auteurs
    examiné — une mesure de comparaison ne doit pas dépendre de l'ordre dans lequel on compare.
    """
    df = {}
    for index in groupes:
        for g in index.values():
            for x in g:
                df[x] = df.get(x, 0) + 1
    return df


def reprises(atomes_a, atomes_b, df=None):
    """Passages que deux auteurs ont en commun → [{a, b, partages, contenance}], triés.

    FORMULE, écrite sans ambiguïté parce qu'elle a été trouvée sous-spécifiée à la relecture —
    deux implémentations de bonne foi différaient d'un facteur 8 :
        G(x)  = TOUS les n-grammes de l'atome x                    (le dénominateur)
        D     = les n-grammes DISCRIMINANTS (df ≤ DOCUMENTS_MAXIMUM) (la condition d'admission)
        contenance(a, b) = |G(a) ∩ G(b)| / min(|G(a)|, |G(b)|)
    L'intersection doit contenir au moins deux n-grammes discriminants pour que la paire soit
    seulement examinée. Le dénominateur, lui, prend TOUS les n-grammes : rapporter une
    intersection filtrée à un ensemble filtré ferait monter le score des atomes les plus banals.

    Le rapport au PLUS COURT des deux, et non à l'union, est délibéré : une citation partielle
    (Freud cité dans une phrase de Rank plus longue) doit compter pour ce qu'elle est.
    """
    index_a = _n_grammes_utiles(atomes_a, df)
    index_b = _n_grammes_utiles(atomes_b, df)
    if df is None:
        df = frequences_documentaires([index_a, index_b])

    # Index inversé sur les seuls n-grammes discriminants : sans lui, la comparaison est
    # quadratique et devient impraticable au-delà de quelques milliers d'atomes.
    par_gramme = {}
    for ida, g in index_a.items():
        for x in g:
            if df.get(x, 0) <= DOCUMENTS_MAXIMUM:
                par_gramme.setdefault(x, []).append(ida)

    candidats = {}
    for idb, g in index_b.items():
        for x in g:
            if df.get(x, 0) <= DOCUMENTS_MAXIMUM:
                for ida in par_gramme.get(x, ()):
                    candidats[(ida, idb)] = candidats.get((ida, idb), 0) + 1

    par_id_a = {a["id"]: a for a in atomes_a}
    par_id_b = {b["id"]: b for b in atomes_b}
    out = []
    for (ida, idb), n_discriminants in candidats.items():
        if n_discriminants < 2:
            continue
        ga, gb = index_a[ida], index_b[idb]
        partages = ga & gb
        contenance = len(partages) / min(len(ga), len(gb))
        out.append({
            "a": par_id_a[ida],
            "b": par_id_b[idb],
            "partages": sorted(partages),
            "n_partages": len(partages),
            "n_discriminants": n_discriminants,
            "contenance": round(contenance, 4),
        })
    out.sort(key=lambda r: (-r["contenance"], -r["n_partages"]))
    return out


def evenements(liens):
    """Regroupe les paires d'atomes CONTIGUËS des deux côtés en un seul événement de reprise.

    L'unité qui compte n'est pas la phrase, c'est l'acte de citation. Un auteur qui recopie un
    paragraphe de trois phrases produit trois paires d'atomes ; les annoncer comme « trois
    liens » gonfle le chiffre et, pire, le gonfle INÉGALEMENT selon les auteurs — celui qui cite
    par longs blocs paraît lié trois fois plus que celui qui cite par touches.
    La paire d'atomes reste la preuve ; l'événement est ce qu'on compte et ce qu'on affiche.
    """
    restants = sorted(liens, key=lambda r: (r["a"]["index"], r["b"]["index"]))
    vus, out = set(), []
    for depart in restants:
        cle = (depart["a"]["id"], depart["b"]["id"])
        if cle in vus:
            continue
        suite, ia, ib = [depart], depart["a"]["index"], depart["b"]["index"]
        vus.add(cle)
        # On avance tant que les deux côtés progressent ensemble, d'un atome à la fois.
        avance = True
        while avance:
            avance = False
            for autre in restants:
                c2 = (autre["a"]["id"], autre["b"]["id"])
                if c2 in vus:
                    continue
                if autre["a"]["index"] == ia + 1 and autre["b"]["index"] == ib + 1:
                    suite.append(autre)
                    vus.add(c2)
                    ia, ib = autre["a"]["index"], autre["b"]["index"]
                    avance = True
                    break
        out.append({
            "paires": suite,
            "longueur": len(suite),
            "contenance_max": max(p["contenance"] for p in suite),
            "contenance_moyenne": round(sum(p["contenance"] for p in suite) / len(suite), 4),
        })
    out.sort(key=lambda e: (-e["longueur"], -e["contenance_max"]))
    return out


def direction(atome_a, atome_b):
    """Qui précède qui → 'a_vers_b', 'b_vers_a' ou None. JAMAIS deviné.

    Un atome ne porte pas une date mais une FENÊTRE : les œuvres de Freud sont lues dans des
    éditions tardives et il a cessé de signaler ses ajouts dès la 3e édition. On ne conclut donc
    que si les deux fenêtres sont DISJOINTES. Quand elles se chevauchent, le sens est indécidable
    et doit être affiché comme tel — c'est une information sur ce que le corpus permet, pas un
    manque à combler.

    La fenêtre est lue par `corpus.fenetre_datation`, qui sait déjà réconcilier les deux formes
    d'attestation (œuvre collationnée, datée par atome ; ou non collationnée, datée par édition).
    """
    from .corpus import fenetre_datation
    a_min, a_max = fenetre_datation(atome_a)
    b_min, b_max = fenetre_datation(atome_b)
    if a_max is None or b_max is None:
        return None
    if a_max < b_min:
        return "a_vers_b"
    if b_max < a_min:
        return "b_vers_a"
    return None


def qualifier(lien):
    """Ajoute à un lien de reprise ce qui est ÉTABLI sur lui — et rien de plus.

    Trois champs, tous vérifiables à l'œil sur les deux passages affichés côte à côte :
      • `force`      — « manifeste » ou « partielle », d'après la contenance mesurée ;
      • `source_tierce` — les deux passages nomment un auteur classique extérieur au corpus ;
        dans ce cas le lien n'est PAS orienté, parce que les deux peuvent tenir leur formulation
        de ce tiers plutôt que l'un de l'autre ;
      • `sens`       — seulement si les fenêtres de datation sont disjointes, jamais autrement.

    Ce que la fonction ne fait PAS, délibérément : nommer la NATURE du rapport. Aucun champ ne
    dira « socle », « emprunt » ou « contradiction ». Le précédent du projet est net — le signal
    « ecart_freud » nommait une nature que le motif ne prouvait pas, et n'a rien confirmé sur cinq
    candidats. On nomme ici le FAIT mesuré ; l'interprétation revient au lecteur, devant les deux
    passages.
    """
    a, b = lien["a"], lien["b"]
    tierce = bool(SOURCES_TIERCES.search(a["texte"]) and SOURCES_TIERCES.search(b["texte"]))
    sens = None if tierce else direction(a, b)
    return dict(lien, **{
        "force": "manifeste" if lien["contenance"] >= SEUIL_MANIFESTE else "partielle",
        "source_tierce": tierce,
        "sens": sens,
        "a_verifier": lien["contenance"] < SEUIL_MANIFESTE,
    })


def densite_comparee(motif, atomes_par_auteur, langue_par_auteur=None, langue_motif=None):
    """UN SEUL motif, appliqué à TOUS les corpus → densité par auteur et par œuvre.

    LA MÉTHODE QUI RÉSOUT LE PROBLÈME DE LA COMPARAISON, en le contournant.

    Comparer deux CONCEPTS d'auteurs différents demanderait de supposer qu'ils désignent la même
    chose — et cette supposition ne peut pas être validée : le seul témoin disponible dans la base
    (un concept comparé à lui-même, coupé en deux moitiés) mesure la stabilité d'échantillonnage
    d'une signature, pas une correspondance entre auteurs. C'est pourquoi l'appariement de concepts
    a été écarté.

    Comparer un MOT ne demande rien de tel. On applique le même motif partout et on compte : la
    mesure ne dépend plus d'aucune décision de lexicographe, seulement du texte.

    LA MÉTHODE A ÉTÉ VALIDÉE AVANT D'ÊTRE ÉCRITE, sur un cas où les deux mesures existent.
    Le concept « oedipus » a des motifs DIFFÉRENTS selon les lexiques — ['oedipus','odipus'] chez
    Freud, ['odipus','odipal'] chez Rank, ['odipus'] chez Abraham. Mesuré avec ces motifs propres :
    Freud 3,6 ‰, Rank 20,6 ‰. Mesuré avec un motif UNIQUE appliqué aux trois : Freud 3,2 ‰,
    Rank 21,6 ‰, Abraham 5,4 ‰. L'écart persiste presque à l'identique — il vient donc des
    AUTEURS, non des choix de motifs. C'est ce contrôle qui autorise à publier la mesure.

    CE QU'ELLE N'ÉTABLIT PAS, et qu'il ne faut jamais lui faire dire : que deux auteurs pensent
    la même chose quand ils emploient le même mot, ni qu'ils divergent quand l'un l'emploie moins.
    Elle mesure un USAGE DE MOT. Le reste demande de lire — et le corpus rend les passages.

    LIMITE DE LANGUE, dirimante : un motif allemand ne dit rien d'un corpus français. Les auteurs
    dont la langue diffère de celle du motif sont rendus avec une densité NULLE et non zéro —
    l'absence de mesure n'est pas une absence d'emploi.
    """
    # La langue du motif est DÉCLARÉE, jamais devinée. Une première version la déduisait du
    # premier auteur rencontré : le motif français « \bfoule » se retrouvait alors marqué
    # « non mesurable » sur le corpus de Le Bon, qui est précisément celui où il a un sens.
    # Deviner la langue d'une expression régulière n'est pas faisable de façon fiable — et ce
    # projet ne devine pas.
    langues = langue_par_auteur or {}
    re_motif = re.compile(motif)

    out = []
    for auteur in sorted(atomes_par_auteur):
        atomes = atomes_par_auteur[auteur]
        if not atomes:
            continue
        langue_auteur = langues.get(auteur)
        # DÉFAUT MESURÉ. Une langue inconnue valait auparavant « mesure quand même », et le
        # résultat était pire qu'inutile : Josef Breuer, dont le corpus est allemand, ressortait
        # à 0,0 ‰ sur le motif FRANÇAIS « \bfoule ». Ce zéro était vrai et vide de sens, et il
        # descendait le minimum du classement par contraste. Breuer passait au travers parce
        # qu'il est auteur d'ATOMES (ses parts des « Studien über Hysterie ») sans être auteur
        # d'une ŒUVRE : la table des langues, bâtie sur les œuvres, ne le connaissait pas.
        # On préfère désormais le silence à un zéro faux — voir `langues_par_auteur()`.
        if langue_auteur is None and langue_motif is not None and langues:
            out.append({"auteur": auteur, "atomes": len(atomes), "porteurs": None,
                        "pour_mille": None,
                        "non_mesurable": "langue du corpus de %s inconnue — on ne mesure pas un "
                                         "motif de langue déclarée sur un texte dont on ignore "
                                         "la langue" % auteur})
            continue
        comparable = langue_auteur is None or langue_motif is None or langue_auteur == langue_motif
        if not comparable:
            out.append({"auteur": auteur, "atomes": len(atomes), "porteurs": None,
                        "pour_mille": None,
                        "non_mesurable": "corpus en %s, motif en %s — un motif d'une langue ne dit "
                                         "rien d'un texte écrit dans une autre" % (langue_auteur, langue_motif)})
            continue
        porteurs = [a for a in atomes if re_motif.search(_replie(a))]
        par_oeuvre = {}
        for a in porteurs:
            par_oeuvre[a["oeuvre"]] = par_oeuvre.get(a["oeuvre"], 0) + 1
        total_oeuvre = {}
        for a in atomes:
            total_oeuvre[a["oeuvre"]] = total_oeuvre.get(a["oeuvre"], 0) + 1
        out.append({
            "auteur": auteur,
            "atomes": len(atomes),
            "porteurs": len(porteurs),
            "pour_mille": round(1000 * len(porteurs) / len(atomes), 1),
            "par_oeuvre": sorted(
                ({"oeuvre": o, "atomes": total_oeuvre[o], "porteurs": par_oeuvre.get(o, 0),
                  "pour_mille": round(1000 * par_oeuvre.get(o, 0) / total_oeuvre[o], 1)}
                 for o in total_oeuvre), key=lambda x: -x["pour_mille"]),
            "exemples": [{"id": a["id"], "oeuvre": a["oeuvre"], "texte": a["texte"][:400]}
                         for a in porteurs[:3]],
        })
    return {
        "motif": motif,
        "auteurs": out,
        "note": ("Le MÊME motif est appliqué à tous les corpus : la mesure ne dépend d'aucun "
                 "lexique, seulement du texte. Elle compare un USAGE DE MOT — pas une pensée."),
    }


def replier_comparaison(texte):
    """Forme repliée commune à la mesure de densité — minuscules, sans diacritiques, ß→ss."""
    s = unicodedata.normalize("NFD", (texte or "").replace("ß", "ss"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


# Le pliage est de loin l'opération la plus chère de la mesure de densité, et `table_des_usages`
# repasse ~200 motifs sur les ~45 000 atomes du corpus : replier à chaque fois faisait 9 millions
# de normalisations Unicode et dépassait les dix minutes. On plie donc UNE fois par atome.
#
# Le cache est EXTÉRIEUR aux atomes, volontairement. Ranger la forme repliée dans le dictionnaire
# de l'atome serait plus court, mais les atomes traversent les fiches d'agents et les exports :
# une clé technique ajoutée là ressortirait un jour dans une réponse d'API sans que personne ne
# l'ait voulu.
#
# La clé est le TEXTE, pas l'identifiant d'atome. Une première version indexait par identifiant,
# ce qui paraissait plus économique — un test l'a prise en défaut : deux jeux d'atomes distincts
# peuvent réutiliser les mêmes identifiants, et le cache rendait alors le pliage du MAUVAIS texte,
# sans rien signaler. Le corpus réel n'a pas de collision, mais un cache qui peut mentir en
# silence n'a pas sa place ici. Indexé par le texte, il est juste par construction.
_REPLIES = {}


def _replie(atome):
    texte = atome["texte"]
    r = _REPLIES.get(texte)
    if r is None:
        r = _REPLIES[texte] = replier_comparaison(texte)
    return r


def temoin_negatif(atomes_par_auteur):
    """Plancher de bruit, DÉTERMINISTE : deux auteurs allemands partagent-ils un n-gramme par
    hasard ? Appariement forcé par RANG, sans tirage aléatoire — donc reproductible à l'identique.

    Un témoin par échantillonnage aléatoire ne peut structurellement pas voir la queue de la
    distribution qu'il prétend borner ; celui-ci compare des atomes appariés position par
    position, ce qui est arbitraire mais total et rejouable.
    """
    noms = sorted(atomes_par_auteur)
    pires = []
    for i in range(len(noms)):
        for j in range(i + 1, len(noms)):
            a = [x for x in atomes_par_auteur[noms[i]] if x["nb_mots"] >= MOTS_MINIMUM]
            b = [x for x in atomes_par_auteur[noms[j]] if x["nb_mots"] >= MOTS_MINIMUM]
            pire = 0.0
            for x, y in zip(a, b):          # appariement par rang, tronqué au plus court
                gx = collation.ngrammes(collation.normaliser(x["texte"]), N_GRAMME)
                gy = collation.ngrammes(collation.normaliser(y["texte"]), N_GRAMME)
                if gx and gy:
                    pire = max(pire, len(gx & gy) / min(len(gx), len(gy)))
            pires.append({"couple": (noms[i], noms[j]), "contenance_max": round(pire, 4)})
    return {
        "methode": "appariement forcé par rang, sans tirage — reproductible",
        "couples": pires,
        "plancher": round(max([p["contenance_max"] for p in pires] or [0.0]), 4),
    }


def table_des_usages(atomes_par_auteur, langue_par_auteur):
    """Chaque sous-concept de CHAQUE lexique, mesuré sur TOUS les corpus de sa langue.

    C'est `densite_comparee` appliquée systématiquement. L'intérêt n'est pas la ligne d'un auteur
    sur son propre motif — le lexique a été écrit pour lui, elle est haute par construction — mais
    la ligne des AUTRES sur ce motif, que personne n'a choisie pour eux.

    Le motif garde la mention de qui l'a défini (`lexique`). Ce n'est pas un détail de traçabilité :
    tant qu'on sait que « geburtstrauma » vient du lexique de Rank, on lit le 141,4 ‰ de Rank comme
    une évidence et le 0,0 ‰ de Freud comme une information. Effacer la provenance ferait croire à
    une mesure neutre des deux côtés.

    Rend une liste de lignes plates, prête pour l'export SQL.
    """
    from . import lexiques as _lex, lexique as _base

    catalogue = [("Sigmund Freud", _base.CONCEPTS, "de")]
    for auteur, module in sorted(_lex.PAR_AUTEUR.items()):
        catalogue.append((auteur, module.CONCEPTS, module.LANGUE))

    lignes, vus = [], set()
    for proprietaire, concepts, langue in catalogue:
        for groupe, meta in sorted(concepts.items()):
            for sous, motifs in sorted(meta["termes"].items()):
                motif = r"\b(" + "|".join(motifs) + ")"
                # Deux lexiques peuvent définir le même sous-concept avec les mêmes motifs ; on
                # ne mesure qu'une fois, et on garde le premier propriétaire par ordre alphabétique.
                if (motif, langue) in vus:
                    continue
                vus.add((motif, langue))
                mesure = densite_comparee(motif, atomes_par_auteur, langue_par_auteur,
                                          langue_motif=langue)
                for a in mesure["auteurs"]:
                    if a["pour_mille"] is None:
                        continue
                    lignes.append({
                        "sous_concept": sous, "groupe": groupe, "libelle": meta["label"],
                        "lexique": proprietaire, "langue": langue, "motif": motif,
                        "auteur": a["auteur"], "atomes": a["atomes"],
                        "porteurs": a["porteurs"], "pour_mille": a["pour_mille"],
                    })
    return lignes


def langues_par_auteur(atomes, oeuvres):
    """Langue de chaque auteur, déduite de SES ATOMES et non des métadonnées d'œuvre.

    La différence n'est pas cosmétique. Une œuvre déclare UN auteur ; ses atomes peuvent en
    porter plusieurs. Les « Studien über Hysterie » sont enregistrées sous Freud, et Josef Breuer
    n'existe qu'au niveau des atomes — il était donc absent d'une table bâtie sur les œuvres, et
    se retrouvait mesuré contre des motifs français.

    Un auteur dont les atomes traversent plusieurs langues rend None : c'est un cas que le corpus
    ne connaît pas encore, et il vaut mieux qu'il soit signalé comme non mesurable que traité au
    petit bonheur.
    """
    vues = {}
    for a in atomes:
        auteur = a.get("auteur", "Sigmund Freud")
        lg = oeuvres.get(a["oeuvre"], {}).get("langue", "de")
        vues.setdefault(auteur, set()).add(lg)
    return {auteur: (lgs.pop() if len(lgs) == 1 else None) for auteur, lgs in vues.items()}
