# Architecture and supported boundary

The separate development project implements lot-based stock, PO/GRN scheduling,
causal transfers, supplier weekly capacity, effective assortment and restricted
oracle separation. Historical replay generated the frozen public pilot. This
repository reproduces descriptive analysis **from those approved public CSVs**;
it does not regenerate the physical simulation or validate its entire event ledger.

Public flow: four CSVs ? validated Python dictionaries and SQLite tables/views ?
seven analytical output CSVs ? existing native Power BI model/report.
The native model directly imports the four CSVs, not the aggregated outputs.
No private evaluator flow is connected to public SQL or Power Query.

`tools/release_qa.py` enforces the frozen input contract and model inventory.
`tools/reproduce.py` independently accumulates Python groups and compares SQL.
`launch_powerbi.py` validates inputs before preparing a unique local runtime copy.
`.github/workflows/qa.yml` exercises public-only checks on Windows and Linux.

Future phases include rolling forecasts, uncertainty and constrained decision
comparisons; this repository asserts no completed scores or economic gains.
