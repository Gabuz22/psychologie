#!/usr/bin/env python3
"""TESTS de la couche de vérification — la mémoire des jugements portés en contexte.

Ce qui est protégé ici : un signal non lu n'est jamais promu ni écarté, un jugement est toujours
argumenté, et la précision annoncée ne porte que sur ce qui a été réellement lu.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import verification          # noqa: E402
from core.corpus import Corpus         # noqa: E402


class TestRegistre(unittest.TestCase):

    def test_integrite(self):
        r = verification.valider()
        self.assertTrue(r["ok"], "registre incohérent : %s" % r["erreurs"])
        self.assertGreater(r["juges"], 0)

    def test_tout_jugement_est_argumente(self):
        """Un verdict sans motif ne vaut rien : on doit pouvoir contester la lecture."""
        for aid, j in verification.charger()["verdicts"].items():
            self.assertTrue(j.get("motif", "").strip(), "verdict non argumenté : %s" % aid)
            self.assertIn(j["verdict"], verification.VERDICTS)

    def test_reclassement_dit_vers_quoi(self):
        for aid, j in verification.charger()["verdicts"].items():
            if j["verdict"] == "reclasse":
                self.assertTrue(j.get("vers"), "reclassement sans cible : %s" % aid)


class TestEtat(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Corpus()

    def test_revisions_toutes_jugees(self):
        """Le signal « révision » — le plus précieux — a été instruit en entier."""
        e = verification.etat(self.c.atomes)["par_signal"]["revision"]
        self.assertEqual(e["restants"], 0)
        self.assertEqual(e["juges"], e["total"])
        self.assertGreater(e["confirmes"], 0)

    def test_precision_mesuree_seulement_sur_le_lu(self):
        """Un signal non instruit n'a PAS de précision : on ne l'invente pas."""
        p = verification.etat(self.c.atomes)["par_signal"]
        self.assertIsNotNone(p["revision"]["precision_mesuree"])
        for s in ("objection", "auto_citation"):
            if p[s]["juges"] == 0:
                self.assertIsNone(p[s]["precision_mesuree"])

    def test_confirmes_sont_un_sous_ensemble_strict(self):
        """Seuls les signaux CONFIRMÉS sont opposables — les rejetés ne reviennent pas."""
        tous = self.c.a_confirmer("revision")
        ok = verification.confirmes(tous, "revision")
        self.assertLess(len(ok), len(tous), "aucun candidat écarté : la lecture n'a rien filtré ?")
        table = verification.charger()
        for a, j in ok:
            self.assertEqual(table["verdicts"][a["id"]]["verdict"], "confirme")

    def test_signal_non_juge_reste_en_attente(self):
        """Ni promu, ni écarté : un candidat non lu doit rester dans les restants."""
        table = verification.charger()
        attente = [a for a in self.c.a_confirmer() if a["id"] not in table["verdicts"]]
        self.assertGreater(len(attente), 0)
        for a in attente[:20]:
            self.assertIsNone(verification.verdict(a["id"], table))


if __name__ == "__main__":
    unittest.main(verbosity=2)
