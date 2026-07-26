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
            self.assertEqual(table["verdicts"][verification.cle(a)]["verdict"], "confirme")

    def test_signal_non_juge_reste_en_attente(self):
        """Ni promu, ni écarté : un candidat non lu doit compter comme « restant ».

        Le mécanisme est éprouvé sur un atome FICTIF plutôt que sur l'état courant du corpus :
        l'instruction étant aujourd'hui complète, un test adossé à des candidats en attente
        tomberait précisément parce que le travail a été fait.
        """
        table = verification.charger()
        inconnu = {"id": "oeuvre_fictive:a999999", "empreinte": "0" * 16,
                   "signaux_a_confirmer": ["revision"]}
        self.assertIsNone(verification.verdict(inconnu["id"], table))
        e = verification.etat([inconnu], table)["par_signal"]["revision"]
        self.assertEqual(e["total"], 1)
        self.assertEqual(e["juges"], 0)
        self.assertEqual(e["restants"], 1)
        self.assertIsNone(e["precision_mesuree"])
        self.assertEqual(verification.confirmes([inconnu], table=table), [])

    def test_verdicts_ancres_sur_le_texte_pas_sur_le_rang(self):
        """Un jugement suit la PHRASE, pas son numéro d'ordre.

        Les identifiants « oeuvre:aN » sont positionnels : retirer du paratexte en amont les
        décale. Le nettoyage des blocs de notes Wikisource, intercalés dans les Neue Folge, avait
        ainsi fait pointer 30 verdicts dans le vide. Le registre est donc clé par EMPREINTE.
        """
        table = verification.charger()
        for k in table["verdicts"]:
            self.assertRegex(k, r"^[0-9a-f]{16}$", "clé non conforme à une empreinte : %s" % k)
        # Un atome retrouve son verdict quel que soit son rang : on le déplace artificiellement.
        juge = next(a for a in self.c.atomes if verification.verdict(a, table))
        deplace = dict(juge, id="oeuvre:a999999", index=999999)
        self.assertEqual(verification.verdict(deplace, table), verification.verdict(juge, table))

    def test_instruction_complete(self):
        """État atteint : tous les signaux repérés du corpus ont été lus et jugés."""
        table = verification.charger()
        restants = [a["id"] for a in self.c.a_confirmer()
                    if verification.cle(a) not in table["verdicts"]]
        self.assertEqual(restants, [], "signaux encore non instruits : %s" % restants[:5])


if __name__ == "__main__":
    unittest.main(verbosity=2)
