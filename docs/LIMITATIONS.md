# Scientific and operational limitations

**Synthetic 56-day descriptive pilot ? NOT TRAINING APPROVED.**

- Sales are fulfilled units, not latent demand. Neither censoring nor closing zero
  stock reveals the quantity of unmet demand. No such quantities are exported.
- One synthetic world, one fixed-target recurring policy, six stores and eight
  durable SKUs are a bounded descriptive example, not a representative population.
- Finite-window transfer effects affect the last two days. PO residuals were explicitly
  cancelled at receipt in the generating scenario. No policy superiority is inferred.
- Full exposure and censored observations must remain distinct. A no-exposure zero
  is not evidence of no demand. Full-exposure zero sales are counted separately.
- Store closing stock applies to the last selected simulation day; it is not total
  network stock, a flow or a sum over time. This public export is not a movement ledger.
- No forecast training, rolling-origin results, economic optimization, savings or
  production integration are certified by this release.
- The expected-cell DAX assumes this complete single-run grid. Do not append sparse,
  closed/ineligible periods or additional runs without redesigning its denominator.
- Automated/static checks cannot prove live visual interaction. See QA_EVIDENCE.md.
