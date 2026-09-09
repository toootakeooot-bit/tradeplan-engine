# Input Contract

Status: **conceptual / not final**

TC4-0 fixes only the responsibility boundary of the input, not a final transport schema.

## Common input condition

Both future NODA② and TC② are intended to receive equivalent market context for the same symbol and observation time, centered on:

- D1
- H4
- H1
- M15

The concrete payload may later contain screenshots, derived market data, metadata, or references to prepared artifacts.

## Boundary

The TradePlan Engine consumes **prepared market input**.

Acquisition and transport concerns are outside the strategy-decision responsibility unless explicitly assigned by a later interface specification.

TC4-0 therefore does not define MT4 startup, profile switching, screenshot capture, Drive storage, ticket retrieval, or scheduler behavior as TradePlan Engine responsibilities.

## Separation requirement

The input contract must not inject NODA strategy rules into TC② or TC strategy rules into NODA②.

Shared input means shared observation conditions, not shared internal reasoning.
