# TC5-12 — Gmail Host Binding

Status: **FIXED — AUTHENTICATED GMAIL SELF**

Date: 2026-09-14

## 1. Production recipient mode

The ChatGPT Host Gmail recipient binding is fixed as:

```text
recipient_mode = AUTHENTICATED_GMAIL_SELF
```

The Host resolves the currently authenticated/connected Gmail profile at delivery time and sends the TC notification to that same Gmail account.

The literal email address is deliberately **not** stored in this repository.

This prevents account identifiers and Gmail credentials from becoming TC strategy/configuration state and allows the connected Gmail account to remain the single source of truth for the actual destination.

## 2. Scope

This binding applies to both:

```text
TC Spot
TC Periodic
```

Spot remains the TC5-10 ChatGPT On-Demand Host path.

Periodic remains the existing external periodic chain. The current production periodic integration is:

```text
Trade Plan A W10 Scheduler
-> GitHub [A-W10-EVENT]
-> existing single ChatGPT W10 consumer
-> TC processing
-> grouped TC periodic notification
-> AUTHENTICATED_GMAIL_SELF
```

No second W10 consumer or second PC Scheduler is introduced by this binding.

## 3. Delivery order

```text
TC result fixed
-> notification payload fixed
-> outbox PENDING
-> resolve authenticated Gmail profile
-> send to same authenticated Gmail account
-> SENT / FAILED
```

Gmail resolution or send failure is notification failure only. It must not alter TC state or trigger TradingCursor/provider acquisition again.

## 4. Periodic send unit

Each accepted periodic source cycle produces at most one successfully delivered grouped Gmail message.

The message groups all supported contexts in that W10 cycle rather than sending one email per instrument.

Accepted operational handling includes:

- normal completed cycle -> one grouped result email;
- partial cycle -> one grouped PARTIAL email;
- source W10 ERROR/unusable cycle -> zero provider calls and one ERROR email;
- accepted scheduled slot with no eligible W10 event -> zero provider calls and one NO_EVENT email;
- manual-test/outside-window invocation -> no periodic Gmail.

## 5. Periodic idempotency

```text
notification_id = tc:periodic:<cycle_key-or-event_id>
```

A SENT marker for the same notification id prohibits another Gmail send.

FAILED retry uses the stored notification payload only and performs zero TradingCursor/provider calls.

## 6. Spot idempotency

```text
notification_id = tc:spot:<run_id>
```

A completed Spot TC result is sent through the same authenticated-self Gmail binding.

A Gmail retry must use the saved Spot payload only. It must not repeat the Spot TC analysis.

## 7. Credentials and privacy boundary

The repository must not contain:

- Gmail password;
- App Password;
- OAuth access/refresh token;
- literal production recipient email address.

The Host connector/account binding supplies Gmail authorization and resolves the actual authenticated address at runtime.

## 8. Live binding qualification

The Gmail Host path was live-qualified on 2026-09-14 by resolving the connected Gmail profile and successfully delivering a self-addressed TC notification connection test.

The qualification proves the ChatGPT Host can resolve the authenticated Gmail identity and complete a Gmail send without placing credentials or the literal production address in this repository.

This test did not invoke TradingCursor and did not alter any Trade State.
