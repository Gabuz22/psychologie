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


class TestRegistreDesReprises(unittest.TestCase):
    """Le registre des reprises LUES — jugements portés sur des COUPLES, non sur des atomes."""

    def test_le_registre_est_valide(self):
        r = verification.valider_reprises()
        self.assertTrue(r["ok"], r["erreurs"])
        self.assertGreater(r["juges"], 0)

    def test_la_cle_ne_depend_pas_de_l_ordre_de_lecture(self):
        """Le même couple lu dans un sens ou dans l'autre doit retrouver le même verdict : sinon
        un changement d'ordre d'itération dans le calcul perdrait silencieusement la lecture."""
        self.assertEqual(verification.cle_reprise("aaa", "bbb"),
                         verification.cle_reprise("bbb", "aaa"))

    def test_un_sens_sans_identifiants_est_refuse(self):
        """PIÈGE RÉEL. La clé est triée, donc elle perd l'ordre (a, b) sur lequel le sens a été
        rendu. Sans id_a/id_b, « a_vers_b » ne désigne plus personne — et publier l'emprunt à
        l'envers serait pire que ne rien publier."""
        faux = {"verdicts": {"x|y": {"verdict": "confirme", "motif": "m", "sens_lu": "a_vers_b"}}}
        self.assertFalse(verification.valider_reprises(faux)["ok"])

    def test_un_verdict_sans_motif_est_refuse(self):
        faux = {"verdicts": {"x|y": {"verdict": "confirme"}}}
        self.assertFalse(verification.valider_reprises(faux)["ok"])

    def test_un_reclassement_sans_cible_est_refuse(self):
        """« Reclassé » veut dire : ces deux-là citent un TIERS. Sans nommer le tiers, l'énoncé
        est vide — et le lien resterait affiché comme un rapport entre les deux auteurs."""
        faux = {"verdicts": {"x|y": {"verdict": "reclasse", "motif": "m"}}}
        self.assertFalse(verification.valider_reprises(faux)["ok"])

    def test_les_verdicts_lus_portent_bien_sur_des_couples_du_corpus(self):
        """Un verdict qui ne s'ancre plus sur aucun couple calculé est du travail de lecture
        PERDU : c'est arrivé deux fois quand la segmentation a changé. Le test le dit tout de
        suite au lieu de laisser la perte passer inaperçue à l'export.
        """
        from core import comparaison
        from core.corpus import Corpus
        corpus = Corpus()
        par_auteur = {}
        for a in corpus.atomes:
            par_auteur.setdefault(a.get("auteur", "Sigmund Freud"), []).append(a)
        index = [comparaison._n_grammes_utiles(v, None) for v in par_auteur.values()]
        df = comparaison.frequences_documentaires(index)
        vus = set()
        noms = sorted(par_auteur)
        for i, x in enumerate(noms):
            for y in noms[i + 1:]:
                for l in comparaison.reprises(par_auteur[x], par_auteur[y], df):
                    if l["contenance"] >= comparaison.SEUIL_PUBLICATION:
                        vus.add(verification.cle_reprise(l["a"]["empreinte"], l["b"]["empreinte"]))
        orphelins = set(verification.charger_reprises()["verdicts"]) - vus
        self.assertFalse(orphelins, "verdicts de lecture désancrés : %s" % sorted(orphelins))

    def test_le_sens_lu_ne_se_retourne_pas_sur_une_derive_de_numero(self):
        """DÉFAUT MESURÉ, ET IL PUBLIAIT DES EMPRUNTS À L'ENVERS — le seul risque que le registre
        des reprises se donne explicitement pour mission d'écarter.

        La clé d'un verdict est faite des deux empreintes TRIÉES : elle perd l'ordre (a, b) sur
        lequel « a_vers_b » a été rendu. L'export doit donc retourner le sens quand le calcul
        présente le couple dans l'autre ordre. Il décidait ce retournement en comparant
        `id_a` à l'identifiant courant du côté a — deux identifiants POSITIONNELS. Or ceux-ci
        dérivent dès qu'on retire du paratexte en amont : c'est la raison même pour laquelle ce
        registre est clé par empreinte, et le commentaire du code le disait deux lignes plus haut.

        Mesuré au moment de la correction : sur 56 liens portant un sens lu, 16 avaient dérivé
        dans leur propre œuvre — et le retournement se déclenchait pour rien, publiant l'inverse
        de ce qui avait été lu. Aucun ne relevait d'un vrai changement d'ordre. Le cas le plus net
        est Abraham citant Freud en toutes lettres (« Ich zitiere den folgenden Passus wörtlich
        nach Freud », 1909) publié comme Freud citant Abraham — neuf ans avant que le texte
        d'Abraham existe.

        Le discriminant correct est l'ŒUVRE, qui ne dérive pas, et qui suffit parce que les deux
        côtés d'une reprise appartiennent toujours à des auteurs — donc à des œuvres — différents.
        """
        table = verification.charger_reprises()
        avec_sens = [j for j in table["verdicts"].values() if j.get("sens_lu")]
        self.assertGreater(len(avec_sens), 0)
        for j in avec_sens:
            self.assertTrue(j.get("empreinte_a"),
                            "verdict portant un sens sans empreinte_a : %r" % j.get("id_a"))

        # Le validateur doit REFUSER un sens qu'on ne saurait pas orienter.
        sans_ancre = {"verdicts": {"x|y": {"verdict": "confirme", "motif": "m",
                                           "sens_lu": "a_vers_b",
                                           "id_a": "o:a1", "id_b": "p:a2"}}}
        self.assertFalse(verification.valider_reprises(sans_ancre)["ok"])

        # Et une ancre qui ne désigne aucun des deux côtés est une erreur, pas un détail.
        hors_couple = {"verdicts": {"x|y": {"verdict": "confirme", "motif": "m",
                                            "sens_lu": "a_vers_b", "id_a": "o:a1",
                                            "id_b": "p:a2", "empreinte_a": "zzz"}}}
        self.assertFalse(verification.valider_reprises(hors_couple)["ok"])

        # LE FAIT QUI A INVALIDÉ LA PREMIÈRE CORRECTION, gardé pour qu'on ne la refasse pas :
        # on avait d'abord voulu trancher sur l'ŒUVRE, en supposant que les deux côtés d'une
        # reprise appartiennent toujours à des œuvres différentes. C'est faux — les volumes
        # CO-ÉCRITS existent, et « Studien über Hysterie » porte à la fois du Breuer et du Freud.
        import sqlite3
        racine = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        base = os.path.join(racine, "derive", "d1", "corpus.sqlite")
        if os.path.exists(base):
            with sqlite3.connect(base) as db:
                memes = db.execute(
                    "SELECT COUNT(*) FROM liens_reprise l"
                    " JOIN atomes a ON a.id = l.atome_a JOIN atomes b ON b.id = l.atome_b"
                    " WHERE a.oeuvre_id = b.oeuvre_id").fetchone()[0]
            self.assertGreater(memes, 0,
                               "plus aucune reprise intra-œuvre : si c'est durable, la note "
                               "ci-dessus sur les volumes co-écrits est à revoir")
