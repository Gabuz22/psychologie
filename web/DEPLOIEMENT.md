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

## 3. Générer et charger les données

Depuis la racine du dépôt :

```bash
python bin/exporter_d1.py
```

Puis, depuis `web/`, charger le schéma et les tranches de données **dans l'ordre** :

```bash
wrangler d1 execute psychologie-corpus --remote --file ../derive/d1/01_schema.sql
wrangler d1 execute psychologie-corpus --remote --file ../derive/d1/02_donnees_01.sql
wrangler d1 execute psychologie-corpus --remote --file ../derive/d1/02_donnees_02.sql
wrangler d1 execute psychologie-corpus --remote --file ../derive/d1/02_donnees_03.sql
wrangler d1 execute psychologie-corpus --remote --file ../derive/d1/02_donnees_04.sql
```

**Rechargement après mise à jour du corpus** : le schéma commence par des `CREATE TABLE` —
pour repartir propre, supprimer puis recréer la base (`wrangler d1 delete psychologie-corpus`
→ étape 2) ; l'`database_id` change alors, le remettre dans `wrangler.jsonc`.

## 4. Déployer

Depuis `web/` :

```bash
wrangler deploy
```

Le site répond sur `https://psychologie.<compte>.workers.dev`. Contrôle immédiat :
`/api/sante` doit rendre `{"ok":true,"atomes":18659}`.

## 5. (Option) Domaine personnalisé

Dashboard Cloudflare → Workers & Pages → `psychologie` → Settings → Domains & Routes →
Add custom domain.

## Test local, sans toucher à la production

```bash
wrangler d1 execute psychologie-corpus --local --file ../derive/d1/01_schema.sql
wrangler d1 execute psychologie-corpus --local --file ../derive/d1/02_donnees_01.sql
wrangler d1 execute psychologie-corpus --local --file ../derive/d1/02_donnees_02.sql
wrangler d1 execute psychologie-corpus --local --file ../derive/d1/02_donnees_03.sql
wrangler d1 execute psychologie-corpus --local --file ../derive/d1/02_donnees_04.sql
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
| `/api/grappes` | les huit grappes avec leurs concepts |

Principes tenus par l'API : lecture seule, paramètres liés (jamais concaténés), toute citation
porte sa règle de datation, le filtre par année s'appuie sur la fenêtre de chaque atome.
