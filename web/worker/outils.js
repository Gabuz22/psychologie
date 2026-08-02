/* OUTILS — définition CANONIQUE des requêtes possibles sur le corpus.
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
  "Corpus déterministe de psychologie (116 500+ atomes = phrases, 57 œuvres, 7 auteurs), chaque " +
  "œuvre dans sa langue ORIGINALE : Sigmund Freud 1895-1933 en allemand (avec les contributions " +
  "de Josef Breuer et Otto Rank dans certains volumes), Otto Rank 1907-1928, Karl Abraham " +
  "1909-1925, Sándor Ferenczi 1907-1933, Wilhelm Stekel 1907-1917 — ces quatre-là en allemand — " +
  "et Gustave Le Bon 1895 en français. " +
  "AUCUN modèle de langage n'intervient dans le calcul : segmentation, catégorisation et " +
  "datation sont produites par un pipeline Python testé, pas par une IA.\n" +
  "RÈGLE IMPÉRATIVE : ne jamais répondre sur ces auteurs à partir de connaissances générales " +
  "sans avoir appelé un de ces outils — chaque affirmation doit s'appuyer sur un atome retourné " +
  "ici, cité avec sa règle de datation.\n" +
  "CHAQUE AUTEUR A SON PROPRE JEU DE CONCEPTS, et c'est essentiel : un même nom peut désigner " +
  "deux choses différentes selon l'auteur. « geburt » est chez Rank le traumatisme d'origine de " +
  "toute angoisse ; le mot n'a pas ce statut chez Freud. NE JAMAIS additionner ni comparer " +
  "directement les compteurs de deux auteurs sans le dire explicitement à l'utilisateur : les " +
  "grilles ne sont pas les mêmes, et un écart de chiffres peut ne mesurer que cela. " +
  "Appeler `referentiel` EN PREMIER pour voir, par auteur, les concepts réellement disponibles.\n" +
  "TROIS RÉSERVES À TRANSMETTRE quand elles s'appliquent : (1) un atome n'est jamais daté de " +
  "l'année de l'œuvre — Freud a cessé de signaler ses ajouts dès la 3e édition, voir `datation` ; " +
  "(2) plusieurs œuvres (Otto Rank, Karl Abraham, Sándor Ferenczi, Wilhelm Stekel) viennent de " +
  "FAC-SIMILÉS OCRISÉS NON RELUS (aucune transcription relue n'existe pour eux) : le champ " +
  "`qualite_source` vaut alors « ocr », et un atome dont `ocr_suspect` vaut 1 porte une trace de " +
  "corruption repérée — le signaler à l'utilisateur, qui doit vérifier la citation sur le scan " +
  "avant de la publier ; (3) dans l'outil `comparaison`, un lien de reprise n'est opposable QUE " +
  "si son `verdict` vaut « confirme » — un lien encore NULL (non lu) ou « rejete »/« reclasse » " +
  "ne doit jamais être présenté comme un emprunt entre les deux auteurs, voir la description de " +
  "cet outil. La même règle vaut pour les MENTIONS (`nominations`) : citer `confirmees`, jamais " +
  "le compte brut `atomes`, qui contient 180 faux positifs sur 2 899 — dont 57 « Abraham » qui " +
  "sont le patriarche biblique et non le collègue.";

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
      + "optionnels. Rend des citations COMPLÈTES (texte dans la langue de l'œuvre, œuvre, "
      + "position, règle de datation) — jamais un chiffre nu.",
    schema: {
      concept: z.string().optional().describe("nom exact d'un concept, voir `referentiel`"),
      groupe: z.string().optional().describe("nom exact d'un groupe conceptuel"),
      auteur: z.string().optional().describe(
        "« Sigmund Freud », « Otto Rank », « Karl Abraham », « Gustave Le Bon » ou « Josef Breuer »"),
      oeuvre: z.string().optional().describe("clé exacte d'une œuvre, voir `referentiel`"),
      statut: z.enum(["affirme", "modalise", "interrogatif", "rapporte"]).optional()
        .describe("force épistémique de l'énoncé"),
      mot_cle: z.string().max(120).optional()
        .describe("sous-chaîne dans la langue de l'œuvre cherchée, insensible aux diacritiques"),
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
      + "QUAND un concept apparaît ou s'intensifie. Fonctionne pour tout auteur, pas seulement "
      + "Freud. Quand l'œuvre a été collationnée avec sa première édition, donne aussi la "
      + "densité « d'origine » (passages authentifiés de la première édition, la seule mesure "
      + "comparable sans réserve).\n"
      + "`auteur` EST FORTEMENT RECOMMANDÉ, PAS SEULEMENT UTILE : les noms de concepts "
      + "collisionnent entre lexiques (« angst » désigne quatre motifs distincts selon qui l'a "
      + "défini), et SANS `auteur`, la courbe elle-même mélange les porteurs de TOUS les "
      + "lexiques qui ont choisi ce nom, sans distinction. Avec `auteur`, la courbe est scopée à "
      + "SON concept précis, et la réponse porte aussi `dossier` : ce qui, ailleurs dans le "
      + "corpus, touche VÉRIFIABLEMENT ce concept précis de cet auteur — actes de citation, "
      + "comparaison de densité avec les autres auteurs, mentions où cet auteur nomme un autre "
      + "en parlant de ce concept. CHAQUE ACTE ET CHAQUE MENTION PORTE SON PROPRE `verdict` "
      + "(confirme/rejete/reclasse/NULL) — rien n'est présélectionné aux seuls confirmés, lire "
      + "`dossier_reserve` avant de citer quoi que ce soit : seul « confirme » autorise à "
      + "présenter un fait comme réel, les trois signaux ne se fusionnent jamais en un score, "
      + "et aucun ne dit si le rapport est un accord ou un désaccord. Un `dossier` aux trois "
      + "signaux vides n'est pas forcément un fait négatif : un auteur isolé dans sa langue "
      + "(Gustave Le Bon, seul francophone du corpus) aura structurellement peu ou rien à "
      + "montrer — `dossier.silence` le précise quand c'est le cas.",
    schema: {
      concept: z.string().describe("nom exact du concept, voir `referentiel`"),
      auteur: z.string().optional().describe(
        "auteur propriétaire de ce concept — désambiguïse les noms partagés entre lexiques "
        + "et déclenche le calcul du `dossier`"),
    },
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
  {
    nom: "comparaison",
    description:
      "CE QU'UN AUTEUR REPREND D'UN AUTRE : passages partagés mot pour mot ou presque, chapitres "
      + "où un auteur annonce qu'il en lit un autre, et qui nomme qui. Rend TOUJOURS les deux "
      + "passages entiers côte à côte — un lien qu'on ne peut pas lire n'est pas rendu.\n"
      + "CE QUE CET OUTIL N'ÉTABLIT PAS, et qu'il ne faut jamais lui faire dire : la NATURE du "
      + "rapport. Reprendre une formulation n'est pas partager une thèse ; nommer n'est ni "
      + "suivre, ni approuver, ni contredire. Aucun chiffre ici ne mesure un accord ni un "
      + "désaccord, et il n'existe aucun champ « socle », « emprunt » ou « contradiction » DANS "
      + "CET OUTIL-CI — voir l'outil séparé `socle` pour une vue à seuils réglables entre deux "
      + "auteurs, qui n'invente pas davantage un score unique : ses deux axes restent séparés. "
      + "Le champ `sens` (calculé) n'est rempli que si les dates le permettent — NULL veut dire "
      + "INDÉCIDABLE, jamais « aucun lien ».\n"
      + "CHAQUE LIEN DE `liens` PORTE UN ÉTAT DE LECTURE, À VÉRIFIER AVANT DE LE CITER : "
      + "`verdict` vaut « confirme » (une lecture humaine en contexte tient le lien pour réel — "
      + "seul cas où il est correct de le présenter comme un emprunt entre les deux auteurs), "
      + "« rejete » (faux positif identifié à la lecture — titre, apparat bibliographique, tête "
      + "de page recollée par l'OCR : NE JAMAIS le publier comme un emprunt), « reclasse » (les "
      + "deux auteurs citent le MÊME TIERS, nommé dans `reclasse_vers` — aucun des deux ne lit "
      + "l'autre ici), ou NULL (pas encore lu : seuls `sens`/`a_verifier` informent, avec la même "
      + "prudence qu'avant). `sens_lu` est le sens établi par cette lecture et prévaut sur `sens` "
      + "quand il est renseigné. `motif_lecture` cite le texte qui fonde le verdict — à rapporter "
      + "avec lui, jamais le verdict seul, sans quoi l'affirmation redevient invérifiable pour "
      + "l'utilisateur.\n"
      + "`nominations` (QUI NOMME QUI) OBÉIT À LA MÊME RÈGLE, et l'oublier est le piège le plus "
      + "facile de cet outil : `atomes` est le compte BRUT des mentions du nom, et les 2 899 "
      + "mentions du corpus ont été lues en contexte le 2026-08-01. Citer `confirmees`, jamais "
      + "`atomes` seul. Le compte brut contient 180 faux positifs : « Abraham » qui est le "
      + "patriarche biblique (57 cas, soit 39 % des mentions de ce nom), Anna Freud prise pour "
      + "Sigmund, « freud'ger » qui est l'adjectif « freudig » élidé, « Frau Dr. Rank » qui est "
      + "l'épouse, « Abraham a Santa Clara » qui est un prédicateur baroque. `reclassees` compte "
      + "les cas où le nom est écrit par un TIERS que l'auteur recopie, non par l'auteur lui-même. "
      + "Rapporter le champ `reserve` avec tout chiffre.",
    schema: {
      auteur: z.string().optional().describe("restreindre aux liens impliquant cet auteur"),
      autre: z.string().optional().describe("second auteur, pour n'avoir qu'un couple"),
      limite: z.number().int().min(1).max(100).optional().describe("défaut 30"),
    },
    fn: (env, p) => donnees.comparaison(env, p),
  },
  {
    nom: "socle",
    description:
      "CONCEPTS CANDIDATS ENTRE DEUX AUTEURS QUELCONQUES, à seuil réglable, sur DEUX AXES QUI NE "
      + "SE FUSIONNENT JAMAIS EN UN SCORE : `actes_confirmes` (texte partagé, relu) et "
      + "`mentions_confirmees` (nom écrit, relu) — jamais additionnés, ce sont deux sortes de "
      + "faits différentes, un acte et une mention. `densites` (pour-mille d'usage comparé entre "
      + "les deux auteurs, une ligne par variante de motif quand leurs lexiques diffèrent) ne se "
      + "combine avec aucun des deux comptes ci-dessus. Baisser un seuil élargit seulement la "
      + "liste renvoyée ; les chiffres d'un concept déjà visible ne bougent jamais. AUCUN champ "
      + "ne nomme la nature du rapport (pas de « socle », « emprunt » ni « accord ») : un concept "
      + "qui passe les deux seuils est un endroit où deux mesures indépendantes sont hautes, pas "
      + "une thèse partagée. Sans `auteur`/`autre`, rend le nombre de concepts candidats par "
      + "couple, pour choisir une paire. Rapporter le champ `reserve` avec tout chiffre.",
    schema: {
      auteur: z.string().optional().describe("premier auteur de la paire"),
      autre: z.string().optional().describe("second auteur de la paire"),
      seuil_actes: z.number().int().min(0).max(50).optional()
        .describe("nombre minimal d'actes confirmés touchant le concept (axe 1) — défaut 1"),
      seuil_densite: z.number().min(0).max(100).optional()
        .describe("pour-mille minimal chez CHAQUE auteur de la paire (axe 2) — défaut 1.0"),
    },
    fn: (env, p) => donnees.socle(env, p),
  },
  {
    nom: "buisson_concepts",
    description:
      "FORCE GRADUÉE ENTRE DEUX CONCEPTS D'UN MÊME AUTEUR — un graphe de cooccurrence intra-atome, "
      + "CORRIGÉ du biais des atomes qui portent beaucoup de concepts à la fois (voir "
      + "core/agents.py:_paires_ponderees). `poids` est cette cooccurrence corrigée ; "
      + "`occurrences_brutes` est un compte NON corrigé, un garde-fou de lecture séparé, jamais "
      + "additionné ni mélangé au poids. `auteur` est OBLIGATOIRE : deux lexiques ne se mélangent "
      + "jamais, même quand deux concepts portent le même nom chez deux auteurs différents — "
      + "n'appeler cet outil qu'une fois par auteur, jamais pour comparer deux auteurs entre eux "
      + "(voir l'outil `socle` pour ça). AUCUN champ ici ne nomme une synonymie ni une proximité "
      + "de sens : c'est une cooccurrence textuelle mesurée, vérifiable atome par atome via "
      + "`buisson_concepts_atomes`. Rapporter le champ `reserve` avec tout chiffre.",
    schema: {
      auteur: z.string().describe("l'auteur dont on mesure les concepts (obligatoire)"),
      seuil_brut: z.number().int().min(0).max(1000).optional()
        .describe("nombre minimal d'occurrences brutes pour retenir une paire — défaut 8"),
    },
    fn: (env, p) => donnees.buissonConcepts(env, p),
  },
  {
    nom: "buisson_concepts_atomes",
    description:
      "Les atomes qui portent RÉELLEMENT les deux concepts demandés À LA FOIS, chez un même "
      + "auteur — pour vérifier un poids de `buisson_concepts` en revenant au texte, jamais un "
      + "chiffre qu'on ne peut pas retrouver dans le corpus.",
    schema: {
      auteur: z.string().describe("l'auteur des deux concepts"),
      concept_a: z.string().describe("premier concept"),
      concept_b: z.string().describe("second concept"),
    },
    fn: (env, p) => donnees.buissonConceptsAtomes(env, p),
  },
  {
    nom: "signaux",
    description:
      "Les passages où Freud parle de SON PROPRE travail : objections qu'il dresse contre ses "
      + "thèses, renvois à ses écrits antérieurs, révisions de ses positions. Uniquement ceux "
      + "CONFIRMÉS par une lecture en contexte — le `motif` du jugement accompagne chaque "
      + "citation et doit être rapporté avec elle, car c'est de lui que vient l'opposabilité. "
      + "Un marqueur lexical ne prouve jamais qu'un auteur se corrige : les candidats rejetés "
      + "(personnage de roman qui se corrige, objection adressée à un tiers, homonyme) ne sont "
      + "pas rendus ici.",
    schema: {
      type: z.enum(["objection", "auto_citation", "revision"]).optional()
        .describe("restreindre à un type ; sans ce filtre, les trois sont rendus"),
      limite: z.number().int().min(1).max(50).optional().describe("défaut 20, max 50"),
      decalage: z.number().int().min(0).optional().describe("pagination, défaut 0"),
    },
    fn: (env, p) => donnees.signaux(env, p),
  },
  {
    nom: "couverture_dossier",
    description:
      "CE QUE LE DOSSIER EXTERNE (voir `chronologie`) COUVRE RÉELLEMENT, sur l'ensemble des "
      + "concepts des six auteurs concernés — à appeler AVANT de conclure quoi que ce soit d'un "
      + "dossier vide. Un dossier vide n'est pas nécessairement un fait négatif : `part_remplie` "
      + "donne la part réelle de concepts ayant au moins un signal vérifié, et distingue le "
      + "« silence_structurel » (auteur isolé dans sa langue, aujourd'hui Gustave Le Bon — sa "
      + "vacuité est une limite de méthode, pas un fait sur lui) du « silence_non_explique » "
      + "(aucune barrière connue, simplement rien trouvé pour l'instant). `detail` liste, par "
      + "concept, quels signaux exacts sont non vides — utile pour savoir OÙ chercher avant "
      + "d'appeler `chronologie` concept par concept.",
    schema: {},
    fn: (env) => donnees.dossierCouverture(env),
  },
];
