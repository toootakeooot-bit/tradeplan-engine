# TC4-1 Input Audit

Repository: \`toootakeooot-bit/tradeplan-engine\`

Branch: \`feature/tc-v1\`

Start HEAD: \`6879cdbc4f23d42fcf3034644b9799b7205a0391\`

Scope: input specification only.

## Hard Gate

| Gate | Result | Evidence |
|---|---|---|
| TC② minimum required input defined | PASS | \`spec/INPUT_CONTRACT.md\` sections 2-3 |
| D1/H4/H1/M15 conditions defined | PASS | section 6 |
| Symbol identification defined | PASS | section 4 |
| Observation/capture tracking defined | PASS | sections 5 and 7 |
| Same input set replayable | PASS | section 9 |
| Same conditions usable by NODA② / TC② | PASS | section 10 |
| REQUIRED / OPTIONAL / FORBIDDEN explicit | PASS | section 3 |
| NODA rules absent from TC input logic | PASS | forbidden leakage rules |
| Trading outcomes / answer labels excluded | PASS | forbidden leakage rules |
| Capture vs TradePlan Engine responsibility separated | PASS | sections 8 and 11 |
| Position sizing information excluded | PASS | sections 3 and 11 |
| No unsupported numeric threshold added | PASS | time/freshness thresholds remain TBD |
| \`trade-plan-a\` modified | NO | no operation performed against that repository |
| main merged/modified by TC4-1 | NO | TC4-1 commit is restricted to \`feature/tc-v1\` |

## Required input audit

Required top-level fields:

- \`input_set_id\`
- \`symbol\`
- \`observation_timestamp\`
- D1
- H4
- H1
- M15

Required per-timeframe fields:

- \`timeframe\`
- \`artifact_ref\`
- \`capture_timestamp\`
- \`source_id\`

## Optional input audit

Optional non-strategy metadata:

- \`canonical_symbol\`
- \`broker\` / \`broker_id\`
- \`artifact_hash\`
- \`capture_session_id\`
- \`artifact_metadata\`
- \`source_metadata\`

## Forbidden input audit

Forbidden strategy leakage / downstream data includes:

- LONG / SHORT recommendation;
- Entry / SL / TP answer information;
- NODA evaluation / rules result;
- previous TC analysis result;
- future outcome or realized trading result;
- account/risk/lot/position-size information;
- execution and position-management instructions.

## Threshold audit

TC4-1 intentionally does not introduce unsupported numeric limits for:

- capture-to-capture time spread;
- maximum age/freshness.

Both remain TBD pending evidence.

## Responsibility audit

No change is made to the TC4-0 responsibility chain:

Environment → Setup → Trigger → Entry → SL → TP → Wait / Invalidation

No strategy analysis implementation is introduced.

## Verdict

**TC4-1: PASS**, subject to final branch/commit verification after commit.
