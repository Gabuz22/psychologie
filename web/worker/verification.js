/* VÉRIFICATION DÉTERMINISTE des réponses du LLM — le garde-fou qui manquait.
 *
 * Le function-calling garantit que le modèle APPELLE les bons outils ; il ne garantit pas
 * qu'il reste FIDÈLE à ce qu'ils ont répondu quand il rédige sa synthèse. Une citation
 * allemande inventée, un ‰ arrondi « à peu près », une nuance modalisée durcie en affirmation :
 * autant d'erreurs qu'aucune instruction de prompt ne peut empêcher mécaniquement.
 *
 * Ce module compare la réponse aux DONNÉES RÉELLEMENT RETOURNÉES par les outils. Aucun modèle
 * de langage n'intervient ici — vérifier avec un second LLM ne ferait que déplacer le problème.
 * Ce qui est vérifiable est vérifié ; ce qui ne l'est pas est dit tel quel, jamais présenté
 * comme validé (même doctrine que les signaux « à confirmer » du corpus).
 *
 * TROIS CHOSES SONT MÉCANIQUEMENT VÉRIFIABLES :
 *   1. les citations allemandes entre guillemets — présentes ou non dans un atome retourné ;
 *   2. les densités en ‰ — présentes ou non dans un résultat de `chronologie`/`grappe` ;
 *   3. les identifiants d'atomes (« traumdeutung:a915 ») — existants ou non.
 * Le reste (la prose d'analyse) ne l'est pas, et le document ne prétend pas le contraire.
 */
import { replier } from "./donnees.js";

/* Mots-outils allemands : servent à décider si une citation entre guillemets est de l'ALLEMAND
 * (donc à vérifier contre le corpus) ou du français (un titre traduit, une glose — à ignorer).
 * Sans ce filtre, « L'interprétation des rêves » serait signalé comme citation introuvable. */
const MOTS_ALLEMANDS = new Set([
  "der", "die", "das", "den", "dem", "des", "ein", "eine", "einen", "einem", "eines", "einer",
  "und", "oder", "aber", "auch", "nicht", "kein", "keine", "ist", "sind", "war", "waren",
  "hat", "haben", "wird", "werden", "wurde", "sich", "wir", "ich", "es", "sie", "er",
  "von", "zu", "zur", "zum", "im", "in", "mit", "auf", "fur", "durch", "uber", "aus", "bei",
  "dass", "wie", "so", "wenn", "als", "nur", "noch", "schon", "diese", "dieser", "dieses",
  "seine", "seiner", "ihre", "ihrer", "man", "wird", "kann", "muss", "soll",
]);

/** Forme de comparaison : lettres seulement, séparées par une espace simple.
 *
 * Même parti-pris que `core/collation.py:normaliser`, et pour la même raison — comparer deux
 * états d'un texte qui ne diffèrent que par leur mise en forme. Ici l'écart vient des marqueurs
 * d'emphase de Project Gutenberg conservés dans les atomes (« von W. _Stekel_ »), des appels de
 * note (« (183) ») et de la ponctuation : un modèle qui cite fidèlement le passage n'en
 * reproduit aucun. Ne garder que les lettres rend la vérification insensible à tout cela, sans
 * rien céder sur ce qui compte : les mots eux-mêmes, dans l'ordre.
 */
function pourComparaison(s) {
  return replier(s).replace(/[^a-z]+/g, " ").trim();
}

/** Un texte est-il vraisemblablement allemand ? Deux mots-outils suffisent — un ß aussi, il
 *  n'existe pas en français. Prudence assumée : en cas de doute, on ne vérifie pas plutôt que
 *  de signaler à tort. */
export function semblerAllemand(s) {
  if (/ß/.test(s)) return true;
  const mots = replier(s).split(/[^a-z]+/).filter(Boolean);
  let n = 0;
  for (const m of mots) if (MOTS_ALLEMANDS.has(m) && ++n >= 2) return true;
  return false;
}

/* Paires de guillemets rencontrées dans une réponse en français citant de l'allemand. */
const PAIRES = [["«", "»"], ["„", "“"], ["“", "”"], ["\"", "\""]];

/** Extrait les passages entre guillemets, quel que soit le style de guillemet employé. */
export function extraireCitations(texte) {
  const trouvees = [];
  for (const [ouvrant, fermant] of PAIRES) {
    const motif = new RegExp(
      `${echapper(ouvrant)}\\s*([^${echapper(ouvrant)}${echapper(fermant)}]{12,800}?)\\s*${echapper(fermant)}`,
      "g");
    let m;
    while ((m = motif.exec(texte)) !== null) trouvees.push(m[1].trim());
  }
  return trouvees;
}

const echapper = (c) => c.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

/** Découpe une citation sur ses ellipses : « … habe ich SEITHER … » se vérifie par morceaux.
 *  Les morceaux de moins de 4 mots sont écartés — trop courts pour prouver quoi que ce soit,
 *  exactement comme la collation refuse de dater un atome de moins de 8 mots. */
export function segmentsVerifiables(citation) {
  return citation
    .split(/\s*(?:\[\s*(?:\.\.\.|…)\s*\]|\.\.\.|…|\[\s*\])\s*/)
    .map((s) => s.trim())
    .filter((s) => s.split(/\s+/).filter(Boolean).length >= 4);
}

/** Parcourt un résultat d'outil (JSON arbitraire) et collecte ce qui sert à vérifier :
 *  les textes d'atomes, les titres d'œuvres, les densités en ‰, les identifiants d'atomes. */
function parcourir(valeur, ctx, profondeur = 0) {
  if (valeur == null || profondeur > 10) return;
  if (Array.isArray(valeur)) {
    for (const v of valeur) parcourir(v, ctx, profondeur + 1);
    return;
  }
  if (typeof valeur !== "object") return;

  for (const champ of ["texte", "titre", "titre_fr", "nom", "edition_lue", "chapitre"]) {
    if (typeof valeur[champ] === "string") ctx.textes.push(valeur[champ]);
  }
  for (const champ of ["pour_mille", "pour_mille_origine"]) {
    if (typeof valeur[champ] === "number") ctx.pourMille.add(valeur[champ]);
  }
  if (typeof valeur.id === "string" && /^[a-z_]+:a\d+$/.test(valeur.id)) {
    ctx.identifiants.add(valeur.id);
  }
  for (const v of Object.values(valeur)) parcourir(v, ctx, profondeur + 1);
}

/** Rassemble tout ce que les outils ont réellement retourné pendant la conversation. */
export function contexteVerification(resultatsOutils) {
  const ctx = { textes: [], pourMille: new Set(), identifiants: new Set() };
  for (const r of resultatsOutils) parcourir(r, ctx);
  // Un seul grand texte normalisé : la vérification d'une citation devient une recherche de
  // sous-chaîne, insensible aux diacritiques, au ß, aux retours à la ligne, à la ponctuation
  // et aux marqueurs d'emphase du texte source. Le séparateur empêche une citation de
  // chevaucher deux atomes distincts et de passer à tort.
  ctx.corpusNormalise = ctx.textes.map(pourComparaison).join(" | ");
  return ctx;
}

/**
 * Vérifie une réponse du modèle contre les données réellement retournées.
 * Rend { ok, problemes: [{type, extrait, motif}], controles: {…} } — `controles` dit ce qui a
 * été vérifié et combien, pour que « aucun problème » ne se confonde jamais avec « rien vérifié ».
 */
export function verifierReponse(reponse, ctx, { outilsAppeles = 0 } = {}) {
  const problemes = [];
  const controles = { citations_verifiees: 0, citations_ignorees: 0, pour_mille_verifies: 0,
                      identifiants_verifies: 0 };

  // 1. Citations allemandes — le cœur du projet : une citation fausse est le pire défaut possible.
  for (const citation of extraireCitations(reponse)) {
    if (!semblerAllemand(citation)) { controles.citations_ignorees++; continue; }
    const segments = segmentsVerifiables(citation);
    if (!segments.length) { controles.citations_ignorees++; continue; }
    controles.citations_verifiees++;
    for (const seg of segments) {
      if (!ctx.corpusNormalise.includes(pourComparaison(seg))) {
        problemes.push({
          type: "citation_introuvable",
          extrait: seg.length > 160 ? seg.slice(0, 160) + "…" : seg,
          motif: "ce texte allemand n'apparaît dans aucun atome retourné par les outils",
        });
        break;   // un segment fautif suffit à disqualifier la citation
      }
    }
  }

  // 2. Densités en ‰ — elles viennent telles quelles des outils, aucune raison de les recalculer.
  for (const m of reponse.matchAll(/(\d+(?:[.,]\d+)?)\s*(?:‰|pour\s?mille|pour-mille)/gi)) {
    const valeur = Number(m[1].replace(",", "."));
    controles.pour_mille_verifies++;
    if (!ctx.pourMille.has(valeur)) {
      problemes.push({
        type: "chiffre_non_atteste",
        extrait: m[0],
        motif: "cette densité n'apparaît dans aucun résultat d'outil (valeurs obtenues : "
             + (ctx.pourMille.size ? [...ctx.pourMille].sort((a, b) => a - b).join(", ")
                                   : "aucune") + ")",
      });
    }
  }

  // 3. Identifiants d'atomes — vérifiables au caractère près.
  for (const m of reponse.matchAll(/\b([a-z_]+:a\d+)\b/g)) {
    controles.identifiants_verifies++;
    if (!ctx.identifiants.has(m[1])) {
      problemes.push({
        type: "atome_inexistant",
        extrait: m[1],
        motif: "cet identifiant d'atome n'a été retourné par aucun outil",
      });
    }
  }

  // 4. Réponse substantielle sans aucun appel d'outil — le cas « répondu de mémoire », que ce
  //    projet s'interdit partout ailleurs. Les réponses courtes (salutation, question sur le
  //    site lui-même) restent légitimes sans outil.
  if (outilsAppeles === 0 && reponse.trim().length > 400) {
    problemes.push({
      type: "sans_source",
      extrait: reponse.trim().slice(0, 120) + "…",
      motif: "réponse longue produite sans qu'aucun outil du corpus n'ait été appelé",
    });
  }

  return { ok: problemes.length === 0, problemes, controles };
}

/** Message de correction adressé au modèle — factuel, sans commentaire, sans excuse demandée. */
export function messageCorrection(problemes) {
  const liste = problemes
    .map((p) => `- ${p.extrait ? `« ${p.extrait} » : ` : ""}${p.motif}`)
    .join("\n");
  return (
    "VÉRIFICATION AUTOMATIQUE DÉTERMINISTE (contrôle du serveur, pas un message d'utilisateur).\n"
    + "Les éléments suivants de ta réponse NE SE RETROUVENT PAS dans les données que les outils "
    + "t'ont renvoyées :\n" + liste + "\n\n"
    + "Réécris ta réponse en ne conservant QUE ce qui est attesté par les résultats d'outils déjà "
    + "obtenus. S'il te manque une donnée, APPELLE l'outil approprié plutôt que de la reconstituer "
    + "de mémoire. Ne commente pas ce contrôle et ne t'excuse pas : produis directement la "
    + "réponse corrigée."
  );
}
