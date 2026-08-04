# Schéma relationnel v2 — proposition compatible

**Statut : proposition initiale, désormais complétée par** `SCHEMA_CANONIQUE_OBJETS_V2.md`,
`MODELE_RELATIONS_MULTIPLES_V2.md` et les schémas exécutables de `schemas/`. Le SQL ci-dessous est
conservé comme historique de conception ; le prototype canonique est `schemas/relations_v2.sql`.
Pas de migration générale appliquée. Le but est d'ajouter de la
provenance et des dimensions, sans casser les tables ni l'API v1.

## Modèle

Une relation n'est pas un scalaire mais un faisceau d'observations :

```text
observation
  ├─ type : mention | lecture_declaree | reprise | usage | cooccurrence
  ├─ sujets : auteur/œuvre/atome, avec rôles explicites
  ├─ mesure : valeur + unité + règle + version
  ├─ décision(s) : annotation indépendante, verdict, motif
  ├─ provenance : source, offsets, empreinte, export/commit
  └─ réserve : non comparable, langue, source tierce, absence/indécidable
```

Ne pas créer `relation.force_globale`, `relation.influence` ni une moyenne automatique.

## Ajouts proposés

```sql
CREATE TABLE relation_observations (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL CHECK(type IN
    ('mention','lecture_declaree','reprise','usage','cooccurrence')),
  objet_v1_table TEXT NOT NULL,
  objet_v1_id TEXT NOT NULL,
  regle TEXT NOT NULL,
  regle_version TEXT NOT NULL,
  valeur REAL,
  unite TEXT,
  langue_a TEXT,
  langue_b TEXT,
  comparable INTEGER NOT NULL,
  reserve TEXT,
  corpus_sha256 TEXT NOT NULL,
  git_commit TEXT NOT NULL
);

CREATE TABLE relation_annotations (
  id TEXT PRIMARY KEY,
  observation_id TEXT NOT NULL REFERENCES relation_observations(id),
  campagne TEXT NOT NULL,
  annotateur TEXT NOT NULL,
  guide_version TEXT NOT NULL,
  independante INTEGER NOT NULL,
  verdict TEXT NOT NULL,
  orientation TEXT,
  position TEXT,
  certitude_declaree TEXT,
  motif TEXT,
  cree_le TEXT NOT NULL
);

CREATE TABLE concept_alignements (
  concept_a_id INTEGER NOT NULL REFERENCES concepts(id),
  concept_b_id INTEGER NOT NULL REFERENCES concepts(id),
  relation TEXT NOT NULL CHECK(relation IN
    ('equivalent','proche','plus_large','plus_etroit','homonyme','indecidable')),
  annotation_id TEXT REFERENCES relation_annotations(id),
  PRIMARY KEY (concept_a_id, concept_b_id)
);
```

`concept_alignements` est indispensable avant d'appeler deux concepts « communs ». Une absence de
ligne signifie **non évalué**, jamais « différent ».

## Migration sans rupture

1. Ajouter les trois tables, les index et les versions dans `meta`; ne modifier aucune table v1.
2. Backfiller une observation par ligne v1, avec `comparable = 0` quand langue/règle ne permet pas
   la comparaison. Le backfill ne fabrique aucune annotation individuelle.
3. Importer les verdicts historiques comme `campagne = legacy`, `annotateur = unknown`,
   `independante = 0`; cette provenance incomplète reste visible.
4. Exposer `/api/v2/relations` en parallèle de v1. Les champs v1 restent inchangés.
5. Construire le socle v2 uniquement sur des alignements `equivalent|proche` validés et afficher
   la relation d'alignement.
6. Après une campagne et une période de comparaison, déprécier les libellés v1 trompeurs sans
   supprimer leurs données.

## Décisions requises avant implémentation

- prêts identiques entre langues (`prestige`) : comparable sur liste blanche ou toujours séparé ;
- Breuer sans lexique propre : densités exploratoires permises ou mesure non applicable ;
- règle d'alignement conceptuel et qualification requise des annotateurs ;
- statut des verdicts historiques sans identité d'annotateur.
