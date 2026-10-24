# Analytics export dictionary

**56-day synthetic descriptive pilot. NOT TRAINING APPROVED.**
CSV: UTF-8, comma-separated, header row, integers as unformatted numbers, flags
0/1. No nulls are allowed in these selected export columns. No currency or dates.

| File | Grain / key | Rows |
|---|---|---:|
| data/fact_observed.csv | run/scenario/policy/day_index/store_id/sku_id | 2,688 |
| data/dim_store.csv | store_id | 6 |
| data/dim_sku.csv | sku_id | 8 |
| data/dim_day.csv | day_index | 56 |

This release contains one run/scenario/policy combination and the complete
eligible 6 x 8 x 56 grid. Do not concatenate another policy run into the model
without introducing a Run dimension and explicit selection/comparison measures.

## Fact fields

| Fields | Type | Meaning |
|---|---|---|
| run_id, scenario_id, policy_id | Text | Explicit simulation lineage; controller and review/disposition settings also in manifest |
| day_index, available_at_day | Integer | Relative simulation day, observation publication day; both 2..57 here |
| store_id, sku_id | Text | Foreign keys, unchanged master identifiers |
| opening_saleable_qty | Integer >=0 | Availability at demand fulfillment, after that day's scheduled receipts; NOT necessarily previous EOD stock |
| gross_sales_qty | Integer >=0 | Physically fulfilled observed unit sales |
| eod_saleable_qty | Integer >=0 | Closing store/SKU saleable balance; snapshot, not a time-additive flow |
| availability_status | Text enum | FULL_EXPOSURE, DEPLETED_UNCONFIRMED, NO_EXPOSURE |
| eod_zero_stock_flag | Integer 0/1 | Closing saleable stock equals zero |
| full_exposure_flag | Integer 0/1 | Status FULL_EXPOSURE |
| censored_flag | Integer 0/1 | Status is not FULL_EXPOSURE |
| no_exposure_flag | Integer 0/1 | Status NO_EXPOSURE |
| zero_sales_flag | Integer 0/1 | Observed sales equal zero; NOT proof of zero underlying demand |
| provenance | Text | SYN_OBSERVED |

For this daily service observation: opening_saleable_qty = gross_sales_qty +
eod_saleable_qty. This is not a full movement ledger. Transfers, receipts, returns
and DC inventory are not independently exported as movement facts in this package.
Full exposure + censored = observed cells. Statuses are mutually exclusive.

## Store and SKU

Store fields: store_id, city_id, city_name, region_id, region_name,
assigned_dc_id (Text); capacity_liters (Integer); provenance (SYN_MASTER).
City/region names are the existing explicitly fictional master names. Do not
invent store brands, coordinates or store names. DC is a grouping attribute,
not an additional relationship or DC stock fact.

SKU fields: sku_id, category (Text); expirable, lot_tracking_required (0/1);
unit_volume_ml (Integer); provenance (SYN_MASTER). All selected SKUs are durable.
No product names, prices, margins or unit costs are synthesized.

## Day

day_index (Integer) preserves 2..57. pilot_day_number = day_index - 1 (1..56).
pilot_week_index = floor((day_index-2)/7)+1 (1..8).
pilot_week_label = Week 1..Week 8; sort by pilot_week_index.
pilot_day_in_week_index = ((day_index-2) mod 7)+1 (1..7).
These are derived analytical indices from approved simulation day coverage, not
real dates, calendar weekdays or a fabricated master date table.

## Missingness, eligibility and lineage

The package builder verifies exact cell coverage, uniqueness, foreign keys,
as-of bounds, original observation stock/status consistency, and master hashes.
Every selected cell has exactly one master assortment interval known by day 1.
No absent/closed cell is converted to zero. Nullable unused master columns are
omitted, not filled. Input file hashes and export hashes appear in manifest.json.
Only observed partitions and selected approved master files are read; no restricted
truth/latent outcomes, evaluator records or seeds are exported.

Results CSVs are grouped query outputs for review, not additional Power BI facts.
Ratios use summed numerators/denominators. Chart data is in those same results;
every chart is calculated, not illustrative. No causal or financial inference.
