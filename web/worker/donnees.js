/* DONNÉES — les requêtes sur le corpus, indépendantes du protocole qui les sert.
 *
 * Ce module ne connaît ni HTTP ni MCP : il prend des paramètres (objet simple), interroge D1,
 * rend des données JS. `worker/index.js` (REST) et `worker/mcp.js` (MCP) l'appellent tous les
 * deux — UNE seule logique de requête, deux façons d'y accéder. Le Worker ne calcule rien :
 * il interroge ce que Python a produit (bin/exporter_d1.py).
 *
 * Deux règles héritées du projet, tenues jusque dans ces requêtes :
 *   1. TOUTE citation porte sa règle de datation — jamais une année nue.
 *   2. Le filtre par année s'appuie sur la FENÊTRE de chaque atome (annee_min/annee_max),
 *      jamais sur l'année de l'œuvre : un ajout de 1914 dans un livre de 1900 n'apparaît
 *      pas dans une recherche bornée à 1905.
 */

export class ErreurAPI extends Error {
  constructor(message, statut = 400) {
    super(message);
    this.statut = statut;
  }
}

/** Repliement identique à core/segmentation.py:replier — la recherche par mot-clé doit
 *  retrouver « Wunscherfüllung » qu'on tape « wunscherfullung » ou « WUNSCHERFÜLLUNG ». */
export function replier(s) {
  return (s || "")
    .replace(/ß/g, "ss")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

/** SELECT de rendu d'une citation — tout ce que corpus.citer() donne, plus la fenêtre. */
const CHAMPS_CITATION = `
  a.atome_id AS id, a.texte, a.chapitre, a.debut, a.fin, a.nb_mots, a.statut,
  a.couche, a.annee_min, a.annee_max, a.datation_regle AS datation,
  au.nom AS auteur, o.titre AS oeuvre, o.titre_fr AS oeuvre_fr, o.cle AS oeuvre_cle,
  o.edition AS edition_lue, o.annee_edition, o.annee_oeuvre`;

const DE_CITATION = `
  FROM atomes a
  JOIN auteurs au ON au.id = a.auteur_id
  JOIN oeuvres o  ON o.id = a.oeuvre_id`;

/** Construit WHERE + paramètres depuis un objet de filtres — chaque filtre est un ET,
 *  aucun requis. `p` est un objet simple ({concept, groupe, ...}), pas des URLSearchParams :
 *  REST comme MCP y convergent après avoir parsé leur propre format d'entrée. */
function construireFiltres(p) {
  const ou = [], params = [];
  if (p.concept) {
    ou.push(`a.id IN (SELECT ac.atome_id FROM atome_concepts ac
             JOIN concepts c ON c.id = ac.concept_id WHERE c.nom = ?)`);
    params.push(p.concept);
  }
  if (p.groupe) {
    ou.push(`a.id IN (SELECT ac.atome_id FROM atome_concepts ac
             JOIN concepts c ON c.id = ac.concept_id WHERE c.groupe = ?)`);
    params.push(p.groupe);
  }
  if (p.sous_concept) {
    ou.push(`a.id IN (SELECT sc.atome_id FROM atome_sous_concepts sc WHERE sc.sous = ?)`);
    params.push(p.sous_concept);
  }
  if (p.grappe) {
    ou.push(`a.id IN (SELECT ac.atome_id FROM atome_concepts ac
             JOIN grappe_concepts gc ON gc.concept_id = ac.concept_id
             JOIN grappes g ON g.id = gc.grappe_id WHERE g.rang = ?)`);
    params.push(Number(p.grappe));
  }
  if (p.auteur) { ou.push("au.nom = ?"); params.push(p.auteur); }
  if (p.oeuvre) { ou.push("o.cle = ?"); params.push(p.oeuvre); }
  if (p.statut) { ou.push("a.statut = ?"); params.push(p.statut); }
  if (p.couche) { ou.push("a.couche = ?"); params.push(p.couche); }
  if (p.fonction) {
    ou.push("a.id IN (SELECT f.atome_id FROM fonctions f WHERE f.fonction = ?)");
    params.push(p.fonction);
  }
  if (p.signal) {
    ou.push("a.id IN (SELECT s.atome_id FROM signaux s WHERE s.signal = ? AND s.verdict = 'confirme')");
    params.push(p.signal);
  }
  if (p.mot_cle) {
    // Repli identique des deux côtés + neutralisation des jokers LIKE de l'utilisateur.
    const aiguille = replier(p.mot_cle).slice(0, 120).replace(/([\\%_])/g, "\\$1");
    ou.push("a.texte_replie LIKE '%' || ? || '%' ESCAPE '\\'");
    params.push(aiguille);
  }
  // Fenêtre de datation : l'atome est retenu si SA fenêtre chevauche celle demandée.
  if (p.annee_min != null && p.annee_min !== "") {
    ou.push("a.annee_max >= ?"); params.push(Number(p.annee_min));
  }
  if (p.annee_max != null && p.annee_max !== "") {
    ou.push("a.annee_min <= ?"); params.push(Number(p.annee_max));
  }
  return { where: ou.length ? "WHERE " + ou.join(" AND ") : "", params };
}

export async function rechercher(env, p = {}) {
  const { where, params } = construireFiltres(p);
  const limite = Math.min(Math.max(Number(p.limite) || 20, 1), 100);
  const decalage = Math.max(Number(p.decalage) || 0, 0);

  const total = await env.DB.prepare(`SELECT COUNT(*) AS n ${DE_CITATION} ${where}`)
    .bind(...params).first("n");
  const { results } = await env.DB.prepare(
    `SELECT ${CHAMPS_CITATION} ${DE_CITATION} ${where}
     ORDER BY o.annee_oeuvre, o.cle, a.debut LIMIT ? OFFSET ?`)
    .bind(...params, limite, decalage).all();

  return { total, rendus: results.length, decalage, citations: results };
}

export async function obtenirAtome(env, { id } = {}) {
  const a = await env.DB.prepare(
    `SELECT a.id AS rowid_interne, ${CHAMPS_CITATION} ${DE_CITATION} WHERE a.atome_id = ?`)
    .bind(id || "").first();
  if (!a) throw new ErreurAPI("atome inconnu : " + id, 404);
  const [concepts, sous, fonctions, signaux] = await Promise.all([
    env.DB.prepare(`SELECT c.nom, c.groupe FROM atome_concepts ac
                    JOIN concepts c ON c.id = ac.concept_id WHERE ac.atome_id = ?`)
      .bind(a.rowid_interne).all(),
    env.DB.prepare(`SELECT sc.sous, c.nom AS concept FROM atome_sous_concepts sc
                    JOIN concepts c ON c.id = sc.concept_id WHERE sc.atome_id = ?`)
      .bind(a.rowid_interne).all(),
    env.DB.prepare("SELECT fonction FROM fonctions WHERE atome_id = ?")
      .bind(a.rowid_interne).all(),
    env.DB.prepare("SELECT signal, verdict, motif FROM signaux WHERE atome_id = ?")
      .bind(a.rowid_interne).all(),
  ]);
  delete a.rowid_interne;
  return {
    ...a,
    concepts: concepts.results,
    sous_concepts: sous.results,
    fonctions: fonctions.results.map((f) => f.fonction),
    signaux: signaux.results,
  };
}

export async function referentiel(env) {
  const [auteurs, oeuvres, concepts, grappes, meta] = await Promise.all([
    env.DB.prepare("SELECT nom, naissance, mort, courant FROM auteurs ORDER BY nom").all(),
    env.DB.prepare(`SELECT cle, titre, titre_fr, annee_oeuvre, annee_edition, edition,
                    datation_precise, collationnee FROM oeuvres ORDER BY annee_oeuvre`).all(),
    env.DB.prepare(`SELECT nom, groupe, n_atomes FROM concepts
                    WHERE n_atomes > 0 ORDER BY groupe, n_atomes DESC`).all(),
    env.DB.prepare("SELECT rang, nom, taille, atomes_concernes FROM grappes ORDER BY rang").all(),
    env.DB.prepare("SELECT cle, valeur FROM meta").all(),
  ]);
  const groupes = {};
  for (const c of concepts.results) (groupes[c.groupe] ??= []).push(c);
  return {
    auteurs: auteurs.results,
    oeuvres: oeuvres.results,
    groupes,
    grappes: grappes.results,
    statuts: ["affirme", "modalise", "interrogatif", "rapporte"],
    meta: Object.fromEntries(meta.results.map((m) => [m.cle, m.valeur])),
  };
}

export async function grappesListe(env) {
  const { results } = await env.DB.prepare(
    `SELECT g.rang, g.nom, g.taille, g.atomes_concernes, c.nom AS concept, c.n_atomes
     FROM grappes g JOIN grappe_concepts gc ON gc.grappe_id = g.id
     JOIN concepts c ON c.id = gc.concept_id
     ORDER BY g.rang, c.n_atomes DESC`).all();
  const parRang = {};
  for (const l of results) {
    parRang[l.rang] ??= { rang: l.rang, nom: l.nom, taille: l.taille,
                          atomes_concernes: l.atomes_concernes, concepts: [] };
    parRang[l.rang].concepts.push({ nom: l.concept, n_atomes: l.n_atomes });
  }
  return { grappes: Object.values(parRang) };
}

/** Détail d'UNE grappe : éditorial, concepts, citation vedette (choisie par l'agent Python,
 *  jamais ici) et densité par œuvre — restreinte à Sigmund Freud, comme AgentCourants.executer()
 *  restreint son propre calcul (l'appendice d'Otto Rank fausserait « ce que Freud pense »). */
export async function grappeDetail(env, { rang } = {}) {
  const r = Number(rang);
  if (!r) throw new ErreurAPI("paramètre 'rang' requis", 400);

  const g = await env.DB.prepare(
    `SELECT rang, nom, description, reserve, taille, atomes_concernes, citation_atome_id
     FROM grappes WHERE rang = ?`).bind(r).first();
  if (!g) throw new ErreurAPI("grappe inconnue : " + r, 404);

  const [concepts, densite, citation] = await Promise.all([
    env.DB.prepare(
      `SELECT c.nom, c.groupe, c.n_atomes FROM grappe_concepts gc
       JOIN concepts c ON c.id = gc.concept_id
       JOIN grappes gr ON gr.id = gc.grappe_id
       WHERE gr.rang = ? ORDER BY c.n_atomes DESC`).bind(r).all(),
    env.DB.prepare(`
      WITH grappe_atomes AS (
        SELECT DISTINCT ac.atome_id FROM atome_concepts ac
        JOIN grappe_concepts gc ON gc.concept_id = ac.concept_id
        JOIN grappes gr ON gr.id = gc.grappe_id WHERE gr.rang = ?
      )
      SELECT o.cle, o.titre, o.titre_fr, o.annee_oeuvre, o.collationnee,
        COUNT(*) AS total,
        SUM(CASE WHEN ga.atome_id IS NOT NULL THEN 1 ELSE 0 END) AS porteurs,
        SUM(CASE WHEN a.couche = 'origine' THEN 1 ELSE 0 END) AS total_origine,
        SUM(CASE WHEN a.couche = 'origine' AND ga.atome_id IS NOT NULL THEN 1 ELSE 0 END)
          AS porteurs_origine
      FROM atomes a
      JOIN oeuvres o ON o.id = a.oeuvre_id
      JOIN auteurs au ON au.id = a.auteur_id
      LEFT JOIN grappe_atomes ga ON ga.atome_id = a.id
      WHERE au.nom = 'Sigmund Freud'
      GROUP BY o.id ORDER BY o.annee_oeuvre`).bind(r).all(),
    g.citation_atome_id
      ? env.DB.prepare(`SELECT ${CHAMPS_CITATION} ${DE_CITATION} WHERE a.atome_id = ?`)
          .bind(g.citation_atome_id).first()
      : null,
  ]);

  const parOeuvre = densite.results.map((l) => ({
    oeuvre: l.cle, titre: l.titre, titre_fr: l.titre_fr, annee_oeuvre: l.annee_oeuvre,
    total: l.total, porteurs: l.porteurs,
    pour_mille: l.total ? Math.round((1000 * l.porteurs) / l.total) : 0,
    collationnee: !!l.collationnee,
    pour_mille_origine: l.collationnee && l.total_origine
      ? Math.round((1000 * l.porteurs_origine) / l.total_origine) : null,
  }));

  return { ...g, concepts: concepts.results, citation, densite_par_oeuvre: parOeuvre };
}

/** Chronologie d'UN concept — miroir exact d'AgentChronologie (core/agents.py) : densité sur
 *  TOUS les atomes de l'œuvre (Otto Rank compris, comme l'agent), plus la densité « d'origine »
 *  quand l'œuvre a été collationnée. Jamais un pour-cent sans le rappel de sa réserve d'édition. */
export async function chronologieConcept(env, { concept } = {}) {
  const existe = await env.DB.prepare("SELECT 1 FROM concepts WHERE nom = ?")
    .bind(concept || "").first();
  if (!existe) throw new ErreurAPI("concept inconnu : " + concept, 404);

  const { results } = await env.DB.prepare(`
    WITH concept_atomes AS (
      SELECT ac.atome_id FROM atome_concepts ac
      JOIN concepts c ON c.id = ac.concept_id WHERE c.nom = ?
    )
    SELECT o.cle, o.titre, o.titre_fr, o.annee_oeuvre, o.annee_edition, o.edition,
      o.datation_regle, o.collationnee,
      COUNT(*) AS total,
      SUM(CASE WHEN ca.atome_id IS NOT NULL THEN 1 ELSE 0 END) AS porteurs,
      SUM(CASE WHEN a.couche = 'origine' THEN 1 ELSE 0 END) AS total_origine,
      SUM(CASE WHEN a.couche = 'origine' AND ca.atome_id IS NOT NULL THEN 1 ELSE 0 END)
        AS porteurs_origine
    FROM atomes a
    JOIN oeuvres o ON o.id = a.oeuvre_id
    LEFT JOIN concept_atomes ca ON ca.atome_id = a.id
    GROUP BY o.id ORDER BY o.annee_oeuvre`).bind(concept).all();

  const etapes = results.map((l) => ({
    oeuvre: l.cle, titre: l.titre, titre_fr: l.titre_fr, annee_oeuvre: l.annee_oeuvre,
    annee_edition: l.annee_edition, edition_lue: l.edition, datation_regle: l.datation_regle,
    total: l.total, porteurs: l.porteurs,
    pour_mille: l.total ? Math.round((1000 * l.porteurs) / l.total) : 0,
    collationnee: !!l.collationnee,
    pour_mille_origine: l.collationnee && l.total_origine
      ? Math.round((1000 * l.porteurs_origine) / l.total_origine) : null,
  }));

  return {
    concept, etapes,
    reserve: "Pour les œuvres COLLATIONNÉES, « pour_mille_origine » ne compte que les "
      + "passages retrouvés dans la première édition. Pour les autres, l'œuvre est lue dans "
      + "une édition postérieure dont Freud n'a pas signalé les ajouts : une variation peut y "
      + "refléter un ajout tardif plutôt qu'un mouvement de la pensée.",
  };
}

/** « Ce que Freud dit de lui-même » — les signaux CONFIRMÉS (objection, révision, auto-citation)
 *  lus en contexte et jugés un par un (verification/signaux_verifies.json), jamais les simples
 *  candidats détectés par le lexique : un marqueur ne prouve rien, seule la lecture tranche.
 *  Le `motif` du jugement est rendu à chaque fois — l'opposabilité vient de lui, pas du verdict
 *  seul. */
export async function signaux(env, { type, limite, decalage } = {}) {
  const resume = await env.DB.prepare(
    `SELECT signal, COUNT(*) AS n FROM signaux WHERE verdict = 'confirme' GROUP BY signal`).all();

  const ou = ["s.verdict = 'confirme'"], params = [];
  if (type) { ou.push("s.signal = ?"); params.push(type); }
  const where = "WHERE " + ou.join(" AND ");
  const lim = Math.min(Math.max(Number(limite) || 20, 1), 100);
  const dec = Math.max(Number(decalage) || 0, 0);

  const total = await env.DB.prepare(`SELECT COUNT(*) AS n FROM signaux s ${where}`)
    .bind(...params).first("n");
  const { results } = await env.DB.prepare(`
    SELECT s.signal, s.motif, ${CHAMPS_CITATION}
    FROM signaux s
    JOIN atomes a ON a.id = s.atome_id
    JOIN auteurs au ON au.id = a.auteur_id
    JOIN oeuvres o ON o.id = a.oeuvre_id
    ${where}
    ORDER BY o.annee_oeuvre, a.debut
    LIMIT ? OFFSET ?`).bind(...params, lim, dec).all();

  return {
    total, rendus: results.length, decalage: dec,
    resume: Object.fromEntries(resume.results.map((r) => [r.signal, r.n])),
    signaux: results,
  };
}

/** Lecture séquentielle d'une œuvre — les atomes dans l'ordre du texte, pas filtrés par
 *  pertinence. Pour suivre un raisonnement plutôt que chercher un mot. */
export async function lireOeuvre(env, { oeuvre, page, taille } = {}) {
  const o = await env.DB.prepare(
    "SELECT cle, titre, titre_fr FROM oeuvres WHERE cle = ?").bind(oeuvre || "").first();
  if (!o) throw new ErreurAPI("œuvre inconnue : " + oeuvre, 404);

  const t = Math.min(Math.max(Number(taille) || 20, 1), 100);
  const pg = Math.max(Number(page) || 0, 0);

  const total = await env.DB.prepare(
    `SELECT COUNT(*) AS n ${DE_CITATION} WHERE o.cle = ?`).bind(oeuvre).first("n");
  const { results } = await env.DB.prepare(
    `SELECT ${CHAMPS_CITATION} ${DE_CITATION}
     WHERE o.cle = ? ORDER BY a.debut LIMIT ? OFFSET ?`)
    .bind(oeuvre, t, pg * t).all();

  return { oeuvre: o, page: pg, taille: t, total, pages: Math.max(1, Math.ceil(total / t)),
           atomes: results };
}
