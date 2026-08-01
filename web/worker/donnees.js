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
  o.langue AS langue, o.edition AS edition_lue, o.annee_edition, o.annee_oeuvre,
  o.qualite_source, a.ocr_suspect`;

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
    env.DB.prepare(`SELECT o.cle, o.titre, o.titre_fr, o.langue, au.nom AS auteur,
                    o.annee_oeuvre, o.annee_edition, o.edition, o.datation_precise,
                    o.collationnee, o.qualite_source, o.ocr_phrases_corrompues_pct
                    FROM oeuvres o JOIN auteurs au ON au.id = o.auteur_id
                    ORDER BY au.nom, o.annee_oeuvre`).all(),
    // Les concepts appartiennent à UN AUTEUR : deux auteurs peuvent employer le même mot pour
    // deux choses différentes, et l'interface doit permettre de les distinguer.
    env.DB.prepare(`SELECT c.nom, c.groupe, c.n_atomes, au.nom AS auteur
                    FROM concepts c JOIN auteurs au ON au.id = c.auteur_id
                    WHERE c.n_atomes > 0
                    ORDER BY au.nom, c.groupe, c.n_atomes DESC`).all(),
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
    SELECT o.cle, o.titre, o.titre_fr, o.langue, au.nom AS auteur,
      o.annee_oeuvre, o.annee_edition, o.edition,
      o.datation_regle, o.collationnee,
      COUNT(*) AS total,
      SUM(CASE WHEN ca.atome_id IS NOT NULL THEN 1 ELSE 0 END) AS porteurs,
      SUM(CASE WHEN a.couche = 'origine' THEN 1 ELSE 0 END) AS total_origine,
      SUM(CASE WHEN a.couche = 'origine' AND ca.atome_id IS NOT NULL THEN 1 ELSE 0 END)
        AS porteurs_origine
    FROM atomes a
    JOIN oeuvres o ON o.id = a.oeuvre_id
    JOIN auteurs au ON au.id = o.auteur_id
    LEFT JOIN concept_atomes ca ON ca.atome_id = a.id
    GROUP BY o.id ORDER BY o.annee_oeuvre`).bind(concept).all();

  const etapes = results.map((l) => ({
    oeuvre: l.cle, titre: l.titre, titre_fr: l.titre_fr, langue: l.langue, auteur: l.auteur,
    annee_oeuvre: l.annee_oeuvre,
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
    `SELECT o.cle, o.titre, o.titre_fr, o.langue, au.nom AS auteur
     FROM oeuvres o JOIN auteurs au ON au.id = o.auteur_id
     WHERE o.cle = ?`).bind(oeuvre || "").first();
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

/** ARBRE ATOMIQUE — la structure d'un auteur, à plusieurs niveaux de détail.
 *
 *  Auteur → œuvres → chapitres → concepts → atomes. Chaque niveau porte deux chiffres : combien
 *  d'atomes il contient, et combien de liens le rattachent à d'AUTRES auteurs.
 *
 *  L'agrégation des liens vers les niveaux grossiers est légitime parce qu'elle ne fait que
 *  COMPTER : un lien entre deux atomes est un lien entre leurs œuvres, entre leurs chapitres.
 *  Rien n'est inféré en montant. C'est la différence avec un rapprochement de concepts, qui
 *  demanderait, lui, de supposer une équivalence — raison pour laquelle il n'est pas ici.
 *
 *  LES ATOMES HORS CHAPITRE SONT MONTRÉS, PAS CACHÉS. 16 057 atomes (35 % du corpus) appartiennent
 *  à des œuvres dont le découpage en chapitres n'est pas repérable — préfaces, articles de revue,
 *  volumes sans intitulé de section. Les omettre ferait paraître ces œuvres plus petites qu'elles
 *  ne sont ; ils forment donc un nœud explicite « hors chapitre ».
 */
export async function arbre(env, { auteur, oeuvre } = {}) {
  const nom = auteur || "Sigmund Freud";
  const existe = await env.DB.prepare("SELECT id, nom, naissance, mort, courant FROM auteurs WHERE nom = ?")
    .bind(nom).first();
  if (!existe) throw new ErreurAPI("auteur inconnu : " + nom, 404);

  const oeuvres = await env.DB.prepare(
    `SELECT o.cle, o.titre, o.titre_fr, o.annee_oeuvre, o.annee_edition, o.langue,
            o.qualite_source, o.datation_precise,
            COUNT(a.id) AS atomes,
            SUM(CASE WHEN a.non_qualifie = 0 THEN 1 ELSE 0 END) AS qualifies,
            SUM(a.ocr_suspect) AS ocr_suspects
     FROM oeuvres o
     JOIN auteurs au ON au.id = o.auteur_id
     LEFT JOIN atomes a ON a.oeuvre_id = o.id
     WHERE au.nom = ?
     GROUP BY o.id ORDER BY o.annee_oeuvre`).bind(nom).all();

  // Liens inter-auteurs agrégés par ŒUVRE — les deux sens réunis, puisqu'un lien n'est pas
  // orienté par nature (son sens est une propriété séparée, souvent indécidable).
  const liensOeuvre = await env.DB.prepare(
    `SELECT o_mien.cle AS mienne, au_autre.nom AS autre_auteur, o_autre.titre AS autre_oeuvre,
            COUNT(*) AS n
     FROM liens_reprise l
     JOIN atomes xa ON xa.id = l.atome_a
     JOIN atomes xb ON xb.id = l.atome_b
     JOIN auteurs aa ON aa.id = l.auteur_a
     JOIN auteurs ab ON ab.id = l.auteur_b
     JOIN oeuvres o_mien  ON o_mien.id  = CASE WHEN aa.nom = ?1 THEN xa.oeuvre_id ELSE xb.oeuvre_id END
     JOIN oeuvres o_autre ON o_autre.id = CASE WHEN aa.nom = ?1 THEN xb.oeuvre_id ELSE xa.oeuvre_id END
     JOIN auteurs au_autre ON au_autre.id = CASE WHEN aa.nom = ?1 THEN l.auteur_b ELSE l.auteur_a END
     WHERE aa.nom = ?1 OR ab.nom = ?1
     GROUP BY 1, 2, 3 ORDER BY n DESC`).bind(nom).all();

  const parOeuvre = {};
  for (const l of liensOeuvre.results) {
    (parOeuvre[l.mienne] ??= []).push(l);
  }

  // Chapitres : chargés seulement pour l'œuvre demandée, pour ne pas envoyer tout l'arbre
  // d'un coup — le corpus compte 109 chapitres et 45 588 atomes.
  let chapitres = null;
  if (oeuvre) {
    const r = await env.DB.prepare(
      `SELECT COALESCE(a.chapitre, '— hors chapitre —') AS chapitre,
              COUNT(*) AS atomes,
              SUM(CASE WHEN a.non_qualifie = 0 THEN 1 ELSE 0 END) AS qualifies,
              MIN(a.debut) AS ordre
       FROM atomes a JOIN oeuvres o ON o.id = a.oeuvre_id
       WHERE o.cle = ?
       GROUP BY 1 ORDER BY ordre`).bind(oeuvre).all();
    chapitres = r.results;
  }

  // Concepts dominants de l'auteur — la matière de ses atomes, dans SON lexique.
  const concepts = await env.DB.prepare(
    `SELECT c.nom, c.groupe, c.n_atomes
     FROM concepts c JOIN auteurs au ON au.id = c.auteur_id
     WHERE au.nom = ? AND c.n_atomes > 0
     ORDER BY c.n_atomes DESC`).bind(nom).all();

  const groupes = {};
  for (const c of concepts.results) (groupes[c.groupe] ??= []).push(c);

  return {
    auteur: existe,
    oeuvres: oeuvres.results.map((o) => ({ ...o, liens: parOeuvre[o.cle] || [] })),
    chapitres,
    oeuvre_ouverte: oeuvre || null,
    groupes,
    total_atomes: oeuvres.results.reduce((s, o) => s + o.atomes, 0),
    note:
      "Les liens comptés à chaque niveau sont des liens d'ATOME à atome, simplement additionnés "
      + "en remontant : rien n'est inféré. Un chapitre « — hors chapitre — » réunit les atomes "
      + "des œuvres dont le découpage en sections n'est pas repérable (préfaces, articles de "
      + "revue) — ils sont montrés plutôt que retirés, sans quoi l'œuvre paraîtrait plus petite "
      + "qu'elle n'est.",
  };
}

/** COMPARAISON INTER-AUTEURS — ce qu'un auteur reprend d'un autre, et où il le lit.
 *
 *  Cette vue relie des graphes construits SÉPARÉMENT (chaque auteur a ses propres concepts) et
 *  ne les fusionne jamais : un lien va d'un ATOME à un ATOME, et se déroule toujours jusqu'aux
 *  deux passages entiers, affichés côte à côte. C'est la contrainte fondatrice de la couche —
 *  un lien qu'on ne peut pas lire n'existe pas.
 *
 *  Aucun champ ne nomme la NATURE du rapport. Le corpus a mesuré ce piège : un signal construit
 *  pour repérer les écarts d'un disciple avec Freud n'a rien confirmé sur cinq candidats — les
 *  cinq étaient des renvois d'accord. La couche établit qu'un TEXTE est partagé ; l'interprétation
 *  revient au lecteur, devant les deux passages.
 */
export async function comparaison(env, { auteur, autre, limite } = {}) {
  const lim = Math.min(Math.max(Number(limite) || 30, 1), 100);

  const matrice = await env.DB.prepare(
    `SELECT a.nom AS auteur_a, b.nom AS auteur_b,
            COUNT(*) AS paires,
            COUNT(DISTINCT l.evenement) AS evenements,
            SUM(CASE WHEN l.force = 'manifeste' THEN 1 ELSE 0 END) AS manifestes,
            SUM(CASE WHEN l.sens IS NOT NULL THEN 1 ELSE 0 END) AS orientes,
            SUM(l.source_tierce) AS source_tierce
     FROM liens_reprise l
     JOIN auteurs a ON a.id = l.auteur_a
     JOIN auteurs b ON b.id = l.auteur_b
     GROUP BY 1, 2 ORDER BY paires DESC`).all();

  const filtres = [], params = [];
  if (auteur) { filtres.push("(a.nom = ? OR b.nom = ?)"); params.push(auteur, auteur); }
  if (autre) { filtres.push("(a.nom = ? OR b.nom = ?)"); params.push(autre, autre); }
  const ou = filtres.length ? "WHERE " + filtres.join(" AND ") : "";

  const liens = await env.DB.prepare(
    `SELECT l.contenance, l.force, l.sens, l.source_tierce, l.a_verifier, l.partages,
            l.evenement, l.verdict, l.sens_lu, l.reclasse_vers, l.motif_lecture,
            a.nom AS auteur_a, b.nom AS auteur_b,
            xa.atome_id AS id_a, xa.texte AS texte_a, oa.titre AS oeuvre_a,
            oa.annee_oeuvre AS annee_a, oa.qualite_source AS source_a, xa.ocr_suspect AS suspect_a,
            xb.atome_id AS id_b, xb.texte AS texte_b, ob.titre AS oeuvre_b,
            ob.annee_oeuvre AS annee_b, ob.qualite_source AS source_b, xb.ocr_suspect AS suspect_b
     FROM liens_reprise l
     JOIN auteurs a ON a.id = l.auteur_a
     JOIN auteurs b ON b.id = l.auteur_b
     JOIN atomes xa ON xa.id = l.atome_a
     JOIN atomes xb ON xb.id = l.atome_b
     JOIN oeuvres oa ON oa.id = xa.oeuvre_id
     JOIN oeuvres ob ON ob.id = xb.oeuvre_id
     ${ou}
     ORDER BY l.contenance DESC, l.evenement LIMIT ?`).bind(...params, lim).all();

  const lectures = await env.DB.prepare(
    `SELECT a.nom AS auteur, b.nom AS auteur_lu, o.titre AS oeuvre, o.annee_oeuvre,
            l.chapitre, l.portee_atomes, l.homographe
     FROM lectures_declarees l
     JOIN auteurs a ON a.id = l.auteur_id
     JOIN auteurs b ON b.id = l.auteur_lu_id
     JOIN oeuvres o ON o.id = l.oeuvre_id
     ORDER BY l.portee_atomes DESC`).all();

  const noms = await env.DB.prepare(
    `SELECT a.nom AS auteur, b.nom AS auteur_nomme, n.atomes, n.homographe
     FROM nominations n
     JOIN auteurs a ON a.id = n.auteur_id
     JOIN auteurs b ON b.id = n.auteur_nomme_id
     ORDER BY n.atomes DESC`).all();

  return {
    matrice: matrice.results,
    liens: liens.results,
    lectures_declarees: lectures.results,
    nominations: noms.results,
    reserve:
      "Un lien établit qu'un TEXTE est partagé, jamais qu'une THÈSE l'est. `sens` est ce que le "
      + "CALCUL établit à partir des seules fenêtres de datation — INDÉCIDABLE (NULL) si elles se "
      + "chevauchent, ce qui est une information sur ce que le corpus permet, pas une absence. "
      + "Quand les deux passages nomment une source tierce (Sophocle, Shakespeare), aucun sens "
      + "n'est donné : les deux auteurs peuvent tenir leur formulation d'elle plutôt que l'un de "
      + "l'autre. `verdict`/`sens_lu`/`reclasse_vers`/`motif_lecture` viennent d'une LECTURE "
      + "humaine en contexte (354 événements du corpus instruits ainsi) et PRÉVALENT sur `sens` "
      + "et `a_verifier` quand ils sont renseignés — `verdict` vaut « confirme » (le lien tient), "
      + "« rejete » (faux positif : titre, apparat, tête de page — ne pas le publier comme un "
      + "emprunt), ou « reclasse » (les deux auteurs citent le même TIERS nommé dans "
      + "`reclasse_vers`, aucun ne lit l'autre). `motif_lecture` cite le texte qui fonde le "
      + "jugement — à rapporter avec lui, jamais le verdict seul. `verdict` NULL veut dire non "
      + "encore lu : `sens`/`a_verifier` restent alors la seule information disponible. Enfin, "
      + "une PAIRE est deux phrases ; un ÉVÉNEMENT est une citation continue — c'est lui qui dit "
      + "combien de fois un auteur en cite un autre, et un même verdict de lecture couvre toutes "
      + "les paires de l'événement.",
    ne_pas_conclure:
      "Nommer n'est ni suivre, ni approuver, ni contredire — et reprendre une formulation n'est "
      + "pas partager une thèse. Aucun chiffre de cette page ne mesure un accord ni un désaccord.",
  };
}


/** USAGE D'UN MOT — le même motif appliqué à tous les corpus de sa langue.
 *
 * Sans `sous`, rend le palmarès des mots les plus CONTRASTÉS : ceux dont la densité varie le
 * plus d'un auteur à l'autre. Le contraste est un écart de densité, pas un désaccord — un mot
 * peut manquer chez un auteur parce qu'il ne traite pas le sujet, parce qu'il le nomme
 * autrement, ou parce qu'il le combat sans le nommer.
 */
export async function usages(env, { sous, limite } = {}) {
  const lim = Math.min(Math.max(Number(limite) || 40, 1), 200);

  if (sous) {
    const lignes = await env.DB.prepare(
      `SELECT u.sous_concept, u.groupe, u.libelle, u.langue, u.motif, u.atomes, u.porteurs,
              u.pour_mille, a.nom AS auteur, x.nom AS lexique
       FROM usages u
       JOIN auteurs a ON a.id = u.auteur_id
       JOIN auteurs x ON x.id = u.lexique
       WHERE u.sous_concept = ? ORDER BY u.motif, u.pour_mille DESC`).bind(sous).all();
    return { sous_concept: sous, lignes: lignes.results, reserve: RESERVE_USAGE };
  }

  // Le contraste se calcule par MOTIF et non par sous-concept : deux lexiques peuvent définir le
  // même mot avec des motifs légèrement différents, et mêler leurs densités additionnerait des
  // mesures qui ne portent pas exactement sur la même chose.
  const contrastes = await env.DB.prepare(
    `SELECT u.sous_concept, u.groupe, u.libelle, u.motif, u.langue, x.nom AS lexique,
            COUNT(*) AS auteurs_mesures,
            MAX(u.pour_mille) AS maximum, MIN(u.pour_mille) AS minimum
     FROM usages u JOIN auteurs x ON x.id = u.lexique
     GROUP BY u.motif HAVING auteurs_mesures > 1
     ORDER BY (maximum - minimum) DESC LIMIT ?`).bind(lim).all();

  const motifs = contrastes.results.map((c) => c.motif);
  const detail = motifs.length ? await env.DB.prepare(
    `SELECT u.motif, u.pour_mille, u.porteurs, u.atomes, a.nom AS auteur
     FROM usages u JOIN auteurs a ON a.id = u.auteur_id
     WHERE u.motif IN (${motifs.map(() => "?").join(",")})
     ORDER BY u.pour_mille DESC`).bind(...motifs).all() : { results: [] };

  const parMotif = new Map();
  for (const d of detail.results) {
    if (!parMotif.has(d.motif)) parMotif.set(d.motif, []);
    parMotif.get(d.motif).push(d);
  }
  return {
    mots: contrastes.results.map((c) => ({ ...c, auteurs: parMotif.get(c.motif) || [] })),
    reserve: RESERVE_USAGE,
  };
}

const RESERVE_USAGE =
  "Cette page compare un USAGE DE MOT, jamais une pensée. Le même motif est appliqué à tous les "
  + "corpus de sa langue et on compte les phrases qui le portent : la mesure ne dépend d'aucun "
  + "lexique, seulement du texte. Un écart de densité ne dit ni accord ni désaccord — un auteur "
  + "peut soutenir une thèse sans jamais employer le terme qui la nomme, et employer ce terme "
  + "sans cesse pour la combattre. La colonne « lexique » dit qui a défini le motif : la ligne "
  + "de cet auteur est haute par construction, ce sont les AUTRES lignes qui informent.";


/** CARTE DES ACTES DE CITATION — les endroits où un texte passe d'une œuvre à une autre.
 *
 * L'unité est l'ACTE (des phrases contiguës des deux côtés = un seul acte), jamais le couple de
 * concepts : agréger les concepts de part et d'autre donnerait 1 366 « arêtes » là où il y a 107
 * actes réels. Les concepts sont rendus comme CONTEXTE, et seuls ceux que les deux passages
 * portent ensemble sont présentés comme informatifs.
 *
 * Les couples SANS acte sont rendus eux aussi, avec la raison de leur silence — un silence de
 * méthode (langues différentes, détection impossible) n'est pas un silence de corpus.
 */
export async function carte(env, { auteur, autre, limite } = {}) {
  const lim = Math.min(Math.max(Number(limite) || 40, 1), 200);

  const couples = await env.DB.prepare(
    `SELECT a.nom AS auteur_a, b.nom AS auteur_b, c.evenements, c.atomes, c.manifestes,
            c.orientes, c.lus, c.confirmes, c.reclasses, c.rejetes, c.source_tierce,
            c.silence, c.langue_a, c.langue_b
     FROM carte_couples c
     JOIN auteurs a ON a.id = c.auteur_a
     JOIN auteurs b ON b.id = c.auteur_b
     ORDER BY c.evenements DESC, a.nom, b.nom`).all();

  const filtres = [], params = [];
  if (auteur) { filtres.push("(a.nom = ? OR b.nom = ?)"); params.push(auteur, auteur); }
  if (autre) { filtres.push("(a.nom = ? OR b.nom = ?)"); params.push(autre, autre); }
  const ou = filtres.length ? "WHERE " + filtres.join(" AND ") : "";

  const actes = await env.DB.prepare(
    `SELECT k.poids, k.contenance_max, k.force, k.sens, k.sens_lu, k.verdict, k.reclasse_vers,
            k.source_tierce, k.partage_replie, k.citation_a, k.citation_b,
            k.concepts_communs, k.concepts_a_seul, k.concepts_b_seul,
            k.id_debut_a, k.id_fin_a, k.id_debut_b, k.id_fin_b,
            a.nom AS auteur_a, b.nom AS auteur_b,
            oa.titre AS oeuvre_a, oa.annee_oeuvre AS annee_a, oa.qualite_source AS source_a,
            ob.titre AS oeuvre_b, ob.annee_oeuvre AS annee_b, ob.qualite_source AS source_b
     FROM carte_actes k
     JOIN auteurs a ON a.id = k.auteur_a
     JOIN auteurs b ON b.id = k.auteur_b
     JOIN oeuvres oa ON oa.id = k.oeuvre_a
     JOIN oeuvres ob ON ob.id = k.oeuvre_b
     ${ou}
     ORDER BY k.poids DESC, k.contenance_max DESC LIMIT ?`).bind(...params, lim).all();

  // LES MENTIONS — seconde couche, jamais fusionnée avec les actes. Un acte est un TEXTE
  // partagé ; une mention est un NOM écrit. Les additionner referait l'erreur que cette carte
  // a été bâtie pour éviter. Mais les taire ferait mentir la carte par omission : Ferenczi
  // nomme Freud dans 960 phrases et ne partage un texte avec lui que dans 9.
  const mentions = await env.DB.prepare(
    `SELECT a.nom AS auteur, b.nom AS auteur_nomme, COUNT(*) AS n,
            SUM(CASE WHEN m.homographe IS NOT NULL THEN 1 ELSE 0 END) AS homographes
     FROM mentions m
     JOIN auteurs a ON a.id = m.auteur_id
     JOIN auteurs b ON b.id = m.auteur_nomme_id
     GROUP BY 1, 2 ORDER BY n DESC`).all();

  // Les PASSAGES, quand un couple est demandé : un compte qu'on ne peut pas aller lire ne vaut
  // rien. Sans filtre on ne les charge pas — 2 216 passages sur une page d'accueil noieraient
  // les actes, qui sont le sujet de la page.
  const passages = (auteur || autre) ? await env.DB.prepare(
    `SELECT x.atome_id, x.texte, o.titre AS oeuvre, o.annee_oeuvre,
            a.nom AS auteur, b.nom AS auteur_nomme, m.homographe
     FROM mentions m
     JOIN atomes x ON x.id = m.atome_id
     JOIN oeuvres o ON o.id = x.oeuvre_id
     JOIN auteurs a ON a.id = m.auteur_id
     JOIN auteurs b ON b.id = m.auteur_nomme_id
     ${ou}
     ORDER BY o.annee_oeuvre, x.atome_id LIMIT ?`).bind(...params, lim).all()
    : { results: [] };

  // CE QUE LA CARTE NE VOIT PAS — servi avec elle, jamais relégué en note de bas de page.
  // `atomes` compte des atomes DISTINCTS, et `part_touchee` a sa propre colonne : elle était
  // rangée dans `part_trop_courts` et relue sous alias, si bien que le détournement ne se lisait
  // nulle part. Le chiffre lui-même était faux de +14,5 % (des côtés d'acte comptés pour des
  // atomes) — voir `carte.couverture`.
  const totaux = await env.DB.prepare(
    `SELECT atomes AS atomes_touches, part_touchee
     FROM carte_couverture WHERE cle IS NULL`).first();
  const muettes = await env.DB.prepare(
    `SELECT c.cle, c.atomes, c.part_trop_courts, o.titre, a.nom AS auteur
     FROM carte_couverture c
     JOIN oeuvres o ON o.id = c.oeuvre_id
     JOIN auteurs a ON a.id = o.auteur_id
     WHERE c.muette = 1 ORDER BY c.atomes DESC`).all();

  return {
    couples: couples.results,
    actes: actes.results,
    mentions: mentions.results,
    mentions_passages: passages.results,
    couverture: { ...(totaux || {}), muettes: muettes.results },
    reserve:
      "Cette carte montre des ACTES DE CITATION — des endroits où un texte passe d'une œuvre à "
      + "une autre, établis par le partage de suites de six mots et vérifiés par lecture. Elle ne "
      + "relie pas des CONCEPTS et ne pondère aucune proximité d'idées : un graphe de concepts a "
      + "été tenté, mesuré, puis écarté. Le poids d'un acte est le nombre de phrases qu'il "
      + "couvre, jamais un produit de concepts.",
    mentions_reserve:
      "Une MENTION est un nom écrit, pas un texte partagé — les deux couches ne sont jamais "
      + "additionnées. Nommer n'est d'ailleurs ni suivre, ni approuver, ni contredire : le corpus "
      + "a éprouvé ce piège, un marqueur construit pour repérer les écarts d'un disciple avec "
      + "Freud n'a rien confirmé sur cinq candidats, les cinq passages étant des renvois "
      + "d'accord. Le passage est donné en entier pour qu'on aille lire. Attention enfin aux "
      + "homographes : « Abraham » désigne aussi le patriarche biblique, que Rank et Freud citent "
      + "abondamment dans leurs travaux sur le mythe — 104 mentions sur 2 216 sont dans ce cas.",
    ne_pas_conclure:
      "Ce que la carte ne montre pas ne veut PAS dire que rien n'a eu lieu. Elle touche moins "
      + "d'un demi pour cent du corpus, plus de la moitié des œuvres n'y apparaissent jamais, et "
      + "un tiers des phrases sont trop courtes pour être comparables. Entre deux auteurs de "
      + "langues différentes elle est aveugle par construction — les corpus français et allemand "
      + "du projet partagent UN seul groupe de six mots, alors même que Freud consacre à Le Bon "
      + "un chapitre entier. Chaque couple sans acte porte donc la raison de son silence.",
  };
}
