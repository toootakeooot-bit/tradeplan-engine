# Status Definition

Status: **provisional**

TC4-0 fixes semantic requirements, not the final enum set.

A future TradePlanState status model must be able to distinguish at minimum:

- a plan that is still waiting for setup/trigger/entry conditions;
- a plan whose entry conditions are satisfied or otherwise actionable at the strategy-decision layer;
- a plan that has been invalidated;
- an unavailable/invalid/error result when the engine cannot produce a usable plan.

## Wait

WAIT is a legitimate TradePlan Engine outcome.

It means the strategy-side conditions required to proceed are not currently satisfied. WAIT must not be converted downstream into an automatic entry.

## Invalidation

Invalidation is also a first-class strategy outcome.

It records the condition under which the current setup or trade plan is no longer valid.

## No sizing implication

Status values must not directly decide lot, monetary risk, or position size.

Those remain downstream common responsibilities.
