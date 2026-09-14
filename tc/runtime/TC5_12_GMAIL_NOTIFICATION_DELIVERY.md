# TC5-12 — Gmail Notification Delivery

Status: **ACTIVE TC5 NOTIFICATION CONTRACT**

Date: 2026-09-14

## 1. Purpose

TC5-12 adds one common Gmail notification layer for both:

```text
TC Spot
TC Periodic
```

The notification layer is downstream of TC analysis. It must never influence TradingCursor acquisition, TradePlanState construction, Trade State, or execution permission.

## 2. Architecture

```text
TC Spot
  -> TradePlanState
  -> runtime_usage
  -> TCNotificationPayload
  -> durable Outbox
  -> Gmail Adapter

TC Periodic
  -> one cycle result set
  -> cycle runtime_usage
  -> one TCNotificationPayload
  -> durable Outbox
  -> Gmail Adapter
```

Spot and Periodic share the same payload, formatter, outbox, idempotency and delivery-state contract.

The trigger source remains separate:

- Spot is ChatGPT On-Demand Host under TC5-10;
- Periodic is initiated by an external Scheduler/periodic host;
- TC5-12 does not turn TC5-10 into an autonomous scheduler.

## 3. Send unit

### 3.1 Spot

One completed Spot run produces exactly one notification id and at most one successfully delivered Gmail message.

```text
notification_id = tc:spot:<run_id>
```

Successful TRADE/WAIT/HOLD/INVALID results are sent.

A Native/runtime failure after a valid Spot command is also eligible for an ERROR notification.

Command syntax/validation failures before a TC run is established are not Gmail notifications.

### 3.2 Periodic

One periodic cycle produces exactly one grouped Gmail message, not one message per symbol.

```text
notification_id = tc:periodic:<cycle_id>
```

Example four-instrument cycle:

```text
GOLD
USDJPY
US100
JP225
```

All successful states and per-symbol runtime failures are grouped in one payload.

Partial acquisition failure is represented as mixed normal results plus `ERROR` result(s).

If all periodic results fail, the same one-cycle notification is sent as an all-error notification.

## 4. Notification model

```text
TCNotificationPayload
  notification_id
  trigger_type       SPOT / PERIODIC
  run_id              Spot run id or periodic cycle id
  timestamp
  results[]
  runtime_usage
  runtime_error
```

Each result may contain:

```text
symbol
status               TRADE / WAIT / HOLD / INVALID / ERROR
direction
profile
environment
setup
entry_price
stop_loss
take_profits
invalidation
used_timeframes
provider
provider_symbol
execution_permission
runtime_error
```

Notification delivery state is persisted in an envelope:

```text
PENDING
SENT
FAILED
```

with:

```text
attempts
last_error
provider_message_id
```

## 5. Gmail formatting

### 5.1 Spot subject

```text
[TC Spot][<symbol>][<status>][<profile>] YYYY-MM-DD HH:MM JST
```

Example:

```text
[TC Spot][US100][WAIT][NORMAL] 2026-09-14 20:15 JST
```

### 5.2 Periodic subject

```text
[TC定期][TRADE:n WAIT:n HOLD:n INVALID:n ERROR:n] YYYY-MM-DD HH:MM JST
```

Zero-count states may be omitted from the compact subject.

### 5.3 Body

The email body preserves the TC result only. It may include:

- canonical symbol;
- profile;
- status and direction;
- Environment / Setup;
- Entry / SL / TP / Invalidation;
- used timeframes;
- provider route;
- TC5-11 runtime usage block;
- Run ID / Notification ID;
- explicit `Execution Permission: NO` when execution is not authorized.

No web price, web analysis, NODA inference, or missing Entry/SL/TP fabrication may be inserted by Gmail formatting.

## 6. Outbox-first delivery

The payload MUST be saved before attempting Gmail delivery.

```text
TC result fixed
-> build TCNotificationPayload
-> Outbox PENDING
-> Gmail send
-> SENT or FAILED
```

This preserves the exact result that was intended for delivery.

## 7. Idempotency / duplicate prevention

`notification_id` is the idempotency key.

If an Outbox record is already `SENT`, another delivery request for the same id MUST return the existing SENT record without sending another email.

This protects against:

- repeated ChatGPT host steps;
- process restart;
- scheduler restart;
- repeated delivery function calls.

## 8. Gmail failure and retry rule

A Gmail failure must never re-run TC analysis.

Forbidden:

```text
Gmail FAILED
-> TradingCursor acquisition again
-> new TradePlanState
-> Gmail retry
```

Required:

```text
Gmail FAILED
-> Outbox FAILED with saved TCNotificationPayload
-> retry_saved_notification(notification_id)
-> Gmail only
```

The retry API intentionally accepts no TradingCursor client, TC planner, or TC service object.

Gmail failure does not change TRADE/WAIT/HOLD/INVALID or any Entry/SL/TP field.

## 9. Runtime usage consistency

TC5-11 `runtime_usage` is passed into the notification payload directly.

The Gmail layer MUST NOT recalculate TC usage independently.

Therefore ChatGPT display and Gmail use the same source object for:

```text
今回消費
予定を抜いた残り
スポット換算
次回リセット
```

## 10. Host/Gmail adapter boundary

The repository does not store Gmail passwords, App Passwords, OAuth refresh tokens, or other Gmail credentials.

The notification layer exposes a host-injected EmailSender contract:

```text
send_email(to, subject, body)
```

For ChatGPT Spot operation, the connected Gmail action may be bound through `CallableEmailSender`.

For periodic operation, the periodic host/Scheduler must bind an authorized email sender to the same contract.

Recipient configuration is external to the TC repository and must not be hard-coded into TC strategy/state files.

## 11. Periodic integration boundary

The current `tradeplan-engine` branch contains no autonomous TC periodic Scheduler implementation. TC5-12 therefore implements the complete periodic notification payload/format/outbox/delivery contract, but does not invent a new scheduler inside TC5-10.

The periodic host only needs to supply:

```text
cycle_id
timestamp
tradeplan_states[]
runtime_errors{}
cycle runtime_usage
recipient
EmailSender
```

Then one cycle can be delivered through the common Gmail layer.

## 12. Execution boundary

Email is information delivery only.

```text
Gmail sent != order permission
Gmail sent != automatic execution
TRADE email != broker order
```

TC5 execution permission remains unchanged.
