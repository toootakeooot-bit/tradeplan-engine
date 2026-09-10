# TC4-2 Raw Analysis Audit — TC4-2R reflected restart

Repository: `toootakeooot-bit/tradeplan-engine`  
Branch: `feature/tc-v1`  
Restart start HEAD: `be4835cabfa5d505d3c12d79c58c616f879ec0ac`

## Result

**PASS WITH NOTES**

Formal mode:

```text
survey_mode = TC_NATIVE_RAW_SURVEY
comparison_level = LEVEL_C
```

Formal run: `TC4-2-OANDA-XAUUSD-20260910-01`

## Hard Gate audit

| Hard Gate | Result | Evidence / note |
|---|---|---|
| Repository is tradeplan-engine | PASS | Correct repository. |
| Branch is feature/tc-v1 | PASS | Correct branch. |
| Started from TC4-2R HEAD | PASS | Restart baseline exactly `be4835ca...`. |
| survey_mode fixed | PASS | `TC_NATIVE_RAW_SURVEY`. |
| comparison_level fixed | PASS | `LEVEL_C`. |
| TradingCursor Native Analysis executed | PASS | OANDA / XAUUSD formal run. |
| D1 executed | PASS | `1D` completed. |
| H4 executed | PASS | `4h` completed. |
| H1 executed | PASS | `1h` completed. |
| M15 executed | PASS | `15m` completed. |
| 4TF Raw independently retained | PASS | Four separate Raw files. |
| Raw preserved before mapping | PASS | Raw files are separate from observation matrix. |
| source retained | PASS | OANDA. |
| symbol retained | PASS | XAUUSD. |
| interval retained | PASS | 1D / 4h / 1h / 15m. |
| model result retained | PASS | `qwen.qwen3-vl-235b-a22b` returned on all formal calls. |
| timestamp retained | PASS | Returned UTC timestamps retained. |
| chartId where available retained | PASS | Derived only from explicit Raw action_url query value and recorded in manifest. |
| Q1 Environment observed/classified | PASS | Per-TF mapping completed. |
| Q2 Setup observed/classified | PASS | Per-TF mapping completed. |
| Q3 Trigger observed/classified | PASS | 1h OBSERVED; other formal TFs NOT_PROVIDED. Missing values not filled. |
| Q4 Entry observed/classified | PASS | Explicit potentialPosition data. |
| Q5 SL observed/classified | PASS | Explicit stopLoss data. |
| Q6 TP observed/classified | PASS | Explicit takeProfits data. |
| Q7 Wait / Invalidation observed/classified | PASS | Wait and invalidation/alternative aspects kept distinct. |
| NOT_PROVIDED allowed | PASS | Used for absent Trigger / Wait sub-aspects. |
| AMBIGUOUS allowed | PASS | Contract retained; not forced where no ambiguity needed. |
| Raw and Question Mapping separated | PASS | Separate Raw and `observation_matrix.md`. |
| EXTRACT only for semantic mapping | PASS | No missing strategic field created. |
| LIGHT NORMALIZATION only for representation | PASS | No added strategic meaning. |
| INFERENCE absent | PASS | No indicator commentary promoted to Trigger without explicit pre-entry condition. |
| NODA rules injected | NO / PASS | No NODA terminology or rule logic supplied to TradingCursor. |
| Position Size promoted to common answer | NO / PASS | Raw advice retained but excluded as out of scope. |
| ChatGPT 4TF synthesis created | NO / PASS | Four TFs remain independent. |
| TradingCursor answer correctness scored | NO / PASS | No quality or outcome scoring. |
| LEVEL C described as fair NODA-vs-TC comparison | NO / PASS | Explicitly prohibited. |
| TC4-0 responsibility changed | NO / PASS | Responsibility baseline unchanged. |
| TC4-1 discarded | NO / PASS | TC4-1 remains; TC4-2R addendum governs LEVEL C survey use. |
| TCTradePlanRaw finalized | NO / PASS | Only candidate fields recorded. |
| Adapter / Normalizer implemented | NO / PASS | No implementation added. |
| trade-plan-a changed | NO / PASS | No writes performed to that repository. |
| main merged/changed by TC4-2 | NO / PASS | Work remains feature-only. |

## Formal Raw evidence

The formal native calls all returned `completed`:

- 1D: 2026-09-10T10:13:39.412Z, chartId `b03658c0-d0f8-431b-b819-87f841d54e7f`
- 4h: 2026-09-10T10:14:05.800Z, chartId `914e5b19-6c30-4e33-93bd-ff0a4fc1df57`
- 1h: 2026-09-10T10:14:36.173Z, chartId `db4c53c3-20c1-43e6-a2e8-d1f823a5f64a`
- 15m: 2026-09-10T10:15:01.090Z, chartId `37a6052b-8def-4837-8793-8006966c03af`

One additional 1h live-repeat call completed at 2026-09-10T10:15:30.706Z, chartId `a53a8f2f-940b-4c51-826f-b1810303e45f`.

## Question mapping audit

| Question | Formal observation conclusion |
|---|---|
| Q1 Environment | OBSERVED on all four TFs |
| Q2 Setup | OBSERVED on all four TFs |
| Q3 Trigger | OBSERVED on initial 1h only; NOT_PROVIDED on 1D/4h/15m |
| Q4 Entry | OBSERVED on all four TFs |
| Q5 SL | OBSERVED on all four TFs |
| Q6 TP | OBSERVED on all four TFs |
| Q7 Wait / Invalidation | OBSERVED on all four TFs through explicit wait and/or invalidation/alternative conditions; sub-aspects remain separate |

## Inference audit

Potential ambiguity was deliberately handled conservatively.

Indicator crossover, breakout, rejection or pullback wording was not automatically treated as an Entry Trigger. A Q3 Trigger was accepted only where the Raw explicitly prescribed waiting for a decisive break/volume confirmation before a long or an opposite break for a short.

No hidden reasoning sequence is claimed.

## Out-of-scope Raw content audit

The initial formal 1h Raw explicitly contains position-sizing advice. It is preserved verbatim in the Raw response file.

Mapping disposition:

```text
Raw: KEEP
Common Question mapping: EXCLUDE_OUT_OF_SCOPE
```

TC4-0 Position Sizing boundary therefore remains intact.

## Repeatability audit

Mode: `LIVE REPEATABILITY OBSERVATION`.

The formal 1h and repeat 1h runs used the same request identity but not a frozen market input. Observed differences include trend, entry price, SL, TP, pattern and entry timing/state. Both proposed LONG direction and confidence 0.65.

Classification: **VALUE_VARIATION**.

The cause is not attributed to model randomness because live market-data change cannot be separated from model output variation.

## Phase audit

- Phase A / Native Default Analysis: **EXECUTED**.
- Phase B / custom minimal trade-plan prompt: **NOT_SUPPORTED** by the confirmed interface; no pseudo-Phase-B output created.

## Handoff audit

Actual Raw evidence now supports TC4-3 if TC4-3 is scoped as:

**TC出力判断構造定義 / TC Observable Decision Structure**.

It does not support a claim about TradingCursor hidden internal reasoning order.

TC4-4 may use observed Raw fields as schema candidates, but no schema is finalized by TC4-2.

## Final audit verdict

**TC4-2 = PASS WITH NOTES**

**TC4-3 (Observable Decision Structure) = GO, but not started.**
