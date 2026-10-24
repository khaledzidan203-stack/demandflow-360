# DemandFlow 360: observed sales and availability

**56-day synthetic descriptive pilot. NOT TRAINING APPROVED.**

The release covers simulation days 2-57, six stores and eight durable SKUs:
2,688 complete observed cells and 5,272 physically
fulfilled units. No restricted evaluator quantities are included.

## Findings

- Full exposure occurred in 1,259 cells
  (46.84%); 1,429 cells
  (53.16%) were censored. 1,080
  had no opening availability. EOD zero does not establish unmet demand.
- Seven-day observed sales declined from 942 in pilot week 1
  to 438 in week 8. Full exposure also declined from
  57.44% to
  22.92%. These are parallel
  observations, not an identified cause or evidence of lower underlying demand.
- STORE-018 leads observed sales with 904 units; STORE-017 records 845.
  Equal 448-cell store coverage permits descriptive comparison, but stock
  availability differs. Rankings do not measure profitability or demand potential.
- SKU-0169 and SKU-0242 each record 1,332 sales. SKU-0245 records only 47, with
  full exposure in all 336 cells; SKU-0011 records 300 with only 5 full-exposure
  cells. Low sales under availability and low sales under censoring need different
  interpretation. No missing demand is estimated here.
- Closing saleable stock in the selected stores on day 57 is
  119 units. This is a single-day snapshot,
  not a sum of balances across time or all-network inventory.

## Evidence and use

Run `python tools/reproduce.py` to regenerate SQLite and grouped results from the public CSVs using `sql/business_queries.sql`. Every grouped sales/count metric and daily stock snapshot
matches independent Python calculations from the observed input rows. The exported
data contains no missing expected cells, duplicates or orphan dimension keys.

The policy uses fixed target quantities, recurring supply and explicit cancellation
of unfilled supplier residuals. The final two days have finite-horizon transfer
boundary effects. All products are durable; one synthetic world and policy were
tested. This is not a representative retail sample, causal comparison, demand
estimate, financial analysis, training dataset or validation of future forecasts.
No price, revenue, savings, real date or additional simulated day was invented.

