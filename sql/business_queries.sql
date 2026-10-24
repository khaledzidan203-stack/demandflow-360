-- SQLite business views. Dataset: one declared 56-day synthetic pilot.
-- Fact grain: run_id/scenario_id/policy_id/day_index/store_id/sku_id.
-- Opening quantity is availability at demand fulfillment, AFTER scheduled receipts.
-- It is not necessarily the previous calendar day's closing inventory.
CREATE VIEW v_enriched AS
SELECT f.*, d.pilot_week_index, s.city_name, k.category
FROM fact_observed f
JOIN dim_day d USING(day_index)
JOIN dim_store s USING(store_id)
JOIN dim_sku k USING(sku_id);

CREATE VIEW v_daily AS
SELECT day_index, COUNT(*) AS cells, SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells,
 SUM(eod_saleable_qty) AS closing_store_units
FROM v_enriched GROUP BY day_index;

CREATE VIEW v_weekly AS
SELECT pilot_week_index, COUNT(*) AS cells, SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells
FROM v_enriched GROUP BY pilot_week_index;

CREATE VIEW v_store AS
SELECT store_id, COUNT(*) AS cells, SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells
FROM v_enriched GROUP BY store_id;

CREATE VIEW v_sku AS
SELECT sku_id, COUNT(*) AS cells, SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells
FROM v_enriched GROUP BY sku_id;

CREATE VIEW v_exposure AS
SELECT availability_status, COUNT(*) AS cells, SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells
FROM v_enriched GROUP BY availability_status;

CREATE VIEW v_totals AS
SELECT COUNT(*) AS cells, SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells,
 1.0*SUM(full_exposure_flag)/NULLIF(COUNT(*),0) AS full_exposure_rate,
 1.0*SUM(censored_flag)/NULLIF(COUNT(*),0) AS censored_rate,
 (SELECT closing_store_units FROM v_daily ORDER BY day_index DESC LIMIT 1)
   AS closing_store_units_last_day
FROM v_enriched;

CREATE VIEW v_sku_week AS
SELECT sku_id, pilot_week_index, COUNT(*) AS cells,
 SUM(gross_sales_qty) AS sales_units,
 SUM(full_exposure_flag) AS full_exposure_cells,
 SUM(censored_flag) AS censored_cells, SUM(no_exposure_flag) AS no_exposure_cells,
 SUM(eod_zero_stock_flag) AS eod_zero_cells, SUM(zero_sales_flag) AS zero_sales_cells
FROM v_enriched GROUP BY sku_id,pilot_week_index;

-- Reusable business queries (add WHERE filters to source views as appropriate):
SELECT * FROM v_daily ORDER BY day_index;
SELECT *, 1.0*full_exposure_cells/NULLIF(cells,0) AS full_exposure_rate
 FROM v_weekly ORDER BY pilot_week_index;
SELECT v.*, s.city_name FROM v_store v JOIN dim_store s USING(store_id)
 ORDER BY sales_units DESC,store_id;
SELECT v.*, k.category FROM v_sku v JOIN dim_sku k USING(sku_id)
 ORDER BY sales_units DESC,sku_id;
SELECT *, 1.0*cells/(SELECT cells FROM v_totals) AS cell_share
 FROM v_exposure ORDER BY availability_status;
SELECT * FROM v_totals;
