# TC4-0 Boundary Audit

Repository: \`toootakeooot-bit/tradeplan-engine\`

Scope: STEP4-A / TC4-0 only

## Responsibility matrix

| Responsibility | ② TradePlan Engine | Downstream/common layer |
|---|---:|---:|
| Environment | YES | NO |
| Setup | YES | NO |
| Trigger | YES | NO |
| Entry plan | YES | NO |
| SL plan | YES | NO |
| TP plan | YES | NO |
| Wait | YES | NO |
| Invalidation | YES | NO |
| Account balance management | NO | YES |
| Monetary risk amount | NO | YES |
| Lot calculation | NO | YES |
| Position size | NO | YES |
| Order issue/execution | NO | YES |
| Open-position management | NO | YES |
| Ticket tracking | NO | YES |

## Engine separation audit

| Check | Result |
|---|---|
| Formal name is ② TradePlan Engine | PASS |
| Environment through TP is in scope | PASS |
| Wait / Invalidation included | PASS |
| Position sizing excluded | PASS |
| TC / NODA internal logic separated | PASS |
| NODA-specific rules injected into TC | NO |
| NODA implementation added | NO |
| TradePlanState marked provisional | PASS |
| TC raw retention layer defined | PASS |
| Future NODA directory reserved | PASS |

## Existing trade-plan-a boundary

TC4-0 does not modify \`toootakeooot-bit/trade-plan-a\`.

No W12, W8, or W9 file is part of this repository change.

The future connection is documented conceptually only; no integration code is added.

## Implementation audit

TC4-0 changes are documentation/specification only.

No:

- strategy implementation;
- adapter implementation;
- normalizer implementation;
- sizing implementation;
- execution implementation;
- performance evaluation

is introduced.

## Verdict

**TC4-0 responsibility definition: PASS**, subject to repository/branch SHA verification after commit.
