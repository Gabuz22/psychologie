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
        case "/api/referentiel": return await referentiel(env);
        case "/api/recherche":   return await recherche(env, p);
        case "/api/atome":       return await atome(env, p);
        case "/api/grappes":     return await grappesDetail(env);
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
