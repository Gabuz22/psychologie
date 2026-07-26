#!/usr/bin/env python3
"""TESTS des agents déterministes et du chef d'orchestre.

Ce qui est protégé ici n'est pas « le code tourne » mais les trois règles qui rendent une analyse
opposable : elle est reproductible, elle est citable, et elle ne durcit rien.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import agents                 # noqa: E402
from core.corpus import Corpus          # noqa: E402


class TestCorpus(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Corpus()                 # corpus complet : les agents doivent tenir à l'échelle réelle

    def test_charge_tout_le_corpus(self):
        """Le corpus doit suivre l'extension : le compte vient du registre, jamais d'un nombre figé."""
        from core import sources
        r = self.c.resume()
        self.assertEqual(r["oeuvres"], len(sources.OEUVRES))
        self.assertGreater(r["atomes"], 15000)

    def test_selections(self):
        self.assertTrue(self.c.par_concept("traum"))
        self.assertTrue(self.c.par_groupe("pulsion"))
        self.assertTrue(self.c.par_sous_concept("todestrieb"))
        self.assertEqual(self.c.par_concept("concept_inexistant_xyz"), [])

    def test_citation_est_verifiable(self):
        """Une citation doit permettre de retrouver le passage — sinon elle ne vaut rien."""
        a = self.c.par_concept("traum")[0]
        cit = self.c.citer(a)
        for champ in ("id", "texte", "oeuvre", "position", "edition_lue", "datation"):
            self.assertIn(champ, cit)
        # Une citation dit TOUJOURS ce que vaut sa date — soit qu'elle est certaine (édition
        # d'origine, ou réimpression inchangée), soit qu'elle n'est qu'une borne supérieure.
        self.assertRegex(cit["datation"], r"date certaine|au plus tard")

    def test_datation_certaine_pour_les_editions_d_origine(self):
        """L'extension a apporté des œuvres lues dans leur édition d'origine : à ne pas brader.

        Les traiter comme incertaines par prudence mécanique reviendrait à jeter l'information la
        plus précieuse du corpus pour toute chronologie.
        """
        from core import sources
        exactes = [k for k in sources.OEUVRES if sources.datation(sources.OEUVRES[k])["precise"]]
        self.assertGreaterEqual(len(exactes), 4)
        for k in ("gradiva", "unheimliche", "massenpsychologie"):
            self.assertIn(k, exactes)


class TestAgents(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Corpus()

    def test_profil_signature_distingue_les_oeuvres(self):
        """Contrôle de sens : chaque œuvre doit ressortir avec sa marque propre."""
        r = agents.AgentProfil().executer(self.c)
        p = r["profils"]
        self.assertIn("reve", p["traumdeutung"]["signature"])
        self.assertIn("pulsion", p["drei_abhandlungen"]["signature"])

    def test_concept_exige_son_parametre(self):
        with self.assertRaises(ValueError):
            agents.AgentConcept().executer(self.c)

    def test_concept_rend_des_citations(self):
        r = agents.AgentConcept().executer(self.c, concept="trieb")
        self.assertGreater(r["atomes"], 100)
        self.assertTrue(r["citations"])
        self.assertIn("sexualtrieb", r["sous_concepts"])

    def test_citations_ne_sont_pas_des_vers_cites(self):
        """Freud cite beaucoup de poésie ; ces vers ne sont pas SES thèses.

        Sélectionner « l'atome affirmé le plus long » remontait des blocs de vers (la poésie forme
        de longs atomes faute de ponctuation de fin) et les présentait comme des affirmations de
        Freud. Les citations doivent être de la prose théorique.
        """
        r = agents.AgentConcept().executer(self.c, concept="angst")
        for cit in r["citations"]:
            lignes = [l.strip() for l in cit["texte"].split("\n") if l.strip()]
            if len(lignes) >= 3:
                courtes = sum(1 for l in lignes if len(l) < 55)
                self.assertLess(courtes, max(3, int(0.7 * len(lignes))),
                                "citation en vers : %s" % cit["texte"][:80])

    def test_concept_absent_ne_ment_pas(self):
        r = agents.AgentConcept().executer(self.c, concept="concept_inexistant_xyz")
        self.assertEqual(r["atomes"], 0)
        self.assertIn("note", r)

    def test_cooccurrence_retrouve_les_couples_freudiens(self):
        """Validation de fond : la mesure doit retrouver des couples que tout lecteur reconnaît."""
        r = agents.AgentCooccurrence().executer(self.c)
        couples = {tuple(sorted(l["concepts"])) for l in r["liens"]}
        self.assertIn(("wunsch", "wunscherfuellung"), couples)
        self.assertIn(("masochismus", "sadismus"), couples)

    def test_chronologie_porte_toujours_sa_reserve(self):
        """Aucune chronologie ne doit être lisible sans l'incertitude d'édition qui la limite."""
        r = agents.AgentChronologie().executer(self.c, concept="trieb")
        self.assertIn("reserve", r)
        self.assertIn("collation", r["reserve"])
        for e in r["etapes"]:
            self.assertIn("incertitude_annees", e)

    def test_tension_ne_conclut_jamais(self):
        """Une divergence de polarité est un CANDIDAT — jamais une contradiction établie."""
        r = agents.AgentTension().executer(self.c)
        self.assertEqual(r["statut"], "a_confirmer")
        self.assertIn("pas contradictions", r["note"])
        for c in r["candidats"]:
            self.assertEqual(len(c["paire"]), 2)

    def test_signaux_restent_a_confirmer(self):
        r = agents.AgentSignaux().executer(self.c)
        self.assertEqual(r["statut"], "a_confirmer")
        self.assertGreater(r["total"], 0)

    def test_tous_les_agents_sont_deterministes(self):
        """Même corpus, même sortie : sans cela, aucune analyse n'est reproductible."""
        for nom in ("profil", "cooccurrence"):
            a, b = agents.AGENTS[nom].executer(self.c), agents.AGENTS[nom].executer(self.c)
            self.assertEqual(a, b, "agent « %s » non déterministe" % nom)


class TestOrchestrateur(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.c = Corpus()

    def test_passe_generale_sans_demande(self):
        r = agents.orchestrer(self.c)
        self.assertEqual(r["plan"], ["profil", "cooccurrence", "signaux"])
        self.assertEqual(r["erreurs"], {})

    def test_passe_ciblee_sur_un_concept(self):
        r = agents.orchestrer(self.c, "trieb")
        self.assertEqual(r["plan"], ["concept", "chronologie", "tension"])
        self.assertEqual(r["erreurs"], {})
        self.assertGreater(r["resultats"]["concept"]["atomes"], 0)

    def test_un_agent_en_echec_ne_casse_pas_le_dossier(self):
        """L'échec doit être VISIBLE et isolé, jamais silencieux ni fatal."""
        class Cassé:
            nom, question = "casse", "?"

            def executer(self, corpus, **kw):
                raise RuntimeError("panne simulée")

        secours = agents.AGENTS.get("profil")
        agents.AGENTS["profil"] = Cassé()
        try:
            r = agents.orchestrer(self.c)
            self.assertIn("profil", r["erreurs"])
            self.assertIn("cooccurrence", r["resultats"])     # les autres ont bien tourné
        finally:
            agents.AGENTS["profil"] = secours


if __name__ == "__main__":
    unittest.main(verbosity=2)
