# TC Engine v1 Change Policy

Status: **TC4-9 post-freeze change-control baseline**

## 1. Purpose

This policy governs changes to the TC Engine v1 specification baseline after TC4-9. It is intentionally small: it prevents silent drift without creating a large governance process.

The policy applies to artifacts classified as `FIXED` in `tc/spec/TC_V1_BASELINE_MANIFEST.md`.

## 2. Core rule

A FIXED TC v1 artifact must not be silently edited after the freeze.

Any proposed change must answer, at minimum:

```text
Why is the change needed?
Which frozen artifacts are affected?
Does TCTradePlanRaw compatibility change?
Does TCREG behavior change?
Does Adapter responsibility change?
Does Mapping/State meaning change?
Does Common/NODA compatibility change?
Does versioning change?
```

## 3. Minimum change procedure

1. **Change request**
   - state the concrete problem/evidence;
   - identify whether it is provider-interface change, bug, evidence expansion, Common/NODA alignment, or implementation need.

2. **Baseline identification**
   - record the current TC Engine v1 Freeze Point SHA;
   - list affected FIXED/PROVISIONAL/TBD artifacts.

3. **Impact assessment**
   - responsibility boundary impact;
   - Native Interface impact;
   - Raw preservation/schema impact;
   - Mapping impact;
   - State Semantics impact;
   - Adapter/failure-boundary impact;
   - regression impact;
   - Common/NODA impact;
   - production implementation impact.

4. **Regression assessment**
   - run or re-check applicable TCREG cases;
   - do not rewrite a failing expected result merely to make implementation pass;
   - if semantics intentionally change, create an explicit new regression baseline and explain why.

5. **Schema compatibility decision**
   - if TCTradePlanRaw changes, classify backward compatibility and decide schema-version impact;
   - never silently modify `tc_tradeplan_raw.schema.json` because a provider field cannot be represented.

6. **Common/NODA review**
   - any change to provisional Common Mapping or TC provisional state names must be reviewed against current NODA/Common work;
   - TC must not be rewritten into NODA-specific logic merely for symmetry.

7. **Version decision**
   - retain TC Engine v1 label for compatible clarifications/additive evidence where appropriate;
   - create a new baseline/version when fixed semantics or contracts materially change;
   - preserve TCTradePlanRaw's own versioning rules independently.

8. **Explicit approval**
   - do not treat proposed changes as effective until the change work explicitly approves them.

9. **New baseline**
   - record new commit SHA, changed artifacts, regression result, and unresolved items;
   - preserve prior audit/history rather than rewriting it.

## 4. Change classes

### A. Documentation clarification

No data shape or semantic behavior changes.

Required checks:
- confirm no TCREG expectation changes;
- confirm no responsibility change;
- record reason.

### B. Native Interface change

Examples:
- TradingCursor adds/removes request fields;
- image/snapshot/free-prompt capability becomes actually available;
- interval contract changes.

Required checks:
- re-observe real callable interface;
- update Adapter boundary explicitly;
- review Raw schema compatibility;
- do not infer undocumented capabilities.

### C. Raw schema change

Any modification to `TCTradePlanRaw v1.0.0` requires explicit schema/version review and migration/compatibility assessment.

Unknown provider field additions that are already losslessly preserved by the open Native objects do not automatically require a schema bump.

### D. Mapping / State semantics change

Because current Mapping and State names are PROVISIONAL, they may later change after NODA/Common review, but only through an explicit reviewed work.

Required checks:
- mapping provenance preserved;
- `INFERENCE=NO` remains unless a separately approved architecture change says otherwise;
- TCREG impact reviewed;
- final Common schema not silently inferred from TC.

### E. Evidence expansion

New real TradingCursor evidence may be added without rewriting historical fixtures.

Examples:
- positive Current INVALID sample;
- true same-axis Structured/Text conflict;
- new provider fields.

Rule:

```text
new evidence -> new fixture/audit
not -> rewrite old evidence
```

## 5. Regression protection

TCREG-01 through TCREG-20 form the TC v1 semantic regression baseline.

A later implementation must preserve these unless a deliberate, separately approved semantic change supersedes the baseline.

Known anti-regressions include:

```text
LONG + WAIT may coexist
Trigger NOT_PROVIDED != WAIT
Entry presence != automatic ACTIONABLE
Invalidation Rule != Current INVALID
ACTIONABLE != Execution Permission
no current_price-derived INVALID
no TC-side 4TF synthesis
```

## 6. NOT_TESTABLE handling

The five existing NOT_TESTABLE cases must not be reclassified to PASS without genuine evidence or runtime implementation sufficient to test them.

When one becomes testable:
- add real evidence/test;
- record previous NOT_TESTABLE status;
- do not erase the historical limitation;
- update the new baseline explicitly.

## 7. Adapter and failure-boundary protection

Changes must preserve, unless explicitly re-architected:

```text
Adapter != Mapper
Adapter != State Evaluator
Adapter != Execution
transport failure != Trade State
PARSE_ERROR != Trade State
```

Adapter-owned automatic retry is fixed as `NONE` for TC v1. A future upper-layer retry policy is separate from the Adapter contract and each explicit retry must create a new request/record.

## 8. NODA/Common protection

TC Engine v1 must remain independently traceable to TradingCursor Native behavior.

Do not add NODA-only concepts to TC solely to make output look symmetric.

The Common TradePlanState remains provisional until NODA requirements are reviewed. Any Common finalization must explicitly compare both engine requirements.

## 9. Historical integrity

Prefer additive history:
- new spec amendment;
- new fixture;
- new audit;
- new baseline.

Do not rewrite old evidence/audits merely because the current design has evolved.

## 10. Version labels

Current baseline label:

```text
TC Engine v1
```

Current Raw schema:

```text
TCTradePlanRaw v1.0.0
```

The two version domains are related but not identical. A TC Engine baseline update does not necessarily imply a Raw schema version change, and vice versa.

## 11. Completion requirement for future change work

Every future TC v1 change work should report at least:
- starting baseline SHA;
- ending SHA;
- files changed;
- rationale;
- TCREG result/impact;
- Raw schema impact;
- Common/NODA impact;
- FIXED/PROVISIONAL/TBD/NOT_TESTABLE changes;
- whether a new baseline is created.
