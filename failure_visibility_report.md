# Failure Visibility Report

**Generated**: 2026-05-25T13:49:08.668620+00:00
**Status**: CONSTITUTIONAL RESILIENCE VERIFIED

## Summary

- **Total Tests**: 6
- **Passed**: 6
- **Failed**: 0
- **Rejections Logged**: 6

## Adversarial Test Results

| Test | Expected | Result |
|------|----------|--------|
| malformed_contract | REJECTION_WITH_LOGGING | [PASS] REJECTED |
| trace_corruption | DETECTION_WITH_REJECTION | [PASS] REJECTED |
| replay_poisoning | PREVENTION_WITH_REJECTION | [PASS] REJECTED |
| schema_mutation | REJECTION_WITH_LOGGING | [PASS] REJECTED |
| unauthorized_execution | BLOCKED_BY_GATE | [PASS] REJECTED |
| duplicate_trace_replay | HANDLED_GRACEFULLY | [PASS] REJECTED |

## Rejection Reasons

- **malformed_contract**: Missing required fields: ['trace_id', 'execution_plan', 'contract_hash']
- **trace_corruption**: Artifact hash mismatch detected
- **replay_poisoning**: Parent hash mismatch - replay poisoning detected
- **schema_mutation**: Invalid schema version; Undeclared fields: {'undeclared_field'}
- **unauthorized_execution**: Gate blocked execution: unauthorized_module_access
- **duplicate_trace_replay**: Handled deterministically

## Constitutional Guarantees

- [PASS] All adversarial inputs rejected safely
- [PASS] All rejections logged deterministically
- [PASS] Lineage preserved through rejection
- [PASS] System remains replay-safe
