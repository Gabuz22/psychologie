#!/usr/bin/env python3
"""AGENTS DÉTERMINISTES — ce qui transforme des atomes en lecture du corpus.

Chaque agent répond à UNE question, sans modèle de langage, sans réseau, sans aléa : même corpus,
même réponse, toujours. C'est ce qui rend une analyse reproductible — et donc discutable par un
chercheur, qui peut refaire le calcul au lieu de faire confiance.

Trois règles tenues par tous les agents, héritées de l'audit du corpus AXA :
  1. TOUT RÉSULTAT EST CITABLE. Un chiffre sans atome derrière n'est pas un résultat ; chaque
     sortie porte les citations qui la fondent (texte allemand + repère de position).
  2. RIEN N'EST DURCI. Ce que le texte modalise reste modalisé ; ce qui n'est pas établi part dans
     « a_confirmer » et est compté à part, jamais mêlé aux faits.
  3. LA DATATION EST UNE BORNE. Aucun agent ne date un énoncé de l'année de l'œuvre : l'écart entre
     parution et édition lue est rappelé partout où une chronologie est produite.

Les agents sont volontairement composables : le chef d'orchestre choisit lesquels activer selon la
question posée, et chacun ignore l'existence des autres.
"""
import itertools
import re

from . import verification
from .segmentation import replier

AGENTS_VERSION = "1.0.0"

# Négation allemande — sert à repérer les DIVERGENCES DE POLARITÉ entre énoncés sur un même
# concept. Repère un candidat, ne prouve jamais une contradiction (voir AgentTension).
_NEGATION = re.compile(r"\b(nicht|kein|keine|keinen|keiner|keinem|niemals|nie|weder|ohne)\b")


def _est_vers(texte):
    """Bloc de vers ? (plusieurs lignes courtes d'affilée — la poésie citée par Freud)."""
    lignes = [l.strip() for l in texte.split("\n") if l.strip()]
    if len(lignes) < 3:
        return False
    courtes = sum(1 for l in lignes if len(l) < 55)
    return courtes >= max(3, int(0.7 * len(lignes)))


def _ecart_longueur_ideale(atome, ideal=45):
    """Distance à la longueur d'un énoncé théorique — évite l'incise comme le bloc cité."""
    return abs(atome["nb_mots"] - ideal)


class Agent:
    """Contrat commun : un nom, une question, une exécution pure sur le corpus."""

    nom = "agent"
    question = ""

    def executer(self, corpus, **kw):
        raise NotImplementedError

    def _fiche(self, resultat, **entetes):
        return dict({"agent": self.nom, "question": self.question,
                     "deterministe": True, "version": AGENTS_VERSION}, **entetes, **resultat)


# --------------------------------------------------------------------------------------------
class AgentProfil(Agent):
    """Ce dont une œuvre PARLE, mesuré — et ce qui la distingue des autres."""

    nom = "profil"
    question = "De quoi cette œuvre parle-t-elle, et qu'est-ce qui lui est propre ?"

    def executer(self, corpus, oeuvre=None, **kw):
        cles = [oeuvre] if oeuvre else list(corpus.oeuvres)
        profils = {}
        for cle in cles:
            atomes = corpus.par_oeuvre(cle)
            groupes, concepts = {}, {}
            for a in atomes:
                for c in a["concepts"]:
                    groupes[c["groupe"]] = groupes.get(c["groupe"], 0) + 1
                    concepts[c["concept"]] = concepts.get(c["concept"], 0) + 1
            total = max(1, len(atomes))
            profils[cle] = {
                "titre": corpus.oeuvres[cle]["oeuvre"],
                "atomes": len(atomes),
                "groupes_pour_mille": {g: round(1000 * n / total) for g, n in
                                       sorted(groupes.items(), key=lambda x: -x[1])},
                "concepts_dominants": dict(sorted(concepts.items(), key=lambda x: -x[1])[:12]),
            }
        # Signature : les groupes SUR-représentés dans une œuvre par rapport au reste du corpus.
        # C'est ce qui distingue, pas ce qui domine — un livre peut parler beaucoup d'un thème
        # banal dans tout le corpus sans que ce soit sa marque propre.
        if len(profils) > 1:
            for cle, p in profils.items():
                autres = [q["groupes_pour_mille"] for k, q in profils.items() if k != cle]
                signature = {}
                for g, v in p["groupes_pour_mille"].items():
                    moyenne_ailleurs = sum(a.get(g, 0) for a in autres) / len(autres)
                    if v > moyenne_ailleurs:
                        signature[g] = round(v - moyenne_ailleurs)
                p["signature"] = dict(sorted(signature.items(), key=lambda x: -x[1])[:4])
        return self._fiche({"profils": profils})


# --------------------------------------------------------------------------------------------
class AgentConcept(Agent):
    """Dossier complet d'un concept : où, comment, avec quelle force, et avec quelles citations."""

    nom = "concept"
    question = "Que dit Freud de ce concept, et sur quel ton ?"

    def executer(self, corpus, concept=None, citations=5, **kw):
        if not concept:
            raise ValueError("agent « concept » : paramètre `concept` requis")
        atomes = corpus.par_concept(concept)
        if not atomes:
            return self._fiche({"concept": concept, "atomes": 0,
                                "note": "aucun atome — ce concept n'apparaît pas dans le corpus chargé"})
        par_oeuvre, par_statut, par_fonction, sous = {}, {}, {}, {}
        for a in atomes:
            par_oeuvre[a["oeuvre"]] = par_oeuvre.get(a["oeuvre"], 0) + 1
            par_statut[a["statut"]] = par_statut.get(a["statut"], 0) + 1
            for f in a["fonctions"]:
                par_fonction[f] = par_fonction.get(f, 0) + 1
            for c in a["concepts"]:
                if c["concept"] == concept:
                    for sc in c.get("sous_concepts", []):
                        sous[sc] = sous.get(sc, 0) + 1
        # Citations : on veut les THÈSES de Freud, pas les blocs qu'il cite. Sélectionner « le plus
        # long » remontait des vers (« Bei Nacht, wann ich soll schlafen… ») : la poésie citée forme
        # de longs atomes, faute de ponctuation de fin. On écarte donc le vers (lignes courtes en
        # série) et on vise une longueur de prose théorique plutôt que le maximum absolu.
        candidats = [a for a in atomes if a["statut"] == "affirme" and not _est_vers(a["texte"])]
        choisis = sorted(candidats, key=_ecart_longueur_ideale)[:citations]
        return self._fiche({
            "concept": concept,
            "atomes": len(atomes),
            "par_oeuvre": dict(sorted(par_oeuvre.items(), key=lambda x: -x[1])),
            "par_statut": dict(sorted(par_statut.items(), key=lambda x: -x[1])),
            "par_fonction": dict(sorted(par_fonction.items(), key=lambda x: -x[1])),
            "sous_concepts": dict(sorted(sous.items(), key=lambda x: -x[1])),
            "citations": [corpus.citer(a) for a in choisis],
        })


# --------------------------------------------------------------------------------------------
class AgentCooccurrence(Agent):
    """Quels concepts VOYAGENT ENSEMBLE — la brique du regroupement en courants.

    C'est l'agent qui sert directement l'objectif long terme du projet : si des courants
    postérieurs se recomposent à partir des mêmes atomes fondateurs, ils apparaîtront d'abord ici,
    comme des grappes de concepts que Freud pense ensemble.

    Mesure : indice de Jaccard (atomes où A et B sont ensemble / atomes où l'un ou l'autre paraît).
    On le préfère au comptage brut, qui ne ferait que remonter les concepts les plus fréquents.
    """

    nom = "cooccurrence"
    question = "Quels concepts un auteur pense-t-il ensemble ?"

    def executer(self, corpus, minimum=8, sommet=25, auteur="Sigmund Freud", **kw):
        """Cooccurrences AU SEIN D'UN SEUL AUTEUR. `auteur` n'est pas un filtre commode, c'est
        une nécessité : chaque auteur a son propre jeu de concepts, et mesurer sur le corpus
        entier produirait un classement où les couples de Le Bon, de Rank et de Freud se
        départageraient par leurs fréquences respectives, sans qu'aucune paire ne signifie plus
        rien. Le défaut a été RÉEL — quand Rank et Abraham sont entrés, la liste des vingt-cinq
        couples les plus liés mêlait « foule/individu », « anal/sadismus » et « aussetzung/wasser »,
        et le couple sadisme/masochisme de Freud en était sorti. C'est un test qui l'a signalé.

        Comparer deux auteurs reste possible, mais c'est une opération EXPLICITE : on exécute
        l'agent une fois par auteur et on rapproche les deux fiches, en sachant que les concepts
        comparés ne portent pas nécessairement le même sens.
        """
        atomes = [a for a in corpus.atomes if a.get("auteur", "Sigmund Freud") == auteur]
        presence, paires = {}, {}
        for a in atomes:
            concepts = sorted({c["concept"] for c in a["concepts"]})
            for c in concepts:
                presence[c] = presence.get(c, 0) + 1
            for x, y in itertools.combinations(concepts, 2):
                paires[(x, y)] = paires.get((x, y), 0) + 1
        liens = []
        for (x, y), n in paires.items():
            if n < minimum:
                continue
            union = presence[x] + presence[y] - n
            liens.append({"concepts": [x, y], "ensemble": n,
                          "jaccard": round(n / union, 3) if union else 0.0})
        liens.sort(key=lambda l: -l["jaccard"])
        return self._fiche({
            "auteur": auteur,
            "atomes_mesures": len(atomes),
            "seuil_minimum": minimum,
            "liens": liens[:sommet],
            "note": ("Jaccard = force du lien, indépendante de la fréquence brute. Mesuré sur les "
                     "seuls atomes de %s, avec SES concepts. Une grappe de concepts fortement "
                     "liés est un CANDIDAT de regroupement thématique, pas une thèse de l'auteur : "
                     "elle demande lecture." % auteur),
        })


def _paires_ponderees(atomes):
    """Cooccurrence intra-atome CORRIGÉE. AgentCooccurrence.executer et AgentCourants._graphe
    créditent chaque paire d'un atome à PLEIN (1), via itertools.combinations(concepts, 2) — un
    atome à 13 concepts crédite ses 78 paires comme 78 attestations indépendantes, alors qu'il ne
    fournit qu'UN SEUL geste de citation. CORRECTION : le vote d'un atome reste total = 1, réparti
    entre SES paires (1/C(k,2) chacune). Un atome à 2 concepts (1 paire) garde son poids plein ;
    un atome à 13 concepts (78 paires) crédite chacune de 1/78 — aucun atome ne pèse plus qu'un
    autre, seule la RÉPÉTITION à travers plusieurs atomes construit une paire forte.

    Rend (presence: {concept: n_atomes}, brut: {(x,y) triés: n entier, NON corrigé},
    reparti: {(x,y) triés: somme fractionnaire, corrigée}). `brut` reste un vrai décompte
    d'atomes, gardé comme garde-fou séparé — seul `reparti` est corrigé.
    """
    presence, brut, reparti = {}, {}, {}
    for a in atomes:
        concepts = sorted({c["concept"] for c in a["concepts"]})
        for c in concepts:
            presence[c] = presence.get(c, 0) + 1
        paires = list(itertools.combinations(concepts, 2))
        if not paires:
            continue
        part = 1.0 / len(paires)
        for x, y in paires:
            brut[(x, y)] = brut.get((x, y), 0) + 1
            reparti[(x, y)] = reparti.get((x, y), 0.0) + part
    return presence, brut, reparti


# --------------------------------------------------------------------------------------------
class AgentBuissonConcepts(Agent):
    """Force graduée entre deux concepts d'UN SEUL auteur — jamais un jugement de sens.

    Réutilise la cooccurrence intra-atome d'AgentCooccurrence, mais CORRIGÉE par
    _paires_ponderees : un atome dense (beaucoup de concepts à la fois) ne domine plus le
    graphe. C'est une cooccurrence textuelle MESURÉE (deux concepts reviennent souvent dans les
    mêmes phrases), jamais une synonymie ni une proximité de sens — vérifiable en revenant aux
    atomes qui la portent.
    """

    nom = "buisson_concepts"
    question = "Quelle force graduée relie deux concepts d'un même auteur ?"

    def executer(self, corpus, auteur="Sigmund Freud", minimum_brut=8, **kw):
        atomes = [a for a in corpus.atomes if a.get("auteur", "Sigmund Freud") == auteur]
        presence, brut, reparti = _paires_ponderees(atomes)
        liens = []
        for (x, y), n_brut in brut.items():
            if n_brut < minimum_brut:
                continue
            union = presence[x] + presence[y] - n_brut
            poids = round(reparti[(x, y)] / union, 4) if union else 0.0
            if poids <= 0:
                continue
            liens.append({"concepts": [x, y], "occurrences_brutes": n_brut, "poids": poids})
        liens.sort(key=lambda l: -l["poids"])
        return self._fiche({
            "auteur": auteur,
            "atomes_mesures": len(atomes),
            "seuil_minimum_brut": minimum_brut,
            "concepts_relies": len({c for l in liens for c in l["concepts"]}),
            "liens": liens,
            "note": ("poids = cooccurrence CORRIGÉE (vote de chaque atome réparti entre ses "
                     "propres paires) ; occurrences_brutes = compte NON corrigé, garde-fou "
                     "séparé, jamais mélangé au poids. Aucun des deux champs ne nomme une "
                     "synonymie ni une proximité de sens : une cooccurrence mesurée, à vérifier "
                     "atome par atome."),
        })


# --------------------------------------------------------------------------------------------
class AgentCourants(Agent):
    """Les concepts que Freud pense ensemble forment-ils déjà des grappes distinctes ?

    Prolonge AgentCooccurrence : au lieu de lister les paires les plus liées, PARTITIONNE tout le
    graphe de concepts en communautés, par maximisation gloutonne de la modularité (Newman, 2004)
    — un algorithme classique, entièrement déterministe : à chaque étape on fusionne la paire dont
    la fusion améliore le plus la modularité, et les égalités sont tranchées par ordre alphabétique
    des concepts, jamais par hasard. On s'arrête dès qu'aucune fusion n'améliore plus le score —
    le nombre et la taille des grappes ne sont donc jamais choisis à l'avance, ils sont mesurés.

    C'est la première brique de l'objectif final du projet : si des courants postérieurs se
    recomposent à partir des atomes du fondateur, un signe attendu est que ces atomes se
    regroupent DÉJÀ en grappes distinctes dans son propre corpus, avant même qu'aucun courant
    rival n'existe. Une grappe computée n'est PAS un courant : c'est un CANDIDAT à faire lire,
    exactement comme AgentTension produit des candidats de contradiction plutôt que des preuves.

    Restreint aux atomes de Sigmund Freud lui-même — l'appendice d'Otto Rank dans la Traumdeutung
    parle d'une autre plume et fausserait la mesure de CE qu'il pense ensemble (voir sources.py).
    """

    nom = "courants"
    question = "Les concepts que Freud pense ensemble forment-ils des grappes distinctes ?"

    def executer(self, corpus, minimum=8, auteur="Sigmund Freud", **kw):
        # Une partition se calcule SUR UN SEUL AUTEUR, pour la même raison que les cooccurrences :
        # deux lexiques distincts ne forment pas un graphe interprétable, et les communautés
        # obtenues ne diraient que la séparation des vocabulaires, qui est acquise d'avance.
        # Freud reste le défaut parce que l'export des « courants » du site porte sur lui.
        atomes = [a for a in corpus.atomes if a.get("auteur", "Sigmund Freud") == auteur]
        graphe, presence = self._graphe(atomes, minimum)
        communautes, m = self._partitionner(graphe)
        modularite = self._modularite(graphe, m, communautes)
        grappes = [self._decrire_grappe(corpus, atomes, c, presence)
                   for c in communautes if len(c) >= 2]
        grappes.sort(key=lambda g: -g["atomes_concernes"])
        return self._fiche({
            "statut": "a_confirmer",
            "seuil_minimum": minimum,
            "concepts_relies": len(graphe),
            "grappes": grappes,
            "modularite": round(modularite, 3),
            "note": ("Grappes CANDIDATES, pas des courants établis : un ensemble de concepts que "
                     "Freud pense souvent ensemble, mesuré par cooccurrence — pas une filiation "
                     "théorique ni un courant reconnu. Ça demande une lecture qualitative. Une "
                     "modularité au-delà de 0,30 est généralement jugée porter une structure "
                     "réelle plutôt qu'un artefact de graphe (Newman & Girvan, 2004)."),
        })

    @staticmethod
    def _graphe(atomes, minimum):
        """Graphe pondéré {concept: {autre: jaccard}}, restreint aux paires assez attestées."""
        presence, paires = {}, {}
        for a in atomes:
            concepts = sorted({c["concept"] for c in a["concepts"]})
            for c in concepts:
                presence[c] = presence.get(c, 0) + 1
            for x, y in itertools.combinations(concepts, 2):
                paires[(x, y)] = paires.get((x, y), 0) + 1
        graphe = {}
        for (x, y), n in sorted(paires.items()):
            if n < minimum:
                continue
            union = presence[x] + presence[y] - n
            poids = n / union if union else 0.0
            if poids <= 0:
                continue
            graphe.setdefault(x, {})[y] = poids
            graphe.setdefault(y, {})[x] = poids
        return graphe, presence

    @staticmethod
    def _partitionner(graphe):
        """Maximisation gloutonne de la modularité — une fusion par tour, la meilleure d'abord,
        égalités tranchées par ordre alphabétique. Rend (communautés, m = poids total du graphe).
        """
        noeuds = sorted(graphe)
        if not noeuds:
            return [], 0.0
        membres = {n: {n} for n in noeuds}
        deg = {n: sum(graphe[n].values()) for n in noeuds}     # K_i
        adj = {n: dict(graphe[n]) for n in noeuds}             # arêtes ENTRE communautés
        m = sum(deg.values()) / 2
        if m == 0:
            return [{n} for n in noeuds], 0.0
        EPS = 1e-9
        while True:
            meilleur, meilleur_dq = None, EPS
            for i in sorted(adj):
                for j in sorted(adj[i]):
                    if j <= i:
                        continue
                    dq = adj[i][j] / m - (deg[i] * deg[j]) / (2 * m * m)
                    if dq > meilleur_dq:
                        meilleur, meilleur_dq = (i, j), dq
            if meilleur is None:
                break
            i, j = meilleur
            membres[i] |= membres.pop(j)
            deg[i] += deg.pop(j)
            for k in list(adj[j]):
                if k == i:
                    continue
                adj[i][k] = adj[i].get(k, 0.0) + adj[j][k]
                adj[k][i] = adj[i][k]
                del adj[k][j]
            del adj[j]
            adj[i].pop(j, None)
        return list(membres.values()), m

    @staticmethod
    def _modularite(graphe, m, communautes):
        if m == 0:
            return 0.0
        q = 0.0
        for c in communautes:
            interne = sum(graphe[a].get(b, 0.0) for a in c for b in c if a < b)
            degre = sum(sum(graphe[a].values()) for a in c)
            q += interne / m - (degre / (2 * m)) ** 2
        return q

    @staticmethod
    def _decrire_grappe(corpus, atomes, membres, presence):
        concepts = sorted(membres, key=lambda c: -presence.get(c, 0))
        porteurs = [a for a in atomes if any(c["concept"] in membres for c in a["concepts"])]
        # Citation : un atome qui porte au moins DEUX concepts de la grappe À LA FOIS — preuve
        # directe que Freud les pense ensemble, pas seulement dans le même livre.
        croises = [a for a in porteurs
                   if len({c["concept"] for c in a["concepts"]} & membres) >= 2
                   and a["statut"] == "affirme" and not _est_vers(a["texte"])]
        citation = min(croises, key=_ecart_longueur_ideale) if croises else None
        return {
            "concepts": concepts,
            "taille": len(membres),
            "atomes_concernes": len(porteurs),
            "citation": corpus.citer(citation) if citation else None,
        }


# --------------------------------------------------------------------------------------------
class AgentChronologie(Agent):
    """Comment la place d'un concept évolue d'une œuvre à l'autre — avec la réserve de datation.

    Ne date JAMAIS un énoncé : compare des œuvres, en rappelant que chaque œuvre est lue dans une
    édition tardive dont les couches sont indiscernables. Une variation observée peut donc venir
    d'un ajout postérieur ; l'agent le dit à chaque fois plutôt que de laisser conclure.
    """

    nom = "chronologie"
    question = "La place de ce concept change-t-elle d'une œuvre à l'autre ?"

    def executer(self, corpus, concept=None, **kw):
        if not concept:
            raise ValueError("agent « chronologie » : paramètre `concept` requis")
        etapes, collationnees = [], 0
        for cle, meta in sorted(corpus.oeuvres.items(), key=lambda x: x[1]["annee_oeuvre"]):
            atomes = corpus.par_oeuvre(cle)
            porteurs = [a for a in atomes
                        if any(c["concept"] == concept for c in a["concepts"])]
            # Quand la collation a pu conclure, on sait pour chaque atome s'il était là DÈS
            # L'ORIGINE ou s'il fut ajouté ensuite. La densité d'origine est alors la seule
            # comparable d'une œuvre à l'autre : elle exclut ce que Freud a greffé après coup.
            couches = [a["attestation"].get("couche") for a in atomes]
            collationnee = any(c in ("origine", "ajout") for c in couches)
            etape = {
                "oeuvre": meta["oeuvre"],
                "annee_oeuvre": meta["annee_oeuvre"],
                "edition_lue": meta["edition_lue"],
                "annee_edition": meta["annee_edition"],
                "atomes_du_concept": len(porteurs),
                "pour_mille": round(1000 * len(porteurs) / max(1, len(atomes))),
                "incertitude_annees": meta["annee_edition"] - meta["annee_oeuvre"],
                "collationnee": collationnee,
            }
            if collationnee:
                collationnees += 1
                base = [a for a in atomes if a["attestation"].get("couche") == "origine"]
                dorigine = [a for a in porteurs if a["attestation"].get("couche") == "origine"]
                ajoutes = [a for a in porteurs if a["attestation"].get("couche") == "ajout"]
                etape.update({
                    "incertitude_annees": 0,
                    "pour_mille_origine": round(1000 * len(dorigine) / max(1, len(base))),
                    "du_concept_ajoutes_apres": len(ajoutes),
                })
            etapes.append(etape)
        return self._fiche({
            "concept": concept,
            "etapes": etapes,
            "oeuvres_collationnees": collationnees,
            "reserve": (
                "Pour les œuvres COLLATIONNÉES, « pour_mille_origine » ne compte que les passages "
                "retrouvés dans la première édition : cette densité-là est datée avec certitude. "
                "Pour les autres, l'œuvre est lue dans une édition postérieure dont Freud n'a pas "
                "signalé les ajouts — une variation peut y refléter un ajout tardif plutôt qu'un "
                "mouvement de la pensée. La collation lève cette réserve là où elle a pu conclure."),
        })


# --------------------------------------------------------------------------------------------
class AgentTension(Agent):
    """CANDIDATS de tension : deux énoncés affirmés sur un même concept, de polarité opposée.

    Ne conclut jamais à une contradiction. Une divergence de polarité peut relever d'un changement
    de contexte, d'une distinction que Freud pose explicitement, ou d'une simple négation locale.
    L'agent produit une LISTE À LIRE, classée pour que le temps humain aille au plus prometteur —
    exactement l'usage des « à vérifier » de l'audit AXA.
    """

    nom = "tension"
    question = "Où trouve-t-on, sur un même concept, des énoncés de sens opposé ?"

    def executer(self, corpus, concept=None, maximum=12, **kw):
        concepts = [concept] if concept else self._concepts_frequents(corpus)
        candidats = []
        for c in concepts:
            atomes = [a for a in corpus.par_concept(c)
                      if a["statut"] == "affirme" and a["nb_mots"] >= 8]
            avec = [a for a in atomes if _NEGATION.search(replier(a["texte"]))]
            sans = [a for a in atomes if not _NEGATION.search(replier(a["texte"]))]
            if not avec or not sans:
                continue
            # On rapproche les énoncés les plus « thétiques » de chaque polarité.
            a1 = max(sans, key=lambda a: a["nb_mots"])
            a2 = max(avec, key=lambda a: a["nb_mots"])
            candidats.append({
                "concept": c,
                "affirmes_sans_negation": len(sans),
                "affirmes_avec_negation": len(avec),
                "paire": [corpus.citer(a1), corpus.citer(a2)],
                "meme_oeuvre": a1["oeuvre"] == a2["oeuvre"],
            })
        candidats.sort(key=lambda x: -min(x["affirmes_sans_negation"], x["affirmes_avec_negation"]))
        return self._fiche({
            "statut": "a_confirmer",
            "candidats": candidats[:maximum],
            "note": ("CANDIDATS, pas contradictions. La divergence de polarité est un indice de "
                     "lecture ; elle ne prouve rien seule et demande le contexte complet."),
        })

    @staticmethod
    def _concepts_frequents(corpus, minimum=40):
        compte = {}
        for a in corpus.atomes:
            for c in a["concepts"]:
                compte[c["concept"]] = compte.get(c["concept"], 0) + 1
        return [c for c, n in sorted(compte.items(), key=lambda x: -x[1]) if n >= minimum]


# --------------------------------------------------------------------------------------------
class AgentSignaux(Agent):
    """La liste de travail : ce qui est REPÉRÉ, ce qui est JUGÉ, ce qui reste à lire.

    L'agent distingue trois états et ne les mélange jamais : un signal confirmé en contexte est
    opposable ; un signal rejeté est écarté avec son motif ; un signal non lu reste une piste.
    C'est ce qui rend la vérification cumulative — sans quoi chaque relecture repartirait de zéro.
    """

    nom = "signaux"
    question = "Quels passages sont vérifiés, et lesquels demandent encore une lecture ?"

    def executer(self, corpus, signal=None, maximum=40, **kw):
        atomes = corpus.a_confirmer(signal)
        table = verification.charger()
        par_signal = {}
        for a in atomes:
            for s in a["signaux_a_confirmer"]:
                par_signal[s] = par_signal.get(s, 0) + 1

        juges = verification.confirmes(atomes, signal, table)
        restants = [a for a in atomes if not table["verdicts"].get(a["id"])]
        return self._fiche({
            "statut": "a_confirmer",
            "total": len(atomes),
            "par_signal": dict(sorted(par_signal.items(), key=lambda x: -x[1])),
            "avancement": verification.etat(corpus.atomes, table),
            "confirmes": [dict(corpus.citer(a), signal=j["signal"], motif=j["motif"])
                          for a, j in juges[:maximum]],
            "restants": [dict(corpus.citer(a), signaux=a["signaux_a_confirmer"])
                         for a in restants[:maximum]],
            "note": ("Un marqueur lexical ne prouve pas qu'un auteur se corrige. Sur les 15 "
                     "candidats « révision » lus en contexte, 5 se sont confirmés : les autres "
                     "étaient un personnage de roman qui se corrige, un correcteur d'imprimerie, "
                     "ou un auteur tiers en corrigeant d'autres."),
        })


# --------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------
class AgentReprises(Agent):
    """Ce qu'un auteur REPREND d'un autre, mot pour mot ou presque.

    Le premier agent qui traverse la frontière entre auteurs — et il ne peut le faire que parce
    qu'il s'appuie sur un FAIT DE TEXTE, jamais sur un rapprochement de concepts. Deux passages
    partagent des suites de six mots : cela se vérifie à l'œil, sans qu'aucune grille
    d'interprétation n'ait à être partagée entre les deux auteurs.

    C'est le seul terrain sur lequel comparer SANS enfreindre la règle fondatrice du corpus
    (chaque auteur a ses catégories propres, voir core/lexiques/) : on ne rapproche pas des
    concepts, on constate un texte commun.

    Ce que l'agent REFUSE de faire : nommer la nature du rapport. Il ne dira jamais « socle »,
    « emprunt » ni « contradiction ». Il rend deux passages, leur mesure, leur sens quand les
    dates le permettent — et laisse lire.
    """

    nom = "reprises"
    question = "Quels passages un auteur reprend-il d'un autre ?"

    def executer(self, corpus, auteur=None, autre=None, minimum=None, **kw):
        from . import comparaison
        seuil = comparaison.SEUIL_PUBLICATION if minimum is None else minimum

        par_auteur = {}
        for a in corpus.atomes:
            par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)

        # Fréquences documentaires calculées sur le corpus ENTIER : une mesure de comparaison ne
        # doit pas changer selon le couple d'auteurs qu'on examine.
        index = [comparaison._n_grammes_utiles(v, None) for v in par_auteur.values()]
        df = comparaison.frequences_documentaires(index)

        noms = sorted(par_auteur)
        couples = [(x, y) for i, x in enumerate(noms) for y in noms[i + 1:]
                   if (auteur is None or auteur in (x, y))
                   and (autre is None or autre in (x, y))]

        fiches, total = [], 0
        for x, y in couples:
            bruts = comparaison.reprises(par_auteur[x], par_auteur[y], df)
            retenus = [comparaison.qualifier(l) for l in bruts if l["contenance"] >= seuil]
            if not retenus:
                continue
            total += len(retenus)
            evts = comparaison.evenements(retenus)
            fiches.append({
                "couple": [x, y],
                "paires": len(retenus),
                "evenements": len(evts),
                "manifestes": sum(1 for l in retenus if l["force"] == "manifeste"),
                "source_tierce": sum(1 for l in retenus if l["source_tierce"]),
                "sens_etabli": sum(1 for l in retenus if l["sens"]),
                "liens": [{
                    "contenance": l["contenance"], "force": l["force"],
                    "source_tierce": l["source_tierce"], "sens": l["sens"],
                    "a_verifier": l["a_verifier"],
                    "a": {"id": l["a"]["id"], "oeuvre": l["a"]["oeuvre"], "texte": l["a"]["texte"]},
                    "b": {"id": l["b"]["id"], "oeuvre": l["b"]["oeuvre"], "texte": l["b"]["texte"]},
                    "partages": l["partages"][:6],
                } for l in retenus[:40]],
            })
        fiches.sort(key=lambda f: -f["paires"])

        return self._fiche({
            "seuil": seuil,
            "couples": fiches,
            "total_paires": total,
            "total_evenements": sum(f["evenements"] for f in fiches),
            "note": ("Une PAIRE est deux phrases ; un ÉVÉNEMENT est une citation continue, qui "
                     "peut en compter plusieurs. C'est l'événement qui dit combien de fois un "
                     "auteur en cite un autre — compter les phrases avantagerait celui qui cite "
                     "par longs blocs sur celui qui cite par touches."),
            "reserve": ("Un lien dit qu'un TEXTE est partagé, jamais qu'une THÈSE l'est. Le sens "
                        "n'est donné que si les fenêtres de datation sont disjointes ; et quand "
                        "les deux passages nomment une source tierce (Sophocle, Shakespeare), "
                        "aucun sens n'est donné — les deux peuvent tenir leur formulation d'elle "
                        "plutôt que l'un de l'autre."),
        })


# --------------------------------------------------------------------------------------------
class AgentLectures(Agent):
    """Où un auteur LIT un autre : chapitres qui l'annoncent, passages qui le nomment.

    Complète `reprises` là où celui-ci est structurellement aveugle — entre deux langues. Freud
    consacre un chapitre entier, « II. Le Bon's Schilderung der Massenseele », à rendre compte de
    Le Bon, qu'il lit en traduction allemande. Aucune suite de mots ne peut relier les deux
    textes, puisqu'ils ne sont pas écrits dans la même langue. Sans cet agent, la relation
    inter-auteurs la mieux documentée du corpus serait absente de la couche.
    """

    nom = "lectures"
    question = "Où un auteur lit-il et nomme-t-il un autre ?"

    def executer(self, corpus, auteur=None, **kw):
        from . import comparaison
        par_auteur = {}
        for a in corpus.atomes:
            par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)

        chapitres, nominations = [], {}
        for nom_auteur, atomes in sorted(par_auteur.items()):
            if auteur and nom_auteur != auteur:
                continue
            for lec in comparaison.lectures_declarees(atomes, nom_auteur):
                chapitres.append({
                    "auteur": nom_auteur, "auteur_lu": lec["auteur_lu"],
                    "chapitre": lec["chapitre"], "portee_atomes": lec["portee"],
                    "oeuvre": lec["atomes"][0]["oeuvre"], "homographe": lec["homographe"],
                })
            for m in comparaison.mentions(atomes, nom_auteur):
                cle = (nom_auteur, m["auteur_nomme"])
                e = nominations.setdefault(cle, {
                    "auteur": nom_auteur, "auteur_nomme": m["auteur_nomme"],
                    "atomes": 0, "homographe": m["homographe"], "exemples": []})
                e["atomes"] += 1
                if len(e["exemples"]) < 5:
                    e["exemples"].append({
                        "id": m["atome"]["id"], "oeuvre": m["atome"]["oeuvre"],
                        "texte": m["atome"]["texte"][:400], "statut": m["atome"]["statut"]})

        chapitres.sort(key=lambda c: -c["portee_atomes"])
        return self._fiche({
            "chapitres_declares": chapitres,
            "nominations": sorted(nominations.values(), key=lambda e: -e["atomes"]),
            "note": ("Un CHAPITRE dont le titre nomme un autre auteur est le lien le plus solide "
                     "du corpus : c'est l'édition elle-même qui déclare la lecture, et c'est le "
                     "seul signal qui traverse la barrière des langues."),
            "reserve": ("Nommer n'est ni suivre, ni approuver, ni contredire. Le corpus a déjà "
                        "mesuré ce piège : un signal construit pour repérer les écarts de Rank "
                        "avec Freud n'a rien confirmé sur cinq candidats — les cinq passages "
                        "étaient des renvois d'ACCORD. Un motif localise, il ne qualifie pas. "
                        "Certains noms sont en outre des HOMOGRAPHES : « Abraham » désigne aussi "
                        "le patriarche biblique, que Rank et Freud citent abondamment."),
        })


# --------------------------------------------------------------------------------------------
class AgentUsage(Agent):
    """Comment un MOT se distribue entre les auteurs — un seul motif, appliqué à tous.

    RÉPOND À LA QUESTION DE LA COMPARAISON EN LA CONTOURNANT. Demander si la `verdraengung` de
    Rank est « la même » que celle de Freud suppose une équivalence qu'aucun témoin disponible
    ne permet de valider. Demander combien de fois chacun ÉCRIT le mot ne suppose rien : on
    applique le même motif partout et on compte.

    La méthode a été validée sur un cas où les deux mesures existent. Le concept « oedipus » a
    des motifs différents selon les lexiques ; mesuré avec ces motifs propres, l'écart Freud/Rank
    est de 3,6 ‰ contre 20,6 ‰ ; mesuré avec un motif UNIQUE, de 3,4 ‰ contre 21,5 ‰. L'écart
    persiste, donc il vient des auteurs et non du lexicographe.

    Ce que l'agent ne dit pas : que deux auteurs pensent la même chose quand ils emploient le
    même mot. Il rend les passages pour qu'on aille lire.
    """

    nom = "usage"
    question = "Comment un mot se distribue-t-il entre les auteurs ?"

    def executer(self, corpus, motif=None, langue=None, **kw):
        from . import comparaison
        if not motif:
            raise ValueError("l'agent `usage` demande un motif (par exemple « \\bverdrang »)")
        par_auteur = {}
        for a in corpus.atomes:
            par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
        langues = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)
        r = comparaison.densite_comparee(motif, par_auteur, langues, langue_motif=langue)
        return self._fiche({
            "motif": motif,
            "langue_motif": langue,
            "auteurs": r["auteurs"],
            "note": r["note"],
            "reserve": ("Un écart de densité mesure un USAGE DE MOT, jamais un accord ni un "
                        "désaccord. Un auteur peut soutenir une thèse sans employer le terme "
                        "qui la nomme, et l'employer souvent pour la combattre. Les passages "
                        "sont rendus pour qu'on aille voir. Sans `langue`, la mesure porte sur "
                        "tous les corpus — n'a de sens que pour un mot commun aux deux langues."),
        })


AGENTS = {a.nom: a for a in (AgentProfil(), AgentConcept(), AgentCooccurrence(),
                             AgentBuissonConcepts(), AgentCourants(),
                             AgentChronologie(), AgentTension(), AgentSignaux(),
                             AgentReprises(), AgentLectures(), AgentUsage())}


def orchestrer(corpus, demande=None, **kw):
    """CHEF D'ORCHESTRE — choisit les agents à activer, les exécute, rend un dossier unique.

    Sans demande : passe complète (état des lieux du corpus). Avec un concept : active la suite
    qui l'éclaire (dossier, chronologie, tensions). Le plan est explicite dans le résultat — on
    doit pouvoir vérifier ce qui a tourné, et ce qui n'a pas tourné.
    """
    concept = (demande or {}).get("concept") if isinstance(demande, dict) else demande
    if concept:
        plan = ["concept", "chronologie", "tension"]
    else:
        plan = ["profil", "cooccurrence", "courants", "signaux"]
    resultats, erreurs = {}, {}
    for nom in plan:
        try:
            resultats[nom] = AGENTS[nom].executer(corpus, concept=concept, **kw)
        except Exception as e:                                   # un agent qui échoue le DIT
            erreurs[nom] = "%s: %s" % (type(e).__name__, e)
        # Un agent en échec ne fait jamais échouer le dossier : les autres restent exploitables,
        # et l'échec est visible plutôt que silencieux.
    return {"corpus": corpus.resume(), "plan": plan, "concept": concept,
            "resultats": resultats, "erreurs": erreurs}
