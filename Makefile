.PHONY: qa test validate public-data-policy schema graph snapshot dashboard readiness ingestion acquisition vertical-slice source-snapshots seed-lake dashboard-seed

qa:
	pixi run qa

test:
	pixi run test

validate:
	pixi run seed-validate

public-data-policy:
	pixi run public-data-policy

schema:
	pixi run schema-export

graph:
	pixi run graph-seed

snapshot:
	pixi run snapshot

dashboard:
	pixi run dashboard-dev

readiness:
	pixi run readiness

ingestion:
	pixi run ingestion-plan

acquisition:
	pixi run acquisition-plan

vertical-slice:
	pixi run vertical-slice

source-snapshots:
	pixi run source-snapshots

seed-lake:
	pixi run seed-lake

dashboard-seed:
	pixi run dashboard-seed
