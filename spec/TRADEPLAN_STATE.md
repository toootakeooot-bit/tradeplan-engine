# TradePlanState

Status: **PROVISIONAL — not final**

NODA② is not yet defined, so the common output interface must remain provisional during TC4-0.

## Required layering

TC-specific information must not be discarded prematurely.

The required conceptual flow is:

TC raw response
→ TCTradePlanRaw
→ TC Normalizer
→ TradePlanState (provisional)

## TCTradePlanRaw

TCTradePlanRaw is the engine-specific retention layer.

Its purpose is to preserve TradingCursor-native output and evidence before common normalization.

TC4-0 does not finalize its field schema.

## TradePlanState

TradePlanState is the provisional common interface intended to connect either TC② or future NODA② to common downstream validation and sizing.

At the responsibility level, it must be able to represent the strategy-decision outputs for:

- Environment
- Setup
- Trigger
- Entry
- SL
- TP
- Wait / Invalidation

It must not contain authority for:

- account risk policy;
- monetary risk amount selection;
- lot calculation;
- position sizing;
- broker order execution;
- open-position management.

## Finalization rule

Do not finalize TradePlanState solely around TradingCursor.

Its final common schema must be reviewed again after NODA② requirements are known, so that the interface remains genuinely common rather than TC-shaped.
