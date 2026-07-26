/* SERVEUR MCP — le corpus freudien comme outil pour n'importe quel assistant IA.
 *
 * Un chercheur branche son propre client (Claude Desktop, Claude Code, tout client compatible
 * Model Context Protocol) sur cette URL et interroge directement le corpus — sans passer par
 * le site. Mêmes données, mêmes garde-fous que l'API REST (worker/donnees.js) : le Worker ne
 * calcule rien, il sert ce que le pipeline Python (bin/exporter_d1.py) a produit.
 *
 * SIX outils, un par requête possible sur le corpus. Chaque description de paramètre est
 * écrite pour le MODÈLE qui les lira, pas pour un humain qui lirait le code — elle doit lui
 * suffire à choisir le bon outil et le bon filtre sans deviner.
 *
 * Une instance de McpServer est créée PAR REQUÊTE (jamais partagée entre requêtes) : consigne
 * de sécurité du SDK MCP ≥1.26 contre la réutilisation de connexion entre clients différents.
 */
import { createMcpHandler } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { z } from "zod";
import * as donnees from "./donnees.js";

const texte = (o) => ({ content: [{ type: "text", text: JSON.stringify(o, null, 1) }] });

const texteErreur = (e) => ({
  content: [{ type: "text", text: JSON.stringify({ erreur: e.message || String(e) }) }],
  isError: true,
});

const INSTRUCTIONS =
  "Corpus déterministe de Sigmund Freud (1900-1933, texte allemand original, 18 000+ atomes " +
  "= phrases). AUCUN modèle de langage n'intervient dans le calcul : segmentation, " +
  "catégorisation et datation sont produites par un pipeline Python testé, pas par une IA. " +
  "RÈGLE IMPÉRATIVE : ne jamais répondre sur Freud à partir de connaissances générales sans " +
  "avoir appelé un de ces outils — chaque affirmation doit s'appuyer sur un atome retourné " +
  "ici, cité avec sa règle de datation (un atome n'est jamais daté de l'année de l'œuvre : " +
  "Freud a cessé de signaler ses ajouts dès la 3e édition, voir `datation` sur chaque " +
  "citation). Commencer par `referentiel` pour connaître le vocabulaire exact (allemand " +
  "replié : « trieb », « es », « wunscherfuellung »…) à utiliser dans les autres outils.";

function creerServeur(env) {
  const serveur = new McpServer({ name: "corpus-freud", version: "1.0.0",
                                  instructions: INSTRUCTIONS });

  const outil = (nom, description, schema, fn) =>
    serveur.tool(nom, description, schema, async (args) => {
      try { return texte(await fn(env, args)); }
      catch (e) { return texteErreur(e); }
    });

  outil("referentiel",
    "Vue d'ensemble du corpus : auteurs, œuvres (année, fiabilité de datation), tous les "
    + "concepts du lexique groupés par thème avec leur nombre d'atomes, les huit grappes de "
    + "concepts. À appeler EN PREMIER pour connaître le vocabulaire exact à utiliser ensuite.",
    {}, () => donnees.referentiel(env));

  outil("rechercher",
    "Cherche des citations dans le corpus. Chaque filtre restreint (ET logique) ; tous sont "
    + "optionnels. Rend des citations COMPLÈTES (texte allemand, œuvre, position, règle de "
    + "datation) — jamais un chiffre nu.",
    {
      concept: z.string().optional().describe("nom exact d'un concept, voir `referentiel`"),
      groupe: z.string().optional().describe("nom exact d'un groupe conceptuel"),
      auteur: z.string().optional().describe("« Sigmund Freud » ou « Otto Rank »"),
      oeuvre: z.string().optional().describe("clé exacte d'une œuvre, voir `referentiel`"),
      statut: z.enum(["affirme", "modalise", "interrogatif", "rapporte"]).optional()
        .describe("force épistémique de l'énoncé"),
      mot_cle: z.string().max(120).optional()
        .describe("sous-chaîne allemande, insensible aux diacritiques"),
      annee_min: z.number().int().optional(),
      annee_max: z.number().int().optional(),
      limite: z.number().int().min(1).max(50).optional().describe("défaut 20, max 50"),
    },
    (e, p) => donnees.rechercher(e, p));

  outil("atome",
    "Détail complet d'un atome par son identifiant exact (ex. « traumdeutung:a915 », obtenu "
    + "via `rechercher` ou `lire`) : texte, concepts, fonctions argumentatives, signaux "
    + "(objection/révision/auto-citation) et leur verdict jugé en contexte.",
    { id: z.string().describe("identifiant exact de l'atome") },
    (e, p) => donnees.obtenirAtome(e, p));

  outil("grappe",
    "Dossier complet d'UNE des huit grappes de concepts (courants internes du corpus) : "
    + "éditorial, citation vedette choisie par l'algorithme (jamais éditée à la main), "
    + "densité de la grappe par œuvre. Voir `referentiel` pour les 8 rangs disponibles.",
    { rang: z.number().int().min(1).max(8) },
    (e, p) => donnees.grappeDetail(e, p));

  outil("chronologie",
    "Densité d'UN concept œuvre par œuvre (en ‰), dans l'ordre chronologique — pour voir "
    + "QUAND un concept apparaît ou s'intensifie chez Freud. Quand l'œuvre a été collationnée "
    + "avec sa première édition, donne aussi la densité « d'origine » (passages authentifiés "
    + "de la première édition, la seule mesure comparable sans réserve).",
    { concept: z.string().describe("nom exact du concept, voir `referentiel`") },
    (e, p) => donnees.chronologieConcept(e, p));

  outil("lire",
    "Parcourt une œuvre DANS L'ORDRE DU TEXTE (paginé), pour suivre un raisonnement plutôt que "
    + "chercher un mot — utile pour restituer l'argumentation complète d'un chapitre.",
    {
      oeuvre: z.string().describe("clé exacte d'une œuvre, voir `referentiel`"),
      page: z.number().int().min(0).optional().describe("défaut 0"),
      taille: z.number().int().min(1).max(50).optional().describe("atomes par page, défaut 20"),
    },
    (e, p) => donnees.lireOeuvre(e, p));

  return serveur;
}

export async function repondreMcp(request, env, ctx) {
  return createMcpHandler(creerServeur(env))(request, env, ctx);
}
