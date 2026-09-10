# TC4-2P GO / NO-GO

Status: **PASS WITH LIMITATION**

## Decision summary

TC4-2P successfully fixed the observable capability boundary of the current TradingCursor callable path.

The path is sufficient for a **LEVEL C live-native Raw behavior survey**.

It is not yet sufficient to satisfy the original TC4-2 fixed-Market-Input Hard Gate for direct NODA② / TC② comparison.

## What is now confirmed

- `OANDA / XAUUSD` can be analyzed successfully.
- D1 / H4 / H1 / M15 can each be requested separately.
- native Raw JSON can be captured before classification.
- model and completion timestamp can be retained.
- a chart identifier can be traced from the returned TradingCursor action URL.
- TC analysis can be observed without injecting NODA rules.

## What remains unavailable or unproven

- caller-supplied fixed chart-image input;
- direct `artifact_ref` consumption;
- simultaneous D1/H4/H1/M15 input;
- free prompt input;
- Phase B through the current callable path;
- exact artifact replay;
- a frozen cross-timeframe observation state that can be certified as the same input for NODA② and TC②.

## comparison_mode decision

### `STRICT_SAME_ARTIFACT`

NO-GO with current callable TradingCursor path.

### `SAME_MARKET_OBSERVATION`

HOLD until a shared/frozen observation mechanism is demonstrated.

### LEVEL C live-native survey

GO only for TradingCursor Raw schema/behavior investigation. This is an observation mode, not a valid direct-comparison mode.

## TC4-2 restart decision

### Original TC4-2 as currently specified

**HOLD**

Reason: its Hard Gate requires a fixed Market Input and direct reuse/comparability that the current callable path cannot yet certify.

### Limited Raw survey

Technically **GO** if created as an explicitly separate or amended scope that permits LEVEL C native live observations solely to learn TradingCursor Raw structure and field behavior.

Such a survey must not be labeled as satisfying the original fixed-input comparison requirement.

## Recommended next control decision

Before resuming formal TC4-2, choose one of two controlled paths:

1. verify another TradingCursor route (UI/browser/integration) that can consume a frozen artifact or frozen observation; or
2. formally amend the TC4-2 experiment design so that LEVEL C Raw-structure survey is separated from later LEVEL A/B comparison work.

TC4-2P itself does not make either change automatically.

## Final verdict

- TC4-2P: **PASS WITH LIMITATION**
- formal TC4-2 restart: **HOLD**
- TC4-3: **HOLD**
- main merge: **NO**
