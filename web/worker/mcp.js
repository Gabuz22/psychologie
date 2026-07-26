/* SERVEUR MCP — le corpus freudien comme outil pour n'importe quel assistant IA.
 *
 * Un chercheur branche son propre client (Claude Desktop, Claude Code, tout client compatible
 * Model Context Protocol) sur cette URL et interroge directement le corpus — sans passer par
 * le site. Les six outils viennent de worker/outils.js (source canonique, partagée avec le
 * chat du site) : ce fichier ne fait que les brancher sur le protocole MCP.
 *
 * Une instance de McpServer est créée PAR REQUÊTE (jamais partagée entre requêtes) : consigne
 * de sécurité du SDK MCP ≥1.26 contre la réutilisation de connexion entre clients différents.
 */
import { createMcpHandler } from "agents/mcp";
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { OUTILS, INSTRUCTIONS } from "./outils.js";

const texte = (o) => ({ content: [{ type: "text", text: JSON.stringify(o, null, 1) }] });

const texteErreur = (e) => ({
  content: [{ type: "text", text: JSON.stringify({ erreur: e.message || String(e) }) }],
  isError: true,
});

function creerServeur(env) {
  const serveur = new McpServer({ name: "corpus-freud", version: "1.0.0",
                                  instructions: INSTRUCTIONS });
  for (const o of OUTILS) {
    serveur.tool(o.nom, o.description, o.schema, async (args) => {
      try { return texte(await o.fn(env, args)); }
      catch (e) { return texteErreur(e); }
    });
  }
  return serveur;
}

export async function repondreMcp(request, env, ctx) {
  return createMcpHandler(creerServeur(env))(request, env, ctx);
}
