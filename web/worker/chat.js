/* CHAT — assistant du site, en langage naturel, JAMAIS sans données à l'appui.
 *
 * Utilise Groq (API compatible OpenAI, function-calling) avec les MÊMES outils que le serveur
 * MCP (worker/outils.js) : le modèle ne répond jamais « de mémoire » sur Freud — il doit
 * appeler un outil, qui interroge la base D1 réelle. C'est le seul point du projet où un LLM
 * intervient, et il intervient UNIQUEMENT pour choisir quels outils appeler et METTRE EN PROSE
 * leurs résultats — jamais pour produire un fait sur Freud de son propre chef.
 *
 * TROIS ÉTAPES, dont la troisième est ce qui distingue cet assistant d'un chatbot ordinaire :
 *   1. boucle d'outils — le modèle interroge le corpus autant de fois qu'il le faut ;
 *   2. VÉRIFICATION DÉTERMINISTE (worker/verification.js) — la réponse rédigée est confrontée
 *      aux données réellement retournées : citations allemandes, densités en ‰, identifiants
 *      d'atomes. Aucun modèle de langage n'intervient dans ce contrôle ;
 *   3. correction — si la vérification échoue, le modèle est renvoyé à ses propres sources avec
 *      la liste exacte des écarts, puis re-vérifié. Ce qui échoue encore est SIGNALÉ à
 *      l'utilisateur, jamais tu (même doctrine que les signaux « à confirmer » du corpus).
 *
 * Pourquoi Groq : gratuit, rapide, même fournisseur que la voix de Gabriel Virtuel (leçon
 * retenue de ce projet — Gemini exige désormais une facturation).
 */
import { z } from "zod";
import { zodToJsonSchema } from "zod-to-json-schema";
import { OUTILS, INSTRUCTIONS } from "./outils.js";
import { ErreurAPI } from "./donnees.js";
import { contexteVerification, verifierReponse, messageCorrection } from "./verification.js";

const GROQ_URL = "https://api.groq.com/openai/v1/chat/completions";
const MODELE_DEFAUT = "llama-3.3-70b-versatile";
const TOURS_MAX = 5;              // appels d'outils en chaîne avant d'exiger une réponse
const CORRECTIONS_MAX = 1;        // tours de correction après échec de vérification
const HISTORIQUE_MAX = 20;        // derniers messages conservés (coût + abus)
const MESSAGE_MAX = 4000;         // caractères par message utilisateur

const SYSTEM_PROMPT = INSTRUCTIONS + "\n\nTu es l'assistant du site du corpus, pour un " +
  "public allant du curieux au chercheur. Réponds en français, de façon claire et concise. " +
  "Encadre TOUTE citation (allemande ou française) de guillemets « » et reproduis-la " +
  "exactement telle que l'outil te l'a rendue — un contrôle automatique déterministe vérifie " +
  "chaque citation et chaque densité en ‰ contre les données retournées, et te renverra tes " +
  "écarts. Cite systématiquement l'œuvre, l'auteur et la règle de datation de chaque atome " +
  "utilisé. Si aucun outil ne retourne d'information pertinente à la question, dis-le " +
  "explicitement plutôt que de deviner ou de t'appuyer sur ce que tu sais par ailleurs de " +
  "ces auteurs.";

function schemasOpenAI() {
  return OUTILS.map((o) => {
    const brut = zodToJsonSchema(z.object(o.schema), { target: "openApi3" });
    delete brut.$schema;
    return { type: "function",
             function: { name: o.nom, description: o.description, parameters: brut } };
  });
}

async function appelerGroq(env, messages, modele) {
  const rep = await fetch(GROQ_URL, {
    method: "POST",
    headers: { "Content-Type": "application/json",
              "Authorization": `Bearer ${env.GROQ_API_KEY}` },
    body: JSON.stringify({
      model: modele, messages, tools: schemasOpenAI(), tool_choice: "auto", temperature: 0.2,
    }),
  });
  if (!rep.ok) {
    const detail = await rep.text().catch(() => "");
    throw new ErreurAPI(
      `fournisseur LLM en erreur (${rep.status}) : ${detail.slice(0, 300)}`, 502);
  }
  const donnees = await rep.json();
  const msg = donnees.choices?.[0]?.message;
  if (!msg) throw new ErreurAPI("réponse du fournisseur LLM vide ou malformée", 502);
  return msg;
}

/** Boucle d'outils jusqu'à une réponse en prose. Accumule les résultats bruts des outils —
 *  ils sont la SEULE référence contre laquelle la réponse sera ensuite vérifiée. */
async function jusquALaReponse(env, messages, modele, outilsAppeles, resultatsOutils) {
  for (let tour = 0; tour < TOURS_MAX; tour++) {
    const msg = await appelerGroq(env, messages, modele);
    messages.push(msg);
    if (!msg.tool_calls?.length) return msg.content || "";

    for (const appel of msg.tool_calls) {
      const def = OUTILS.find((o) => o.nom === appel.function.name);
      let args = {}, resultat;
      try {
        args = JSON.parse(appel.function.arguments || "{}");
        resultat = def
          ? await def.fn(env, args)
          : { erreur: "outil inconnu : " + appel.function.name };
      } catch (e) {
        resultat = { erreur: e.message || String(e) };
      }
      outilsAppeles.push({ nom: appel.function.name, arguments: args });
      resultatsOutils.push(resultat);
      messages.push({ role: "tool", tool_call_id: appel.id, content: JSON.stringify(resultat) });
    }
  }
  throw new ErreurAPI("trop d'appels d'outils en chaîne sans réponse finale", 502);
}

export async function repondreChat(request, env) {
  if (!env.GROQ_API_KEY) {
    throw new ErreurAPI(
      "Chat indisponible : aucune clé Groq configurée côté serveur (secret GROQ_API_KEY). "
      + "Voir DEPLOIEMENT.md.", 503);
  }
  const corps = await request.json().catch(() => null);
  if (!corps || !Array.isArray(corps.messages) || !corps.messages.length) {
    throw new ErreurAPI("corps invalide : { messages: [{role, content}, …] } attendu", 400);
  }

  const historique = corps.messages.slice(-HISTORIQUE_MAX)
    .filter((m) => m && (m.role === "user" || m.role === "assistant") && m.content)
    .map((m) => ({ role: m.role, content: String(m.content).slice(0, MESSAGE_MAX) }));
  if (!historique.length) throw new ErreurAPI("aucun message utilisateur valide", 400);

  const messages = [{ role: "system", content: SYSTEM_PROMPT }, ...historique];
  const modele = env.GROQ_MODEL || MODELE_DEFAUT;
  const outilsAppeles = [], resultatsOutils = [];

  let reponse = await jusquALaReponse(env, messages, modele, outilsAppeles, resultatsOutils);
  let verdict = verifierReponse(reponse, contexteVerification(resultatsOutils),
                                { outilsAppeles: outilsAppeles.length });
  let corrections = 0;

  while (!verdict.ok && corrections < CORRECTIONS_MAX) {
    corrections++;
    messages.push({ role: "user", content: messageCorrection(verdict.problemes) });
    reponse = await jusquALaReponse(env, messages, modele, outilsAppeles, resultatsOutils);
    verdict = verifierReponse(reponse, contexteVerification(resultatsOutils),
                              { outilsAppeles: outilsAppeles.length });
  }

  return {
    reponse,
    outils_appeles: outilsAppeles,
    modele,
    // Les citations réellement retournées, pour que l'utilisateur recoupe sans quitter la page :
    // la réponse en prose n'est jamais la seule chose montrée.
    sources: resultatsOutils.flatMap((r) => r?.citations || (r?.citation ? [r.citation] : []))
      .filter(Boolean).slice(0, 12),
    verification: {
      // « verifie » = les contrôles mécaniques sont passés, PAS que l'analyse est juste :
      // la prose d'interprétation n'est pas mécaniquement vérifiable, et on ne le prétend pas.
      statut: verdict.ok ? (corrections ? "corrige" : "verifie") : "reserves",
      corrections,
      controles: verdict.controles,
      problemes: verdict.problemes,
    },
  };
}
