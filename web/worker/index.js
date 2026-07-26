/* API du corpus psychanalytique — Cloudflare Worker + D1, LECTURE SEULE.
 *
 * Le Worker ne calcule rien : il interroge ce que Python a produit (bin/exporter_d1.py).
 * Chaque route est le miroir d'un outil existant du dépôt :
 *   /api/recherche   ↔  bin/rechercher.py   (filtres en ET logique, citations complètes)
 *   /api/grappes     ↔  bin/analyser.py --agent courants
 *   /api/referentiel ↔  les registres core/sources.py et core/lexique.py
 *
 * Deux règles héritées du projet, tenues jusque dans l'API :
 *   1. TOUTE citation porte sa règle de datation — jamais une année nue.
 *   2. Le filtre par année s'appuie sur la FENÊTRE de chaque atome (annee_min/annee_max),
 *      jamais sur l'année de l'œuvre : un ajout de 1914 dans un livre de 1900 n'apparaît
 *      pas dans une recherche bornée à 1905.
 */

/** Repliement identique à core/segmentation.py:replier — la recherche par mot-clé doit
 *  retrouver « Wunscherfüllung » qu'on tape « wunscherfullung » ou « WUNSCHERFÜLLUNG ». */
function replier(s) {
  return (s || "")
    .replace(/ß/g, "ss")
    .normalize("NFD")
    .replace(/[̀-ͯ]/g, "")
    .toLowerCase()
    .replace(/\s+/g, " ")
    .trim();
}

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "public, max-age=300",
};

function json(donnees, statut = 200, cache = true) {
  const headers = { ...JSON_HEADERS };
  if (!cache) headers["cache-control"] = "no-store";
  return new Response(JSON.stringify(donnees), { status: statut, headers });
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

/** Construit WHERE + paramètres depuis la requête — chaque filtre est un ET, aucun requis. */
function construireFiltres(p) {
  const ou = [], params = [];
  if (p.get("concept")) {
    ou.push(`a.id IN (SELECT ac.atome_id FROM atome_concepts ac
             JOIN concepts c ON c.id = ac.concept_id WHERE c.nom = ?)`);
    params.push(p.get("concept"));
  }
  if (p.get("groupe")) {
    ou.push(`a.id IN (SELECT ac.atome_id FROM atome_concepts ac
             JOIN concepts c ON c.id = ac.concept_id WHERE c.groupe = ?)`);
    params.push(p.get("groupe"));
  }
  if (p.get("sous_concept")) {
    ou.push(`a.id IN (SELECT sc.atome_id FROM atome_sous_concepts sc WHERE sc.sous = ?)`);
    params.push(p.get("sous_concept"));
  }
  if (p.get("grappe")) {
    ou.push(`a.id IN (SELECT ac.atome_id FROM atome_concepts ac
             JOIN grappe_concepts gc ON gc.concept_id = ac.concept_id
             JOIN grappes g ON g.id = gc.grappe_id WHERE g.rang = ?)`);
    params.push(Number(p.get("grappe")));
  }
  if (p.get("auteur")) { ou.push("au.nom = ?"); params.push(p.get("auteur")); }
  if (p.get("oeuvre")) { ou.push("o.cle = ?"); params.push(p.get("oeuvre")); }
  if (p.get("statut")) { ou.push("a.statut = ?"); params.push(p.get("statut")); }
  if (p.get("couche")) { ou.push("a.couche = ?"); params.push(p.get("couche")); }
  if (p.get("fonction")) {
    ou.push("a.id IN (SELECT f.atome_id FROM fonctions f WHERE f.fonction = ?)");
    params.push(p.get("fonction"));
  }
  if (p.get("signal")) {
    ou.push("a.id IN (SELECT s.atome_id FROM signaux s WHERE s.signal = ? AND s.verdict = 'confirme')");
    params.push(p.get("signal"));
  }
  if (p.get("mot_cle")) {
    // Repli identique des deux côtés + neutralisation des jokers LIKE de l'utilisateur.
    const aiguille = replier(p.get("mot_cle")).slice(0, 120)
      .replace(/([\\%_])/g, "\\$1");
    ou.push("a.texte_replie LIKE '%' || ? || '%' ESCAPE '\\'");
    params.push(aiguille);
  }
  // Fenêtre de datation : l'atome est retenu si SA fenêtre chevauche celle demandée.
  if (p.get("annee_min")) { ou.push("a.annee_max >= ?"); params.push(Number(p.get("annee_min"))); }
  if (p.get("annee_max")) { ou.push("a.annee_min <= ?"); params.push(Number(p.get("annee_max"))); }
  return { where: ou.length ? "WHERE " + ou.join(" AND ") : "", params };
}

async function recherche(env, p) {
  const { where, params } = construireFiltres(p);
  const limite = Math.min(Math.max(Number(p.get("limite")) || 50, 1), 200);
  const decalage = Math.max(Number(p.get("decalage")) || 0, 0);

  const total = await env.DB.prepare(`SELECT COUNT(*) AS n ${DE_CITATION} ${where}`)
    .bind(...params).first("n");
  const { results } = await env.DB.prepare(
    `SELECT ${CHAMPS_CITATION} ${DE_CITATION} ${where}
     ORDER BY o.annee_oeuvre, o.cle, a.debut LIMIT ? OFFSET ?`)
    .bind(...params, limite, decalage).all();

  return json({ total, rendus: results.length, decalage, citations: results });
}

async function atome(env, p) {
  const id = p.get("id") || "";
  const a = await env.DB.prepare(
    `SELECT a.id AS rowid_interne, ${CHAMPS_CITATION} ${DE_CITATION} WHERE a.atome_id = ?`)
    .bind(id).first();
  if (!a) return json({ erreur: "atome inconnu : " + id }, 404, false);
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
  return json({
    ...a,
    concepts: concepts.results,
    sous_concepts: sous.results,
    fonctions: fonctions.results.map((f) => f.fonction),
    signaux: signaux.results,
  });
}

async function referentiel(env) {
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
  return json({
    auteurs: auteurs.results,
    oeuvres: oeuvres.results,
    groupes,
    grappes: grappes.results,
    statuts: ["affirme", "modalise", "interrogatif", "rapporte"],
    meta: Object.fromEntries(meta.results.map((m) => [m.cle, m.valeur])),
  });
}

async function grappesDetail(env) {
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
  return json({ grappes: Object.values(parRang) });
}

/** Détail d'UNE grappe : éditorial, concepts, citation vedette (choisie par l'agent Python,
 *  jamais ici) et densité par œuvre — restreinte à Sigmund Freud, comme AgentCourants.executer()
 *  restreint son propre calcul (l'appendice d'Otto Rank fausserait « ce que Freud pense »). */
async function grappeUne(env, p) {
  const rang = Number(p.get("rang"));
  if (!rang) return json({ erreur: "paramètre 'rang' requis" }, 400, false);

  const g = await env.DB.prepare(
    `SELECT rang, nom, description, reserve, taille, atomes_concernes, citation_atome_id
     FROM grappes WHERE rang = ?`).bind(rang).first();
  if (!g) return json({ erreur: "grappe inconnue : " + rang }, 404, false);

  const [concepts, densite, citation] = await Promise.all([
    env.DB.prepare(
      `SELECT c.nom, c.groupe, c.n_atomes FROM grappe_concepts gc
       JOIN concepts c ON c.id = gc.concept_id
       JOIN grappes gr ON gr.id = gc.grappe_id
       WHERE gr.rang = ? ORDER BY c.n_atomes DESC`).bind(rang).all(),
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
      GROUP BY o.id ORDER BY o.annee_oeuvre`).bind(rang).all(),
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

  return json({ ...g, concepts: concepts.results, citation, densite_par_oeuvre: parOeuvre });
}

/** Chronologie d'UN concept — miroir exact d'AgentChronologie (core/agents.py) : densité sur
 *  TOUS les atomes de l'œuvre (Otto Rank compris, comme l'agent), plus la densité « d'origine »
 *  quand l'œuvre a été collationnée. Jamais un pour-cent sans le rappel de sa réserve d'édition. */
async function chronologieConcept(env, p) {
  const concept = p.get("concept") || "";
  const existe = await env.DB.prepare("SELECT 1 FROM concepts WHERE nom = ?")
    .bind(concept).first();
  if (!existe) return json({ erreur: "concept inconnu : " + concept }, 404, false);

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

  return json({
    concept, etapes,
    reserve: "Pour les œuvres COLLATIONNÉES, « pour_mille_origine » ne compte que les "
      + "passages retrouvés dans la première édition. Pour les autres, l'œuvre est lue dans "
      + "une édition postérieure dont Freud n'a pas signalé les ajouts : une variation peut y "
      + "refléter un ajout tardif plutôt qu'un mouvement de la pensée.",
  });
}

/** Lecture séquentielle d'une œuvre — les atomes dans l'ordre du texte, pas filtrés par
 *  pertinence. Pour suivre un raisonnement plutôt que chercher un mot. */
async function lire(env, p) {
  const oeuvre = p.get("oeuvre") || "";
  const o = await env.DB.prepare(
    "SELECT cle, titre, titre_fr FROM oeuvres WHERE cle = ?").bind(oeuvre).first();
  if (!o) return json({ erreur: "œuvre inconnue : " + oeuvre }, 404, false);

  const taille = Math.min(Math.max(Number(p.get("taille")) || 20, 1), 100);
  const page = Math.max(Number(p.get("page")) || 0, 0);

  const total = await env.DB.prepare(
    `SELECT COUNT(*) AS n ${DE_CITATION} WHERE o.cle = ?`).bind(oeuvre).first("n");
  const { results } = await env.DB.prepare(
    `SELECT ${CHAMPS_CITATION} ${DE_CITATION}
     WHERE o.cle = ? ORDER BY a.debut LIMIT ? OFFSET ?`)
    .bind(oeuvre, taille, page * taille).all();

  return json({
    oeuvre: o, page, taille, total, pages: Math.max(1, Math.ceil(total / taille)),
    atomes: results,
  });
}

export default {
  async fetch(requete, env) {
    const url = new URL(requete.url);
    const p = url.searchParams;
    try {
      switch (url.pathname) {
        case "/api/sante": {
          const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM atomes").first("n");
          return json({ ok: true, atomes: n }, 200, false);
        }
        case "/api/referentiel":  return await referentiel(env);
        case "/api/recherche":    return await recherche(env, p);
        case "/api/atome":        return await atome(env, p);
        case "/api/grappes":      return await grappesDetail(env);
        case "/api/grappe":       return await grappeUne(env, p);
        case "/api/chronologie":  return await chronologieConcept(env, p);
        case "/api/lire":         return await lire(env, p);
        default:
          if (url.pathname.startsWith("/api/"))
            return json({ erreur: "route inconnue : " + url.pathname }, 404, false);
          // Hors /api : les assets statiques ont déjà répondu ; on ne devrait pas arriver ici.
          return new Response("introuvable", { status: 404 });
      }
    } catch (e) {
      return json({ erreur: "erreur serveur", detail: String(e && e.message || e) }, 500, false);
    }
  },
};
