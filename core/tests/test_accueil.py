#!/usr/bin/env python3
"""TESTS du contrat d'accueil — le seul moyen qu'il ne soit pas qu'une déclaration d'intention.

Le dépôt affirme depuis longtemps qu'ajouter un auteur revient à « ajouter des concepts et des
groupes, sans toucher au moteur ». Une affirmation de ce genre ne coûte rien tant qu'aucun test ne
la tient : c'est précisément parce que personne ne la vérifiait que Sándor Ferenczi a pu entrer
avec 16,8 % des atomes du corpus SANS jeton de nom, rendant invisibles 80 mentions de lui.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import accueil          # noqa: E402


class TestAuteurDe(unittest.TestCase):

    def test_un_atome_sans_auteur_ECHOUE_au_lieu_de_devenir_freudien(self):
        """LE DÉFAUT QUE CE MODULE EXISTE POUR SUPPRIMER. Le dépôt écrit quarante fois
        `atome.get("auteur", "Sigmund Freud")`. Ce défaut n'est jamais nécessaire — `atomisation`
        pose le champ sur chaque atome — donc il ne peut se déclencher que si quelque chose est
        cassé, et il attribue alors du texte à Freud sans un mot."""
        with self.assertRaises(ValueError) as e:
            accueil.auteur_de({"id": "oeuvre:a12", "texte": "…"})
        self.assertIn("oeuvre:a12", str(e.exception))
        self.assertIn("Freud", str(e.exception), "le message doit dire QUEL défaut est refusé")

    def test_un_auteur_vide_est_traite_comme_absent(self):
        """Une chaîne vide est le résultat le plus probable d'un chemin qui pose le champ sans
        savoir quoi y mettre. La laisser passer rendrait le garde-fou contournable par accident."""
        with self.assertRaises(ValueError):
            accueil.auteur_de({"id": "x:a1", "auteur": ""})

    def test_un_atome_normal_rend_son_auteur(self):
        self.assertEqual(accueil.auteur_de({"id": "x:a1", "auteur": "Otto Rank"}), "Otto Rank")


class TestFrontiereDuCorpus(unittest.TestCase):
    """Le garde-fou doit protéger le pipeline, pas seulement exister comme fonction isolée."""

    def test_le_corpus_refuse_un_atome_sans_auteur_avant_indexation(self):
        from core.corpus import Corpus
        with self.assertRaisesRegex(ValueError, "SANS AUTEUR"):
            Corpus._valider_atomes([{"id": "x:a1", "texte": "…"}])

    def test_le_corpus_refuse_un_identifiant_duplique(self):
        from core.corpus import Corpus
        atomes = [
            {"id": "x:a1", "auteur": "Otto Rank"},
            {"id": "x:a1", "auteur": "Sigmund Freud"},
        ]
        with self.assertRaisesRegex(ValueError, "DUPLIQUÉ"):
            Corpus._valider_atomes(atomes)

    def test_le_corpus_refuse_un_identifiant_absent(self):
        from core.corpus import Corpus
        with self.assertRaisesRegex(ValueError, "SANS IDENTIFIANT"):
            Corpus._valider_atomes([{"auteur": "Otto Rank"}])


class TestContrat(unittest.TestCase):

    def _registres(self, **surcharges):
        base = {
            "jetons": {"Sigmund Freud": [], "Josef Breuer": [], "Nouvel Auteur": []},
            "biographies": {"Sigmund Freud": {}, "Josef Breuer": {}, "Nouvel Auteur": {}},
            "lexiques": {"Sigmund Freud": object(), "Nouvel Auteur": object()},
            "langues": {"Sigmund Freud": "de", "Josef Breuer": "de", "Nouvel Auteur": "de"},
        }
        base.update(surcharges)
        return base

    def test_un_auteur_sans_JETON_est_signale(self):
        """L'OUBLI RÉEL, rejoué. Sans jeton, aucun auteur ne peut être enregistré comme le
        nommant : l'auteur paraît isolé, et cet isolement se lit comme un fait de texte alors que
        c'est un trou de configuration."""
        r = accueil.verifier({"Nouvel Auteur"}, **self._registres(jetons={}))
        self.assertFalse(r["auteurs"][0]["conforme"])
        self.assertIn("jeton_de_nom", r["auteurs"][0]["manque"])

    def test_un_auteur_sans_LEXIQUE_n_est_pas_en_faute_mais_porte_une_reserve(self):
        """Josef Breuer, 885 atomes, zéro motif défini. Ce n'est pas un manquement — ses pages
        sont dans un volume de Freud et prennent les catégories de ce volume, ce qui est documenté
        — mais la conséquence doit voyager avec lui."""
        r = accueil.verifier({"Josef Breuer"}, **self._registres())
        fiche = r["auteurs"][0]
        self.assertTrue(fiche["conforme"], "l'absence de lexique n'est pas un manquement")
        self.assertIn("lexique", fiche["reserves"])
        self.assertFalse(fiche["lexique_propre"])

    def test_le_controle_porte_sur_les_auteurs_du_CORPUS_pas_sur_les_registres(self):
        """Un nom déclaré sans œuvre n'est pas un problème ; un auteur qui écrit sans être déclaré
        en est un. C'est le sens exact de l'oubli de Ferenczi, et l'inverse ne s'est jamais
        produit."""
        r = accueil.verifier({"Nouvel Auteur"}, **self._registres())
        self.assertEqual(r["total"], 1, "seul l'auteur ayant des atomes est contrôlé")
        self.assertEqual([f["auteur"] for f in r["auteurs"]], ["Nouvel Auteur"])

    def test_une_langue_irresoluble_est_un_manquement(self):
        """Un auteur à cheval sur deux langues rend None : aucune densité n'est alors mesurée sur
        lui. Le silence vaut mieux qu'un zéro faux, mais il doit être déclaré."""
        r = accueil.verifier({"Nouvel Auteur"},
                             **self._registres(langues={"Nouvel Auteur": None}))
        self.assertIn("langue", r["auteurs"][0]["manque"])

    def test_les_points_manquants_disent_QUI_manque_a_QUOI(self):
        """Un contrôle qui dit « non conforme » sans dire quoi ni à qui se contourne en le
        désactivant."""
        r = accueil.verifier({"A", "B"}, jetons={"A": []}, biographies={},
                             lexiques={}, langues={"A": "de", "B": "de"})
        manquants = accueil.points_manquants(r["auteurs"])
        self.assertEqual(sorted(manquants["biographie"]), ["A", "B"])
        self.assertEqual(manquants["jeton_de_nom"], ["B"])


class TestMesuresNonApplicables(unittest.TestCase):

    def test_le_controle_par_le_LEXIQUE_est_vide_pour_qui_n_en_a_pas(self):
        """TROUVÉ EN ÉCRIVANT CE MODULE, ET CELA CORRIGE UNE MESURE DÉJÀ PUBLIÉE.

        La couche des branches écarte une signature quand le motif vient du PROPRE lexique de
        l'auteur qui domine. Ce contrôle élimine 31 des 35 signatures du corpus — mais il est VIDE
        pour un auteur qui ne possède aucun motif : il ne peut jamais le déclencher. Les quatre
        signatures qui « survivaient » étaient toutes de Breuer, et ce n'était pas une
        coïncidence : c'est la seule chose qui pouvait arriver."""
        sans = accueil.mesures_non_applicables(False)
        self.assertTrue(sans)
        self.assertTrue(any("signature lexicale" in m["mesure"] for m in sans))
        self.assertTrue(any("VIDE" in m["pourquoi"] for m in sans))
        self.assertEqual(accueil.mesures_non_applicables(True), [])

    def test_chaque_mesure_ecartee_dit_POURQUOI(self):
        for m in accueil.mesures_non_applicables(False):
            self.assertGreater(len(m["pourquoi"]), 60, "raison trop courte : %s" % m["mesure"])


class TestPointsDuContrat(unittest.TestCase):

    def test_chaque_point_dit_OU_et_ce_qui_arrive_sinon(self):
        """Un contrat qui ne dit pas où écrire ni ce qu'on risque n'est pas un contrat, c'est un
        souhait. Chaque point porte donc son emplacement exact — `fichier : symbole` — et sa
        conséquence mesurée."""
        for p in accueil.POINTS:
            self.assertRegex(p["ou"], r"^[\w/.]+\.py : \w+$",
                             "le point %s ne dit pas où regarder" % p["cle"])
            self.assertGreater(len(p["sinon"]), 40,
                               "le point %s ne dit pas ce qui arrive sinon" % p["cle"])
            self.assertIsInstance(p["obligatoire"], bool)

    def test_un_seul_point_est_DERIVE_et_il_ne_se_declare_pas(self):
        """La distinction n'est pas cosmétique : offrir un endroit où déclarer la langue serait
        offrir un endroit où se tromper — une œuvre française rangée sous un auteur annoncé
        germanophone passerait sans bruit. La langue vient des œuvres, et se vérifie seulement."""
        derives = [p["cle"] for p in accueil.POINTS if p.get("derive")]
        self.assertEqual(derives, ["langue"])

    def test_un_seul_point_est_facultatif(self):
        """Si les exceptions se multipliaient, le contrat cesserait de garantir quoi que ce soit.
        Une seule case tolère l'absence — le lexique propre — et elle porte une réserve."""
        facultatifs = [p["cle"] for p in accueil.POINTS if not p["obligatoire"]]
        self.assertEqual(facultatifs, ["lexique"])


class TestCorpusReel(unittest.TestCase):
    """LE CONTRÔLE QUI COMPTE : les sept auteurs réellement présents le respectent-ils ?"""

    def test_tous_les_auteurs_du_corpus_satisfont_le_contrat(self):
        from core import comparaison, lexiques
        from core.corpus import Corpus
        sys.path.insert(0, os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "bin"))
        from exporter_d1 import AUTEURS                    # noqa: E402

        corpus = Corpus()
        auteurs = {accueil.auteur_de(a) for a in corpus.atomes}
        r = accueil.verifier(
            auteurs,
            jetons=comparaison.NOMS,
            biographies=AUTEURS,
            lexiques=lexiques.AUTEURS_AVEC_LEXIQUE_PROPRE,
            langues=comparaison.langues_par_auteur(corpus.atomes, corpus.oeuvres))
        self.assertEqual(r["conformes"], r["total"],
                         "auteurs non conformes : %s" % accueil.points_manquants(r["auteurs"]))
        # ET SURTOUT : `auteur_de` a été appelé sur les 116 545 atomes sans lever. Le défaut
        # silencieux `get("auteur", "Sigmund Freud")` est donc bien mort — il ne protège rien.
        self.assertGreaterEqual(len(auteurs), 7)

    def test_l_exception_du_lexique_reste_UNIQUE(self):
        """Breuer est le seul auteur sans lexique propre. Si un second apparaissait, ce ne serait
        plus une exception documentée mais une dérive de la règle fondatrice — et il faudrait le
        décider explicitement plutôt que le découvrir.

        LE TEST INTERROGE `AUTEURS_AVEC_LEXIQUE_PROPRE`, PAS `PAR_AUTEUR`, et la différence a
        compté : Freud n'est pas dans `PAR_AUTEUR` — ses tables vivent dans `core/lexique.py` —
        si bien que la première version de ce contrôle le comptait comme dépourvu de lexique. Une
        version antérieure de ce test masquait le défaut en excluant Freud à la main ; le
        générateur, lui, ne le masquait pas, et le document allait imprimer que Freud est décrit
        avec le lexique d'un autre."""
        from core import lexiques
        from core.corpus import Corpus
        auteurs = {accueil.auteur_de(a) for a in Corpus().atomes}
        sans = sorted(a for a in auteurs if a not in lexiques.AUTEURS_AVEC_LEXIQUE_PROPRE)
        self.assertEqual(sans, ["Josef Breuer"],
                         "l'exception au « chaque auteur a ses catégories » a changé : %s" % sans)
        self.assertTrue(lexiques.connu("Sigmund Freud"),
                        "le registre doit dire la vérité sur lui-même")


class TestDocumentGenere(unittest.TestCase):

    def _doc(self):
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        chemin = os.path.join(racine, "documentation", "ACCUEIL_D_UN_AUTEUR.md")
        self.assertTrue(os.path.exists(chemin), "document non généré : bin/generer_accueil.py")
        with open(chemin, encoding="utf-8") as f:
            return f.read()

    def test_le_document_se_declare_genere(self):
        self.assertIn("**DOCUMENT GÉNÉRÉ**", self._doc())

    def test_le_document_porte_les_deux_pannes_reelles(self):
        """Un contrat écrit sans les pannes qui l'ont motivé se lit comme une formalité. Les deux
        qui comptent : l'oubli du jeton de nom (Ferenczi invisible) et le défaut silencieux qui
        attribue à Freud tout atome sans auteur."""
        texte = self._doc()
        for attendu in ("16,8", "Ferenczi", "Sigmund Freud", "116 545", "vide pour lui"):
            self.assertIn(attendu, texte, "le document a perdu une panne : %s" % attendu)


if __name__ == "__main__":
    unittest.main(verbosity=2)
