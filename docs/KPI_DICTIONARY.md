# KPI dictionary

Observed-only; one declared run. All 18 native DAX formulas are preserved.

| Measure | Native DAX |
|---|---|
| Observed Sales Units | `SUM(fact_observed[gross_sales_qty])` |
| Observed Cells | `COUNTROWS(fact_observed)` |
| Full Exposure Cells | `SUM(fact_observed[full_exposure_flag])` |
| Censored Cells | `SUM(fact_observed[censored_flag])` |
| No Exposure Cells | `SUM(fact_observed[no_exposure_flag])` |
| EOD Zero Cells | `SUM(fact_observed[eod_zero_stock_flag])` |
| Zero Sales Cells | `SUM(fact_observed[zero_sales_flag])` |
| Full Exposure Rate | `DIVIDE([Full Exposure Cells], [Observed Cells])` |
| Censored Exposure Rate | `DIVIDE([Censored Cells], [Observed Cells])` |
| No Exposure Rate | `DIVIDE([No Exposure Cells], [Observed Cells])` |
| EOD Zero Rate | `DIVIDE([EOD Zero Cells], [Observed Cells])` |
| Sales per Observed Cell | `DIVIDE([Observed Sales Units], [Observed Cells])` |
| Closing Store Units (Last Selected Day) | `CALCULATE(SUM(fact_observed[eod_saleable_qty]), KEEPFILTERS(dim_day[day_index] = MAX(dim_day[day_index])))` |
| Expected Cells | `COUNTROWS(VALUES(dim_day[day_index])) * COUNTROWS(VALUES(dim_store[store_id])) * COUNTROWS(VALUES(dim_sku[sku_id]))` |
| Duplicate Grain Rows | `[Observed Cells] - COUNTROWS(SUMMARIZE(fact_observed, fact_observed[day_index], fact_observed[store_id], fact_observed[sku_id]))` |
| Missing Cells | `MAX(0, [Expected Cells] - ([Observed Cells] - [Duplicate Grain Rows]))` |
| Observed Coverage Rate | `DIVIDE([Observed Cells] - [Duplicate Grain Rows], [Expected Cells])` |
| Zero Sales With Full Exposure | `CALCULATE([Zero Sales Cells], KEEPFILTERS(fact_observed[availability_status] = "FULL_EXPOSURE"))` |

Rates use ratios of counts. Closing stock is semi-additive over time. Expected cells assumes the complete selected day/store/SKU grid, not arbitrary future assortment. Full exposure plus censored equals all cells. No exposure is a subset of censored.

Required all-data values: 2,688 cells; 5,272 sales; 1,259 full; 1,429 censored; 1,080 no exposure; 1,541 zero sales; 119 closing units; 2,688 expected; zero missing/duplicates; 100% coverage; 461 zero sales with full exposure.

Contexts: week 1 sales 942; week 8 sales 438, full exposure 77, expected 336; STORE-018 sales 904; SKU-0245 sales 47.
