/* OUTILS — définition CANONIQUE des six requêtes possibles sur le corpus.
 *
 * Une seule source de vérité (nom, description, schéma Zod, fonction) consommée par les DEUX
 * façades IA : worker/mcp.js (protocole MCP, pour un assistant externe) et worker/chat.js
 * (function-calling Groq, pour le chat intégré au site). Sans ce fichier, les deux auraient
 * dérivé — deux descriptions d'outil légèrement différentes pour la même requête, ce que le
 * projet ne tolère nulle part ailleurs (une seule logique de requête, voir donnees.js).
 *
 * `schema` est un objet de champs Zod bruts (pas un z.object(...)) — c'est la forme attendue
 * par `McpServer.tool()`, et `z.object(schema)` suffit à la retransformer pour les usages qui
 * en ont besoin (conversion JSON Schema pour Groq, notamment).
 */
import { z } from "zod";
import * as donnees from "./donnees.js";

export const INSTRUCTIONS =
  "Corpus déterministe de Sigmund Freud (1900-1933, texte allemand original, 18 000+ atomes " +
  "= phrases). AUCUN modèle de langage n'intervient dans le calcul : segmentation, " +
  "catégorisation et datation sont produites par un pipeline Python testé, pas par une IA. " +
  "RÈGLE IMPÉRATIVE : ne jamais répondre sur Freud à partir de connaissances générales sans " +
  "avoir appelé un de ces outils — chaque affirmation doit s'appuyer sur un atome retourné " +
  "ici, cité avec sa règle de datation (un atome n'est jamais daté de l'année de l'œuvre : " +
  "Freud a cessé de signaler ses ajouts dès la 3e édition, voir `datation` sur chaque " +
  "citation). Commencer par `referentiel` pour connaître le vocabulaire exact (allemand " +
  "replié : « trieb », « es », « wunscherfuellung »…) à utiliser dans les autres outils.";

export const OUTILS = [
  {
    nom: "referentiel",
    description:
      "Vue d'ensemble du corpus : auteurs, œuvres (année, fiabilité de datation), tous les "
      + "concepts du lexique groupés par thème avec leur nombre d'atomes, les huit grappes de "
      + "concepts. À appeler EN PREMIER pour connaître le vocabulaire exact à utiliser ensuite.",
    schema: {},
    fn: (env) => donnees.referentiel(env),
  },
  {
    nom: "rechercher",
    description:
      "Cherche des citations dans le corpus. Chaque filtre restreint (ET logique) ; tous sont "
      + "optionnels. Rend des citations COMPLÈTES (texte allemand, œuvre, position, règle de "
      + "datation) — jamais un chiffre nu.",
    schema: {
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
    fn: (env, p) => donnees.rechercher(env, p),
  },
  {
    nom: "atome",
    description:
      "Détail complet d'un atome par son identifiant exact (ex. « traumdeutung:a915 », obtenu "
      + "via `rechercher` ou `lire`) : texte, concepts, fonctions argumentatives, signaux "
      + "(objection/révision/auto-citation) et leur verdict jugé en contexte.",
    schema: { id: z.string().describe("identifiant exact de l'atome") },
    fn: (env, p) => donnees.obtenirAtome(env, p),
  },
  {
    nom: "grappe",
    description:
      "Dossier complet d'UNE des huit grappes de concepts (courants internes du corpus) : "
      + "éditorial, citation vedette choisie par l'algorithme (jamais éditée à la main), "
      + "densité de la grappe par œuvre. Voir `referentiel` pour les 8 rangs disponibles.",
    schema: { rang: z.number().int().min(1).max(8) },
    fn: (env, p) => donnees.grappeDetail(env, p),
  },
  {
    nom: "chronologie",
    description:
      "Densité d'UN concept œuvre par œuvre (en ‰), dans l'ordre chronologique — pour voir "
      + "QUAND un concept apparaît ou s'intensifie chez Freud. Quand l'œuvre a été collationnée "
      + "avec sa première édition, donne aussi la densité « d'origine » (passages authentifiés "
      + "de la première édition, la seule mesure comparable sans réserve).",
    schema: { concept: z.string().describe("nom exact du concept, voir `referentiel`") },
    fn: (env, p) => donnees.chronologieConcept(env, p),
  },
  {
    nom: "lire",
    description:
      "Parcourt une œuvre DANS L'ORDRE DU TEXTE (paginé), pour suivre un raisonnement plutôt "
      + "que chercher un mot — utile pour restituer l'argumentation complète d'un chapitre.",
    schema: {
      oeuvre: z.string().describe("clé exacte d'une œuvre, voir `referentiel`"),
      page: z.number().int().min(0).optional().describe("défaut 0"),
      taille: z.number().int().min(1).max(50).optional().describe("atomes par page, défaut 20"),
    },
    fn: (env, p) => donnees.lireOeuvre(env, p),
  },
];
