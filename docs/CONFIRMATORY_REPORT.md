# Confirmatory Report — Study 1 ABM batch

Executed per docs/PREREGISTRATION.md at freeze commit `36d5ac6724d524905d0aa356952286ec3e129b8e`.
Master seed 314159265; 200 pairs/cell; validation: PASS.

## Preregistered verdicts

| hypothesis                                         |   estimate |     ci_lo |    ci_hi | verdict   |
|:---------------------------------------------------|-----------:|----------:|---------:|:----------|
| H4 interaction (participation_rate)                |  0.107135  | 0.0961169 | 0.118825 | SUPPORTED |
| H1 access effect, constrained (participation_rate) |  0.232662  | 0.223962  | 0.241063 | SUPPORTED |
| H1 access effect, abundant (participation_rate)    |  0.339797  | 0.331952  | 0.347828 | SUPPORTED |
| H4 interaction (output_norm)                       |  0.0836418 | 0.0549338 | 0.112523 | SUPPORTED |
| H2 access effect, constrained (output_norm)        |  0.218246  | 0.198949  | 0.238124 | SUPPORTED |
| H2 access effect, abundant (output_norm)           |  0.301888  | 0.28074   | 0.323796 | SUPPORTED |

**Manipulation check:** PASS (influence concentration higher in concentrated cells; access effect on both concentration indices negative with CI excluding zero).

**Falsification arms:** PASS (mechanism-blind policies show |access effect| < 0.03 on participation).

## Cell means

| resources   | access       |      mean |        std |   count | outcome            |
|:------------|:-------------|----------:|-----------:|--------:|:-------------------|
| abundant    | broad        | 0.698016  | 0.0381695  |     200 | participation_rate |
| abundant    | concentrated | 0.358219  | 0.0418927  |     200 | participation_rate |
| constrained | broad        | 0.558724  | 0.0406905  |     200 | participation_rate |
| constrained | concentrated | 0.326063  | 0.0448804  |     200 | participation_rate |
| abundant    | broad        | 0.612377  | 0.12947    |     200 | output_norm        |
| abundant    | concentrated | 0.310489  | 0.0819861  |     200 | output_norm        |
| constrained | broad        | 0.554656  | 0.113519   |     200 | output_norm        |
| constrained | concentrated | 0.33641   | 0.0871433  |     200 | output_norm        |
| abundant    | broad        | 0.0955625 | 0.0272312  |     200 | influence_gini     |
| abundant    | concentrated | 0.84085   | 0.0202872  |     200 | influence_gini     |
| constrained | broad        | 0.150857  | 0.0408678  |     200 | influence_gini     |
| constrained | concentrated | 0.808073  | 0.0344783  |     200 | influence_gini     |
| abundant    | broad        | 0.004775  | 0.00271409 |     200 | influence_nhhi     |
| abundant    | concentrated | 0.831238  | 0.0746397  |     200 | influence_nhhi     |
| constrained | broad        | 0.0116483 | 0.00607922 |     200 | influence_nhhi     |
| constrained | concentrated | 0.719074  | 0.0926084  |     200 | influence_nhhi     |

## All preregistered contrasts

| outcome            | contrast                  |   estimate |       ci_lo |       ci_hi | excludes_zero   |
|:-------------------|:--------------------------|-----------:|------------:|------------:|:----------------|
| participation_rate | access_effect_constrained |  0.232662  |  0.223962   |  0.241063   | True            |
| participation_rate | access_effect_abundant    |  0.339797  |  0.331952   |  0.347828   | True            |
| participation_rate | resource_effect           |  0.0857236 |  0.0800434  |  0.0912616  | True            |
| participation_rate | interaction               |  0.107135  |  0.0961169  |  0.118825   | True            |
| output_norm        | access_effect_constrained |  0.218246  |  0.198949   |  0.238124   | True            |
| output_norm        | access_effect_abundant    |  0.301888  |  0.28074    |  0.323796   | True            |
| output_norm        | resource_effect           |  0.0159002 |  0.00208072 |  0.0303     | True            |
| output_norm        | interaction               |  0.0836418 |  0.0549338  |  0.112523   | True            |
| influence_gini     | access_effect_constrained | -0.657216  | -0.664416   | -0.649624   | True            |
| influence_gini     | access_effect_abundant    | -0.745288  | -0.749964   | -0.74069    | True            |
| influence_gini     | resource_effect           | -0.0112587 | -0.015495   | -0.00673463 | True            |
| influence_gini     | interaction               | -0.0880718 | -0.0967999  | -0.0795645  | True            |
| influence_nhhi     | access_effect_constrained | -0.707425  | -0.719851   | -0.694518   | True            |
| influence_nhhi     | access_effect_abundant    | -0.826463  | -0.836631   | -0.816303   | True            |
| influence_nhhi     | resource_effect           |  0.0526454 |  0.0447603  |  0.0607803  | True            |
| influence_nhhi     | interaction               | -0.119037  | -0.13557    | -0.103156   | True            |

## Standardized effects

| outcome            | resources   |   cohens_d_access |
|:-------------------|:------------|------------------:|
| participation_rate | constrained |           5.43136 |
| participation_rate | abundant    |           8.47916 |
| output_norm        | constrained |           2.1567  |
| output_norm        | abundant    |           2.78595 |

## Robustness and falsification arms (participation_rate)

| outcome            | contrast               |   estimate |       ci_lo |     ci_hi | excludes_zero   | arm                  |
|:-------------------|:-----------------------|-----------:|------------:|----------:|:----------------|:---------------------|
| participation_rate | access_effect_abundant | 0.354167   |  0.336237   | 0.371669  | True            | attention_on         |
| participation_rate | interaction            | 0.0684258  |  0.0439227  | 0.0931717 | True            | attention_on         |
| participation_rate | access_effect_abundant | 0.201771   |  0.17687    | 0.224901  | True            | modal_decider        |
| participation_rate | interaction            | 0.0406564  |  0.00692959 | 0.0719497 | True            | modal_decider        |
| participation_rate | access_effect_abundant | 0.354167   |  0.336237   | 0.371669  | True            | free_participation   |
| participation_rate | interaction            | 0.0311922  |  0.00438947 | 0.0604413 | True            | free_participation   |
| participation_rate | access_effect_abundant | 0.0046875  | -0.0100026  | 0.0189635 | False           | policy_random        |
| participation_rate | interaction            | 0.00506197 | -0.0162784  | 0.0241489 | False           | policy_random        |
| participation_rate | access_effect_abundant | 0.00416667 | -0.020526   | 0.0294818 | False           | policy_material_only |
| participation_rate | interaction            | 0.0034378  | -0.027901   | 0.0362166 | False           | policy_material_only |

## Reproduction

```bash
uv run python scripts/confirmatory.py
```
Run-level data: `data/confirmatory_run_summary.csv`. Event logs regenerate
deterministically from the recorded seeds in `configs/confirmatory.toml`.