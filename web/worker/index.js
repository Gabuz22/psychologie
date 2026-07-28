/* Point d'entrée du Worker — deux façades sur les MÊMES données (worker/donnees.js) :
 *   /api/*  API REST classique, consommée par le site (web/site/app.js)
 *   /mcp    serveur Model Context Protocol, pour brancher un assistant IA (Claude Desktop,
 *           Claude Code, tout client MCP) directement sur le corpus — voir worker/mcp.js
 *
 * Le Worker ne calcule rien dans un cas comme dans l'autre : il interroge ce que Python a
 * produit (bin/exporter_d1.py). Les assets statiques (web/site/) sont servis par Cloudflare
 * avant même d'atteindre ce code (voir wrangler.jsonc:assets) — on n'y arrive que pour /api/*
 * et /mcp, ou si aucun fichier statique ne correspond.
 */
import * as donnees from "./donnees.js";
import { repondreMcp } from "./mcp.js";
import { repondreChat } from "./chat.js";

const JSON_HEADERS = {
  "content-type": "application/json; charset=utf-8",
  "cache-control": "public, max-age=300",
};

function json(corps, statut = 200, cache = true) {
  const headers = { ...JSON_HEADERS };
  if (!cache) headers["cache-control"] = "no-store";
  return new Response(JSON.stringify(corps), { status: statut, headers });
}

/** Exécute une route REST : succès -> JSON 200 (caché) ; ErreurAPI -> son propre statut ;
 *  toute autre exception -> 500, jamais caché. Un seul endroit qui sait traduire les erreurs
 *  de `donnees.js` en réponses HTTP — les fonctions de données, elles, ignorent HTTP. */
async function route(fn) {
  try {
    return json(await fn());
  } catch (e) {
    if (e instanceof donnees.ErreurAPI) return json({ erreur: e.message }, e.statut, false);
    return json({ erreur: "erreur serveur", detail: String(e && e.message || e) }, 500, false);
  }
}

function objetParams(searchParams) {
  return Object.fromEntries(searchParams.entries());
}

export default {
  async fetch(requete, env, ctx) {
    const url = new URL(requete.url);
    const p = objetParams(url.searchParams);

    if (url.pathname === "/mcp") return repondreMcp(requete, env, ctx);

    switch (url.pathname) {
      case "/api/sante":
        return route(async () => {
          const n = await env.DB.prepare("SELECT COUNT(*) AS n FROM atomes").first("n");
          // `chat` dit si l'assistant est utilisable. Le site s'en sert pour ne PAS présenter
          // un formulaire qui échouera : un visiteur qui arrive sur une erreur en conclut que
          // le site est cassé, alors que tout le reste fonctionne sans clé.
          return { ok: true, atomes: n, chat: Boolean(env.GROQ_API_KEY) };
        });
      case "/api/referentiel": return route(() => donnees.referentiel(env));
      case "/api/recherche":   return route(() => donnees.rechercher(env, p));
      case "/api/atome":       return route(() => donnees.obtenirAtome(env, p));
      case "/api/grappes":     return route(() => donnees.grappesListe(env));
      case "/api/grappe":      return route(() => donnees.grappeDetail(env, p));
      case "/api/chronologie": return route(() => donnees.chronologieConcept(env, p));
      case "/api/lire":        return route(() => donnees.lireOeuvre(env, p));
      case "/api/signaux":     return route(() => donnees.signaux(env, p));
      case "/api/comparaison": return route(() => donnees.comparaison(env, p));
      case "/api/arbre":       return route(() => donnees.arbre(env, p));
      case "/api/chat":
        if (requete.method !== "POST")
          return json({ erreur: "POST requis" }, 405, false);
        return route(() => repondreChat(requete, env));
      default:
        if (url.pathname.startsWith("/api/"))
          return json({ erreur: "route inconnue : " + url.pathname }, 404, false);
        // Hors /api et /mcp : les assets statiques ont déjà répondu ; on ne devrait pas y arriver.
        return new Response("introuvable", { status: 404 });
    }
  },
};
