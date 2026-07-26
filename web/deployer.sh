#!/usr/bin/env bash
# DÉPLOYER LE SITE — enchaîne export du corpus, rechargement D1, déploiement.
#
#   ./deployer.sh            recharge la base D1 DISTANTE et déploie (production)
#   ./deployer.sh --local    recharge la base D1 LOCALE seulement (pour `wrangler dev`)
#
# Le schéma (01_schema.sql) commence par des DROP TABLE IF EXISTS : rejouable sur une base
# déjà peuplée sans la supprimer — l'identifiant de la base D1 ne change donc jamais.
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")"

CIBLE="--remote"
if [[ "${1:-}" == "--local" ]]; then
  CIBLE="--local"
fi

echo "1/3 — export du corpus Python -> derive/d1/*.sql"
(cd .. && python bin/exporter_d1.py)

echo "2/3 — rechargement D1 ($CIBLE)"
wrangler d1 execute psychologie-corpus $CIBLE --yes --file ../derive/d1/01_schema.sql
for f in ../derive/d1/02_donnees_*.sql; do
  echo "      -> $(basename "$f")"
  wrangler d1 execute psychologie-corpus $CIBLE --yes --file "$f"
done

if [[ "$CIBLE" == "--remote" ]]; then
  echo "3/3 — déploiement du Worker + site statique"
  wrangler deploy
  echo "terminé : https://psychologie.guzan99.workers.dev"
else
  echo "3/3 — base locale prête ; lancer 'wrangler dev' pour tester avant de déployer"
fi
