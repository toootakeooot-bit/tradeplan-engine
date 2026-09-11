# CURRENT_STATE — TC Production

SYSTEM: TC-E Production
REPO: toootakeooot-bit/tradeplan-engine
BRANCH: feature/tc-prod-v1
BASE_SPEC_BRANCH: feature/tc-v1
BASE_SPEC_COMPLETION_HEAD: 023c8247a1a09900a7f8dccbc8434858ab2697db
SPEC_FREEZE_POINT: 91a146625e45c913efd9cebf63a3d25217c8bafe

STATUS: STOPPED_AT_TC_P3_GATE
LAST_COMPLETED: TC-P3 Raw Storage
NEXT: TC-P4 Mapper

P1_RESULT: PASS WITH NOTES
P1_TESTS: 9 PASS / 0 FAIL
P1_REAL_PROVIDER_BINDING: DEFERRED_BY_SPEC_BOUNDARY
P2_RESULT: PASS WITH NOTES
P2_TESTS: 12 PASS / 0 FAIL
P3_START_HEAD: 46ace92db06ca1157139dc93ba46e9e3652d2ccc
P3_RESULT: PASS WITH NOTES
P3_TESTS: 10 PASS / 0 FAIL
P3_COMBINED_P1_P2_P3_TESTS: 31 PASS / 0 FAIL
P3_ARTIFACT_REFERENCE: tcraw://v1/<source_run_id>/<execution_order>.json
P3_WINDOWS_PUBLICATION_TEST: NOT_EXECUTED_CURRENT_POSIX_HOST

WRITE_ALLOWED:
- toootakeooot-bit/tradeplan-engine / feature/tc-prod-v1

READ_ONLY:
- toootakeooot-bit/tradeplan-engine / feature/tc-v1
- toootakeooot-bit/trade-plan-a

A_INTEGRATION: BLOCKED
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
- auto-advance to TC-P4 without explicit user continuation

RESTART_INSTRUCTION:
"対象TC-E Production。docs/CURRENT_STATE.mdを確認し、現在地から再開して"
