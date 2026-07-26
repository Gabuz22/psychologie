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

function rendreCitation(c) {
  const div = document.createElement("article");
  div.className = "citation";
  const chapitre = c.chapitre ? ` · ${c.chapitre.replace(/\s+/g, " ").slice(0, 60)}` : "";
  const couche = c.couche ? `<span class="badge">${
    { origine: "texte d'origine", ajout: "ajout d'édition", indecis: "non collationnable" }[c.couche]
  }</span>` : "";
  div.innerHTML = `
    <blockquote lang="de">${texteCourt(c.texte)}</blockquote>
    <p class="refs"><b>${c.auteur}</b> — <i>${c.oeuvre}</i>${
      c.oeuvre_fr ? ` (${c.oeuvre_fr})` : ""}${chapitre}
      · ${STATUTS[c.statut] || c.statut}${couche}
      · <span title="position dans le texte source">car. ${c.debut}–${c.fin}</span></p>
    <span class="datation">${c.datation}</span>`;
  return div;
}

function filtres() {
  return {
    groupe: $("#f-groupe").value, concept: $("#f-concept").value,
    oeuvre: $("#f-oeuvre").value, auteur: $("#f-auteur").value,
    statut: $("#f-statut").value, mot_cle: $("#f-mot").value.trim(),
    annee_min: $("#f-amin").value, annee_max: $("#f-amax").value,
    grappe: $("#formulaire").dataset.grappe || "",
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

function remplirConcepts(groupe) {
  const sel = $("#f-concept");
  sel.length = 1;
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
    sel.appendChild(og);
  }
}

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
    carte.title = "Parcourir les atomes de cette grappe";
    carte.addEventListener("click", () => {
      $("#formulaire").dataset.grappe = g.rang;
      $("#effacer").textContent = `Effacer (grappe : ${g.nom})`;
      chercher(false);
      $("#recherche").scrollIntoView({ behavior: "smooth" });
    });
    zone.appendChild(carte);
  }
}

async function demarrer() {
  try {
    referentiel = await api("/api/referentiel");
    const m = referentiel.meta;
    $("#stats").textContent =
      `${Number(m.atomes).toLocaleString("fr")} atomes · ${m.oeuvres} œuvres (1900-1933) · ` +
      `${Number(m.qualifies).toLocaleString("fr")} qualifiés · corpus du ${m.genere_le}`;
    $("#pied").textContent = m.licence;

    remplirSelect($("#f-groupe"), Object.keys(referentiel.groupes).sort(), (g) => [g, g]);
    remplirConcepts("");
    remplirSelect($("#f-oeuvre"), referentiel.oeuvres,
      (o) => [o.cle, `${o.titre} (${o.annee_oeuvre})`]);
    remplirSelect($("#f-auteur"), referentiel.auteurs, (a) => [a.nom, a.nom]);

    const g = await api("/api/grappes");
    rendreGrappes(g.grappes);
  } catch (e) {
    $("#stats").innerHTML =
      `<span class="erreur">API indisponible (${e.message}) — le site est-il déployé avec sa base D1 ?</span>`;
  }
}

$("#f-groupe").addEventListener("change", (e) => remplirConcepts(e.target.value));
$("#formulaire").addEventListener("submit", (e) => { e.preventDefault(); chercher(false); });
$("#plus").addEventListener("click", () => chercher(true));
$("#effacer").addEventListener("click", () => {
  $("#formulaire").reset();
  delete $("#formulaire").dataset.grappe;
  $("#effacer").textContent = "Effacer";
  remplirConcepts("");
  $("#resultats").textContent = "";
  $("#compte").textContent = "";
  $("#plus").hidden = true;
});

demarrer();
