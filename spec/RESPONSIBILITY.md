# ② TradePlan Engine Responsibility

Status: **TC4-0 responsibility baseline**

## 1. Formal name

The formal name of component ② is:

**TradePlan Engine**

It is not limited to environment recognition. It owns the complete strategy-decision chain from environment assessment through take-profit planning.

## 2. In scope

② TradePlan Engine is responsible for:

1. **Environment**
   - assess market environment from the supplied D1 / H4 / H1 / M15 inputs;
   - identify directional, structural, volatility, momentum, support/resistance, or other engine-native context as applicable.

2. **Setup**
   - determine whether a trade setup exists under the selected engine's own logic;
   - describe the setup without importing logic from another engine.

3. **Trigger**
   - define the event or condition that must occur before an entry becomes valid;
   - distinguish an observed setup from an activated trigger.

4. **Entry**
   - produce the intended direction and entry condition/zone/level when supported by the engine;
   - permit no-entry outcomes.

5. **SL**
   - provide the stop-loss plan and the strategy-side reason or invalidation basis.

6. **TP**
   - provide the take-profit plan and the strategy-side reason.

7. **Wait / Invalidation**
   - explicitly represent waiting conditions, no-trade states, and conditions that invalidate the active trade plan.

The responsibility boundary is therefore:

**Environment → Setup → Trigger → Entry → SL → TP → Wait / Invalidation**

## 3. Out of scope

② TradePlan Engine must not perform:

- account balance management;
- selection of monetary risk amount;
- risk-percent policy;
- lot calculation;
- position-size calculation;
- broker order creation;
- order execution;
- order modification or close execution;
- open-position lifecycle management;
- ticket tracking;
- W8 / W9 modification or ownership.

These responsibilities belong to future common Validator / Risk / Sizing / Execution / Position Management layers.

In particular, **TC② must not decide Position Size**.

## 4. TC② / NODA② separation principle

TC② and NODA② are separate strategy engines.

They may share:

- the same supplied input conditions;
- a provisional common TradePlanState interface;
- common validation outside the strategy engine.

They must not share or blend internal strategy logic.

TC② must not be forced to apply NODA-specific concepts such as R01-R37, 大ダウ, 小ダウ, 際, 先行局面, 本格局面, 最終局面, or BR.

NODA② is reserved for future work and is not implemented during TC4-0.

## 5. Relationship to trade-plan-a

The existing repository \`toootakeooot-bit/trade-plan-a\` remains outside this TC4-0 work.

During TC4-0:

- no file in \`trade-plan-a\` is modified;
- no W12 file is modified;
- no W8 / W9 behavior is modified;
- no responsibility is moved from \`trade-plan-a\` into this repository by implementation.

The intended future integration boundary is:

prepared market input → TradePlan Engine → provisional TradePlanState → common Validator / Sizing / Execution.

The integration mechanism itself is not implemented in TC4-0.

## 6. TC4-0 non-goals

TC4-0 does not:

- optimize TradingCursor prompts or strategy logic;
- implement a TC adapter or normalizer;
- implement NODA logic;
- implement sizing or execution;
- evaluate trading performance;
- merge TC work into main.
