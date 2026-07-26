# Déployer le site sur Cloudflare

Un seul projet Cloudflare : un **Worker** (`worker/index.js`, l'API en lecture seule) qui sert
aussi les **assets statiques** (`site/`), branché sur une base **D1** (`psychologie-corpus`)
remplie par `bin/exporter_d1.py`. Tout le calcul reste en Python dans le dépôt — la base est
une projection, régénérable à volonté.

Prérequis (déjà en place sur cette machine) : Node.js ≥ 20, `wrangler` (installé globalement).

## 1. S'authentifier (une fois, action humaine)

```bash
wrangler login
```

Ouvre le navigateur sur l'OAuth Cloudflare — à faire soi-même.

## 2. Créer la base D1 (une fois)

Depuis `web/` :

```bash
wrangler d1 create psychologie-corpus
```

La commande rend un `database_id` : **le coller dans `wrangler.jsonc`** à la place de
`REMPLACER-PAR-L-ID-DE-LA-BASE`.

## 3. Recharger les données et déployer — une seule commande

```bash
cd web
./deployer.sh
```

Ce script (§5 du chantier « préparer l'app Cloudflare ») enchaîne : export du corpus Python →
rechargement complet de la base D1 distante → `wrangler deploy`. Le schéma commence par des
`DROP TABLE IF EXISTS` : **rejouable sur une base déjà peuplée**, sans jamais la supprimer —
l'`database_id` ne change donc plus jamais après la création initiale (étape 2).

`./deployer.sh --local` fait la même chose contre la base D1 **locale** seulement (pour tester
avec `wrangler dev` avant de toucher la production).

Contrôle immédiat après déploiement : `/api/sante` doit rendre
`{"ok":true,"atomes":<N>}`.

## 4. (Option) Domaine personnalisé

Dashboard Cloudflare → Workers & Pages → `psychologie` → Settings → Domains & Routes →
Add custom domain.

## 5. (Option) Cloudflare Web Analytics — mesurer l'usage sans traceur tiers

Étape manuelle unique (dashboard, ~2 min) :

1. Dashboard Cloudflare → **Analytics & Logs → Web Analytics**
2. **Add a site** → renseigner le nom d'hôte (`psychologie.<compte>.workers.dev`, ou le domaine
   personnalisé si l'étape 4 est faite)
3. Cloudflare génère un **jeton** (token) et le snippet correspondant
4. Dans `site/index.html`, décommenter le bloc `<script defer src="...beacon.min.js" ...>` en
   fin de fichier et remplacer `VOTRE_JETON_BEACON` par le jeton obtenu
5. Redéployer : `./deployer.sh`

Aucun cookie, aucune empreinte technique (fingerprinting) — Cloudflare Web Analytics est conçu
pour ne pas nécessiter de bannière de consentement.

## Test local, sans toucher à la production

```bash
cd web
./deployer.sh --local
wrangler dev
```

→ http://localhost:8787 (la copie locale de D1 vit dans `web/.wrangler/`, jamais versionnée).

## L'API

| Route | Rend |
|---|---|
| `/api/sante` | contrôle de vie + nombre d'atomes |
| `/api/referentiel` | auteurs, œuvres, groupes/concepts (avec comptes), grappes, méta |
| `/api/recherche` | citations filtrées — `concept, groupe, sous_concept, grappe, auteur, oeuvre, statut, couche, fonction, signal, mot_cle, annee_min, annee_max, limite, decalage` |
| `/api/atome?id=traumdeutung:a915` | un atome complet : concepts, fonctions, signaux jugés |
| `/api/grappes` | les huit grappes avec leurs concepts (vue liste) |
| `/api/grappe?rang=N` | dossier complet d'UNE grappe : éditorial, citation vedette (choisie par l'agent Python), densité par œuvre (+ densité d'origine si collationnée) |
| `/api/chronologie?concept=X` | densité d'un concept par œuvre — miroir exact d'`AgentChronologie` |
| `/api/lire?oeuvre=X&page=N&taille=M` | atomes d'une œuvre dans l'ordre du texte, paginés |

Principes tenus par l'API : lecture seule, paramètres liés (jamais concaténés), toute citation
porte sa règle de datation, le filtre par année s'appuie sur la fenêtre de chaque atome, la
densité des grappes se restreint à Sigmund Freud (comme `AgentCourants`), la chronologie compte
tous les atomes de l'œuvre y compris ceux d'Otto Rank (comme `AgentChronologie`).
