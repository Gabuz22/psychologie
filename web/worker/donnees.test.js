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
import { comparaison } from "./donnees.js";

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
