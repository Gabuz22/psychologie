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
    question = "Quels concepts Freud pense-t-il ensemble ?"

    def executer(self, corpus, minimum=8, sommet=25, **kw):
        presence, paires = {}, {}
        for a in corpus.atomes:
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
            "seuil_minimum": minimum,
            "liens": liens[:sommet],
            "note": ("Jaccard = force du lien, indépendante de la fréquence brute. "
                     "Une grappe de concepts fortement liés est un CANDIDAT de regroupement "
                     "thématique, pas une thèse de Freud : elle demande lecture."),
        })


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
AGENTS = {a.nom: a for a in (AgentProfil(), AgentConcept(), AgentCooccurrence(),
                             AgentChronologie(), AgentTension(), AgentSignaux())}


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
        plan = ["profil", "cooccurrence", "signaux"]
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
