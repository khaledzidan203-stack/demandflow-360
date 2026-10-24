# Power BI reviewer guide

Launch using `python launch_powerbi.py` or the CMD entry point. DataRoot is the
existing TMDL parameter, used by all four Csv.Document/File.Contents imports.
Only its single canonical string is rebased in a unique ignored runtime copy.
Power Query is given an absolute local data directory; implicit relative-path
resolution is not assumed. Native siblings and PBIP/PBIR links are retained.

The five model tables comprise four imports plus `_Measures`, an empty structural
measure host with 18 measures. Three active single-direction relationships connect
Day, Store and SKU to the observed fact. No calendar dates are invented. Day indices
and pilot-week labels are analytical blocks, not ISO weeks or real weekdays.

After opening select Home > Refresh. A launch message only confirms the open
request. If Python is missing, install Python 3.11+; if PBIP association is missing,
install/update Microsoft Power BI Desktop. Extract ZIP fully before launching.
A changed or missing CSV must be restored from the release; do not edit its hash
to bypass validation. If model source is intentionally changed, review native pins
and regression evidence as a new release.

Use Ctrl+click on INDEX/HOME buttons in Desktop edit mode. Test slicers and empty
filter contexts separately. Required totals and contexts appear in KPI_DICTIONARY.
The initial saved page is the owner's Data Quality page; INDEX remains available.

Three obsolete sort references to a nonexistent donor calendar were corrected only
in the release copy: two weekly charts sort by their existing pilot_week_label
axis, one daily chart by day_index. No layout, theme, DAX, slicer or data change was
made. All other native bytes except DataRoot are preserved from the supplied source.

New interactive UI acceptance is MANUAL_RUNTIME_QA_REQUIRED. Genuine supplied
screenshots and actual release-time engine checks have different evidence scopes.
