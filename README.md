# DemandFlow 360 ? Retail Demand & Supply Chain Analytics

**Synthetic 56-day descriptive pilot ? NOT TRAINING APPROVED.**

Retail sales tell us what was fulfilled, not everything customers wanted to buy.
DemandFlow 360 connects a separately developed physical supply-chain simulation
framework to an observed-only analytical dataset, independently reconciled Python
and SQLite analysis, and a native, editable six-page Power BI report.

This repository is complete for the public descriptive layer: frozen public inputs,
reproducible analysis, validated semantic definitions, a portable launcher and tests.
It does not ship the restricted evaluator, the development archive or a completed
forecasting/optimization application.

## Business questions

- How do fulfilled sales and observed availability vary across the pilot?
- Which stores and SKUs differ in sales and exposure?
- Which zero-sales observations had full exposure, and which were censored?
- Are analytical coverage, grain and cross-tool totals consistent?

Future work concerns leakage-safe rolling forecasts and constrained inventory
experiments. Forecast accuracy, ROI and optimization savings are not release findings.

## Architecture

```mermaid
flowchart LR
  A[Synthetic network and scenario generation] --> B[Physical inventory and supply replay]
  B --> C[Observed sales and availability]
  C --> D[Python and SQLite analytics]
  D --> E[Power BI semantic model]
  E --> F[Six native report pages]
  B -. separate private evaluation .-> R[Restricted evaluator]
```

The published boundary begins at observed CSVs. Private simulation inputs and
outcomes are excluded. See [architecture](docs/ARCHITECTURE.md).

## Scope and findings

One run/scenario/policy; days **2?57**, **6 stores**, **8 durable SKUs**.
One fact row is run ? scenario ? policy ? day ? store ? SKU.
Day indices and seven-day pilot blocks are preserved; no calendar dates or prices
have been invented.

| Metric | Reconciled result |
|---|---:|
| Observed cells / expected cells | 2,688 / 2,688 |
| Fulfilled sales units | 5,272 |
| Full-exposure cells | 1,259 (46.84%) |
| Censored cells | 1,429 (53.16%) |
| No-exposure cells | 1,080 |
| Zero-sales cells | 1,541 |
| Zero sales with full exposure | 461 |
| Day-57 closing store stock | 119 units |

Week 1 sales were 942 units versus 438 in week 8, while full exposure fell from
57.44% to 22.92%. This does **not** establish a decline in underlying demand.
STORE-018 fulfilled 904 units; SKU-0245 fulfilled 47 with full exposure in all its
336 cells. Availability changes how these rankings should be interpreted.
See the [case study](docs/CASE_STUDY.md) and [data dictionary](docs/DATA_MODEL.md).

## Run the interactive report

Requirements: Windows, current Microsoft Power BI Desktop with PBIP support,
and Python 3.11 or newer. No Python third-party libraries, database server or
DAX Studio installation are required for ordinary use.

1. Clone this repository or download and extract the **entire** repository ZIP.
2. Double-click **Launch_DemandFlow360.cmd**, or run:

```powershell
python launch_powerbi.py
```

3. In Power BI Desktop, select **Home > Refresh** and wait for completion.
4. Use INDEX navigation and HOME buttons (Ctrl+click in Desktop edit mode).
   Pilot week, store/city and category slicers filter the native visuals.

The launcher validates CSV fingerprints/schema/keys and the native file inventory,
then prepares an ignored `.runtime/session_.../powerbi` project with a machine-local
DataRoot. It discovers its own checkout location, including spaces and Unicode;
it does not edit the committed report. Each launch creates a fresh session so it
cannot overwrite an already opened project. Runtime copies are disposable local
work; edits made inside one are not changes to the canonical project.

Do not open the canonical PBIP directly: its deliberate DataRoot placeholder
must be configured by the launcher. See [Power BI guide](docs/POWER_BI_GUIDE.md).

## Reproduce and test

From the checkout root (Python/SQL QA also runs on Linux):

```powershell
python -m pip install -r requirements.txt
python tools/reproduce.py
python -m unittest discover -s tests -v
python tools/release_qa.py
python launch_powerbi.py --prepare-only
```

The first command has no third-party packages to install. Reproduction creates
an ignored, fresh `outputs/analysis_...` directory with SQLite, grouped CSVs and
QA totals. The original CSVs remain unchanged. Six grouping levels reconcile
145 output rows independently in Python and SQLite, with total and filter-context
checks. [SQL queries](sql/business_queries.sql) are reusable against the generated
database. See [reproducibility](docs/REPRODUCIBILITY.md).

## Power BI dashboard

These are the owner's genuine approved renderings, visually reviewed for this
release. They are evidence of the source report, not newly captured clean-clone UI tests.

### 00 ? INDEX
Five native navigation buttons connect the analytical pages.

![Index](screenshots/00_index.png)

### 01 ? Executive Overview
Fulfillment, exposure, weekly trends and store/SKU comparisons.

![Executive overview](screenshots/01_executive_overview.png)

### 02 ? Sales & Availability
Read sales alongside exposure status and no-exposure patterns.

![Sales and availability](screenshots/02_sales_availability.png)

### 03 ? Store & SKU Performance
Compare units per cell with full exposure rather than interpreting sales as demand.

![Store and SKU performance](screenshots/03_store_sku_performance.png)

### 04 ? Stockout Diagnostics
Distinguish zero sales, censoring and the last selected day's stock snapshot.

![Stockout diagnostics](screenshots/04_stockout_diagnostics.png)

### 05 ? Data Quality
Expected cells, missingness, duplicate grain and zero sales under full exposure.

![Data quality](screenshots/05_data_quality.png)

## QA and release status

The public workflow validates data hashes/schema/grain/FKs, observation accounting,
Python/SQL parity, six pages, 18 measures, three relationships, native field bindings,
navigation targets, screenshot links and publication safety. Launcher tests cover a
separate Unicode path with spaces, unrelated working directory, repeated preparation,
missing/corrupt files and canonical hash preservation. CI runs on Windows and Linux.

Release-time Windows Power BI engine checks are recorded in
[QA evidence](docs/QA_EVIDENCE.md). Static QA and CI do not replace interactive
Desktop Refresh, slicer and navigation acceptance. The owner previously reviewed
all six pages; new automated UI interaction remains **MANUAL_RUNTIME_QA_REQUIRED**.
See the repository Actions tab for the actual status of each commit; no CI success
is implied for future changes.

## Limitations and technology

Observed sales are not unconstrained demand. Censoring does not quantify unmet demand.
This is one finite synthetic world and policy, with 56 days and durable SKUs only.
Inventory snapshots are not additive over days. Complete coverage is not proof of
forecast-training suitability. No real revenue, dates, savings or production deployment
are claimed. [Full limitations](docs/LIMITATIONS.md).

Python standard library, SQLite, Power BI Desktop, Power Query M, TMDL, PBIR/DAX,
Git and GitHub Actions are used. DAX Studio is an optional release verification tool.
Original project code/data are offered under [MIT](LICENSE); Microsoft-generated
Power BI theme/schema assets retain their respective ownership.
