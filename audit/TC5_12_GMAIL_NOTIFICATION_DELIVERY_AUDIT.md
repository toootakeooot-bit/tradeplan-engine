# TC5-12 Gmail Notification Delivery Audit

Date: 2026-09-14
Branch: `feature/tc-v1`
Scope: notification/delivery only. TC4 and TC decision semantics unchanged.

## Finding

TC5-10/11 already produced a stable TC Spot result and separate runtime usage object, but there was no common notification contract for:

- Gmail delivery of Spot results;
- grouped Gmail delivery of periodic cycle results;
- durable pre-send persistence;
- duplicate prevention;
- Gmail-only retry after send failure.

A direct `TC -> Gmail` call without a durable notification id would risk duplicate email on restart. A naive retry that re-ran TC would also consume additional TradingCursor calls and could produce a different decision from the original notification attempt.

## Implemented boundary

Added a new `tc/notification` layer containing:

```text
model.py
formatter.py
outbox.py
delivery.py
```

The layer supports both `SPOT` and `PERIODIC` trigger types.

## Spot contract

```text
notification_id = tc:spot:<run_id>
one Spot run = one Gmail notification
```

Normal decision states and post-command runtime acquisition errors can be represented.

## Periodic contract

```text
notification_id = tc:periodic:<cycle_id>
one periodic cycle = one grouped Gmail notification
```

Multiple instruments are combined into one message. Per-symbol failures are represented as `ERROR` result records within the same cycle payload.

## Outbox and duplicate prevention

`FileNotificationOutbox` persists the payload before send and records:

```text
PENDING / SENT / FAILED
attempts
last_error
provider_message_id
```

The stable `notification_id` is hashed only for the filesystem filename; the original id remains inside the payload.

A notification already marked SENT is not sent again.

## Retry isolation

`retry_saved_notification(...)` receives only:

```text
notification_id
recipient
EmailSender
Outbox
```

It receives no TradingCursor client, TC planner, TC orchestrator or TC service object. Therefore a Gmail retry cannot trigger another TC acquisition by construction.

## Gmail credential boundary

No Gmail password, App Password, OAuth token, recipient address, or other credential is added to the repository.

`CallableEmailSender` is the ChatGPT/host adapter boundary for an authorized Gmail action.

## Runtime usage consistency

The notification payload receives the same TC5-11 `TCUsageRuntimeInfo` object used by the user-facing runtime display. Gmail formatting does not recalculate remaining calls.

## Periodic implementation limit

No autonomous periodic Scheduler exists in the current `tradeplan-engine` branch. The periodic notification builder/delivery contract is complete, but an existing external Scheduler must supply the cycle result set and invoke it.

This preserves TC5-10's on-demand ChatGPT host boundary rather than silently adding autonomous scheduling to the TC Spot runtime.

## Regression requirements

Tests cover:

- Spot subject/body content;
- runtime usage included in Spot email;
- grouped periodic multi-symbol message;
- partial periodic ERROR result;
- SENT idempotency / no duplicate send;
- FAILED state on Gmail error;
- Gmail-only retry from saved payload;
- payload round-trip through Outbox;
- Spot runtime ERROR email;
- existing TC4/TC5 regressions remain green.

## Non-change audit

No change to:

- TC4 Adapter or schemas;
- TradingCursor analysis prompts/responses;
- symbol/provider mapping;
- NORMAL/SHORT timeframe plans;
- aggregation/state mapping;
- Entry/SL/TP derivation;
- execution permission.
