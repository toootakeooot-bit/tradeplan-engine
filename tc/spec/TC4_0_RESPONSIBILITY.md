# TC4-0 — TradingCursor TradePlan Engine Responsibility

Status: **responsibility fixed for STEP4-A / TC4-0**

## Purpose

TC② evaluates TradingCursor's own analysis and decision capability as an independent TradePlan Engine.

The objective is not to make TradingCursor imitate NODA. The objective is to create a clean TC engine that can later be compared against NODA② under equivalent input conditions.

## TC② in scope

TC② owns:

1. Environment
2. Setup
3. Trigger
4. Entry
5. SL
6. TP
7. Wait / Invalidation

The engine may use TradingCursor-native analytical concepts and outputs necessary to produce that strategy plan.

## TC② out of scope

TC② does not own:

- account balance;
- chosen risk amount;
- risk-percent policy;
- lot;
- position size;
- order issue/placement;
- order execution;
- position management;
- ticket tracking;
- W8 / W9 changes.

## Anti-mixing rule

Do not force the following NODA-specific concepts into TC② decision logic:

- R01-R37
- 大ダウ
- 小ダウ
- 際
- 先行局面
- 本格局面
- 最終局面
- BR or other NODA-specific definitions

If a concept appears independently in TradingCursor's native output, preserve the raw output as TC-native evidence; do not relabel it as NODA logic.

## Output layering

TradingCursor native output is retained before normalization:

TC raw response
→ TCTradePlanRaw
→ TC Normalizer
→ TradePlanState (provisional)

No normalizer or adapter implementation is created in TC4-0.

## Branch rule

TC4-0 work is performed on \`feature/tc-v1\`.

It is not merged to \`main\` in this work.
