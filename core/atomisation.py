#!/usr/bin/env python3
"""ATOMISATION — transforme une œuvre en ATOMES : les unités élémentaires du corpus.

Un ATOME = une phrase, plus tout ce qui permet de la situer, de la qualifier et de la RETROUVER.
C'est la source de données principale : catégorisation, détection de cycles, de progressions et de
contradictions s'appuieront dessus. Aucun LLM, aucun réseau, aucun aléa — même texte, mêmes atomes.

Structure d'un atome :
  id, oeuvre, index, texte, debut, fin, nb_mots     — l'unité et sa position (re-vérifiable)
  chapitre                                          — situation dans l'œuvre
  fonctions[]                                       — ce que la phrase FAIT (multigroupe)
  statut                                            — avec quelle force elle l'affirme
  concepts[]                                        — de quoi elle parle (groupe + concept)
  emphase                                           — mises en relief conservées par Gutenberg
  attestation                                       — datation HONNÊTE (voir sources.datation)

Invariants (tenus par les tests) :
  • RECOMPOSITION : les atomes rendent le texte dans l'ordre, sans perte ni réécriture.
  • LOCALISATION : texte[debut:fin] == texte de l'atome — toute citation est re-vérifiable.
  • JAMAIS DE FAUX ACQUIS : un atome sans fonction/concept reconnu le dit (« non_qualifie »),
    on ne lui invente pas de catégorie.
"""
import hashlib
import re

from . import lexique, ocr, sources
from .segmentation import segmenter

ATOMISATION_VERSION = "1.0.0"

# Titres de chapitre de Die Traumdeutung : chiffre romain seul sur sa ligne, puis le titre.
_CHAPITRE = re.compile(r"^[ \t]*([IVX]{1,5})\.[ \t]*\n\s*\n[ \t]*(\S[^\n]{3,90})", re.M)

# Mises en relief conservées par la transcription Gutenberg (elles portent du sens chez Freud :
# c'est ainsi qu'il détache le texte du rêve, les termes techniques et les noms d'auteurs).
_EMPHASES = {
    "espace": re.compile(r"_[^_\n]{2,}_"),      # gesperrt — mise en valeur forte
    "italique": re.compile(r"~[^~\n]{2,}~"),    # kursiv
    "gras": re.compile(r"[#=][^#=\n]{2,}[#=]"),
}


# Chapitrage FRANÇAIS (édition Alcan 1895) : « LIVRE PREMIER » / « CHAPITRE II » suivis du titre.
# La numérotation des chapitres REPART à chaque livre — le repère porte donc le livre avec lui
# (« II.III » = livre II, chapitre III), sans quoi trois « chapitre premier » seraient indiscernables.
_CHAPITRE_FR = re.compile(
    r"^[ \t]*(LIVRE|CHAPITRE)[ \t]+(PREMIER|[IVX]{1,5})[ \t]*\n\s*\n[ \t]*(\S[^\n]{3,90})", re.M)


def chapitres(texte, langue="de"):
    """[(debut, numero, titre)] — repères de chapitre, pour situer chaque atome."""
    if langue == "fr":
        out, livre = [], None
        for m in _CHAPITRE_FR.finditer(texte):
            numero = "I" if m.group(2) == "PREMIER" else m.group(2)
            if m.group(1) == "LIVRE":
                livre = numero
                continue                      # le titre du livre n'est pas un chapitre
            out.append((m.start(), "%s.%s" % (livre, numero) if livre else numero,
                        m.group(3).strip()))
        return out
    out = []
    for m in _CHAPITRE.finditer(texte):
        titre = m.group(2).strip()
        if len(titre) > 3:
            out.append((m.start(), m.group(1), titre))
    return out


def contributions(texte, meta, reperes):
    """Régions du texte écrites par QUELQU'UN D'AUTRE que l'auteur du volume.

    Déclarées dans le registre des œuvres (voir `sources.OEUVRES[...]["contributions"]`) et
    localisées ici par leur marqueur de début. Sans cela, l'appendice d'Otto Rank dans la 4e
    édition de la Traumdeutung — 7 % du volume — passerait pour du Freud, et toute mesure
    d'auteur mélangerait deux plumes.

    La fin d'une région se déclare de deux façons, au choix :
      • `jusqu_au_chapitre` — le prochain chapitre portant ce numéro ;
      • `fin` — un marqueur de texte explicite. Indispensable pour les œuvres CO-ÉCRITES, où
        un même contributeur signe plusieurs régions disjointes : dans « Studien über Hysterie »
        (1895), Breuer écrit à la fois le cas d'Anna O. et tout le chapitre théorique, soit 30 %
        du volume, et les deux régions sont séparées par trois cas rédigés par Freud.
    Une région déclarée qu'on ne retrouve PAS dans le texte est une erreur de déclaration, pas
    un cas à ignorer en silence : elle lève une exception.
    """
    out = []
    for c in meta.get("contributions", []):
        debut = texte.find(c["debut"])
        if debut < 0:
            raise ValueError("contribution de %s : marqueur de début introuvable — %r"
                             % (c["auteur"], c["debut"][:60]))
        if c.get("fin"):
            pos = texte.find(c["fin"], debut)
            if pos < 0:
                raise ValueError("contribution de %s : marqueur de fin introuvable — %r"
                                 % (c["auteur"], c["fin"][:60]))
            fin = pos
        else:
            fin = len(texte)
            for pos, numero, _titre in reperes:
                if numero == c.get("jusqu_au_chapitre") and pos > debut:
                    fin = pos
                    break
        out.append({"auteur": c["auteur"], "debut": debut, "fin": fin})
    return out


_CACHE_COUCHES = {}


def _couches(cle_oeuvre, meta):
    """Collationne l'œuvre avec sa première édition — {empreinte: attestation}, ou {} si impossible.

    L'étalonnage est OBLIGATOIRE : sans deux populations séparables, on renvoie {} et la datation
    bornée de l'œuvre reste en vigueur. Mieux vaut une incertitude connue qu'une date fausse.
    """
    if cle_oeuvre in _CACHE_COUCHES:
        return _CACHE_COUCHES[cle_oeuvre]
    from . import collation
    resultat = {}
    temoin = collation.temoin_de(cle_oeuvre)
    if temoin is not None:
        phrases = segmenter(sources.charger(cle_oeuvre)["texte"])
        propres = [p["texte"] for p in phrases if p["nb_mots"] >= 15][:300]
        # Témoin négatif universel : des passages d'une AUTRE œuvre, forcément absents d'ici.
        etrangere = "totem" if cle_oeuvre != "totem" else "jenseits"
        etrangers = [p["texte"] for p in segmenter(sources.charger(etrangere)["texte"])
                     if p["nb_mots"] >= 15][:80]
        etalon = collation.etalonner(temoin, propres, etrangers)
        if etalon["concluant"]:
            atomes_min = [{"empreinte": empreinte(p["texte"]), "texte": p["texte"],
                           "nb_mots": p["nb_mots"]} for p in phrases]
            resultat = collation.dater_atomes(
                atomes_min, temoin, etalon["seuil"],
                collation.FACSIMILES[cle_oeuvre]["annee"], meta["annee_edition"])
            for v in resultat.values():
                v["etalonnage"] = {"forme": etalon["forme"], "seuil": etalon["seuil"]}
    _CACHE_COUCHES[cle_oeuvre] = resultat
    return resultat


def empreinte(texte):
    """Identifiant STABLE d'un atome : une empreinte de son texte, insensible à sa position.

    L'identifiant `oeuvre:aN` est positionnel — il change dès qu'on retire du paratexte en amont.
    C'est ce qui est arrivé : le retrait de la bibliographie de la Traumdeutung a décalé tous les
    numéros, et les 189 verdicts vérifiés à la main pointaient soudain dans le vide. Un jugement
    porté sur une PHRASE doit rester attaché à cette phrase, quoi qu'il advienne du volume autour.
    Normalisation légère (espaces) pour survivre à un reformatage sans changer de sens.
    """
    return hashlib.sha1(" ".join(str(texte or "").split()).encode("utf-8")).hexdigest()[:16]


def _auteur_de(position, regions, defaut):
    for r in regions:
        if r["debut"] <= position < r["fin"]:
            return r["auteur"]
    return defaut


def _chapitre_de(position, reperes):
    """Chapitre courant pour une position donnée (le dernier repère franchi)."""
    courant = None
    for debut, numero, titre in reperes:
        if debut <= position:
            courant = {"numero": numero, "titre": titre}
        else:
            break
    return courant


def _emphases(texte):
    """Segments mis en relief dans la phrase (sens conservé, jamais inventé)."""
    out = []
    for genre, motif in _EMPHASES.items():
        for m in motif.finditer(texte):
            out.append({"genre": genre, "texte": m.group(0).strip("_~#=").strip()})
    return out


# Mémoire de calcul : l'atomisation est PURE (même texte → mêmes atomes), donc rejouable sans
# risque et coûteuse à refaire. Sans ce cache, chaque agent réatomisait tout le corpus — tenable
# sur trois œuvres, impraticable sur les vingt-quatre volumes visés. Vidable par `oublier()`.
_CACHE = {}


def oublier():
    """Vide la mémoire de calcul (utile après modification du lexique ou des sources)."""
    _CACHE.clear()
    _CACHE_COUCHES.clear()


def atomiser(cle_oeuvre):
    """Atomise une œuvre entière → {atomes, meta, controles}. Résultat mémorisé (calcul pur)."""
    if cle_oeuvre in _CACHE:
        return _CACHE[cle_oeuvre]
    resultat = _atomiser(cle_oeuvre)
    _CACHE[cle_oeuvre] = resultat
    return resultat


def _atomiser(cle_oeuvre):
    charge = sources.charger(cle_oeuvre)
    texte, meta = charge["texte"], charge["meta"]
    langue = meta.get("langue", "de")
    # Une source OCRisée n'a pas la même fiabilité qu'une transcription relue : chaque phrase
    # sera examinée pour d'éventuelles traces de corruption (voir `ocr_suspect` plus bas).
    ocrise = meta.get("provenance") == "archive"
    phrases = segmenter(texte, langue)
    reperes = chapitres(texte, langue)
    regions = contributions(texte, meta, reperes)
    attestation = meta["datation"]
    # Collation : quand un fac-similé de première édition existe ET que l'étalonnage est concluant,
    # chaque atome reçoit sa couche d'écriture — ce qui remplace la datation bornée de l'œuvre par
    # une datation par phrase. Sinon la réserve d'origine subsiste, inchangée.
    couches = _couches(cle_oeuvre, meta)

    atomes = []
    for p in phrases:
        # Les catégories sont celles de l'auteur du VOLUME. Une contribution insérée dans un
        # livre d'autrui (Rank dans la Traumdeutung, Breuer dans les Studien) reste décrite avec
        # les catégories de ce livre : ces pages appartiennent à cet ouvrage-là. L'atome garde
        # son auteur réel, ce qui permet de les isoler ensuite si on le souhaite.
        auteur_lexique = meta["auteur"]
        fonctions, a_confirmer = lexique.fonctions_par_fiabilite(p["texte"], auteur_lexique)
        concepts = lexique.concepts_de(p["texte"], auteur_lexique)
        atomes.append({
            "id": "%s:a%d" % (cle_oeuvre, p["index"]),
            # Clé STABLE, insensible à la position : c'est elle qui porte les jugements de
            # vérification, pour qu'un nettoyage du volume ne les fasse plus pointer dans le vide.
            "empreinte": empreinte(p["texte"]),
            "oeuvre": cle_oeuvre,
            "index": p["index"],
            "texte": p["texte"],
            "debut": p["debut"],
            "fin": p["fin"],
            "nb_mots": p["nb_mots"],
            "chapitre": _chapitre_de(p["debut"], reperes),
            # Qui écrit RÉELLEMENT cette phrase — un volume peut contenir des contributions,
            # et depuis Le Bon l'auteur du volume n'est plus forcément Freud.
            "auteur": _auteur_de(p["debut"], regions, meta["auteur"]),
            "fonctions": fonctions,
            # Signaux repérés mais NON ÉTABLIS (révision, objection, auto-citation) : ils forment
            # la liste de travail à vérifier, jamais des faits acquis. Voir lexique.FIABILITE.
            "signaux_a_confirmer": a_confirmer,
            "statut": lexique.statut_de(p["texte"], auteur_lexique),
            "concepts": concepts,
            "emphase": _emphases(p["texte"]),
            # Aucune catégorie reconnue : on l'AFFICHE au lieu de combler (doctrine AXA).
            "non_qualifie": not fonctions and not a_confirmer and not concepts,
            # Datation par phrase quand la collation a pu conclure ; sinon la réserve d'œuvre.
            "attestation": couches.get(empreinte(p["texte"]), attestation),
            # Cette phrase vient-elle d'un fac-similé ET porte-t-elle une trace de corruption
            # OCR ? On ne la retire pas et on ne la corrige pas : on la MARQUE, pour qu'une
            # citation qui en sort soit vérifiée sur le fac-similé avant d'être publiée.
            # Même doctrine que les signaux « à confirmer » : ce qui n'est pas sûr est affiché.
            "ocr_suspect": ocrise and ocr.phrase_suspecte(p["texte"]),
        })

    return {
        "meta": {
            "oeuvre": meta["titre"],
            "oeuvre_fr": meta["titre_fr"],
            "cle": cle_oeuvre,
            "langue": langue,
            "auteur": meta["auteur"],
            "edition_lue": meta["edition"],
            "annee_edition": meta["annee_edition"],
            "annee_oeuvre": meta["annee_oeuvre"],
            "source": meta["source"],
            "empreinte_fichier": meta["empreinte_fichier"],
            "version_atomisation": ATOMISATION_VERSION,
            "version_lexique": lexique.LEXIQUE_VERSION,
        },
        "atomes": atomes,
        "controles": controler(atomes, phrases, texte),
        "index": indexer(atomes),
    }


def controler(atomes, phrases, texte):
    """Preuves d'intégrité — un chiffre qu'on peut vérifier, pas une promesse."""
    localises = sum(1 for a in atomes if texte[a["debut"]:a["fin"]] == a["texte"])
    a_confirmer = [a for a in atomes if a["signaux_a_confirmer"]]
    return {
        "total_atomes": len(atomes),
        "a_confirmer": len(a_confirmer),
        "recomposition_ordre_ok": [a["texte"] for a in atomes] == [p["texte"] for p in phrases],
        "localisation_exacte": localises,
        "localisation_complete": localises == len(atomes),
        "qualifies": sum(1 for a in atomes if not a["non_qualifie"]),
        "non_qualifies": sum(1 for a in atomes if a["non_qualifie"]),
        "avec_chapitre": sum(1 for a in atomes if a["chapitre"]),
        "par_auteur": {a: sum(1 for x in atomes if x["auteur"] == a)
                       for a in sorted({x["auteur"] for x in atomes})},
        "par_couche": {c: sum(1 for x in atomes if x["attestation"].get("couche") == c)
                       for c in sorted({x["attestation"].get("couche") for x in atomes} - {None})},
    }


def indexer(atomes):
    """Index inversés : par fonction, par concept, par groupe, par statut — pour l'analyse."""
    par_fonction, par_concept, par_groupe, par_statut = {}, {}, {}, {}
    par_signal, par_sous_concept = {}, {}
    for a in atomes:
        for f in a["fonctions"]:
            par_fonction.setdefault(f, []).append(a["id"])
        for s in a["signaux_a_confirmer"]:
            par_signal.setdefault(s, []).append(a["id"])
        for c in a["concepts"]:
            par_concept.setdefault(c["concept"], []).append(a["id"])
            par_groupe.setdefault(c["groupe"], []).append(a["id"])
            for sc in c.get("sous_concepts", []):
                par_sous_concept.setdefault(sc, []).append(a["id"])
        par_statut.setdefault(a["statut"], []).append(a["id"])
    return {
        "par_fonction": {k: len(v) for k, v in sorted(par_fonction.items())},
        "par_signal_a_confirmer": {k: len(v) for k, v in sorted(par_signal.items())},
        "par_concept": {k: len(v) for k, v in sorted(par_concept.items(), key=lambda x: -len(x[1]))},
        "par_sous_concept": {k: len(v) for k, v in sorted(par_sous_concept.items(), key=lambda x: -len(x[1]))},
        "par_groupe": {k: len(v) for k, v in sorted(par_groupe.items(), key=lambda x: -len(x[1]))},
        "par_statut": {k: len(v) for k, v in sorted(par_statut.items(), key=lambda x: -len(x[1]))},
        "_ids": {"par_fonction": par_fonction, "par_concept": par_concept,
                 "par_sous_concept": par_sous_concept, "par_signal_a_confirmer": par_signal},
    }
