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
import { carte, comparaison } from "./donnees.js";

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
