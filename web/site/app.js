/* Atomes — frontend minimal, sans framework ni build.
 * Tout vient de l'API du Worker (/api/*) ; rien n'est calculé ici : l'affichage rend
 * fidèlement ce que le pipeline Python a produit, réserves de datation comprises. */
"use strict";

const $ = (sel) => document.querySelector(sel);
let referentiel = null;
let decalage = 0;
const PAS = 25;

async function api(route, params) {
  const url = new URL(route, location.origin);
  for (const [k, v] of Object.entries(params || {})) if (v) url.searchParams.set(k, v);
  const r = await fetch(url);
  if (!r.ok) throw new Error((await r.json().catch(() => ({}))).erreur || r.statusText);
  return r.json();
}

function texteCourt(t, max = 420) {
  const plat = t.replace(/\s+/g, " ").trim();
  return plat.length > max ? plat.slice(0, max) + "…" : plat;
}

const STATUTS = { affirme: "affirmé", modalise: "modalisé",
                  interrogatif: "interrogatif", rapporte: "rapporté" };

/** Référence bibliographique complète d'une citation — pour un usage académique, copiée
 *  telle quelle. Ne cache jamais la réserve de datation. */
function referenceCitation(c) {
  const annee = c.annee_oeuvre === c.annee_edition
    ? String(c.annee_oeuvre) : `${c.annee_oeuvre}, éd. ${c.annee_edition}`;
  const chap = c.chapitre ? `, ${c.chapitre.replace(/\s+/g, " ")}` : "";
  const lien = new URL("/api/atome", location.origin);
  lien.searchParams.set("id", c.id);
  return `${c.auteur}, « ${texteCourt(c.texte, 300)} », ${c.oeuvre} (${annee})${chap}. `
       + `${c.datation}. Atome ${c.id} — ${lien.toString()}`;
}

async function copier(texte, bouton) {
  try {
    await navigator.clipboard.writeText(texte);
    const avant = bouton.textContent;
    bouton.textContent = "copié !";
    setTimeout(() => { bouton.textContent = avant; }, 1500);
  } catch {
    bouton.textContent = "copie impossible ici";
  }
}

function rendreCitation(c) {
  const div = document.createElement("article");
  div.className = "citation";
  const chapitre = c.chapitre ? ` · ${c.chapitre.replace(/\s+/g, " ").slice(0, 60)}` : "";
  const couche = c.couche ? `<span class="badge">${
    { origine: "texte d'origine", ajout: "ajout d'édition", indecis: "non collationnable" }[c.couche]
  }</span>` : "";
  // La provenance du TEXTE est aussi importante que sa datation : un fac-similé océrisé n'a pas
  // été relu par des humains. On le dit sur chaque citation, et on signale à part les phrases où
  // une trace de corruption a été repérée — celles-là sont à vérifier avant d'être publiées.
  const source = c.qualite_source === "ocr"
    ? `<span class="badge" title="Fac-similé océrisé, non relu par des humains. La citation doit être vérifiée sur le scan avant publication.">fac-similé OCR</span>`
    : "";
  const suspect = c.ocr_suspect
    ? `<span class="badge alerte" title="Une trace de corruption OCR a été repérée dans cette phrase (confusion du digramme « ch »). À vérifier sur le fac-similé.">⚠ OCR douteux</span>`
    : "";
  div.innerHTML = `
    <blockquote lang="${c.langue || "de"}">${texteCourt(c.texte)}</blockquote>
    <p class="refs"><b>${c.auteur}</b> — <i>${c.oeuvre}</i>${
      c.oeuvre_fr && c.oeuvre_fr !== c.oeuvre ? ` (${c.oeuvre_fr})` : ""}${chapitre}
      · ${STATUTS[c.statut] || c.statut}${couche}${source}${suspect}
      · <span title="position dans le texte source">car. ${c.debut}–${c.fin}</span>
      <button type="button" class="citer">citer</button></p>
    <span class="datation">${c.datation}</span>`;
  div.querySelector(".citer").addEventListener("click", (e) =>
    copier(referenceCitation(c), e.target));
  return div;
}

function filtres() {
  return {
    groupe: $("#f-groupe").value, concept: $("#f-concept").value,
    oeuvre: $("#f-oeuvre").value, auteur: $("#f-auteur").value,
    statut: $("#f-statut").value, mot_cle: $("#f-mot").value.trim(),
    annee_min: $("#f-amin").value, annee_max: $("#f-amax").value,
    limite: PAS, decalage,
  };
}

async function chercher(ajouter) {
  const zone = $("#resultats");
  if (!ajouter) { decalage = 0; zone.textContent = ""; }
  $("#compte").textContent = "recherche…";
  try {
    const r = await api("/api/recherche", filtres());
    for (const c of r.citations) zone.appendChild(rendreCitation(c));
    $("#compte").textContent = r.total
      ? `${r.total} atome(s) — ${Math.min(decalage + r.rendus, r.total)} affiché(s)`
      : "aucun résultat";
    $("#plus").hidden = decalage + r.rendus >= r.total;
    decalage += r.rendus;
  } catch (e) {
    $("#compte").innerHTML = `<span class="erreur">erreur : ${e.message}</span>`;
  }
}

function remplirSelect(sel, valeurs, rendu) {
  for (const v of valeurs) {
    const o = document.createElement("option");
    [o.value, o.textContent] = rendu(v);
    sel.appendChild(o);
  }
}

function remplirConcepts(cible, groupe) {
  cible.length = 1;
  const groupes = groupe ? { [groupe]: referentiel.groupes[groupe] || [] } : referentiel.groupes;
  for (const [g, concepts] of Object.entries(groupes)) {
    const og = document.createElement("optgroup");
    og.label = g;
    for (const c of concepts) {
      const o = document.createElement("option");
      o.value = c.nom;
      o.textContent = `${c.nom} (${c.n_atomes})`;
      og.appendChild(o);
    }
    cible.appendChild(og);
  }
}

/* ------------------------------------------------------------ grappes (courants internes) */

function rendreGrappes(grappes) {
  const zone = $("#grappes");
  for (const g of grappes) {
    const carte = document.createElement("div");
    carte.className = "carte";
    carte.innerHTML = `
      <h3>${g.rang}. ${g.nom}</h3>
      <p class="poids">${g.taille} concepts · ${g.atomes_concernes.toLocaleString("fr")} atomes</p>
      <p class="membres">${g.concepts.slice(0, 8).map((c) => c.nom).join(", ")}${
        g.concepts.length > 8 ? "…" : ""}</p>`;
    carte.title = "Ouvrir le dossier complet de cette grappe";
    carte.addEventListener("click", () => { location.hash = "courant-" + g.rang; });
    zone.appendChild(carte);
  }
}

function ligneBarre(label, pourMille, pourMilleOrigine) {
  const largeur = Math.min(100, pourMille / 10);
  const marque = pourMilleOrigine != null ? Math.min(100, pourMilleOrigine / 10) : null;
  const div = document.createElement("div");
  div.className = "ligne-barre";
  div.innerHTML = `
    <span class="label" title="${label}">${label}</span>
    <span class="piste">
      <span class="plein" style="width:${largeur}%"></span>
      ${marque != null ? `<span class="origine-marque" style="left:${marque}%" title="densité d'origine : ${pourMilleOrigine} ‰"></span>` : ""}
    </span>
    <span class="valeur">${pourMille} ‰</span>`;
  return div;
}

async function afficherGrappe(rang) {
  $("#courants").hidden = true;
  $("#courant").hidden = false;
  try {
    const g = await api("/api/grappe", { rang });
    $("#courant-nom").textContent = `${g.rang}. ${g.nom}`;
    $("#courant-poids").textContent =
      `${g.taille} concepts · ${g.atomes_concernes.toLocaleString("fr")} atomes (Sigmund Freud)`;
    $("#courant-description").textContent = g.description || "";
    $("#courant-concepts").innerHTML = g.concepts
      .map((c) => `<span class="etiquette">${c.nom} (${c.n_atomes})</span>`).join("");

    const zoneCit = $("#courant-citation");
    zoneCit.textContent = "";
    if (g.citation) zoneCit.appendChild(rendreCitation(g.citation));

    const zoneDens = $("#courant-densite");
    zoneDens.textContent = "";
    for (const d of g.densite_par_oeuvre) {
      if (!d.total) continue;
      zoneDens.appendChild(ligneBarre(`${d.annee_oeuvre} · ${d.titre}`, d.pour_mille,
        d.pour_mille_origine));
    }
    const legende = document.createElement("p");
    legende.className = "legende-graphique";
    legende.textContent = "Barre pleine : densité sur l'édition lue. Trait vertical : "
      + "densité d'origine (œuvres collationnées seulement).";
    zoneDens.appendChild(legende);

    $("#courant-reserve").textContent = g.reserve ? "Réserve — " + g.reserve : "";
    window.scrollTo({ top: $("#courant").offsetTop - 60, behavior: "smooth" });
  } catch (e) {
    $("#courant-description").innerHTML = `<span class="erreur">erreur : ${e.message}</span>`;
  }
}

/* ------------------------------------------------------------------------- chronologie */

async function afficherChronologie() {
  const concept = $("#chrono-concept").value;
  const zone = $("#chrono-resultat");
  if (!concept) { zone.textContent = ""; return; }
  zone.textContent = "chargement…";
  try {
    const r = await api("/api/chronologie", { concept });
    zone.textContent = "";
    const graphique = document.createElement("div");
    graphique.className = "graphique";
    let matiere = false;
    for (const e of r.etapes) {
      if (!e.total) continue;
      matiere = true;
      graphique.appendChild(ligneBarre(`${e.annee_oeuvre} · ${e.titre}`, e.pour_mille,
        e.pour_mille_origine));
    }
    zone.appendChild(graphique);
    if (!matiere) {
      zone.innerHTML = "<p class=\"note\">Ce concept n'apparaît dans aucune œuvre du corpus.</p>";
      return;
    }
    const legende = document.createElement("p");
    legende.className = "legende-graphique";
    legende.textContent = "Barre pleine : densité sur l'édition lue. Trait vertical : "
      + "densité d'origine (œuvres collationnées seulement).";
    zone.appendChild(legende);
    const reserve = document.createElement("p");
    reserve.className = "reserve";
    reserve.textContent = "Réserve — " + r.reserve;
    zone.appendChild(reserve);
  } catch (e) {
    zone.innerHTML = `<span class="erreur">erreur : ${e.message}</span>`;
  }
}

/* ------------------------------------------------------- Freud sur lui-même (signaux) */

/* Ne sont montrés QUE les signaux confirmés en contexte. Le motif du jugement accompagne
 * chaque citation : c'est de lui que vient l'opposabilité, pas du verdict seul — un lecteur
 * doit pouvoir contester la lecture, pas seulement la croire. */
const LIBELLES_SIGNAL = {
  objection: "objection à sa propre thèse",
  auto_citation: "renvoi à son propre travail",
  revision: "révision de soi",
};

const signaux = { type: "", decalage: 0 };

async function afficherSignaux(ajouter) {
  const zone = $("#signaux-resultats");
  if (!ajouter) { signaux.decalage = 0; zone.textContent = ""; }
  $("#signaux-compte").textContent = "chargement…";
  try {
    const r = await api("/api/signaux",
      { type: signaux.type, limite: PAS, decalage: signaux.decalage });

    for (const s of r.signaux) {
      const bloc = rendreCitation(s);
      const jugement = document.createElement("div");
      jugement.className = "jugement";
      const etiquette = document.createElement("span");
      etiquette.className = "etiquette";
      etiquette.textContent = LIBELLES_SIGNAL[s.signal] || s.signal;
      jugement.appendChild(etiquette);
      const motif = document.createElement("p");
      motif.className = "motif";
      motif.textContent = s.motif || "(motif non renseigné)";
      jugement.appendChild(motif);
      bloc.appendChild(jugement);
      zone.appendChild(bloc);
    }

    // Le compte rappelle toujours la répartition complète : un onglet filtré ne doit pas
    // laisser croire que le corpus ne contient que ce type de signal.
    const repartition = Object.entries(r.resume || {})
      .map(([k, n]) => `${n} ${LIBELLES_SIGNAL[k] || k}`).join(" · ");
    $("#signaux-compte").textContent = r.total
      ? `${r.total} signal(aux) confirmé(s) — ${Math.min(signaux.decalage + r.rendus, r.total)} `
        + `affiché(s)${repartition ? ` · en tout : ${repartition}` : ""}`
      : "aucun signal confirmé pour ce filtre";
    $("#signaux-plus").hidden = signaux.decalage + r.rendus >= r.total;
    signaux.decalage += r.rendus;
  } catch (e) {
    $("#signaux-compte").innerHTML = `<span class="erreur">erreur : ${e.message}</span>`;
  }
}

for (const bouton of document.querySelectorAll("#signaux-onglets .onglet")) {
  bouton.addEventListener("click", () => {
    document.querySelectorAll("#signaux-onglets .onglet")
      .forEach((b) => b.classList.toggle("actif", b === bouton));
    signaux.type = bouton.dataset.type || "";
    afficherSignaux(false);
  });
}
$("#signaux-plus").addEventListener("click", () => afficherSignaux(true));

/* --------------------------------------------------------------- lecture séquentielle */

const lecture = { oeuvre: null, page: 0 };

async function afficherLecture() {
  const oeuvre = $("#lecture-oeuvre").value;
  if (!oeuvre) return;
  lecture.oeuvre = oeuvre;
  const zone = $("#lecture-resultat");
  zone.textContent = "chargement…";
  try {
    const r = await api("/api/lire", { oeuvre, page: lecture.page, taille: 20 });
    $("#lecture-titre").textContent =
      `${r.oeuvre.titre}${r.oeuvre.titre_fr ? " — " + r.oeuvre.titre_fr : ""}`;
    zone.textContent = "";
    let dernierChapitre;
    for (const a of r.atomes) {
      if (a.chapitre && a.chapitre !== dernierChapitre) {
        const titre = document.createElement("div");
        titre.className = "chapitre-titre";
        titre.textContent = a.chapitre;
        zone.appendChild(titre);
      }
      dernierChapitre = a.chapitre || dernierChapitre;
      zone.appendChild(rendreCitation(a));
    }
    $("#lecture-pager").hidden = false;
    $("#lecture-position").textContent = `page ${r.page + 1} / ${r.pages} (${r.total} atomes)`;
    $("#lecture-prec").disabled = r.page <= 0;
    $("#lecture-suiv").disabled = r.page >= r.pages - 1;
    window.scrollTo({ top: $("#lecture-titre").offsetTop - 60, behavior: "smooth" });
  } catch (e) {
    zone.innerHTML = `<span class="erreur">erreur : ${e.message}</span>`;
  }
}

/* -------------------------------------------------------------------------------- assistant */

const conversation = [];   // {role: "user"|"assistant", content}

/* Statut de la vérification déterministe. « Vérifié » ne dit PAS que l'analyse est juste —
 * seulement que les citations, densités et identifiants produits se retrouvent réellement dans
 * les données. La prose d'interprétation n'est pas mécaniquement vérifiable, et l'infobulle
 * le dit plutôt que de laisser croire à une garantie plus large. */
const STATUTS_VERIF = {
  verifie: { texte: "✓ vérifié",
             titre: "Citations, densités et identifiants confrontés aux données retournées par "
                  + "les outils : tous attestés. Ne garantit pas la justesse de l'analyse." },
  corrige: { texte: "✓ vérifié après correction",
             titre: "Un premier jet contenait des éléments non attestés ; le modèle a été "
                  + "renvoyé à ses sources et sa réponse corrigée passe les contrôles." },
  reserves: { texte: "⚠ réserves",
              titre: "Des éléments n'ont pas pu être confirmés dans les données retournées, "
                   + "même après correction. Ils sont listés ci-dessous." },
};

function ajouterMessage(role, texteMsg, extras = {}) {
  const zone = $("#chat-messages");
  const div = document.createElement("div");
  div.className = "msg " + (role === "user" ? "msg-utilisateur"
    : role === "systeme" ? "msg-systeme" : "msg-assistant");
  const p = document.createElement("p");
  p.style.margin = "0";
  p.style.whiteSpace = "pre-wrap";
  p.textContent = texteMsg;                    // jamais innerHTML sur un texte de réponse LLM
  div.appendChild(p);

  const { outilsAppeles, verification, sources } = extras;

  if (verification) {
    const s = STATUTS_VERIF[verification.statut] || STATUTS_VERIF.reserves;
    const badge = document.createElement("div");
    badge.className = "verif verif-" + verification.statut;
    badge.title = s.titre;
    const c = verification.controles || {};
    const compte = [];
    if (c.citations_verifiees) compte.push(`${c.citations_verifiees} citation(s)`);
    if (c.pour_mille_verifies) compte.push(`${c.pour_mille_verifies} densité(s)`);
    if (c.identifiants_verifies) compte.push(`${c.identifiants_verifies} identifiant(s)`);
    badge.textContent = s.texte + (compte.length ? ` — ${compte.join(", ")} contrôlée(s)` : "");
    div.appendChild(badge);

    for (const pb of verification.problemes || []) {
      const alerte = document.createElement("div");
      alerte.className = "verif-probleme";
      alerte.textContent = (pb.extrait ? `« ${pb.extrait} » — ` : "") + pb.motif;
      div.appendChild(alerte);
    }
  }

  if (outilsAppeles?.length) {
    const outils = document.createElement("div");
    outils.className = "msg-outils";
    outils.textContent = "Outils appelés : " + outilsAppeles
      .map((o) => `${o.nom}(${Object.entries(o.arguments || {}).map(([k, v]) => `${k}=${v}`).join(", ")})`)
      .join(" · ");
    div.appendChild(outils);
  }

  // Les citations brutes rendues par les outils — la réponse en prose n'est jamais la seule
  // chose montrée : le lecteur peut recouper sans quitter la page.
  if (sources?.length) {
    const details = document.createElement("details");
    details.className = "sources";
    const resume = document.createElement("summary");
    resume.textContent = `Sources retournées par les outils (${sources.length})`;
    details.appendChild(resume);
    for (const c of sources) details.appendChild(rendreCitation(c));
    div.appendChild(details);
  }

  zone.appendChild(div);
  zone.scrollTop = zone.scrollHeight;
  return div;
}

async function envoyerChat(question) {
  if (!question.trim()) return;
  ajouterMessage("user", question);
  conversation.push({ role: "user", content: question });

  const attente = ajouterMessage("systeme", "réflexion en cours");
  attente.querySelector("p").classList.add("point-suspension");
  $("#chat-saisie").disabled = true;

  try {
    const r = await fetch("/api/chat", {
      method: "POST", headers: { "content-type": "application/json" },
      body: JSON.stringify({ messages: conversation }),
    });
    const data = await r.json();
    attente.remove();
    if (!r.ok) {
      ajouterMessage("systeme", "erreur : " + (data.erreur || r.statusText));
      return;
    }
    conversation.push({ role: "assistant", content: data.reponse });
    ajouterMessage("assistant", data.reponse || "(réponse vide)", {
      outilsAppeles: data.outils_appeles,
      verification: data.verification,
      sources: data.sources,
    });
  } catch (e) {
    attente.remove();
    ajouterMessage("systeme", "erreur réseau : " + e.message);
  } finally {
    $("#chat-saisie").disabled = false;
    $("#chat-saisie").focus();
  }
}

$("#form-chat").addEventListener("submit", (e) => {
  e.preventDefault();
  const champ = $("#chat-saisie");
  const question = champ.value;
  champ.value = "";
  envoyerChat(question);
});

/* --------------------------------------------------------------------------- démarrage */

function gererHash() {
  const h = location.hash.replace(/^#/, "");
  if (h.startsWith("courant-")) {
    afficherGrappe(Number(h.slice("courant-".length)));
  } else {
    $("#courant").hidden = true;
    $("#courants").hidden = false;
  }
  document.querySelectorAll("nav a").forEach((a) =>
    a.classList.toggle("actif", a.getAttribute("href") === "#" + h));
}

async function demarrer() {
  try {
    referentiel = await api("/api/referentiel");
    const m = referentiel.meta;
    $("#stats").textContent =
      `${Number(m.atomes).toLocaleString("fr")} atomes · ${m.oeuvres} œuvres, ` +
      `${(referentiel.auteurs || []).length} auteurs (1895-1933) · ` +
      `${Number(m.qualifies).toLocaleString("fr")} qualifiés · corpus du ${m.genere_le}`;
    $("#pied").textContent = m.licence;

    remplirSelect($("#f-groupe"), Object.keys(referentiel.groupes).sort(), (g) => [g, g]);
    remplirConcepts($("#f-concept"), "");
    remplirSelect($("#f-oeuvre"), referentiel.oeuvres,
      (o) => [o.cle, `${o.titre} (${o.annee_oeuvre}${
        o.auteur && o.auteur !== "Sigmund Freud" ? ", " + o.auteur : ""})`]);
    remplirSelect($("#f-auteur"), referentiel.auteurs, (a) => [a.nom, a.nom]);

    remplirConcepts($("#chrono-concept"), "");
    remplirSelect($("#lecture-oeuvre"), referentiel.oeuvres,
      (o) => [o.cle, `${o.titre} (${o.annee_oeuvre}${
        o.auteur && o.auteur !== "Sigmund Freud" ? ", " + o.auteur : ""})`]);

    const g = await api("/api/grappes");
    rendreGrappes(g.grappes);
    // Chargés d'emblée plutôt qu'au clic : une section visiblement vide se lirait comme
    // « le corpus n'a rien trouvé », alors qu'il s'agit du résultat le plus argumenté du projet.
    afficherSignaux(false);
    afficherComparaison();
    gererHash();
  } catch (e) {
    $("#stats").innerHTML =
      `<span class="erreur">API indisponible (${e.message}) — le site est-il déployé avec sa base D1 ?</span>`;
  }
}

$("#f-groupe").addEventListener("change", (e) => remplirConcepts($("#f-concept"), e.target.value));
$("#formulaire").addEventListener("submit", (e) => { e.preventDefault(); chercher(false); });
$("#plus").addEventListener("click", () => chercher(true));
$("#effacer").addEventListener("click", () => {
  $("#formulaire").reset();
  remplirConcepts($("#f-concept"), "");
  $("#resultats").textContent = "";
  $("#compte").textContent = "";
  $("#plus").hidden = true;
});

$("#form-chrono").addEventListener("submit", (e) => { e.preventDefault(); afficherChronologie(); });

$("#form-lecture").addEventListener("submit", (e) => {
  e.preventDefault();
  lecture.page = 0;
  afficherLecture();
});
$("#lecture-prec").addEventListener("click", () => { lecture.page--; afficherLecture(); });
$("#lecture-suiv").addEventListener("click", () => { lecture.page++; afficherLecture(); });

/* ---------------------------------------------------------------- ENTRE AUTEURS
 * La seule vue qui traverse la frontière entre auteurs. Elle ne montre jamais un lien sans
 * dérouler les DEUX passages entiers : c'est la contrainte fondatrice de la couche — un
 * rapprochement qu'un lecteur ne pourrait pas vérifier ne doit pas exister.
 * Aucun libellé ici ne nomme la nature du rapport (« socle », « emprunt », « contradiction ») :
 * la mesure établit qu'un texte est partagé, et rien de plus. */
const comparaison = { auteur: "", autre: "" };

function surlignerPartages(texte, partages) {
  // Les suites de mots communes sont mises en évidence dans les deux passages : c'est ce qui
  // permet de VOIR la reprise, plutôt que de croire un score.
  let html = texteCourt(texte, 700)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
  for (const g of (partages || "").split(" | ").filter(Boolean).slice(0, 6)) {
    const mots = g.split(" ").filter(Boolean);
    if (mots.length < 3) continue;
    // On surligne sur une forme souple : le texte affiché garde sa ponctuation et ses
    // majuscules, alors que le n-gramme vient de la forme normalisée.
    const motif = new RegExp(mots.map((m) =>
      m.replace(/[.*+?^${}()|[\]\\]/g, "\\$&")).join("[^a-zA-ZäöüÄÖÜß]+"), "i");
    html = html.replace(motif, (m) => `<mark>${m}</mark>`);
  }
  return html;
}

function rendreLien(l) {
  const sens = l.sens === "a_vers_b" ? `${l.auteur_a} → ${l.auteur_b}`
    : l.sens === "b_vers_a" ? `${l.auteur_b} → ${l.auteur_a}` : null;
  const badges = [
    `<span class="badge">${l.force === "manifeste" ? "reprise manifeste" : "reprise partielle"}</span>`,
    `<span class="badge">contenance ${(l.contenance * 100).toFixed(0)} %</span>`,
    sens ? `<span class="badge">${sens}</span>`
         : `<span class="badge" title="Les fenêtres de datation des deux passages se chevauchent : le corpus ne permet pas de dire lequel précède l'autre.">sens indécidable</span>`,
    l.source_tierce
      ? `<span class="badge alerte" title="Les deux passages nomment une source classique extérieure au corpus : chacun peut tenir sa formulation d'elle plutôt que de l'autre. Le lien n'est donc pas orienté.">source tierce</span>`
      : "",
    l.a_verifier ? `<span class="badge">à lire</span>` : "",
  ].filter(Boolean).join("");

  const cote = (auteur, oeuvre, annee, texte, source, suspect) => `
    <div class="cote">
      <p class="ref"><strong>${auteur}</strong> — <em>${oeuvre}</em> (${annee})
        ${source === "ocr" ? '<span class="badge">fac-similé OCR</span>' : ""}
        ${suspect ? '<span class="badge alerte">⚠ OCR douteux</span>' : ""}</p>
      <p class="passage">${surlignerPartages(texte, l.partages)}</p>
    </div>`;

  return `<article class="lien-reprise">
    <div class="etiquettes">${badges}</div>
    <div class="deux-colonnes">
      ${cote(l.auteur_a, l.oeuvre_a, l.annee_a, l.texte_a, l.source_a, l.suspect_a)}
      ${cote(l.auteur_b, l.oeuvre_b, l.annee_b, l.texte_b, l.source_b, l.suspect_b)}
    </div>
  </article>`;
}

async function afficherComparaison() {
  const zone = $("#comp-liens");
  if (!zone) return;
  zone.textContent = "chargement…";
  try {
    const r = await api("/api/comparaison",
      { auteur: comparaison.auteur, autre: comparaison.autre, limite: 30 });

    $("#comp-matrice").innerHTML = r.matrice.map((m) => `
      <button type="button" class="carte carte-couple"
              data-a="${m.auteur_a}" data-b="${m.auteur_b}">
        <h3>${m.auteur_a} ↔ ${m.auteur_b}</h3>
        <p class="poids-grappe">${m.evenements} citation${m.evenements > 1 ? "s" : ""}
           <span class="compte">(${m.paires} phrase${m.paires > 1 ? "s" : ""})</span></p>
        <p class="note">${m.manifestes} manifeste${m.manifestes > 1 ? "s" : ""} ·
           ${m.orientes} orienté${m.orientes > 1 ? "s" : ""} par les dates</p>
      </button>`).join("");

    $("#comp-lectures").innerHTML = r.lectures_declarees.length
      ? r.lectures_declarees.map((l) => `
          <article class="citation">
            <p><strong>${l.auteur}</strong> lit <strong>${l.auteur_lu}</strong> —
               <em>${l.oeuvre}</em> (${l.annee_oeuvre})</p>
            <p class="passage">« ${l.chapitre} »</p>
            <p class="note">${l.portee_atomes} atomes — un chapitre entier.</p>
          </article>`).join("")
      : "<p class='note'>Aucun chapitre ne nomme un autre auteur dans son titre.</p>";

    $("#comp-nominations").innerHTML = `<div class="table-scroll"><table class="auteurs">
      <thead><tr><th>Auteur</th><th>nomme</th><th class="num">Atomes</th><th></th></tr></thead>
      <tbody>${r.nominations.map((n) => `<tr>
        <td>${n.auteur}</td><td>${n.auteur_nomme}</td>
        <td class="num">${n.atomes}</td>
        <td class="note">${n.homographe ? "⚠ homographe — demande lecture" : ""}</td>
      </tr>`).join("")}</tbody></table></div>`;

    zone.innerHTML = r.liens.length
      ? r.liens.map(rendreLien).join("")
      : "<p class='note'>Aucun passage partagé pour ce filtre.</p>";

    $("#comp-filtres").innerHTML = (comparaison.auteur || comparaison.autre)
      ? `<button type="button" class="secondaire" id="comp-tout">Tous les couples</button>`
      : "<span class='compte'>Cliquer un couple ci-dessus pour n'afficher que le sien.</span>";

    $("#comp-reserve").textContent = r.reserve + " " + r.ne_pas_conclure;
  } catch (e) {
    zone.textContent = "erreur : " + e.message;
  }
}

document.addEventListener("click", (e) => {
  const carte = e.target.closest(".carte-couple");
  if (carte) {
    comparaison.auteur = carte.dataset.a;
    comparaison.autre = carte.dataset.b;
    afficherComparaison();
  }
  if (e.target.id === "comp-tout") {
    comparaison.auteur = comparaison.autre = "";
    afficherComparaison();
  }
});

window.addEventListener("hashchange", gererHash);

demarrer();
