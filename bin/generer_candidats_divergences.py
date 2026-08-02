#!/usr/bin/env python3
"""DOSSIERS DE LECTURE DES CANDIDATS DE DIVERGENCE — sur le patron de lire_mentions.py.

    python bin/generer_candidats_divergences.py

Calcule les candidats (core/divergences.candidats), puis pour CHACUN construit un dossier avec de
quoi juger : des passages réels où le vocabulaire apparaît/disparaît, et le texte même du lien
vérifié qui le rattache à un autre auteur — jamais seulement des chiffres. Écrit dans
scratchpad/divergences/candidats.json (chemin donné en argument), pour qu'une campagne de lecture
n'ait pas à ré-atomiser le corpus une fois par candidat.

CE SCRIPT NE JUGE RIEN. Il rassemble ; la lecture tranche — voir `core/divergences.reserve()`.
"""
import argparse
import json
import os
import re
import sqlite3
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, RACINE)
sys.path.insert(0, os.path.join(RACINE, "bin"))
sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from core import branches, comparaison, divergences   # noqa: E402
from core.corpus import Corpus                        # noqa: E402
from generer_socle import catalogue_motifs             # noqa: E402

DB_PATH = os.path.join(RACINE, "derive", "d1", "corpus.sqlite")
ECHANTILLON = 6          # passages montrés par candidat pour l'œuvre dominante


def _q(db, sql, *args):
    return db.execute(sql, args).fetchall()


def calculer_touches(db):
    """{(auteur, sous_concept): {auteurs liés}} — actes ET mentions CONFIRMÉS seulement."""
    touches = {}
    for aa, bb, cc in _q(db,
            "SELECT a.nom, b.nom, k.concepts_communs FROM carte_actes k "
            "JOIN auteurs a ON a.id=k.auteur_a JOIN auteurs b ON b.id=k.auteur_b "
            "WHERE k.verdict='confirme'"):
        for nom in (cc or "").split(", "):
            if not nom:
                continue
            touches.setdefault((aa, nom), set()).add(bb)
            touches.setdefault((bb, nom), set()).add(aa)
    for nom, au, autre in _q(db,
            "SELECT c.nom, au.nom, y.nom FROM mentions m "
            "JOIN atome_concepts ac ON ac.atome_id=m.atome_id "
            "JOIN concepts c ON c.id=ac.concept_id JOIN auteurs au ON au.id=m.auteur_id "
            "JOIN auteurs y ON y.id=m.auteur_nomme_id "
            "WHERE m.auteur_id=c.auteur_id AND m.verdict='confirme'"):
        touches.setdefault((au, nom), set()).add(autre)
    return touches


def preuve_du_lien(db, auteur, autre, concept):
    """Le texte même du lien confirmé entre `auteur` et `autre` touchant `concept` — un acte s'il
    existe, sinon une mention. Sans ce texte, un candidat resterait un chiffre sans preuve."""
    for oa, ob, k_ca, k_cb, cc in _q(db,
            "SELECT a.nom, b.nom, k.citation_a, k.citation_b, k.concepts_communs "
            "FROM carte_actes k JOIN auteurs a ON a.id=k.auteur_a JOIN auteurs b ON b.id=k.auteur_b "
            "WHERE k.verdict='confirme' AND ((a.nom=? AND b.nom=?) OR (a.nom=? AND b.nom=?))",
            auteur, autre, autre, auteur):
        if concept in (cc or "").split(", "):
            return {"type": "acte", "auteur_a": oa, "auteur_b": ob,
                    "citation_a": k_ca, "citation_b": k_cb}
    for texte, motif_lecture in _q(db,
            "SELECT x.texte, m.motif_lecture FROM mentions m "
            "JOIN atomes x ON x.id=m.atome_id "
            "JOIN atome_concepts ac ON ac.atome_id=m.atome_id "
            "JOIN concepts c ON c.id=ac.concept_id JOIN auteurs au ON au.id=m.auteur_id "
            "JOIN auteurs y ON y.id=m.auteur_nomme_id "
            "WHERE m.auteur_id=c.auteur_id AND m.verdict='confirme' "
            "AND au.nom=? AND y.nom=? AND c.nom=?",
            auteur, autre, concept):
        return {"type": "mention", "auteur": auteur, "nomme": autre,
                "texte": texte, "motif_lecture": motif_lecture}
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--sortie", required=True)
    args = p.parse_args()

    db = sqlite3.connect(DB_PATH)
    touches = calculer_touches(db)
    print("liens confirmés (auteur, concept) :", len(touches))

    corpus = Corpus()
    print("corpus chargé :", len(corpus.atomes), "atomes")
    langues = comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres)

    # Index : (auteur, oeuvre) -> [(atome_texte_replie, atome_original)], et années.
    groupes = {}
    annees = {cle: meta["annee_oeuvre"] for cle, meta in corpus.oeuvres.items()}
    for a in corpus.atomes:
        auteur = a.get("auteur", "Sigmund Freud")
        if langues.get(auteur) != "de":
            continue
        groupes.setdefault((auteur, a["oeuvre"]), []).append(a)

    trajectoires_par_auteur = {}
    motif_par_sous = {}
    auteurs_de = sorted({a for (a, o) in groupes})
    motifs = catalogue_motifs("de")
    print("motifs :", len(motifs))
    for i, m in enumerate(motifs):
        if i % 100 == 0:
            print("  ...", i, "/", len(motifs))
        r = re.compile(m["motif"])
        motif_par_sous[m["sous"]] = r
        for auteur in auteurs_de:
            if (auteur, m["sous"]) not in touches:
                continue
            # `comparaison._replie` plie chaque atome UNE fois et met en cache par texte (voir son
            # commentaire) : appeler `replier_comparaison` directement ici, motif par motif,
            # recréait le coût que ce cache existe justement pour éviter — mesuré à ~10 minutes
            # pour les 483 motifs sur ce corpus avant ce correctif.
            oeuvres_auteur = [{"cle": o, "annee": annees.get(o, 0), "atomes": len(atomes),
                              "porteurs": sum(1 for a in atomes if r.search(comparaison._replie(a)))}
                             for (a2, o), atomes in groupes.items() if a2 == auteur]
            traj = branches.trajectoire(m["motif"], oeuvres_auteur)
            if traj:
                trajectoires_par_auteur.setdefault(auteur, []).append((m["sous"], traj))

    candidats = divergences.candidats(trajectoires_par_auteur, touches)
    print("candidats :", len(candidats))
    print(divergences.resume(candidats))

    dossiers = []
    for c in candidats:
        r = motif_par_sous[c["concept"]]
        atomes_dominants = [a for a in groupes.get((c["auteur"], c["oeuvre_dominante"]), [])
                            if r.search(comparaison._replie(a))]
        echantillon = [{"id": a["id"], "texte": a["texte"]} for a in atomes_dominants[:ECHANTILLON]]

        preuves = []
        for autre in c["lie_a"]:
            preuve = preuve_du_lien(db, c["auteur"], autre, c["concept"])
            if preuve:
                preuves.append(preuve)

        dossiers.append({
            **{k: v for k, v in c.items() if k != "lie_a"},
            "lie_a": c["lie_a"],
            "passages_dominants": echantillon,
            "preuves_de_lien": preuves,
        })

    chemin = os.path.abspath(args.sortie)
    with open(chemin, "w", encoding="utf-8") as f:
        json.dump(dossiers, f, ensure_ascii=False, indent=1)
    print("→", chemin, "(%d dossiers)" % len(dossiers))
    sans_preuve = sum(1 for d in dossiers if not d["preuves_de_lien"])
    if sans_preuve:
        print("ATTENTION :", sans_preuve, "candidat(s) sans texte de preuve retrouvé — "
              "à examiner avant la campagne de lecture.")


if __name__ == "__main__":
    main()
