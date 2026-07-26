/* Substitut du paquet npm "ai" (Vercel AI SDK) — jamais installé, jamais utilisé.
 *
 * Le paquet `agents/mcp` importe dynamiquement "ai" pour une fonctionnalité CLIENT (convertir
 * un schéma d'outil MCP au format Vercel AI SDK) que ce Worker n'utilise pas — il ne sert que
 * `createMcpHandler`, côté SERVEUR. Sans ce module, l'empaquetage (esbuild) échoue en essayant
 * de résoudre "ai" pour de vrai. Voir l'alias dans wrangler.jsonc.
 */
export function jsonSchema() {
  throw new Error("stub \"ai\" non implémenté — fonctionnalité client de agents/mcp non utilisée ici");
}
