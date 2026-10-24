# Reproducibility

Run the commands in the README with Python 3.11+. No private files or installation
of third-party Python dependencies is needed. `data/manifest.json` records frozen
CSV SHA-256, exact headers/rows and historical generation lineage. Native source
hashes live in `data/native_manifest.json`. These references detect accidental
changes; they are not cryptographic signatures from an independent authority.

`python tools/reproduce.py` loads public CSVs into in-memory SQLite, creates views
from `sql/business_queries.sql`, checks 145 grouped rows against separate Python
accumulators and exports a fresh local SQLite database plus seven results tables.
Results cover daily, weekly, store, SKU, exposure, SKU/week and total scopes.
No restricted truth is needed or read. Exported SQLite is not committed; regenerate it.

`python -m unittest discover -s tests -v` tests all public contracts and launcher
behavior in a fresh path containing spaces and Unicode, from an unrelated CWD.
Missing/schema/checksum/native corruption cases must fail before runtime creation.
Repeat launch creates separate sessions with identical effective DataRoot; canonical
CSV/PBIP/PBIR/TMDL hashes stay unchanged. This is functional idempotence, not reuse
of a directory that Desktop might currently own.

Public analysis reproduces the supplied observation layer. Re-running the original
simulation requires separately governed development fixtures; that is outside this
release's supported workflow. No development archive or restricted data is shipped.
