# Dependencies

This document lists the dependencies of the `gws_biota` brick: the Constellab bricks it requires, and the external Python packages used by its tasks.

## Constellab bricks

Declared in [`settings.json`](./settings.json):

| Brick | Version |
|---|---|
| `gws_core` | >= 0.22.0 |
| `gws_ai_toolkit` | >= 0.2.6 — powers the AI chat assistant of the Bio Navigator app (`ai/`, `apps/biota_app/`) |

## Python packages (pip)

Declared in `settings.json`, installed in the main environment:

| Package | Version | Used by |
|---|---|---|
| `biopython` | ==1.79 | Sequence/record parsing across the ETL and ontology modules |
| `networkx` | ==3.4.2 | Whole-cell reaction network graph (`unicell/unicell.py`, `unicell/unicell_service.py`) |
| `pronto` | ==2.5.7 | Parsing the GO, SBO, ECO and BTO ontology files (`_helper/ontology.py`, `_helper/brenda.py`) |
| `pyparsing` | ==3.0.6 | Declared as a pinned transitive dependency (used internally by `pronto`); not imported directly |

## Git packages

Declared in `settings.json` under `environment.git` (source: `https://github.com/Constellab`):

| Package | Used by |
|---|---|
| `brendapy` | Parsing BRENDA enzyme data to populate the database (`_helper/brenda.py`, `db/db_service.py`) |
