# Release QA evidence ? 2026-10-24

The approved analytical package's 27 artifact hashes were independently verified.
Python and SQLite reconcile 145 grouped rows, 2,688 cells and 5,272 fulfilled units.
Native static checks cover six pages, 72 visuals, 18 measures, three relationships,
109 field bindings and ten navigation targets.

The release launcher opened a prepared native runtime project in Windows Power BI
Desktop 2.159.883.0. DAX Studio 3.6.0 queried the actual loaded model: all 18 expected
total/filter-context values matched, including week 1/8, STORE-018 and SKU-0245.
The model's DataRoot was queried separately to verify the release-local CSV directory.
This is actual engine evidence, not a new visual interaction/Refresh-button test.

The supplied six owner-approved screenshots were visually inspected: native values
and page content are legible, with no visible personal paths, usernames or private
content. Screenshots were copied unchanged. They are historical source-rendering
evidence, not screenshots of a fresh clone.

The computer-use helper could not initialize (kernel assets path error). Thus new
interactive Refresh-button, navigation and slicer testing is
**MANUAL_RUNTIME_QA_REQUIRED**. Headless CI does not replace these checks. Previously
reported 11/11 Data Quality DAX checks are historical and are not the new test count.

Current automated test outcomes are obtained by the commands in README and by
GitHub Actions on each commit. External release reports retain execution logs and
remote-clone evidence; they are deliberately excluded from the public tree.
