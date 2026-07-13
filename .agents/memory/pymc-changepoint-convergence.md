---
name: PyMC discrete change-point convergence
description: Sampling settings that reliably converge a single discrete change-point (switch-point) model in PyMC on ~10k daily observations.
---

A classic single change-point model (`DiscreteUniform` switch index `tau`,
before/after `Normal` means, before/after `HalfNormal` sigmas, connected via
`pm.math.switch`) on a series of ~10,000 daily log returns is tractable but
convergence is sensitive to sampler settings:

- `draws=1000, tune=1000, chains=4, cores=4, target_accept=0.9` produced
  `max r_hat = 1.01` — borderline (the usual `< 1.01` rule of thumb reads
  this as *not* converged).
- `draws=2000, tune=2000, chains=4, cores=4, target_accept=0.95` cleanly
  produced `max r_hat = 1.00` on the same data, in ~30s total (multi-core).

**Why:** PyMC assigns Metropolis to the discrete `tau` and NUTS to the
continuous params (a `CompoundStep`); Metropolis on a ~10k-index discrete
parameter needs more tuning/draws than NUTS alone to mix well.

**How to apply:** For a single discrete change-point model on a similarly
sized series, start at `draws=2000, tune=2000, target_accept=0.95` rather
than the "default" 1000/1000 — it costs only a few more seconds but avoids
a borderline convergence report.
