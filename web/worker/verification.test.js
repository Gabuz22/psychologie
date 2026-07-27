/* TESTS de la vérification déterministe — `node --test` depuis web/.
 *
 * Ce qui est protégé ici : une citation inventée par le modèle DOIT être détectée, et une
 * citation authentique NE DOIT PAS être signalée à tort. Les deux erreurs sont graves — la
 * première laisse passer une fausse citation de Freud, la seconde rend l'assistant inutilisable
 * en criant au loup. Chaque test correspond à un cas rencontré ou anticipé, jamais décoratif.
 */
import { test } from "node:test";
import assert from "node:assert/strict";
import {
  contexteVerification, verifierReponse, extraireCitations, segmentsVerifiables,
  semblerAllemand, semblerFrancais,
} from "./verification.js";

/* Résultat d'outil réaliste : la forme exacte que rend `donnees.rechercher`. */
const RESULTAT_RECHERCHE = {
  total: 2,
  citations: [
    {
      id: "traumdeutung:a25",
      texte: "Durch eigene Erfahrung wie durch die Arbeiten\nvon W. _Stekel_ und anderen habe "
           + "ich seither den Umfang und die Bedeutung der Symbolik im Traume zu würdigen "
           + "gelernt.",
      titre: "Die Traumdeutung", titre_fr: "L'interprétation des rêves",
      oeuvre: "Die Traumdeutung", annee_oeuvre: 1900,
      datation: "absent de l'édition de 1900 — ajouté entre 1900 et 1914",
    },
    {
      id: "jenseits:a0",
      texte: "In der psychoanalytischen Theorie nehmen wir unbedenklich an, daß der Ablauf der "
           + "seelischen Vorgänge automatisch durch das Lustprinzip reguliert wird.",
      titre: "Jenseits des Lustprinzips", oeuvre: "Jenseits des Lustprinzips",
      annee_oeuvre: 1920,
    },
  ],
};

const RESULTAT_CHRONOLOGIE = {
  concept: "todestrieb",
  etapes: [
    { oeuvre: "jenseits", titre: "Jenseits des Lustprinzips", annee_oeuvre: 1920,
      pour_mille: 35, pour_mille_origine: null },
    { oeuvre: "neue_folge", titre: "Neue Folge", annee_oeuvre: 1933,
      pour_mille: 1, pour_mille_origine: null },
  ],
};

const ctx = () => contexteVerification([RESULTAT_RECHERCHE, RESULTAT_CHRONOLOGIE]);

test("une citation authentique passe la vérification", () => {
  const r = verifierReponse(
    "Freud écrit : « habe ich seither den Umfang und die Bedeutung der Symbolik im Traume » "
    + "(Die Traumdeutung).", ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
  assert.equal(r.controles.citations_verifiees, 1);
});

test("les retours à la ligne du texte source ne cassent pas la vérification", () => {
  // L'atome contient « die Arbeiten\nvon W. » — le modèle, lui, cite sur une seule ligne.
  const r = verifierReponse(
    "Il note : « Durch eigene Erfahrung wie durch die Arbeiten von W. Stekel und anderen »",
    ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
});

test("les diacritiques et le ß ne cassent pas la vérification", () => {
  const r = verifierReponse(
    "« nehmen wir unbedenklich an, dass der Ablauf der seelischen Vorgange »",
    ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
});

test("UNE CITATION INVENTÉE EST DÉTECTÉE — le défaut le plus grave possible", () => {
  const r = verifierReponse(
    "Freud affirme : « Der Traum ist der königliche Weg zum Unbewußten und niemals anders »",
    ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, false);
  assert.equal(r.problemes[0].type, "citation_introuvable");
});

test("une citation à moitié inventée est détectée (segment fautif après ellipse)", () => {
  const r = verifierReponse(
    "« habe ich seither den Umfang … und das beweist die Unsterblichkeit der Seele »",
    ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, false);
  assert.equal(r.problemes[0].type, "citation_introuvable");
});

test("un titre français entre guillemets n'est pas pris pour une citation allemande", () => {
  const r = verifierReponse(
    "Dans « L'interprétation des rêves », Freud développe cette idée.",
    ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
  assert.equal(r.controles.citations_verifiees, 0);
  assert.equal(r.controles.citations_ignorees, 1);
});

test("un ‰ attesté passe, un ‰ inventé est détecté", () => {
  const bon = verifierReponse("La densité atteint 35 ‰ dans Jenseits.", ctx(),
                              { outilsAppeles: 1 });
  assert.equal(bon.ok, true, JSON.stringify(bon.problemes));

  const faux = verifierReponse("La densité atteint 42 ‰ dans Jenseits.", ctx(),
                               { outilsAppeles: 1 });
  assert.equal(faux.ok, false);
  assert.equal(faux.problemes[0].type, "chiffre_non_atteste");
});

test("un identifiant d'atome inexistant est détecté", () => {
  const bon = verifierReponse("Voir l'atome traumdeutung:a25.", ctx(), { outilsAppeles: 1 });
  assert.equal(bon.ok, true, JSON.stringify(bon.problemes));

  const faux = verifierReponse("Voir l'atome traumdeutung:a99999.", ctx(), { outilsAppeles: 1 });
  assert.equal(faux.ok, false);
  assert.equal(faux.problemes[0].type, "atome_inexistant");
});

test("une réponse longue SANS aucun appel d'outil est signalée", () => {
  const r = verifierReponse("Freud pensait que ".repeat(40), ctx(), { outilsAppeles: 0 });
  assert.equal(r.ok, false);
  assert.equal(r.problemes[0].type, "sans_source");
});

test("une réponse courte sans outil reste légitime (salutation, question sur le site)", () => {
  const r = verifierReponse("Bonjour ! Que souhaitez-vous savoir du corpus ?", ctx(),
                            { outilsAppeles: 0 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
});

test("« aucun problème » ne se confond pas avec « rien vérifié »", () => {
  const r = verifierReponse("Une phrase sans citation ni chiffre.", ctx(), { outilsAppeles: 1 });
  assert.equal(r.ok, true);
  assert.equal(r.controles.citations_verifiees, 0);
  assert.equal(r.controles.pour_mille_verifies, 0);
});

test("les guillemets droits sont reconnus comme les français", () => {
  assert.equal(extraireCitations('Il dit "der Ablauf der seelischen Vorgänge" ici.').length, 1);
  assert.equal(extraireCitations("Il dit « der Ablauf der seelischen Vorgänge » ici.").length, 1);
});

test("un fragment trop court n'est pas jugé — mieux vaut ne rien dire que dire faux", () => {
  assert.deepEqual(segmentsVerifiables("das Es"), []);
  assert.equal(segmentsVerifiables("der Ablauf der seelischen Vorgänge").length, 1);
});

test("la détection d'allemand distingue les deux langues", () => {
  assert.equal(semblerAllemand("der Traum ist eine Wunscherfüllung"), true);
  assert.equal(semblerAllemand("Der Witz und seine Beziehung zum Unbewußten"), true);
  assert.equal(semblerAllemand("L'interprétation des rêves"), false);
  assert.equal(semblerAllemand("la pulsion de mort chez Freud"), false);
});

/* ------------------------------------------------ citations FRANÇAISES (Le Bon, 1895) */

/* Résultat d'outil contenant un atome français réel de « Psychologie des foules ». */
const RESULTAT_LEBON = {
  total: 1,
  citations: [{
    id: "psychologie_des_foules:a16",
    texte: "L'ensemble de caractères communs que l'hérédité impose à tous les\nindividus "
         + "d'une race constitue l'âme de cette race.",
    titre: "Psychologie des foules", titre_fr: "Psychologie des foules",
    oeuvre: "Psychologie des foules", annee_oeuvre: 1895, langue: "fr",
  }],
};

const ctxFr = () => contexteVerification([RESULTAT_LEBON]);

test("une citation française authentique de Le Bon passe la vérification", () => {
  const r = verifierReponse(
    "Le Bon écrit : « L'ensemble de caractères communs que l'hérédité impose à tous les "
    + "individus d'une race constitue l'âme de cette race. »", ctxFr(), { outilsAppeles: 1 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
  assert.equal(r.controles.citations_verifiees, 1);
});

test("UNE CITATION FRANÇAISE INVENTÉE EST DÉTECTÉE — même exigence que pour l'allemand", () => {
  const r = verifierReponse(
    "Le Bon affirme : « Les foules sont toujours prêtes à massacrer quiconque ose leur "
    + "résister par la seule force de la raison »", ctxFr(), { outilsAppeles: 1 });
  assert.equal(r.ok, false);
  assert.equal(r.problemes[0].type, "citation_introuvable");
});

test("un passage français COURT entre guillemets reste ignoré (titre, glose) — prudence assumée", () => {
  // Moins de 8 mots : peut être un titre traduit ; on n'accuse pas sans preuve.
  const r = verifierReponse(
    "Dans « Psychologie des foules », puis dans « L'âme des races », Le Bon développe cette idée.",
    ctxFr(), { outilsAppeles: 1 });
  assert.equal(r.ok, true, JSON.stringify(r.problemes));
  assert.equal(r.controles.citations_verifiees, 0);
});

test("la détection de français reconnaît la prose citée", () => {
  assert.equal(semblerFrancais("les foules ne raisonnent pas et n'admettent que des idées"), true);
  assert.equal(semblerFrancais("der Ablauf der seelischen Vorgänge"), false);
});
