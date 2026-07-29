#!/usr/bin/env python3
"""TESTS de la couche d'appariement — celle qui a été MESURÉE PUIS ÉCARTÉE.

Ces tests ne protègent pas une fonctionnalité livrée : `core/appariement.py` n'alimente ni la base
ni le site. Ils protègent trois choses qui, elles, comptent :

  1. l'INSTRUMENT reste juste — un jour où l'on rouvrira le chantier, les mesures publiées dans
     `documentation/APPARIEMENT_ECARTE.md` doivent pouvoir être rejouées à l'identique ;
  2. les GARDE-FOUS qui ont fait échouer honnêtement la méthode restent en place, en particulier
     l'exclusion croisée sans laquelle le témoin se validerait tout seul ;
  3. le DÉFAUT DE LEXIQUE que cet échec a permis de trouver ne revient pas.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core import appariement, comparaison, lexique, lexiques        # noqa: E402
from core.corpus import Corpus                                       # noqa: E402


class TestExclusion(unittest.TestCase):
    """Sans exclusion croisée, le témoin positif se valide lui-même : les deux signatures
    partagent le mot cherché et toute sa famille, et l'on mesure une tautologie."""

    def test_le_radical_est_cherche_ou_qu_il_soit_dans_le_mot(self):
        """L'ALLEMAND COMPOSE. Le motif est appliqué avec « \\b » en tête, donc « \\b(traum) »
        attrape « Traumdeutung » mais pas « Angsttraum », où le radical est en seconde position.

        Mesuré ensuite : cette fuite ne change PAS le résultat (écart médian +0,0000), parce que
        chaque auteur a ses propres composés et que le cosinus ne compte que les mots présents des
        deux côtés. L'exclusion forte est gardée quand même — un garde-fou dont on a mesuré qu'il
        ne sert à rien sur ce corpus peut servir sur le suivant.
        """
        vocabulaire = {"traum", "traumdeutung", "angsttraum", "wunschtraum", "trauma", "baum"}
        touches = appariement.mots_du_motif(r"\b(traum)", vocabulaire)
        self.assertIn("angsttraum", touches)
        self.assertIn("wunschtraum", touches)
        self.assertNotIn("baum", touches)

    def test_les_deux_motifs_sont_retires_des_deux_cotes(self):
        """L'exclusion est CROISÉE : comparer (A, M) à (B, M') retire M et M' des deux signatures.
        Sinon le couple de même mot part avec un avantage que le couple de mots différents n'a
        pas, et la séparation mesurée n'est plus qu'un artefact de protocole."""
        atomes = [
            {"id": "x:1", "texte": "Der Traum ist eine Wunscherfüllung des Kindes.",
             "oeuvre": "x", "auteur": "A"},
            {"id": "x:2", "texte": "Der Traum des Kindes zeigt die Wunscherfüllung.",
             "oeuvre": "x", "auteur": "A"},
            {"id": "y:1", "texte": "Die Angst ist eine Wunscherfüllung des Kindes.",
             "oeuvre": "y", "auteur": "B"},
        ]
        s = appariement.Signatures(atomes, {"A": "de", "B": "de"})
        for exclu in (r"\b(traum)", r"\b(angst)"):
            self.assertTrue(s.exclusion("A", exclu) is not None)
        # Le mot exclu ne doit jamais figurer parmi les mots qui rapprochent deux signatures.
        partages = s.partages("A", r"\b(traum)", "B", r"\b(angst)")
        self.assertNotIn("traum", partages)
        self.assertNotIn("angst", partages)


class TestSignature(unittest.TestCase):

    def test_la_normalisation_est_par_auteur(self):
        """Un tic d'écriture ne doit pas faire se ressembler tous les concepts d'un même homme :
        la sur-représentation est calculée contre la fréquence du mot CHEZ CET AUTEUR."""
        # Trente porteurs : au-dessus du seuil de 25, sinon la signature n'est pas rendue.
        atomes = [{"id": "x:%d" % i, "oeuvre": "x", "auteur": "A",
                   "texte": "Der Patient zeigt eine Verdrängung." if i < 30
                            else "Der Patient schläft ruhig."} for i in range(90)]
        s = appariement.Signatures(atomes, {"A": "de"})
        fiche = s.signature("A", r"\b(verdrang)")
        self.assertIsNotNone(fiche)
        # « patient » est partout chez cet auteur : il ne doit pas caractériser le concept.
        poids = fiche["mots"]
        self.assertLess(poids.get("patient", 0), poids.get("zeigt", 0))

    def test_un_effectif_trop_faible_ne_rend_pas_de_signature(self):
        """Sous 25 porteurs, une signature décrit un échantillon et non un usage : mieux vaut
        rien rendre que rendre du bruit qu'on prendrait pour une mesure."""
        atomes = [{"id": "x:%d" % i, "oeuvre": "x", "auteur": "A",
                   "texte": "Ein Satz ohne das Wort." if i else "Die Verdrängung wirkt."}
                  for i in range(40)]
        s = appariement.Signatures(atomes, {"A": "de"})
        self.assertIsNone(s.signature("A", r"\b(verdrang)"))

    def test_la_concentration_par_oeuvre_est_portee(self):
        """SEPT DES SEIZE DIVERGENCES LUES ÉTAIENT DES ARTEFACTS D'ŒUVRE UNIQUE. Une signature
        tirée à 90 % d'un seul livre décrit le vocabulaire de ce livre ; le chiffre doit voyager
        avec la mesure, sans quoi la réserve se perd."""
        atomes = ([{"id": "x:%d" % i, "oeuvre": "x", "auteur": "A",
                    "texte": "Die Verdrängung des Kindes wirkt."} for i in range(30)]
                  + [{"id": "y:%d" % i, "oeuvre": "y", "auteur": "A",
                      "texte": "Die Verdrängung der Angst wirkt."} for i in range(5)])
        s = appariement.Signatures(atomes, {"A": "de"})
        self.assertAlmostEqual(s.signature("A", r"\b(verdrang)")["concentration"], 30 / 35, places=2)


class TestReference(unittest.TestCase):
    """DÉFAUT MESURÉ. Le score croît avec l'effectif et décroît avec l'écart de taille entre les
    deux corpus — un « détecteur » n'utilisant QUE le rapport des effectifs atteint déjà une AUC
    de 0,576. Juger un score contre une médiane globale confond donc une divergence d'usage avec
    une différence de volume : plusieurs cas spectaculaires (schmerz, schuld, motiv) ne
    survivaient pas à ce contrôle."""

    def test_la_reference_depend_de_l_effectif_et_de_l_ecart(self):
        positifs = [{"score": 0.10, "porteurs_min": 30, "ecart_taille": 0.2},
                    {"score": 0.12, "porteurs_min": 30, "ecart_taille": 0.2},
                    {"score": 0.30, "porteurs_min": 300, "ecart_taille": 0.2},
                    {"score": 0.32, "porteurs_min": 300, "ecart_taille": 0.2}]
        appariement.reference(positifs)
        self.assertLess(positifs[0]["reference"], positifs[2]["reference"])
        # Un score de 0,30 est ORDINAIRE pour un gros effectif, remarquable pour un petit.
        self.assertGreater(positifs[0]["ecart_a_la_reference"], -0.05)


class TestDedoublonnage(unittest.TestCase):

    def test_deux_noms_pour_un_meme_ensemble_d_atomes_sont_reduits(self):
        """DÉFAUT RÉEL DU LEXIQUE. « halluzination » et « halluzinatorisch » sélectionnent les
        mêmes phrases sous deux noms ; le témoin comptait donc deux fois le même couple.
        Dédoublonner sur la CHAÎNE du motif ne suffit pas — il faut comparer ce qui est
        SÉLECTIONNÉ."""
        # Deux moitiés distinctes : « autre » ne doit PAS sélectionner le même ensemble que les
        # deux premiers, sinon le test ne prouverait rien (tout s'effondrerait sur un seul nom).
        atomes = ([{"id": "x:%d" % i, "oeuvre": "x", "auteur": "A",
                    "texte": "Eine halluzinatorische Erscheinung tritt auf."} for i in range(30)]
                  + [{"id": "y:%d" % i, "oeuvre": "y", "auteur": "A",
                      "texte": "Eine Wunscherfüllung tritt auf."} for i in range(30)])
        s = appariement.Signatures(atomes, {"A": "de"})
        catalogue = {"un": (r"\b(halluzin)", "A", "g"),
                     "deux": (r"\b(halluzinator|halluzin)", "A", "g"),
                     "autre": (r"\b(wunsch)", "A", "g")}
        garde = appariement.dedoublonner(s, catalogue)
        self.assertEqual(len(garde), 2, "les deux noms du même ensemble n'ont pas été réduits")
        self.assertIn("autre", garde)


class TestDefautDeLexiqueTrouveParCetEchec(unittest.TestCase):
    """CE QUE L'EXERCICE A RAPPORTÉ, et qu'il faut protéger.

    En lisant les voisinages du concept « tier » d'Otto Rank, on a trouvé que ses motifs
    attrapaient massivement autre chose. Le pire tombait chez l'auteur qu'il pouvait le plus
    fausser : « \\bschwan » attrapait SCHWANGER — enceinte — 65 fois, chez celui dont la thèse
    centrale est le traumatisme de la naissance. Et « \\bwolf » attrapait Wolfram von Eschenbach,
    46 % de ses captures.
    """

    def test_enceinte_n_est_pas_un_animal(self):
        import re
        motifs = lexiques.PAR_AUTEUR["Otto Rank"].CONCEPTS["decor_mythique"]["termes"]["tier"]
        r = re.compile("|".join(r"\b" + m for m in motifs))
        for faux in ("schwanger", "schwangerschaft", "schwangere", "schwanken", "schwankende",
                     "wolfram", "wolfdietrich", "hirschfeld"):
            self.assertIsNone(r.search(faux), "« %s » compté comme un animal" % faux)

    def test_les_vrais_animaux_restent_pris(self):
        """La correction ne doit pas emporter le Chevalier au Cygne, qui est le motif central de
        la Lohengrinsage — c'est bien l'animal qui fait le personnage."""
        import re
        motifs = lexiques.PAR_AUTEUR["Otto Rank"].CONCEPTS["decor_mythique"]["termes"]["tier"]
        r = re.compile("|".join(r"\b" + m for m in motifs))
        for vrai in ("tier", "tiere", "schwan", "schwane", "schwanritter", "schwanenritter",
                     "wolf", "wolfin", "hirsch", "hirschkuh", "vogel", "hund"):
            self.assertIsNotNone(r.search(vrai), "« %s » n'est plus reconnu" % vrai)


class TestLaCoucheNAlimenteRien(unittest.TestCase):
    """L'INVARIANT LE PLUS IMPORTANT DE CE FICHIER.

    La méthode a été mesurée puis écartée : sur la tâche réelle sa précision est de 6 %, elle ne
    distingue pas un mot de son contraire, et la lecture n'a confirmé qu'une divergence sur seize.
    Rien de tout cela ne doit se retrouver publié par inadvertance.
    """

    def test_aucun_export_ni_aucune_route_ne_l_utilise(self):
        """On cherche l'IMPORT du module, pas le mot « appariement » — qui est un mot français
        courant, employé ailleurs dans le dépôt à propos de l'appariement des grappes à leur
        éditorial. Un test qui confond les deux crie au loup et finit par être désactivé."""
        import re
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        usage = re.compile(r"import\s+[\w,\s]*\bappariement\b"     # from core import appariement
                           r"|core\.appariement"
                           r"|/api/appariement")                    # une route côté worker
        for chemin in (os.path.join(racine, "bin", "exporter_d1.py"),
                       os.path.join(racine, "web", "worker", "donnees.js"),
                       os.path.join(racine, "web", "worker", "index.js"),
                       os.path.join(racine, "web", "site", "app.js")):
            with open(chemin, encoding="utf-8") as f:
                self.assertIsNone(usage.search(f.read()),
                                  "%s utilise une couche écartée" % os.path.basename(chemin))

    def test_l_echec_est_documente_avec_ses_chiffres(self):
        """Une décision négative non écrite se refait. Celle-ci a coûté assez cher pour mériter
        ses nombres."""
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        doc = os.path.join(racine, "documentation", "APPARIEMENT_ECARTE.md")
        self.assertTrue(os.path.exists(doc))
        with open(doc, encoding="utf-8") as f:
            texte = f.read()
        for chiffre in ("0,893", "6,2 %", "0,285", "sur seize", "schwanger"):
            self.assertIn(chiffre, texte, "chiffre manquant dans la trace : %s" % chiffre)


if __name__ == "__main__":
    unittest.main()
