CREATE TABLE IF NOT EXISTS v2_runs (
  id TEXT PRIMARY KEY,
  schema_version TEXT NOT NULL,
  corpus_version TEXT NOT NULL,
  rule_version TEXT NOT NULL,
  source_export_sha256 TEXT NOT NULL,
  mode TEXT NOT NULL CHECK(mode IN ('prototype','migration'))
);
CREATE TABLE IF NOT EXISTS v2_relations (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES v2_runs(id),
  type TEXT NOT NULL,
  source_type TEXT NOT NULL, source_id TEXT NOT NULL,
  target_type TEXT NOT NULL, target_id TEXT NOT NULL,
  direction_state TEXT NOT NULL,
  direction_value TEXT,
  validation_state TEXT NOT NULL,
  interpretation TEXT,
  coverage_limit TEXT,
  corpus_version TEXT NOT NULL,
  rule_version TEXT NOT NULL,
  CHECK(direction_state != 'inconnue' OR direction_value IS NULL)
);
CREATE INDEX IF NOT EXISTS idx_v2_relation_pair
  ON v2_relations(source_type, source_id, target_type, target_id);
CREATE TABLE IF NOT EXISTS v2_evidence (
  id TEXT NOT NULL,
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  polarity TEXT NOT NULL CHECK(polarity IN ('favorable','defavorable')),
  target_type TEXT NOT NULL, target_id TEXT NOT NULL,
  source TEXT NOT NULL,
  excerpt TEXT,
  provenance TEXT NOT NULL,
  PRIMARY KEY (relation_id, id)
);
CREATE TABLE IF NOT EXISTS v2_dimensions (
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  name TEXT NOT NULL,
  state TEXT NOT NULL,
  value_json TEXT,
  unit TEXT,
  rule TEXT,
  rule_version TEXT,
  limitations TEXT,
  PRIMARY KEY (relation_id, name)
);
CREATE TABLE IF NOT EXISTS v2_annotations (
  id TEXT PRIMARY KEY,
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  agent_kind TEXT NOT NULL CHECK(agent_kind IN ('humain','automatique','legacy_inconnu')),
  agent_id TEXT NOT NULL,
  independent INTEGER NOT NULL,
  proposition TEXT NOT NULL,
  validation_state TEXT NOT NULL,
  confidence_state TEXT NOT NULL,
  confidence_value TEXT,
  guide_version TEXT
);
CREATE TABLE IF NOT EXISTS v2_history (
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  ordinal INTEGER NOT NULL,
  action TEXT NOT NULL,
  actor TEXT NOT NULL,
  detail TEXT,
  PRIMARY KEY (relation_id, ordinal)
);
CREATE TABLE IF NOT EXISTS v2_legacy_metrics (
  relation_id TEXT NOT NULL REFERENCES v2_relations(id),
  name TEXT NOT NULL,
  value_json TEXT,
  original_rule TEXT NOT NULL,
  original_rule_version TEXT NOT NULL,
  canonical INTEGER NOT NULL DEFAULT 0 CHECK(canonical=0),
  caveat TEXT NOT NULL,
  PRIMARY KEY (relation_id, name)
);
CREATE TABLE IF NOT EXISTS v2_unconvertible (
  source_table TEXT NOT NULL,
  source_id TEXT NOT NULL,
  reason TEXT NOT NULL,
  payload_json TEXT NOT NULL,
  PRIMARY KEY (source_table, source_id)
);
