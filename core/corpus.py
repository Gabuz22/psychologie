#!/usr/bin/env python3
"""CORPUS — charge les atomes de toutes les œuvres et offre les sélections de base.

Couche mince entre l'atomisation (qui produit) et les agents (qui analysent). Elle ne recalcule
rien : elle assemble, indexe et permet de filtrer. Toute vue rendue par un agent doit pouvoir
remonter jusqu'à l'atome, et de l'atome jusqu'à la ligne du texte allemand — c'est la condition
pour qu'un psychanalyste puisse contrôler une affirmation au lieu de la croire.
"""
from . import atomisation, sources


def fenetre_datation(atome):
    """Fenêtre [année min, année max] de l'atome — la forme de `attestation` diffère selon que
    l'œuvre a été COLLATIONNÉE avec sa première édition ou non (voir sources.py et collation.py) ;
    cette fonction normalise les deux pour que le reste du code n'ait jamais à le savoir.
    """
    att = atome["attestation"]
    if "couche" in att:                            # œuvre collationnée : datation par atome
        if att["couche"] == "origine":
            return (att["annee"], att["annee"])
        return (att["annee_min"], att["annee_max"])
    return (att["annee_oeuvre"], att["annee_edition_lue"])  # non collationnée : fenêtre de l'œuvre


class Corpus:
    """Les atomes de toutes les œuvres demandées, avec leurs métadonnées d'édition."""

    def __init__(self, cles=None):
        self.oeuvres, self.atomes = {}, []
        for cle in (cles or list(sources.OEUVRES)):
            r = atomisation.atomiser(cle)
            self.oeuvres[cle] = r["meta"]
            self.atomes.extend(r["atomes"])
        self._par_id = {a["id"]: a for a in self.atomes}

    # ------------------------------------------------------------------ sélections
    def atome(self, aid):
        return self._par_id.get(aid)

    def par_oeuvre(self, cle):
        return [a for a in self.atomes if a["oeuvre"] == cle]

    def par_concept(self, concept):
        return [a for a in self.atomes
                if any(c["concept"] == concept for c in a["concepts"])]

    def par_groupe(self, groupe):
        return [a for a in self.atomes
                if any(c["groupe"] == groupe for c in a["concepts"])]

    def par_sous_concept(self, sous):
        return [a for a in self.atomes
                if any(sous in c.get("sous_concepts", []) for c in a["concepts"])]

    def par_fonction(self, fonction):
        return [a for a in self.atomes if fonction in a["fonctions"]]

    def a_confirmer(self, signal=None):
        return [a for a in self.atomes
                if a["signaux_a_confirmer"] and (signal is None or signal in a["signaux_a_confirmer"])]

    def rechercher(self, concept=None, groupe=None, sous_concept=None, auteur=None, oeuvre=None,
                   statut=None, fonction=None, mot_cle=None, annee_min=None, annee_max=None):
        """Recherche multicritère — chaque filtre fourni est un ET logique, aucun n'est requis.

        `annee_min`/`annee_max` filtrent sur la FENÊTRE DE DATATION propre à chaque atome (voir
        `fenetre_datation`), jamais sur l'année de l'œuvre : un atome ajouté en 1914 dans un livre
        de 1900 ne doit pas apparaître dans une recherche bornée à 1900-1905.
        """
        atomes = self.atomes
        if oeuvre:
            atomes = [a for a in atomes if a["oeuvre"] == oeuvre]
        if concept:
            atomes = [a for a in atomes if any(c["concept"] == concept for c in a["concepts"])]
        if groupe:
            atomes = [a for a in atomes if any(c["groupe"] == groupe for c in a["concepts"])]
        if sous_concept:
            atomes = [a for a in atomes
                     if any(sous_concept in c.get("sous_concepts", []) for c in a["concepts"])]
        if auteur:
            atomes = [a for a in atomes if a.get("auteur", "Sigmund Freud") == auteur]
        if statut:
            atomes = [a for a in atomes if a["statut"] == statut]
        if fonction:
            atomes = [a for a in atomes if fonction in a["fonctions"]]
        if mot_cle:
            aiguille = mot_cle.lower()
            atomes = [a for a in atomes if aiguille in a["texte"].lower()]
        if annee_min is not None or annee_max is not None:
            lo = -10**9 if annee_min is None else annee_min
            hi = 10**9 if annee_max is None else annee_max
            atomes = [a for a in atomes
                     if fenetre_datation(a)[0] <= hi and fenetre_datation(a)[1] >= lo]
        return atomes

    # ------------------------------------------------------------------ citation
    def citer(self, atome, longueur=220):
        """Rend un atome CITABLE : texte allemand + repère exact + réserve de datation.

        La réserve n'est pas un ornement : elle rappelle, à chaque citation, que la date est une
        borne supérieure et non la date d'écriture du passage (voir sources.datation).
        """
        meta = self.oeuvres[atome["oeuvre"]]
        ch = atome["chapitre"]
        return {
            "id": atome["id"],
            "texte": atome["texte"][:longueur],
            # Un volume peut contenir des contributions d'autres auteurs (l'appendice d'Otto Rank
            # dans la Traumdeutung) : la citation dit QUI écrit, sinon elle attribue à tort.
            "auteur": atome.get("auteur", "Sigmund Freud"),
            "oeuvre": meta["oeuvre"],
            "chapitre": ("%s. %s" % (ch["numero"], ch["titre"])) if ch else None,
            "position": [atome["debut"], atome["fin"]],
            "edition_lue": "%s (%d)" % (meta["edition_lue"], meta["annee_edition"]),
            "datation": atome["attestation"]["regle"],
        }

    def resume(self):
        return {
            "oeuvres": len(self.oeuvres),
            "atomes": len(self.atomes),
            "qualifies": sum(1 for a in self.atomes if not a["non_qualifie"]),
            "a_confirmer": sum(1 for a in self.atomes if a["signaux_a_confirmer"]),
        }
