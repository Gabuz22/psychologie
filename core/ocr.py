#!/usr/bin/env python3
"""OCR — traiter les sources NON RELUES (fac-similés d'archive.org), sans mentir sur leur état.

POURQUOI CE MODULE EXISTE, ALORS QUE LE PROJET AVAIT REFUSÉ L'OCR.

Pour Freud, le refus était évident : Project Gutenberg offrait une transcription relue par des
humains, et prendre un fac-similé aurait dégradé le texte sans aucune contrepartie (2 716
caractères parasites, des jetons corrompus du genre « Patielitin » pour *Patientin*). Le refus
portait donc sur un ARBITRAGE, pas sur l'OCR en soi.

Pour l'entourage de Freud — Rank, Abraham, Ferenczi, Stekel —, cet arbitrage n'existe plus :
aucune de leurs œuvres n'a été transcrite par des humains, ni sur Gutenberg, ni sur Wikisource.
Le choix réel est « OCR ou rien ». Renoncer reviendrait à laisser le corpus définitivement
monopolaire, alors que la comparaison entre auteurs est le but même du projet.

La doctrine, elle, ne bouge pas d'un pouce : **une limite se mesure et s'affiche, elle ne se
cache pas.** Ce module fait donc exactement deux choses, et rien de plus :

  1. `mesurer()` — chiffre la qualité d'un texte, dans les mêmes unités que les textes relus,
     pour que la comparaison soit possible et que la réserve portée par chaque œuvre soit un
     NOMBRE, jamais un adjectif vague.
  2. `recoller_cesures()` — répare le seul défaut SYSTÉMATIQUE de ces scans : la césure de fin
     de ligne (« Ent-\\nstehung »), que les relecteurs de Gutenberg résolvent et que l'OCR
     laisse telle quelle. Mesuré : 0 à 4 césures dans les textes relus, 305 à 5 125 dans les
     scans de Rank. Sans réparation, « Entstehung » n'existerait tout simplement pas dans le
     corpus, et une citation sur cent serait coupée en deux.

CE QUE CE MODULE NE FAIT PAS : corriger des mots. Un « Kealen » pour *Realen* resterait tel
quel — le repérer demanderait de deviner, et le projet ne devine pas. Ces résidus sont comptés
par `mesurer()` et portés par l'œuvre comme une réserve explicite.
"""
import re
import unicodedata

# Césure de fin de ligne : une lettre, un trait d'union, un saut de ligne, puis la suite du mot.
# On exige une MINUSCULE après le saut : en allemand, un trait d'union suivi d'une majuscule est
# presque toujours un vrai trait d'union de composition (« Ich-Analyse », « Über-Ich »), qu'il ne
# faut surtout pas souder — c'est ainsi qu'est écrit le surmoi, concept central du corpus.
_CESURE = re.compile(r"([A-Za-zÄÖÜäöüß]{2,})-[ \t]*\n[ \t]*([a-zäöüß]+)")


# Coordination à premier terme ÉLIDÉ : « Sexual- und Aggressionstriebe ». C'est le SEUL cas où
# un trait d'union suivi d'une minuscule ne marque pas une coupure de mot — l'allemand écrit
# alors le trait d'union pour signaler la partie sous-entendue. Tombée en fin de ligne, la forme
# donne « Sexual-\nund », que souder produirait « Sexualund ». Liste close, vérifiée sur le
# corpus : ce sont les seules conjonctions qui peuvent suivre une élision.
_CONJONCTIONS = {"und", "oder", "aber", "sowie", "bzw", "wie", "noch", "sondern"}


def recoller_cesures(texte, vocabulaire):
    """Recolle les mots coupés en fin de ligne → (texte, rapport). Déterministe, en DEUX degrés.

    Degré 1 — le mot reconstitué est ATTESTÉ dans le vocabulaire de référence (corpus déjà relu
    par des humains). Aucun risque : la forme existe.

    Degré 2 — l'ORTHOGRAPHE allemande tranche seule. Un trait d'union en fin de ligne suivi d'une
    minuscule EST une coupure de syllabe, sauf devant une conjonction élidée (voir `_CONJONCTIONS`)
    et sauf devant une majuscule, déjà exclue par le motif — « Ich-Analyse », « Über-Ich » sont de
    vrais traits d'union de composition, et souder le surmoi serait un beau dégât.
    Ce second degré est indispensable pour un auteur qui n'est pas Freud : Rank écrit
    « Brautgemach », « Seelenforschung », « Forschungsmethoden », mots parfaitement corrects que
    Freud n'emploie jamais. Les exiger attestés reviendrait à ne réparer que le vocabulaire d'un
    autre auteur — c'est-à-dire à mesurer Rank avec la langue de Freud, exactement ce que
    l'architecture par auteur cherche à éviter.

    Les deux degrés sont comptés SÉPARÉMENT dans le rapport : le lecteur voit ce qui a été réparé
    sur preuve et ce qui l'a été sur règle. Ce qui n'est recollé par aucun des deux garde son
    trait d'union et reste compté.
    """
    compte = {"attestees": 0, "regle": 0}

    def remplacer(m):
        gauche, droite = m.group(1), m.group(2)
        if (gauche + droite).lower() in vocabulaire:
            compte["attestees"] += 1
            return gauche + droite
        if droite.lower() in _CONJONCTIONS:
            return m.group(0)                    # élision : le trait d'union est voulu
        compte["regle"] += 1
        return gauche + droite

    # Deux passes : une césure peut suivre immédiatement la précédente sur la ligne suivante,
    # et `re.sub` ne revient pas en arrière sur le texte qu'il vient d'écrire.
    resultat = _CESURE.sub(remplacer, texte)
    resultat = _CESURE.sub(remplacer, resultat)

    laisses = [m.group(1) + "-" + m.group(2) for m in _CESURE.finditer(resultat)]
    return resultat, {
        "cesures_recollees_attestees": compte["attestees"],
        "cesures_recollees_par_regle": compte["regle"],
        "cesures_laissees": len(laisses),
        "exemples_laisses": laisses[:8],
    }


# CORRUPTION DU DIGRAMME « ch ». La typographie allemande ancienne lie le c et le h, et deux
# moteurs d'OCR échouent dessus de deux façons distinctes — toutes deux observées sur les scans
# de Rank, et toutes deux invisibles au comptage de caractères parasites (les formes produites
# ne contiennent que des lettres parfaitement ordinaires) :
#
#   • « ch » → « di »  — « nicht » devient « nidit », « Persönlichkeit » « Persönlidikeit ».
#     Mesuré sur « Die Don Juan-Gestalt » (1924) : 30 des 92 « nicht », 184 séquences en tout.
#   • « ch » → « h »   — le c disparaît : « sich » → « sih », « auch » → « auh », « natürlich »
#     → « natürlih ». Mesuré sur « Der Doppelgänger » (1925) : 51 occurrences, 5,1 %.
#
# Le second défaut a failli passer : le premier contrôle, écrit pour « di », donnait 0 % sur le
# Doppelgänger. C'est la LECTURE d'un passage qui l'a révélé. Leçon déjà connue du corpus —
# un contrôle ne prouve que ce qu'il mesure ; on lit toujours le texte avant de le déclarer sain.
_IMPOSSIBLES_DI = ("nidit", "sdiaft", "lidikeit", "spradie", "welder", "mensdi",
                   "gesdi", "zwisdi", "psydi")
_PAIRES_CH = [("sich", "sih"), ("auch", "auh"), ("nicht", "niht"), ("noch", "noh"),
              ("durch", "duh"), ("mich", "mih"), ("doch", "doh"), ("welche", "welhe")]

# Motif servant à marquer les ATOMES individuellement (voir `phrase_suspecte`). Il réunit les
# formes corrompues attestées et les terminaisons impossibles en allemand.
_SUSPECT = re.compile(
    r"\b(?:" + "|".join(_IMPOSSIBLES_DI) + r"|" + "|".join(b for _, b in _PAIRES_CH) + r")\b"
    r"|[a-zäöü]{3,}(?:lih|shen|sh|uh)\b")


def corruption(texte):
    """Corruption du digramme « ch », les DEUX défauts → taux par mot et par phrase.

    Le taux par PHRASE est celui qui décide, parce qu'un atome est une phrase : c'est la part
    des citations qui sortiraient fautives. Mesuré sur les sept fac-similés de Rank : 0,0 à
    1,0 % pour cinq d'entre eux, 7,1 % pour le Doppelgänger, et le Don Juan hors concours.
    """
    t = texte.lower()
    bon = sum(len(re.findall(r"\b%s\b" % a, t)) for a, _ in _PAIRES_CH)
    mal = sum(len(re.findall(r"\b%s\b" % b, t)) for _, b in _PAIRES_CH)
    mal += len(re.findall(r"\bnidit\b", t))
    phrases = [p for p in re.split(r"(?<=[.!?])\s+", texte) if len(p.split()) >= 5]
    atteintes = sum(1 for p in phrases if _SUSPECT.search(p.lower()))
    return {
        "mots_corrects": bon,
        "mots_corrompus": mal,
        "taux_mots_pct": round(100 * mal / max(bon + mal, 1), 1),
        "phrases_mesurees": len(phrases),
        "phrases_atteintes": atteintes,
        "taux_phrases_pct": round(100 * atteintes / max(len(phrases), 1), 1),
        "sequences_impossibles": sum(t.count(s) for s in _IMPOSSIBLES_DI),
    }


# Au-dessus de ce taux de phrases atteintes, une œuvre est ÉCARTÉE du corpus. En dessous, elle
# entre, et chaque phrase touchée est marquée individuellement (`phrase_suspecte`).
#
# Le seuil n'est pas un chiffre rond posé au hasard, il sépare deux régimes que les mesures
# distinguent nettement. En dessous, le défaut est SPORADIQUE : treize phrases sur mille trois
# cents dans le Mythus, qu'on peut marquer une à une, laissant les autres pleinement fiables.
# Au-dessus, il est SYSTÉMATIQUE : marquer une phrase sur quatorze ne sauve rien, car le lecteur
# ne peut plus se fier non plus à celles qui ne sont pas marquées — le défaut est partout, le
# contrôle n'en attrape qu'une partie. Deux œuvres ont été écartées par ce seuil, et le dépôt
# garde leur mesure (voir `sources.FAC_SIMILES_ECARTES`).
SEUIL_PHRASES_CORROMPUES_PCT = 2.0


def _ligne_illisible(ligne, vocabulaire):
    """Cette ligne est-elle du charabia de scan ? Deux signaux, tous deux nécessaires.

    Les volumes numérisés contiennent des pages qui ne sont pas du texte : couvertures, gardes en
    papier marbré, filets d'encadrement. L'OCR en tire des suites de fragments d'une ou deux
    lettres (« DENT IN N w s Ka a le N IM in Tr »). Deux mesures les séparent de la prose :
      • une prose allemande a 14 % de jetons courts (1-2 lettres) ; ce charabia en a 78 % ;
      • ses mots longs sont attestés à 84 % ; ceux du charabia à 16 %.
    Aucun des deux signaux ne suffit seul — c'est leur conjonction qui décide.
    """
    toks = re.findall(r"[a-zäöüßA-ZÄÖÜ]+", ligne)
    if len(toks) < 3:
        return False                      # trop court pour juger : on ne juge pas
    courts = sum(1 for w in toks if len(w) <= 2) / len(toks)
    longs = [w for w in toks if len(w) >= 3]
    attestes = sum(1 for w in longs if w.lower() in vocabulaire) / max(len(longs), 1)
    return courts > 0.40 and attestes < 0.50


def _ligne_lisible(ligne, vocabulaire, exigeante=False):
    """Cette ligne est-elle de la prose allemande CERTAINE ? Le contraire d'illisible n'est pas
    lisible : entre les deux se trouvent les lignes trop courtes pour être jugées (numéros de
    page, titres coupés, mots isolés), qui ne prouvent rien ni dans un sens ni dans l'autre.

    `exigeante` durcit le critère, pour le seul rognage aux extrémités. Il l'a fallu : la ligne
    de charabia « ll ARM arme Bu Bu: Ri use an N Ne ir Ip IN N A a | (R in » compte trois mots
    longs dont deux existent en allemand (*arm*, *Arme*), et passait pour de la prose — elle
    retenait alors toute une page de garde dans le volume. Cinq mots longs attestés à 70 % ne se
    rencontrent pas par accident dans du bruit de scan.
    """
    longs = [w for w in re.findall(r"[a-zäöüßA-ZÄÖÜ]+", ligne) if len(w) >= 3]
    minimum, seuil = (5, 0.70) if exigeante else (3, 0.60)
    if len(longs) < minimum:
        return False
    return sum(1 for w in longs if w.lower() in vocabulaire) / len(longs) >= seuil


# Une ligne isolée peut ressembler à du charabia sans en être — une note bibliographique en
# abrégé, une ligne de chiffres, un vers cité. Mesuré : la règle ligne à ligne prend à tort 7 %
# des lignes d'un texte réel, ce qui serait une destruction inacceptable dans un corpus fait
# pour citer.
#
# Ce qui distingue vraiment le charabia, c'est son VOISINAGE : une page de garde scannée produit
# des dizaines de lignes illisibles sans une seule ligne de prose au milieu. On ne juge donc
# jamais une ligne seule, mais la fenêtre qui l'entoure — et il suffit d'UNE ligne de prose
# certaine dans cette fenêtre pour que rien ne soit retiré. Un texte réel est ainsi protégé même
# quand le scan y glisse quelques lignes de bruit.
_FENETRE = 10
_ILLISIBLES_MINIMUM = 5
_LISIBLES_TOLEREES = 1


def retirer_blocs_illisibles(texte, vocabulaire):
    """Retire les ZONES de charabia de scan → (texte, rapport). Jamais une ligne isolée.

    Ces zones sont les couvertures, gardes en papier marbré et filets d'encadrement numérisés
    avec le volume : elles n'appartiennent pas à l'œuvre, et sans elles le dernier atome d'un
    livre serait « Pen er y ww bo: ji zu, 77 x ».
    """
    lignes = texte.split("\n")
    illisible = [_ligne_illisible(l, vocabulaire) for l in lignes]
    lisible = [_ligne_lisible(l, vocabulaire) for l in lignes]
    a_retirer = set()
    for i in range(len(lignes)):
        if lisible[i]:
            continue                              # prose CERTAINE : jamais retirée, quoi qu'il arrive
        # Tout le reste — lignes illisibles, mais aussi lignes trop courtes pour être jugées
        # (numéros de page, fragments) — n'est retiré que si son VOISINAGE est condamné. C'est
        # ce qui permet d'emporter une page de garde entière sans toucher au texte : dans un
        # vrai chapitre, la moindre ligne de prose voisine suffit à tout protéger.
        a, b = max(0, i - _FENETRE), min(len(lignes), i + _FENETRE + 1)
        if (sum(illisible[a:b]) >= _ILLISIBLES_MINIMUM
                and sum(lisible[a:b]) <= _LISIBLES_TOLEREES):
            a_retirer.add(i)
    garde = [l for i, l in enumerate(lignes) if i not in a_retirer]
    return "\n".join(garde), {
        "lignes_retirees": len(a_retirer),
        "lignes_totales": len(lignes),
        "part_pct": round(100 * len(a_retirer) / max(len(lignes), 1), 1),
    }


def rogner_aux_extremites(texte, vocabulaire):
    """Coupe avant la PREMIÈRE et après la DERNIÈRE ligne de prose certaine → (texte, rapport).

    Règle d'une solidité particulière, parce qu'elle ne suppose rien : ce qui précède la première
    phrase du livre et ce qui suit la dernière ne PEUT pas être du texte de l'auteur. Dans ces
    fac-similés, c'est la couverture, la garde en papier marbré, le filet d'encadrement, la fiche
    de prêt de la bibliothèque. Sans ce rognage, le dernier atome du « Mythus » serait
    « Pen er y ww bo: ji zu, 77 x » — une citation attribuée à Otto Rank.

    Elle ne peut pas mordre sur l'œuvre : elle s'arrête exactement à une ligne de prose attestée.
    """
    lignes = texte.split("\n")
    indices = [i for i, l in enumerate(lignes) if _ligne_lisible(l, vocabulaire, exigeante=True)]
    if not indices:
        return texte, {"rogne_tete": 0, "rogne_queue": 0, "note": "aucune prose certaine trouvée"}
    premier, dernier = indices[0], indices[-1]
    return "\n".join(lignes[premier:dernier + 1]), {
        "rogne_tete": premier,
        "rogne_queue": len(lignes) - 1 - dernier,
        "note": "rogné à la première et à la dernière ligne de prose attestée",
    }


def phrase_suspecte(texte):
    """Cette phrase porte-t-elle une trace de corruption OCR ? Marque l'atome, ne le corrige pas.

    Doctrine du corpus : ce qui n'est pas sûr est AFFICHÉ comme tel, jamais deviné ni tu. Une
    citation issue d'un atome marqué reste consultable — le lecteur sait seulement qu'il doit
    la vérifier sur le fac-similé avant de la publier.
    """
    return bool(_SUSPECT.search(texte.lower()))


# Caractères qu'un texte allemand imprimé peut légitimement contenir. Tout le reste est un
# artefact du scan : bordure de page, tache, papier marbré des gardes, filet d'encadrement.
_ATTENDUS = set(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "äöüÄÖÜßéèêëàâçñíóúāēīōūαβγδεζηθικλμνξοπρστυφχψω"      # grec : Rank cite les mythes en VO
    "0123456789 \n\t.,;:!?()[]«»„“”\"'’‘-–—/*§†%&+=°_|"
)


def mesurer(texte, vocabulaire):
    """Qualité chiffrée d'un texte, dans les unités qui servent aussi aux textes relus.

    Trois mesures, choisies parce qu'elles séparent réellement un scan propre d'un scan sale
    (vérifié sur les deux populations) :

      • `parasites_pour_mille` — caractères impossibles dans un texte allemand imprimé.
        Étalon mesuré sur quatre œuvres relues : 0,45 à 1,23 ‰.
      • `mots_attestes_pct` — part du vocabulaire retrouvée dans le corpus déjà relu.
        Étalon : 93,0 à 95,7 %. ATTENTION à l'interprétation : un écart ne prouve PAS une
        corruption. Rank écrit sur les mythes, avec des centaines de noms propres absents de
        Freud (Astyages, Harpagos, Telephos, Sargon) ; ils comptent ici comme « non attestés »
        alors qu'ils sont parfaitement corrects. Cette mesure sert d'ALERTE, pas de verdict.
      • `cesures_restantes` — mots encore coupés après recollage. Étalon : 0 à 4.

    S'y ajoute `corruption`, le contrôle qui DISQUALIFIE (voir plus haut).

    Aucun seuil n'est appliqué ici : ce module mesure, il ne juge pas. C'est le registre des
    œuvres qui déclare ce qu'il accepte, et le lecteur qui voit le chiffre.
    """
    mots = [m for m in re.findall(r"[a-zäöüß]+", texte.lower()) if len(m) >= 3]
    attestes = sum(1 for m in mots if m in vocabulaire)
    return {
        "caracteres": len(texte),
        "mots_mesures": len(mots),
        "parasites_pour_mille": round(1000 * sum(1 for c in texte if c not in _ATTENDUS)
                                      / max(len(texte), 1), 2),
        "mots_attestes_pct": round(100 * attestes / max(len(mots), 1), 1),
        "cesures_restantes": len(_CESURE.findall(texte)),
        "corruption": corruption(texte),
    }


def vocabulaire_de_reference(textes):
    """Formes fléchies attestées dans des textes RELUS — la référence du recollage et du contrôle.

    Construite uniquement à partir de sources relues par des humains : y verser un texte OCR
    reviendrait à faire valider les erreurs de l'OCR par elles-mêmes.
    """
    voc = set()
    for t in textes:
        voc |= set(re.findall(r"[a-zäöüßA-ZÄÖÜ]+", t.lower()))
    return voc


# Une TÊTE COURANTE est la ligne que l'imprimeur répète en haut de chaque page : numéro de page
# et titre de l'ouvrage, du chapitre, ou nom de l'auteur. L'OCR la lit comme n'importe quelle
# autre ligne, et comme elle tombe entre les deux moitiés d'une phrase que la page a coupée,
# elle se retrouve SOUDÉE au milieu de cette phrase.
#
# Elle échappe à `retirer_blocs_illisibles` : « 122 S. Ferenczi » est parfaitement lisible.
#
# LE DÉGÂT EST MESURÉ, et il n'est pas celui qu'on croit. Il ne porte presque pas sur la longueur
# des atomes (281 signes avant, 281 après sur le corpus de Ferenczi). Il porte sur deux choses :
#   • les suites de six mots, brisées au milieu des phrases — c'est-à-dire l'unité exacte sur
#     laquelle travaille la couche de comparaison inter-auteurs ;
#   • le COMPTE DES CONCEPTS. « Das Trauma der Geburt » figure 85 fois en tête de page dans le
#     livre de Rank de 1924, « Versuch einer Genitaltheorie » 48 fois chez Ferenczi : le titre de
#     l'ouvrage vient gonfler la densité du concept dont l'ouvrage traite. C'est le pire cas
#     possible — un artefact typographique qui ressemble exactement au résultat attendu.
#
# LA RÈGLE NE CONNAÎT AUCUN TITRE. Elle ne repère pas ce qu'on lui a dit de chercher, elle repère
# ce qui SE RÉPÈTE : une même ligne courte, accompagnée de numéros de page DIFFÉRENTS, au moins
# cinq fois dans le volume. Un vers refrain ou une phrase deux fois écrite ne remplit pas ces
# conditions ; une tête courante les remplit toutes.
_LIGNE_TETE = re.compile(r"^[^\w\n]*(?:(\d{1,4})[^\w\n]+)?(.{3,60}?)(?:[^\w\n]+(\d{1,4}))?[^\w\n]*$")

REPETITIONS_MINIMUM = 5
NUMEROS_DISTINCTS_MINIMUM = 3


def _cle_tete(s):
    s = unicodedata.normalize("NFD", s.lower())
    s = "".join(c for c in s if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z]+", " ", s).strip()


# BANDEAU DE NUMÉRISATION, déposé en pied de page par les scans Google. Il s'insère AU MILIEU des
# phrases coupées par le saut de page — le retirer les recolle, ce qui est le comportement voulu.
#
# LE CRITÈRE EST UN ANACHRONISME, ce qui le rend décidable sans jamais lire le contexte : aucun
# texte allemand de 1907-1917 ne contient le mot « Google ». On peut donc retirer TOUTES ses
# occurrences sans risque d'emporter du texte d'auteur — c'est un des rares nettoyages du projet
# qui ne demande aucun arbitrage.
#
# Les formes sont relevées, non supposées : l'OCR massacre le bandeau de vingt-huit façons —
# « Digitized by Google » (217 fois) mais aussi « (iby Google » (346), « dhyGoogle », « chyGoogle »,
# « DigilizeilbyGoOgle », « DiriitizedhyGoOgle ». Le seul invariant est la suite « go?ogle », à
# une capitale près au milieu. On emporte donc le mot ET les caractères accolés, qui sont le
# reliquat de « Digitized by » écrasé par la reconnaissance.
_BANDEAU_SCAN = re.compile(r"\S*[Gg][Oo]{1,2}[Gg][Ll][Ee]\S*|Digiti[sz]ed\s+by", re.I)


def retirer_bandeau_scan(texte):
    """Retire le bandeau de numérisation des scans Google. Rend (texte, rapport).

    Mesuré à l'entrée de Wilhelm Stekel, dont deux volumes viennent de Google : 2,2 % et 3,2 %
    des phrases en portaient un — soit 616 phrases publiées avec « Digitized by Google » au
    milieu. Le mot « google » y était le TROISIÈME plus caractéristique de l'auteur, mesuré
    contre tout le reste du corpus allemand : un lexique construit sans ce nettoyage aurait
    donné à Stekel un vocabulaire signature de bibliothécaire numérique.
    """
    n = len(_BANDEAU_SCAN.findall(texte))
    if not n:
        return texte, {"bandeaux_retires": 0}
    net = _BANDEAU_SCAN.sub(" ", texte)
    net = re.sub(r"[ \t]{2,}", " ", net)
    return net, {"bandeaux_retires": n}


def retirer_tetes_courantes(texte):
    """Retire les lignes de tête courante répétée. Rend (texte, rapport)."""
    groupes = {}
    for ligne in texte.split("\n"):
        m = _LIGNE_TETE.match(ligne)
        if not m or not (m.group(1) or m.group(3)):
            continue
        cle = _cle_tete(m.group(2))
        if len(cle) < 4:
            continue
        groupes.setdefault(cle, []).append((ligne, m.group(1) or m.group(3)))

    a_retirer, formes = set(), []
    for cle, cas in groupes.items():
        numeros = {n for _, n in cas}
        # Deux conditions, et la seconde compte autant que la première : une ligne répétée avec
        # TOUJOURS LE MÊME numéro n'est pas une tête courante, c'est un artefact de scan ou une
        # vraie répétition du texte. Une tête courante change de numéro à chaque page.
        if len(cas) >= REPETITIONS_MINIMUM and len(numeros) >= NUMEROS_DISTINCTS_MINIMUM:
            formes.append((cle, len(cas)))
            a_retirer.update(l for l, _ in cas)

    if not a_retirer:
        return texte, {"tetes_retirees": 0, "formes": []}
    gardees = [l for l in texte.split("\n") if l not in a_retirer]
    return "\n".join(gardees), {
        "tetes_retirees": sum(n for _, n in formes),
        "formes": sorted(formes, key=lambda x: -x[1]),
    }
