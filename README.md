# tradeplan-engine

Dedicated repository for **② TradePlan Engine**.

## Scope

The engine owns the strategy-decision chain:

Environment → Setup → Trigger → Entry → SL → TP → Wait / Invalidation

It does **not** own account balance management, risk amount selection, lot/position sizing, order execution, or open-position management.

## Engine separation

This repository is designed to host independent strategy engines behind common boundaries:

- TC②: TradingCursor TradePlan Engine
- NODA②: future NODA TradePlan Engine

The engines may share input conditions and a provisional common output interface, but their internal decision logic must remain independent.

Current TC work is isolated on \`feature/tc-v1\`. No TC implementation is merged to \`main\` during TC4-0.
