#!/usr/bin/env python3
import unittest

from core import relations_v2


def relation_minimale(**surcharges):
    r = {
        "id": "rel:test:1",
        "type": "correspondance_exploratoire",
        "source": {"type": "atome", "id": "a:a1"},
        "target": {"type": "atome", "id": "b:a1"},
        "direction": {"state": "non_applicable", "value": None},
        "validation_state": "candidate_automatique",
        "evidence": [{"id": "ev:1", "target": "a:a1"}],
        "counterevidence": [],
        "dimensions": {
            "contenance_textuelle": relations_v2.dimension(
                "calculee", 0.4, "proportion", "ngrammes-6", "1.0.0")
        },
        "annotations": [],
        "history": [],
        "corpus_version": "sha256:corpus",
        "rule_version": "relations-v2:0.1.0",
    }
    r.update(surcharges)
    return r


class TestRelationsMultiples(unittest.TestCase):

    def test_plusieurs_relations_distinctes_peuvent_porter_sur_la_meme_paire(self):
        a = relation_minimale(id="rel:proximite", type="proximite_terminologique")
        b = relation_minimale(id="rel:opposition", type="opposition_doctrinale",
                              validation_state="contestee")
        self.assertFalse(relations_v2.valider_relation(a))
        self.assertFalse(relations_v2.valider_relation(b))
        self.assertEqual((a["source"], a["target"]), (b["source"], b["target"]))
        self.assertNotEqual(a["type"], b["type"])

    def test_relation_orientee_et_non_orientee(self):
        orientee = relation_minimale(direction={"state": "reconstruite", "value": "a_vers_b"})
        non_orientee = relation_minimale(id="rel:2",
                                         direction={"state": "non_applicable", "value": None})
        self.assertFalse(relations_v2.valider_relation(orientee))
        self.assertFalse(relations_v2.valider_relation(non_orientee))

    def test_inconnu_est_distinct_de_zero(self):
        inconnu = relation_minimale(dimensions={
            "couverture_documentaire": relations_v2.dimension("inconnue")})
        zero = relation_minimale(id="rel:zero", dimensions={
            "passages_independants": relations_v2.dimension(
                "calculee", 0, "compte", "compte-passages", "1.0.0")})
        self.assertFalse(relations_v2.valider_relation(inconnu))
        self.assertFalse(relations_v2.valider_relation(zero))
        faux = relation_minimale(id="rel:faux", dimensions={
            "couverture_documentaire": relations_v2.dimension("inconnue", 0)})
        self.assertTrue(relations_v2.valider_relation(faux))

    def test_preuve_et_contre_preuve_coexistent(self):
        r = relation_minimale(counterevidence=[{"id": "contre:1", "target": "b:a1"}])
        self.assertFalse(relations_v2.valider_relation(r))
        self.assertEqual(len(r["evidence"]), 1)
        self.assertEqual(len(r["counterevidence"]), 1)

    def test_annotations_divergentes_restent_separees(self):
        r = relation_minimale(validation_state="contestee", annotations=[
            {"id": "ann:A", "agent_kind": "humain", "proposition": "confirme"},
            {"id": "ann:B", "agent_kind": "humain", "proposition": "rejette"},
        ])
        self.assertFalse(relations_v2.valider_relation(r))
        self.assertEqual([a["proposition"] for a in r["annotations"]], ["confirme", "rejette"])

    def test_versions_corpus_et_regles_obligatoires(self):
        r = relation_minimale(corpus_version="")
        self.assertIn("versions du corpus et des règles obligatoires",
                      relations_v2.valider_relation(r))

    def test_score_synthetique_est_refuse(self):
        r = relation_minimale(force_globale=0.8)
        self.assertTrue(any("score synthétique interdit" in e
                            for e in relations_v2.valider_relation(r)))


class TestValidationAgregee(unittest.TestCase):

    def test_acte_sans_verdict_peut_etre_non_lu_ou_discordant(self):
        self.assertEqual(relations_v2.etat_validation_agrege([None, None]), "non_lu")
        self.assertEqual(relations_v2.etat_validation_agrege(["confirme", "reclasse"]),
                         "discordant")
        self.assertEqual(relations_v2.etat_validation_agrege(["confirme", None]),
                         "partiellement_lu")
        self.assertEqual(relations_v2.etat_validation_agrege(["confirme", "confirme"]),
                         "unanime")


class TestAlignementsConceptuels(unittest.TestCase):

    def test_identite_de_libelle_ne_suffit_pas_a_une_equivalence(self):
        alignement = {
            "id": "alignement:rank:freud:geburt",
            "source_entry_id": "lexique:Rank:geburt",
            "target_entry_id": "lexique:Freud:geburt",
            "relation": "equivalence",
            "bases": ["libelle_identique"],
            "validation_state": "candidate_automatique",
            "annotations": [],
        }
        self.assertIn("un libellé identique ne suffit pas à un alignement conceptuel",
                      relations_v2.valider_alignement_conceptuel(alignement))

    def test_alignement_documente_reste_possible_sans_le_valider_humainement(self):
        alignement = {
            "id": "alignement:rank:freud:geburt",
            "source_entry_id": "lexique:Rank:geburt",
            "target_entry_id": "lexique:Freud:geburt",
            "relation": "proximite",
            "bases": ["libelle_identique", "passages_compares", "fonctions_comparees"],
            "validation_state": "proposee",
            "annotations": [],
        }
        self.assertFalse(relations_v2.valider_alignement_conceptuel(alignement))

    def test_validation_humaine_sans_annotation_humaine_est_refusee(self):
        alignement = {
            "id": "alignement:rank:freud:geburt",
            "source_entry_id": "lexique:Rank:geburt",
            "target_entry_id": "lexique:Freud:geburt",
            "relation": "indecidable",
            "bases": ["passages_compares"],
            "validation_state": "validee_humainement",
            "annotations": [],
        }
        self.assertIn("validation humaine annoncée sans annotation humaine",
                      relations_v2.valider_alignement_conceptuel(alignement))


if __name__ == "__main__":
    unittest.main(verbosity=2)
