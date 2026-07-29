#!/usr/bin/env python3
"""APPARIEMENT DE CONCEPTS — ce que la ressemblance de VOISINAGE établit, et ce qu'elle ne peut pas.

POURQUOI CE MODULE N'EXISTAIT PAS, ET POURQUOI IL EXISTE MAINTENANT.

`core/comparaison.py` avait explicitement ÉCARTÉ cette piste, et disait pourquoi : « aucun témoin
positif VALIDE n'existe aujourd'hui dans la base. Le seul disponible (un concept comparé à
lui-même, coupé en deux moitiés) mesure la stabilité d'échantillonnage d'une signature, pas la
correspondance entre deux auteurs. Un seuil calibré là-dessus mesurerait la reproductibilité et
serait présenté comme mesurant l'équivalence. »

Le témoin manquant est venu d'ailleurs. La couche « usage des mots » applique UN MÊME MOTIF à tous
les corpus. Le couple (motif M chez l'auteur A, motif M chez l'auteur B) est donc « le même mot
chez deux auteurs » : deux corpus distincts, deux jeux de phrases distincts, une identité lexicale
connue par construction. Ce n'est plus une moitié comparée à elle-même — c'est un couple
inter-auteurs dont on sait ce qui le lie.

  témoin POSITIF   (A, M) contre (B, M)     — même mot, deux auteurs
  témoin NÉGATIF   (A, M) contre (B, M')    — deux mots différents

CE QUE LA MESURE DIT, ET CE QU'ELLE NE DIT PAS.

Elle mesure la STABILITÉ DU VOISINAGE d'un mot d'un auteur à l'autre : les mots qui l'entourent
sont-ils les mêmes ? C'est un fait de texte, vérifiable en lisant les passages.

Elle n'établit à aucun moment que deux concepts sont ÉQUIVALENTS. Le témoin valide « même MOT »,
jamais « même CONCEPT » — et l'écart entre les deux est précisément l'objet du projet. On ne
trouvera donc ici ni « équivalent », ni « socle », ni « correspond à » : seulement un score de
proximité de voisinage, ses deux témoins, et les passages à lire.

LE RÉSULTAT LE PLUS UTILE EST LE PLUS BAS. Un même mot dont le voisinage DIVERGE d'un auteur à
l'autre, c'est la thèse fondatrice du projet enfin mesurée : `wasser`, `feuer`, `tier`,
`berg_hoehle`, `schuld` sont partagés par tous et n'ont pas la même compagnie chez chacun.
"""
import collections
import math
import re
import unicodedata

APPARIEMENT_VERSION = "1.0.0"

# Taille de la signature comparée. Mesurée : au-delà, on ajoute surtout du bruit de queue ; en
# deçà, les signatures des concepts larges deviennent instables d'un tirage à l'autre.
MOTS_COMPARES = 120

# Réserve conservée avant exclusion. Il en faut plus que MOTS_COMPARES, parce que l'exclusion
# retire des mots et qu'on veut pouvoir recompléter jusqu'à la taille cible.
MOTS_RESERVE = 400

# Sous ce nombre d'atomes porteurs, une signature décrit un échantillon, pas un usage.
MINIMUM_PORTEURS = 25

# Un mot présent dans moins de trois atomes porteurs ne caractérise rien.
MINIMUM_ATOMES_PAR_MOT = 3

_MOT = re.compile(r"[a-z]{4,}")


def plier(texte):
    """Forme repliée : minuscules, sans diacritiques, ß→ss. Commune à toute la comparaison."""
    s = unicodedata.normalize("NFD", (texte or "").replace("ß", "ss"))
    return "".join(c for c in s if unicodedata.category(c) != "Mn").lower()


def _radical(motif):
    """Le motif privé de sa frontière de mot initiale — pour le chercher AU MILIEU d'un mot.

    L'ALLEMAND COMPOSE, et c'est ce qui rend cette fonction nécessaire. Les motifs du lexique sont
    appliqués avec « \\b » en tête : « \\b(traum) » attrape « Traumdeutung » mais pas
    « Angsttraum », « Wunschtraum », « Kindertraum », où le radical est en seconde position. Or
    ces composés sont partagés par les deux auteurs comparés dès qu'ils emploient le même mot :
    les laisser dans la signature ferait valider le témoin positif PAR LUI-MÊME.
    """
    return re.sub(r"^\\b", "", motif.strip())


def mots_du_motif(motif, vocabulaire):
    """Les mots du vocabulaire que ce motif touche, radical compris où qu'il soit dans le mot."""
    r = re.compile(_radical(motif))
    return {m for m in vocabulaire if r.search(m)}


class Signatures:
    """Les signatures de voisinage d'un corpus, calculées une fois et réutilisées.

    La signature d'un couple (auteur, motif) est la liste des mots SUR-REPRÉSENTÉS chez les atomes
    qui portent le motif, relativement à la fréquence de ces mots CHEZ CET AUTEUR — jamais dans le
    corpus entier. Cette normalisation par auteur est ce qui empêche un tic d'écriture de faire se
    ressembler tous les concepts d'un même homme.
    """

    def __init__(self, atomes, langues):
        self.langues = langues
        self.sacs = collections.defaultdict(list)
        for a in atomes:
            auteur = a.get("auteur", "Sigmund Freud")
            p = plier(a["texte"])
            self.sacs[auteur].append((a, p, frozenset(_MOT.findall(p))))
        self.base = {}
        self.vocabulaire = {}
        for auteur, sac in self.sacs.items():
            n = collections.Counter()
            for _, _, s in sac:
                n.update(s)
            self.base[auteur] = (n, len(sac))
            self.vocabulaire[auteur] = set(n)
        self._cache = {}
        self._exclus = {}

    def auteurs(self, langue=None):
        return sorted(a for a in self.sacs
                      if langue is None or self.langues.get(a) == langue)

    def exclusion(self, auteur, motif):
        cle = (auteur, motif)
        if cle not in self._exclus:
            self._exclus[cle] = mots_du_motif(motif, self.vocabulaire[auteur])
        return self._exclus[cle]

    def signature(self, auteur, motif):
        """→ {mots pondérés, porteurs, oeuvres} ou None si le motif est trop peu porté."""
        cle = (auteur, motif)
        if cle in self._cache:
            return self._cache[cle]
        r = re.compile(motif)
        pts = [(a, s) for a, p, s in self.sacs[auteur] if r.search(p)]
        if len(pts) < MINIMUM_PORTEURS:
            self._cache[cle] = None
            return None
        n_base, total = self.base[auteur]
        local = collections.Counter()
        for _, s in pts:
            local.update(s)
        poids = {}
        for mot, k in local.items():
            if k < MINIMUM_ATOMES_PAR_MOT:
                continue
            # Log-odds pondéré par la racine du compte : retient ce qui est à la fois
            # sur-représenté ET attesté, plutôt que les hapax spectaculaires.
            poids[mot] = math.log((k / len(pts)) / ((n_base.get(mot, 0) + 0.5) / total)) \
                * math.sqrt(k)
        par_oeuvre = collections.Counter(a["oeuvre"] for a, _ in pts)
        fiche = {
            "mots": dict(sorted(poids.items(), key=lambda x: -x[1])[:MOTS_RESERVE]),
            "porteurs": len(pts),
            "oeuvres": dict(par_oeuvre),
            # Part des porteurs venant de l'œuvre dominante. Une signature concentrée à 90 % sur
            # un seul livre décrit le vocabulaire DE CE LIVRE autant que celui du concept — c'est
            # une réserve à porter, pas un défaut à corriger.
            "concentration": round(max(par_oeuvre.values()) / len(pts), 3),
        }
        self._cache[cle] = fiche
        return fiche

    def proximite(self, auteur_a, motif_a, auteur_b, motif_b):
        """Cosinus des deux signatures, LES DEUX MOTIFS RETIRÉS des deux côtés.

        Le retrait croisé n'est pas une précaution de style : sans lui, deux occurrences du même
        mot partageraient ce mot et toute sa famille de composés, et le témoin positif se
        validerait tout seul.
        """
        sa = self.signature(auteur_a, motif_a)
        sb = self.signature(auteur_b, motif_b)
        if not sa or not sb:
            return None
        retirer = (self.exclusion(auteur_a, motif_a) | self.exclusion(auteur_a, motif_b)
                   | self.exclusion(auteur_b, motif_a) | self.exclusion(auteur_b, motif_b))
        a = sorted(((m, v) for m, v in sa["mots"].items() if m not in retirer),
                   key=lambda x: -x[1])[:MOTS_COMPARES]
        b = sorted(((m, v) for m, v in sb["mots"].items() if m not in retirer),
                   key=lambda x: -x[1])[:MOTS_COMPARES]
        if not a or not b:
            return None
        na = math.sqrt(sum(v * v for _, v in a)) or 1.0
        nb = math.sqrt(sum(v * v for _, v in b)) or 1.0
        db = dict(b)
        return round(sum(v * db[m] for m, v in a if m in db) / (na * nb), 4)

    def partages(self, auteur_a, motif_a, auteur_b, motif_b, combien=12):
        """Les mots qui portent la proximité — pour qu'un score puisse être CONTESTÉ."""
        sa = self.signature(auteur_a, motif_a)
        sb = self.signature(auteur_b, motif_b)
        if not sa or not sb:
            return []
        retirer = (self.exclusion(auteur_a, motif_a) | self.exclusion(auteur_a, motif_b)
                   | self.exclusion(auteur_b, motif_a) | self.exclusion(auteur_b, motif_b))
        a = dict(sorted(((m, v) for m, v in sa["mots"].items() if m not in retirer),
                        key=lambda x: -x[1])[:MOTS_COMPARES])
        b = dict(sorted(((m, v) for m, v in sb["mots"].items() if m not in retirer),
                        key=lambda x: -x[1])[:MOTS_COMPARES])
        communs = [(m, round(a[m] * b[m], 3)) for m in set(a) & set(b)]
        return [m for m, _ in sorted(communs, key=lambda x: -x[1])[:combien]]


def dedoublonner(signatures, catalogue, langue="de"):
    """Écarte les sous-concepts qui sélectionnent LES MÊMES ATOMES sous un autre nom.

    DÉFAUT MESURÉ, et il faussait le témoin. Le lexique de Freud définit « kind » par
    « \\b(kind|kindheit|kindlich|infantil) » et « infantil » par
    « \\b(infantil|infantile|kindheit|kindlich|kind) » : deux chaînes différentes, un seul et même
    ensemble de phrases — « infantile » étant déjà couvert par « infantil ». Le témoin positif
    comptait donc deux fois le même couple, et le classement présentait « kind ↔ infantil » comme
    une belle correspondance à noms différents alors que c'est le même motif.

    Dédoublonner sur la CHAÎNE du motif ne suffit pas : il faut comparer ce que les motifs
    SÉLECTIONNENT. On garde le premier nom par ordre alphabétique, pour que le choix ne dépende
    pas de l'ordre d'itération des lexiques.
    """
    vus, garde = {}, {}
    for sous in sorted(catalogue):
        motif = catalogue[sous][0]
        empreinte = []
        for auteur in signatures.auteurs(langue):
            r = re.compile(motif)
            empreinte.append(frozenset(a["id"] for a, p, _ in signatures.sacs[auteur]
                                       if r.search(p)))
        cle = tuple(empreinte)
        if cle in vus:
            continue
        vus[cle] = sous
        garde[sous] = catalogue[sous]
    return garde


def reference(positifs):
    """La médiane de score attendue selon l'EFFECTIF et l'ÉCART DE TAILLE des deux côtés.

    POURQUOI UNE RÉFÉRENCE PAR CASE, ET NON UNE MÉDIANE GLOBALE. Deux mesures l'imposent :
    le score croît avec l'effectif (médiane 0,126 sous 50 porteurs, 0,297 au-delà de 500), et il
    décroît avec l'écart de taille entre les deux corpus — au point qu'un « détecteur » n'utilisant
    QUE le rapport des effectifs atteint déjà une AUC de 0,576. Juger un score bas contre la
    médiane globale reviendrait donc à confondre une divergence d'usage avec une différence de
    volume : plusieurs cas spectaculaires (« schmerz », « schuld », « motiv ») ne survivent pas à
    ce contrôle, et c'est exactement pourquoi il existe.
    """
    def case(e):
        n, d = e["porteurs_min"], e["ecart_taille"]
        return (0 if n < 50 else 1 if n < 100 else 2 if n < 200 else 3,
                0 if d < 0.5 else 1 if d < 1.0 else 2)

    cases = collections.defaultdict(list)
    for e in positifs:
        cases[case(e)].append(e["score"])
    medianes = {k: sorted(v)[len(v) // 2] for k, v in cases.items()}
    for e in positifs:
        e["reference"] = medianes[case(e)]
        e["ecart_a_la_reference"] = round(e["score"] - e["reference"], 4)
    return medianes


def temoins(signatures, catalogue, langue="de", graine=20260729):
    """LES DEUX TÉMOINS, mesurés sur le corpus réel. C'est la fonction qui fonde la couche.

    `catalogue` : {sous_concept: (motif, propriétaire, groupe)}.

    Rend les trois populations : positive (même mot), négative ALÉATOIRE (deux mots tirés au
    hasard) et négative DIFFICILE (deux mots du même groupe conceptuel — topiquement voisins,
    lexicalement distincts). La troisième est la seule qui compte vraiment : deux mots tirés au
    hasard parlent trivialement d'autre chose, et un seuil calibré là-dessus serait trop permissif.
    """
    import random
    auteurs = signatures.auteurs(langue)
    noms = sorted(catalogue)
    par_groupe = collections.defaultdict(list)
    for sous, (_, _, groupe) in catalogue.items():
        par_groupe[groupe].append(sous)

    alea = random.Random(graine)      # rejouable à l'identique, jamais un tirage libre
    positifs, negatifs, difficiles = [], [], []
    for i, x in enumerate(auteurs):
        for y in auteurs[i + 1:]:
            for sous in noms:
                m = catalogue[sous][0]
                s = signatures.proximite(x, m, y, m)
                if s is not None:
                    sa, sb = signatures.signature(x, m), signatures.signature(y, m)
                    positifs.append({
                        "auteurs": (x, y), "sous": sous, "score": s,
                        "porteurs_a": sa["porteurs"], "porteurs_b": sb["porteurs"],
                        "porteurs_min": min(sa["porteurs"], sb["porteurs"]),
                        # L'écart de taille est porté avec le score, jamais séparément : sans lui
                        # un score bas se lit comme une divergence d'usage alors qu'il peut n'être
                        # qu'une différence de volume entre les deux corpus.
                        "ecart_taille": round(abs(math.log(sa["porteurs"] / sb["porteurs"])), 3),
                        "concentration_max": max(sa["concentration"], sb["concentration"]),
                    })
            tirage = list(noms)
            alea.shuffle(tirage)
            for a, b in zip(noms, tirage):
                if a == b:
                    continue
                s = signatures.proximite(x, catalogue[a][0], y, catalogue[b][0])
                if s is not None:
                    negatifs.append({"auteurs": (x, y), "sous": (a, b), "score": s})
            for groupe, membres in sorted(par_groupe.items()):
                for j, a in enumerate(sorted(membres)):
                    for b in sorted(membres)[j + 1:]:
                        s = signatures.proximite(x, catalogue[a][0], y, catalogue[b][0])
                        if s is not None:
                            difficiles.append({"auteurs": (x, y), "sous": (a, b),
                                               "groupe": groupe, "score": s})
    return {"positifs": positifs, "negatifs": negatifs, "difficiles": difficiles}


def separation(positifs, negatifs):
    """Ce que les deux témoins établissent — ou n'établissent pas.

    On ne rend PAS un « seuil » nu. On rend les deux distributions et la part des positifs qui
    dépasse les centiles du bruit : c'est ce qui permet à un lecteur de juger lui-même si la
    discrimination suffit à son usage, au lieu de lui vendre une frontière.
    """
    vp = sorted(x["score"] for x in positifs)
    vn = sorted(x["score"] for x in negatifs)
    if not vp or not vn:
        return None

    def centile(v, q):
        return v[min(int(q * len(v)), len(v) - 1)]

    c95, c99 = centile(vn, 0.95), centile(vn, 0.99)
    return {
        "positifs": len(vp), "negatifs": len(vn),
        "mediane_positive": round(vp[len(vp) // 2], 4),
        "mediane_negative": round(vn[len(vn) // 2], 4),
        "bruit_95": round(c95, 4), "bruit_99": round(c99, 4),
        "part_positifs_au_dessus_95": round(sum(1 for s in vp if s > c95) / len(vp), 3),
        "part_positifs_au_dessus_99": round(sum(1 for s in vp if s > c99) / len(vp), 3),
        "note": ("La discrimination est PARTIELLE, et le chiffre à retenir est celui-là : au "
                 "seuil qui ne laisse passer que 5 % du bruit, une partie seulement des couples "
                 "de même mot est retrouvée. Ce détecteur classe des candidats à lire ; il ne "
                 "tranche pas."),
    }
