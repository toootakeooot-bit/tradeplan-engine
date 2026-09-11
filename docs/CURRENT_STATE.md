# CURRENT_STATE — TC Production

SYSTEM: TC-E Production
REPO: toootakeooot-bit/tradeplan-engine
BRANCH: feature/tc-prod-v1
BASE_SPEC_BRANCH: feature/tc-v1
BASE_SPEC_COMPLETION_HEAD: 023c8247a1a09900a7f8dccbc8434858ab2697db
SPEC_FREEZE_POINT: 91a146625e45c913efd9cebf63a3d25217c8bafe

STATUS: STOPPED_AT_TC_P5_GATE
LAST_COMPLETED: TC-P5 State Evaluator + pipeline regression
TC_ENGINE_PRODUCTION_IMPLEMENTATION: COMPLETE_WITH_NOTES
TC_SIDE_INTEGRATION_READINESS: GO_WITH_NOTES
NEXT: A-side minimum 72-hour W12-5 finalization; then separate Trade Plan TC integration phase

P1_RESULT: PASS WITH NOTES
P1_TESTS: 9 PASS / 0 FAIL
P1_REAL_PROVIDER_BINDING: DEFERRED_BY_SPEC_BOUNDARY
P2_RESULT: PASS WITH NOTES
P2_TESTS: 12 PASS / 0 FAIL
P3_RESULT: PASS WITH NOTES
P3_TESTS: 10 PASS / 0 FAIL
P3_ARTIFACT_REFERENCE: tcraw://v1/<source_run_id>/<execution_order>.json
P3_WINDOWS_PUBLICATION_TEST: NOT_EXECUTED_CURRENT_POSIX_HOST
P4_RESULT: PASS WITH NOTES
P4_TESTS: 10 PASS / 0 FAIL
P4_MAPPING: DIRECT + LIGHT_NORMALIZATION + DETERMINISTIC_TEXT_EXTRACT
P4_INFERENCE: NO
P5_START_HEAD: a7139bf14e148532de453a69c909bb4459c24c9e
P5_RESULT: PASS WITH NOTES
P5_TESTS: 25 PASS / 0 FAIL
P5_FULL_P1_P5_REGRESSION: 66 PASS / 0 FAIL
P5_TCREG_01_20: 20 PASS / 0 FAIL
P5_NOT_TESTABLE: NT01-NT05 unchanged
P5_STATE_MODEL: PROVISIONAL_TC
P5_4TF_SYNTHESIS: NO
P5_EXECUTION_AUTHORITY: NO

WRITE_ALLOWED:
- toootakeooot-bit/tradeplan-engine / feature/tc-prod-v1

READ_ONLY:
- toootakeooot-bit/tradeplan-engine / feature/tc-v1
- toootakeooot-bit/trade-plan-a

A_INTEGRATION: BLOCKED_PENDING_A_72H_BASELINE
A_INTEGRATION_RELEASE_CONDITION:
- A-side minimum 72-hour W12-5 baseline explicitly finalized by user
- TC-P5 production-engine audit PASS/PASS WITH NOTES with integration GO

DO_NOT:
- modify feature/tc-v1 frozen specification
- modify trade-plan-a runtime/config/W10/Scheduler/MT4
- merge main
- create trade-plan-tc yet
- add NODA logic
- add Position Sizing / Risk Amount / Lot / execution
- auto-start A + TC integration before the A gate and explicit user instruction

RESTART_INSTRUCTION:
"対象TC-E Production。docs/CURRENT_STATE.mdを確認し、現在地から再開して"
