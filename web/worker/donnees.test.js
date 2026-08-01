/* TESTS de `donnees.js` — `node --test` depuis web/.
 *
 * Un seul test ici, mais il protège un défaut réel : l'API `comparaison` a longtemps CALCULÉ
 * les liens de reprise sans jamais exposer le VERDICT DE LECTURE humaine (confirme/rejete/
 * reclasse, 507 entrées au 2026-08-01) — trouvé en lisant le code, pas en le testant, ce qui est
 * précisément la faute que ce test empêche de refaire. Sans lui, une IA connectée au corpus
 * pouvait citer comme un emprunt un lien identifié par la lecture comme un faux positif.
 *
 * Le stub D1 ci-dessous n'a pas la prétention de couvrir tout `env.DB` : il route chaque
 * requête vers des lignes canned selon la table interrogée, assez pour que `comparaison()`
 * s'exécute réellement et que la plomberie SQL → JS soit protégée par une assertion, pas par une
 * relecture.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import { carte, chronologieConcept, comparaison } from "./donnees.js";

const LIEN_LU = {
  contenance: 1.0, force: "manifeste", sens: "a_vers_b", source_tierce: 0, a_verifier: 0,
  partages: "…", evenement: 1,
  verdict: "confirme", sens_lu: "a_vers_b", reclasse_vers: null,
  motif_lecture: "Freud recopie la vignette d'Anna O. de Breuer, attribution six atomes en amont.",
  auteur_a: "Josef Breuer", auteur_b: "Sigmund Freud",
  id_a: "studien_ueber_hysterie:a281", texte_a: "…", oeuvre_a: "Studien über Hysterie",
  annee_a: 1895, source_a: "relu", suspect_a: 0,
  id_b: "ueber_psychoanalyse:a67", texte_b: "…", oeuvre_b: "Über Psychoanalyse",
  annee_b: 1910, source_b: "relu", suspect_b: 0,
};

function stubDB(lignesLiens) {
  return {
    prepare(sql) {
      const s = sql.trim();
      // La matrice appelle `.all()` directement (pas de paramètre à lier) ; les liens, lectures
      // et nominations appellent `.bind(...).all()`. Le stub sert les deux formes, exactement
      // comme le fait D1.
      const resoudre = async () => {
        if (s.includes("FROM liens_reprise") && s.includes("GROUP BY")) {
          return { results: [] };                      // matrice : non testée ici
        }
        if (s.includes("FROM liens_reprise")) return { results: lignesLiens };
        if (s.includes("FROM lectures_declarees")) return { results: [] };
        if (s.includes("FROM nominations")) return { results: [] };
        throw new Error("requête non anticipée par le stub : " + s.slice(0, 60));
      };
      return { all: resoudre, bind: () => ({ all: resoudre }) };
    },
  };
}

test("comparaison() expose le verdict de lecture, pas seulement le sens calculé", async () => {
  const rep = await comparaison({ DB: stubDB([LIEN_LU]) }, {});
  assert.equal(rep.liens.length, 1);
  const lien = rep.liens[0];
  // Les quatre champs de lecture doivent traverser la couche SQL → JS sans être perdus en route.
  assert.equal(lien.verdict, "confirme");
  assert.equal(lien.sens_lu, "a_vers_b");
  assert.equal(lien.reclasse_vers, null);
  assert.ok(lien.motif_lecture.includes("Anna O."));
});

test("comparaison() distingue toujours le sens CALCULÉ du sens LU, même verdict absent", async () => {
  const nonLu = { ...LIEN_LU, verdict: null, sens_lu: null, motif_lecture: null };
  const rep = await comparaison({ DB: stubDB([nonLu]) }, {});
  const lien = rep.liens[0];
  assert.equal(lien.verdict, null);
  assert.equal(lien.sens, "a_vers_b", "le sens calculé doit rester lisible même sans lecture");
});

test("la réserve documente le verdict et met en garde contre le publier sans motif", async () => {
  const rep = await comparaison({ DB: stubDB([]) }, {});
  assert.match(rep.reserve, /verdict/);
  assert.match(rep.reserve, /rejete/);
  assert.match(rep.reserve, /reclasse/);
  assert.match(rep.reserve, /motif_lecture/);
});

/* LES MENTIONS — même défaut que les reprises, découvert en fermant celui-là. Les 2 899 mentions
 * ont été lues le 2026-08-01 et 180 sont des faux positifs (dont 57 « Abraham » qui sont le
 * patriarche biblique). Servir le compte brut ferait publier « Rank nomme Abraham 62 fois » alors
 * que la lecture en rejette une partie. Ces tests protègent l'exposition du verdict.
 */
const MENTION_LUE = {
  auteur: "Otto Rank", auteur_nomme: "Karl Abraham", n: 62, homographes: 62,
  confirmees: 38, rejetees: 24, reclassees: 0, non_lues: 0,
};
const PASSAGE_LU = {
  atome_id: "inzest_motiv:a11", texte: "…", oeuvre: "Das Inzest-Motiv", annee_oeuvre: 1912,
  auteur: "Otto Rank", auteur_nomme: "Karl Abraham",
  homographe: "« Abraham » est aussi le patriarche biblique.",
  verdict: "rejete", reclasse_vers: null,
  motif_lecture: "Il s'agit du patriarche biblique — « der Stammvater Abraham », non du collègue.",
};

function stubCarteDB() {
  const par = (s) => {
    if (s.includes("FROM carte_couples")) return { results: [] };
    if (s.includes("FROM carte_actes")) return { results: [] };
    if (s.includes("FROM mentions") && s.includes("GROUP BY")) return { results: [MENTION_LUE] };
    if (s.includes("FROM mentions")) return { results: [PASSAGE_LU] };
    if (s.includes("FROM carte_couverture")) return { results: [] };
    throw new Error("requête non anticipée par le stub : " + s.slice(0, 60));
  };
  return {
    prepare(sql) {
      const s = sql.trim();
      const resoudre = async () => par(s);
      // `carte()` lit les totaux de couverture avec `.first()`, les autres avec `.all()`.
      return {
        all: resoudre,
        first: async () => (par(s).results || [])[0] || null,
        bind: () => ({ all: resoudre, first: async () => (par(s).results || [])[0] || null }),
      };
    },
  };
}

test("carte() rend le compte des mentions AVEC leur verdict de lecture, jamais brut", async () => {
  const rep = await carte({ DB: stubCarteDB() }, { auteur: "Otto Rank" });
  const m = rep.mentions[0];
  assert.equal(m.n, 62);
  // Sans ces quatre champs, « Rank nomme Abraham 62 fois » est publié comme un fait alors que
  // la lecture en rejette 24.
  assert.equal(m.confirmees, 38);
  assert.equal(m.rejetees, 24);
  assert.equal(m.reclassees, 0);
  assert.equal(m.non_lues, 0);
});

test("carte() fait voyager le verdict avec le PASSAGE, pas seulement avec le compte", async () => {
  const rep = await carte({ DB: stubCarteDB() }, { auteur: "Otto Rank" });
  const p = rep.mentions_passages[0];
  assert.equal(p.verdict, "rejete");
  assert.ok(p.motif_lecture.includes("patriarche"),
            "le motif doit accompagner le verdict — un jugement non argumenté ne se conteste pas");
});

test("la réserve des mentions chiffre l'homographe au lieu de seulement l'annoncer", async () => {
  const rep = await carte({ DB: stubCarteDB() }, {});
  assert.match(rep.mentions_reserve, /2 899/);
  assert.match(rep.mentions_reserve, /39 %/, "le taux de rejet de « Abraham » doit être donné");
  assert.match(rep.mentions_reserve, /rejete/);
  assert.match(rep.mentions_reserve, /reclasse_vers/);
});

/* LE DOSSIER EXTERNE D'UN CONCEPT — trois signaux déjà vérifiés (actes, densité, mentions),
 * jamais fusionnés en un score. Le défaut réel qu'un stub naïf laisserait passer : joindre
 * `usages` par le seul NOM du concept, qui collisionne entre lexiques (mesuré : 80 sous-concepts
 * du corpus ont plusieurs motifs distincts sous le même nom, « angst » en a quatre). Le stub
 * capture donc les paramètres liés pour vérifier que `lexique` — pas seulement `sous_concept` —
 * fait bien partie de la requête, sans quoi ce test ne détecterait pas une régression sur ce
 * point précis.
 */
const ID_RANK = 3;
const ID_FREUD = 5;

const ACTE_TOUCHANT = {
  contenance_max: 0.62, force: "partielle", sens: "b_vers_a", sens_lu: null,
  verdict: "confirme", reclasse_vers: null,
  concepts_communs: "geburt, mutter, vater",
  citation_a: "…passage de Rank…", citation_b: "…passage de Freud…",
  auteur_a: "Otto Rank", auteur_b: "Sigmund Freud",
  oeuvre_a: "Das Inzest-Motiv", annee_a: 1912, oeuvre_b: "Neue Folge", annee_b: 1933,
};
const ACTE_SANS_LE_CONCEPT = {
  contenance_max: 0.9, force: "manifeste", sens: null, sens_lu: null,
  verdict: "confirme", reclasse_vers: null,
  concepts_communs: "kind, familie",             // ne contient PAS "geburt"
  citation_a: "…", citation_b: "…",
  auteur_a: "Otto Rank", auteur_b: "Karl Abraham",
  oeuvre_a: "Das Inzest-Motiv", annee_a: 1912, oeuvre_b: "Klinische Beiträge", annee_b: 1907,
};
// UN ACTE REJETÉ, qui doit survivre au dossier avec son verdict intact — DÉFAUT TROUVÉ PAR REVUE
// ADVERSARIALE : sans ce cas, rien ne distingue « personne n'a testé le cas rejete » de « le
// filtre WHERE verdict='confirme' a été retiré par erreur ». Les deux se ressemblent : zéro
// assertion qui casse. Ce test-ci casse si un tel filtre est ajouté.
const ACTE_REJETE = {
  contenance_max: 0.31, force: "partielle", sens: null, sens_lu: null,
  verdict: "rejete", reclasse_vers: null,
  concepts_communs: "geburt, koenigsfamilie",
  citation_a: "…titre d'ouvrage recopié par l'OCR…", citation_b: "…",
  auteur_a: "Otto Rank", auteur_b: "Wilhelm Stekel",
  oeuvre_a: "Das Inzest-Motiv", annee_a: 1912, oeuvre_b: "Nervöse Angstzustände", annee_b: 1908,
};
const USAGE_RANK = { lexique: ID_RANK, auteur: "Otto Rank", pour_mille: 51.1,
                     atomes: 14938, porteurs: 764 };
const USAGE_FREUD = { lexique: ID_RANK, auteur: "Sigmund Freud", pour_mille: 3.2,
                      atomes: 40276, porteurs: 129 };
// LA MÊME MESURE, SOUS UN AUTRE LEXIQUE — le cas « angst » du corpus réel, rejoué ici : un motif
// concurrent, DÉFINI PAR UN AUTRE AUTEUR, sous le même sous_concept. S'il apparaissait dans le
// dossier de Rank, ce serait la régression exacte que ce chantier a mesurée et corrigée.
const USAGE_MOTIF_CONCURRENT = { lexique: ID_FREUD, auteur: "Karl Abraham", pour_mille: 999.9,
                                 atomes: 1, porteurs: 1 };
const MENTION_DOSSIER = {
  auteur_nomme: "Sigmund Freud", id: "inzest_motiv:a204", texte: "…",
  oeuvre: "Das Inzest-Motiv", annee_oeuvre: 1912,
  verdict: "confirme", reclasse_vers: null,
  motif_lecture: "Rank renvoie explicitement à la Traumdeutung sur ce point.",
};
const MENTION_NON_LUE = {
  auteur_nomme: "Karl Abraham", id: "inzest_motiv:a311", texte: "…",
  oeuvre: "Das Inzest-Motiv", annee_oeuvre: 1912,
  verdict: null, reclasse_vers: null, motif_lecture: null,
};

function stubDossierDB({ possede = true, actes = [ACTE_TOUCHANT, ACTE_SANS_LE_CONCEPT, ACTE_REJETE],
                         usages = [USAGE_RANK, USAGE_FREUD, USAGE_MOTIF_CONCURRENT],
                         mentions = [MENTION_DOSSIER, MENTION_NON_LUE],
                         couples = [{ silence: null }] } = {}) {
  return {
    prepare(sql) {
      const s = sql.trim();
      return {
        bind(...args) {
          const resoudre = async () => {
            // Variante AVEC auteur (deux paramètres liés) : simule la vraie appartenance —
            // c'est CE garde-fou que le défaut Breuer a fait échouer avant correction.
            if (s.includes("SELECT 1 FROM concepts") && args.length === 2) {
              return possede ? { 1: 1 } : null;
            }
            // Variante SANS auteur (comportement historique, un seul paramètre) : le concept
            // existe toujours dans ces tests, quel que soit l'auteur demandé ailleurs.
            if (s.includes("SELECT 1 FROM concepts") && args.length === 1) return { 1: 1 };
            if (s.includes("SELECT id FROM auteurs")) return { id: ID_RANK };
            if (s.includes("WITH concept_atomes")) return { results: [] };
            if (s.includes("FROM carte_actes")) return { results: actes };
            if (s.includes("FROM usages")) {
              // LE POINT QUE CE STUB DOIT PROTÉGER : filtrage RÉEL par `lexique`, pas seulement
              // vérification de présence du paramètre — une ligne sous un autre lexique
              // (USAGE_MOTIF_CONCURRENT) est présente dans les données canned ; si le SQL perdait
              // son `AND u.lexique = ?2`, ce test la verrait apparaître à tort.
              const lexiqueLie = args[1];
              return { results: usages.filter((u) => u.lexique === lexiqueLie) };
            }
            if (s.includes("FROM mentions")) return { results: mentions };
            if (s.includes("FROM carte_couples")) return { results: couples };
            throw new Error("requête non anticipée par le stub : " + s.slice(0, 70));
          };
          return { all: resoudre, first: async (col) => {
            const r = await resoudre();
            if (r == null) return null;
            return col ? r[col] : (Array.isArray(r.results) ? r.results[0] || null : r);
          } };
        },
        first: async () => {
          // Variante SANS auteur (un seul paramètre, appelée via .bind(x).first() plus haut) :
          // n'est jamais exercée directement ici (chronologieConcept passe toujours par bind),
          // conservée pour les appels historiques à un seul paramètre.
          if (s.includes("SELECT 1 FROM concepts")) return { 1: 1 };
          throw new Error("requête .first() sans bind non anticipée : " + s.slice(0, 70));
        },
      };
    },
  };
}

test("chronologieConcept() sans auteur ne calcule PAS de dossier — comportement inchangé", async () => {
  const rep = await chronologieConcept({ DB: stubDossierDB() }, { concept: "geburt" });
  assert.equal(rep.concept, "geburt");
  assert.equal(rep.auteur, null);
  assert.deepEqual(rep.etapes, [], "sans auteur, la requête etapes historique reste inchangée");
  assert.equal(typeof rep.reserve, "string");
  assert.ok(rep.reserve.length > 20);
  assert.equal(rep.dossier, null);
  assert.equal(rep.dossier_reserve, null);
});

test("quand `auteur` est donné, la requête etapes est SCOPÉE — pas seulement le dossier", async () => {
  // DÉFAUT TROUVÉ PAR REVUE ADVERSARIALE : fournir `auteur` désambiguïsait le dossier mais
  // laissait le graphique principal (etapes) continuer à mélanger plusieurs motifs distincts
  // sous un même nom. Ce test vérifie le TEXTE SQL réellement envoyé, pas seulement son résultat
  // canned — sans quoi une régression qui retirerait le JOIN ne serait pas détectée.
  let sqlEtapesVu = null;
  const db = {
    prepare(sql) {
      const s = sql.trim();
      if (s.includes("WITH concept_atomes")) sqlEtapesVu = s;
      const stubInterne = stubDossierDB().prepare(sql);
      return stubInterne;
    },
  };
  await chronologieConcept({ DB: db }, { concept: "geburt", auteur: "Otto Rank" });
  assert.ok(sqlEtapesVu, "la requête etapes doit avoir été exécutée");
  assert.match(sqlEtapesVu, /au2\.nom/,
              "sans le JOIN sur auteurs + filtre au2.nom, la collision entre lexiques revient");
});

test("un couple (concept, auteur) qui n'existe pas RÉELLEMENT est refusé — pas de fuite Breuer", async () => {
  // LE DÉFAUT BLOQUANT TROUVÉ PAR REVUE ADVERSARIALE, REJOUÉ ICI. Josef Breuer ne possède aucun
  // concept propre mais apparaît comme auteur dans `carte_actes` (lexique emprunté de Freud) :
  // avant correction, demander son dossier sur un concept qui n'est PAS le sien laissait
  // `dossierExterne` s'exécuter quand même et remonter les actes d'un AUTRE auteur portant ce
  // nom. Le garde-fou doit maintenant refuser la requête AVANT tout calcul.
  await assert.rejects(
    () => chronologieConcept({ DB: stubDossierDB({ possede: false }) },
      { concept: "angst", auteur: "Josef Breuer" }),
    /concept inconnu/);
});

test("le dossier ne retient que les actes qui touchent VRAIMENT ce concept", async () => {
  const rep = await chronologieConcept({ DB: stubDossierDB() },
    { concept: "geburt", auteur: "Otto Rank" });
  // ACTE_SANS_LE_CONCEPT est écarté ; ACTE_TOUCHANT et ACTE_REJETE portent tous deux « geburt ».
  assert.equal(rep.dossier.actes.length, 2,
              "l'acte Rank↔Abraham ne porte pas « geburt » dans ses concepts_communs");
  const confirme = rep.dossier.actes.find((a) => a.verdict === "confirme");
  assert.equal(confirme.autre_auteur, "Sigmund Freud");
  assert.equal(confirme.contenance, 0.62);
});

test("un acte REJETÉ touchant le concept apparaît quand même, avec son verdict intact", async () => {
  // Protège exactement le défaut que la revue a signalé : aucune assertion ne détectait
  // auparavant un filtre `verdict = 'confirme'` ajouté par erreur à la requête des actes.
  const rep = await chronologieConcept({ DB: stubDossierDB() },
    { concept: "geburt", auteur: "Otto Rank" });
  const rejete = rep.dossier.actes.find((a) => a.verdict === "rejete");
  assert.ok(rejete, "l'acte rejeté doit être présent, pas filtré silencieusement");
  assert.equal(rejete.autre_auteur, "Wilhelm Stekel");
});

test("une mention NON LUE (verdict NULL) apparaît aussi, jamais confirmée par défaut", async () => {
  const rep = await chronologieConcept({ DB: stubDossierDB() },
    { concept: "geburt", auteur: "Otto Rank" });
  const nonLue = rep.dossier.mentions.find((m) => m.auteur_nomme === "Karl Abraham");
  assert.ok(nonLue, "la mention non lue doit être présente");
  assert.equal(nonLue.verdict, null);
});

test("la densité comparée EXCLUT tout motif défini par un AUTRE lexique — pas de collision", async () => {
  // Rejoue le cas réel « angst » (quatre motifs distincts sous un même nom) : si le filtre
  // `AND u.lexique = ?2` disparaissait du SQL, USAGE_MOTIF_CONCURRENT (999,9 ‰, un lexique
  // différent) apparaîtrait ici et ce test le détecterait.
  const rep = await chronologieConcept({ DB: stubDossierDB() },
    { concept: "geburt", auteur: "Otto Rank" });
  const noms = rep.dossier.densite_comparee.map((d) => d.auteur);
  assert.ok(!noms.includes("Otto Rank"), "on compare AUX autres, jamais à soi");
  assert.ok(!noms.includes("Karl Abraham"),
           "USAGE_MOTIF_CONCURRENT vient d'un AUTRE lexique — ne doit jamais apparaître ici");
  assert.deepEqual(noms, ["Sigmund Freud"]);
});

test("les mentions du dossier voyagent avec leur verdict et leur motif", async () => {
  const rep = await chronologieConcept({ DB: stubDossierDB() },
    { concept: "geburt", auteur: "Otto Rank" });
  const m = rep.dossier.mentions.find((x) => x.verdict === "confirme");
  assert.equal(m.auteur_nomme, "Sigmund Freud");
  assert.ok(m.motif_lecture.includes("Traumdeutung"));
});

test("un dossier vide sur les trois signaux porte un silence EXPLICITE, jamais un vide muet", async () => {
  const rep = await chronologieConcept(
    { DB: stubDossierDB({ actes: [ACTE_SANS_LE_CONCEPT], usages: [], mentions: [],
                          couples: [{ silence: "aucun_acte" }] }) },
    { concept: "geburt", auteur: "Otto Rank" });
  assert.equal(rep.dossier.actes.length, 0);
  assert.ok(rep.dossier.silence, "le silence doit être une phrase, pas null, quand tout est vide");
  assert.match(rep.dossier.silence, /aucune connexion externe vérifiée/);
});

test("un auteur isolé dans sa langue reçoit un silence qui le dit, pas la phrase générique seule", async () => {
  // Le Bon, seul francophone du corpus : `carte_couples.silence` vaut « langues » pour TOUS ses
  // couples. Le dossier doit le dire, réutilisant une information déjà calculée ailleurs plutôt
  // que de répéter la même phrase générique sur ses 46 concepts sans jamais expliquer pourquoi.
  const rep = await chronologieConcept(
    { DB: stubDossierDB({ actes: [], usages: [], mentions: [],
                          couples: [{ silence: "langues" }, { silence: "langues" }] }) },
    { concept: "credulite", auteur: "Gustave Le Bon" });
  assert.match(rep.dossier.silence, /isolé dans sa langue/);
});

test("la réserve du dossier interdit explicitement le score fusionné et l'inférence d'accord", async () => {
  const rep = await chronologieConcept({ DB: stubDossierDB() },
    { concept: "geburt", auteur: "Otto Rank" });
  assert.match(rep.dossier_reserve, /jamais/i);
  assert.match(rep.dossier_reserve, /accord/);
  assert.match(rep.dossier_reserve, /désaccord/);
  // Le dossier expose actes ET mentions rejetés ou non lus (même discipline que comparaison()) :
  // la réserve doit donc redire, ici aussi, que seul « confirme » autorise à citer le fait.
  assert.match(rep.dossier_reserve, /rejete/);
  assert.match(rep.dossier_reserve, /confirme/);
});
