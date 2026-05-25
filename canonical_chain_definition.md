# Canonical Artifact Chain Definition

**Version**: 1.0.0-FINAL  
**Status**: FROZEN  
**Last Modified**: 2025-01-15  
**Authority**: TANTRA Constitutional Governance  

---

## 1. CANONICAL CHAIN STRUCTURE

### Immutable Sequence

```
instruction → blueprint → contract → execution → result
```

**FROZEN**: This sequence CANNOT be modified, extended, or bypassed.

---

## 2. ARTIFACT DEFINITIONS

### 2.1 Instruction Artifact (A1)

**Purpose**: Captures initial intent from Prompt Runner or Creator Core

**Required Fields**:
- `artifact_id`: `artifact_instruction_{hash8}`
- `artifact_type`: `"instruction"` (IMMUTABLE)
- `trace_id`: Unique trace identifier
- `instruction_id`: MUST equal trace_id
- `schema_version`: Version string
- `timestamp`: ISO 8601
- `artifact_hash`: SHA-256 of canonical payload
- `payload`:
  - `origin`: `"prompt_runner" | "creator_core" | "external"`
  - `intent_type`: Intent classification
  - `target_product`: `"creator" | "ttg" | "ttv" | "finance" | "education"`
  - `instruction_data`: Instruction-specific data

**Parent Linkage**: NONE (root of chain)

**Immutability**: Once created, CANNOT be modified

---

### 2.2 Blueprint Artifact (A2)

**Purpose**: Captures Creator Core blueprint generation

**Required Fields**:
- `artifact_id`: `artifact_blueprint_{hash8}`
- `artifact_type`: `"blueprint"` (IMMUTABLE)
- `trace_id`: MUST match instruction trace_id
- `instruction_id`: MUST match instruction trace_id
- `schema_version`: Version string
- `timestamp`: ISO 8601
- `artifact_hash`: SHA-256 of canonical payload
- `parent_artifact_id`: Reference to instruction artifact
- `parent_hash`: Hash of parent instruction artifact
- `payload`:
  - `blueprint_id`: Blueprint identifier
  - `instruction_reference`: Reference to instruction
  - `blueprint_data`: Blueprint-specific data

**Parent Linkage**: MUST reference instruction artifact

**Validation**: `parent_hash` MUST match stored instruction artifact hash

---

### 2.3 Contract Artifact (A3)

**Purpose**: Captures CET-generated execution contract

**Required Fields**:
- `artifact_id`: `artifact_contract_{hash8}`
- `artifact_type`: `"contract"` (IMMUTABLE)
- `trace_id`: MUST match instruction trace_id
- `instruction_id`: MUST match instruction trace_id
- `schema_version`: Version string
- `timestamp`: ISO 8601
- `artifact_hash`: SHA-256 of canonical payload
- `parent_artifact_id`: Reference to blueprint artifact
- `parent_hash`: Hash of parent blueprint artifact
- `payload`:
  - `contract_id`: CET-generated contract ID
  - `execution_plan`:
    - `target_module`: Module to execute
    - `execution_intent`: Execution intent
    - `execution_data`: Execution data
  - `constraints`:
    - `deterministic`: MUST be `true`
    - `replay_safe`: MUST be `true`
  - `contract_hash`: Deterministic contract hash
  - `authority_decision`:
    - `allowed`: Sarathi decision
    - `reason`: Decision reason
    - `decision_id`: Decision identifier

**Parent Linkage**: MUST reference blueprint artifact

**Validation**: 
- `parent_hash` MUST match stored blueprint artifact hash
- `constraints.deterministic` MUST be `true`
- `constraints.replay_safe` MUST be `true`

---

### 2.4 Execution Artifact (A4)

**Purpose**: Captures Gate-approved execution

**Required Fields**:
- `artifact_id`: `artifact_execution_{hash8}`
- `artifact_type`: `"execution"` (IMMUTABLE)
- `trace_id`: MUST match instruction trace_id
- `instruction_id`: MUST match instruction trace_id
- `schema_version`: Version string
- `timestamp`: ISO 8601
- `artifact_hash`: SHA-256 of canonical payload
- `parent_artifact_id`: Reference to contract artifact
- `parent_hash`: Hash of parent contract artifact
- `payload`:
  - `execution_id`: Execution identifier
  - `contract_reference`: Reference to contract
  - `gate_status`: `"EXECUTED" | "REJECTED" | "FAILED"`
  - `execution_envelope`:
    - `input_hash`: Input data hash
    - `output_hash`: Output data hash
    - `duration_ms`: Execution duration

**Parent Linkage**: MUST reference contract artifact

**Validation**: 
- `parent_hash` MUST match stored contract artifact hash
- `gate_status` MUST be one of allowed values

---

### 2.5 Result Artifact (A5)

**Purpose**: Captures final execution result

**Required Fields**:
- `artifact_id`: `artifact_result_{hash8}`
- `artifact_type`: `"result"` (IMMUTABLE)
- `trace_id`: MUST match instruction trace_id
- `instruction_id`: MUST match instruction trace_id
- `schema_version`: Version string
- `timestamp`: ISO 8601
- `artifact_hash`: SHA-256 of canonical payload
- `parent_artifact_id`: Reference to execution artifact
- `parent_hash`: Hash of parent execution artifact
- `payload`:
  - `status`: `"success" | "error" | "rejected"`
  - `result_data`: Final result payload
  - `deterministic_hash`: Deterministic result hash for replay

**Parent Linkage**: MUST reference execution artifact

**Validation**: 
- `parent_hash` MUST match stored execution artifact hash
- `deterministic_hash` MUST be reproducible on replay

---

## 3. CONSTITUTIONAL RULES

### 3.1 Trace ID Consistency

**Rule**: `trace_id` MUST be identical across ALL artifacts in a chain

**Enforcement**: Runtime validation on artifact creation

**Failure Mode**: Artifact creation REJECTED if trace_id mismatch

---

### 3.2 Parent Linkage Validation

**Rule**: Every artifact (except instruction) MUST have:
- `parent_artifact_id`: Reference to parent
- `parent_hash`: Hash of parent artifact

**Enforcement**: 
1. Parent artifact MUST exist in storage
2. `parent_hash` MUST match stored parent artifact hash
3. Parent artifact type MUST be correct predecessor in chain

**Failure Mode**: Artifact creation REJECTED if parent validation fails

---

### 3.3 Schema Version Presence

**Rule**: Every artifact MUST have `schema_version` field

**Enforcement**: Schema validation on artifact creation

**Failure Mode**: Artifact creation REJECTED if schema_version missing

---

### 3.4 Deterministic Serialization

**Rule**: Artifacts MUST be serialized using canonical JSON:
- Sorted keys
- No whitespace variations
- Consistent encoding

**Enforcement**: Hash generation uses canonical serialization

**Failure Mode**: Hash mismatch on replay indicates serialization drift

---

### 3.5 No Undeclared Fields

**Rule**: Artifacts MUST NOT contain fields outside schema

**Enforcement**: `additionalProperties: false` in JSON schema

**Failure Mode**: Artifact creation REJECTED if undeclared fields present

---

### 3.6 Immutable Artifact Types

**Rule**: `artifact_type` enum is FROZEN:
- `instruction`
- `blueprint`
- `contract`
- `execution`
- `result`

**Enforcement**: Schema validation

**Failure Mode**: Artifact creation REJECTED if invalid type

---

## 4. HASH GENERATION

### Algorithm

**Hash Function**: SHA-256

**Input**: Canonical JSON serialization of payload

**Process**:
1. Extract `payload` field
2. Serialize to canonical JSON (sorted keys)
3. Compute SHA-256 hash
4. Store as `artifact_hash`

**Exclusions**: `metadata` field NOT included in hash

**Determinism**: MUST produce identical hash for identical payload

---

## 5. REPLAY VALIDATION

### Replay Process

1. Retrieve artifact chain by `trace_id`
2. Validate parent linkage for each artifact
3. Recompute hashes for each artifact
4. Compare recomputed hashes with stored hashes
5. Validate trace_id consistency

### Replay Success Criteria

- All parent hashes match
- All artifact hashes match recomputed hashes
- trace_id consistent across chain
- No missing artifacts in chain

### Replay Failure Modes

- **Hash Mismatch**: Artifact payload was mutated
- **Parent Missing**: Parent artifact not found
- **Parent Hash Mismatch**: Parent artifact was mutated
- **Trace ID Mismatch**: Chain integrity violated
- **Missing Artifact**: Chain incomplete

---

## 6. ENFORCEMENT BOUNDARIES

### Creation Enforcement

**Location**: `src/core/lineage_manager.py::create_artifact()`

**Validations**:
1. Schema validation
2. Parent existence check
3. Parent hash validation
4. Trace ID consistency check
5. No undeclared fields check

**Failure Action**: REJECT artifact creation, log rejection reason

---

### Retrieval Enforcement

**Location**: `src/core/bucket_reader.py::get_artifact_by_id()`

**Validations**:
1. Artifact exists
2. Schema valid
3. Hash integrity

**Failure Action**: Return error, log retrieval failure

---

### Replay Enforcement

**Location**: `src/core/replay_engine.py::replay_instruction()`

**Validations**:
1. Complete chain exists
2. Parent linkage valid
3. Hash integrity maintained
4. Trace ID consistent

**Failure Action**: REJECT replay, log validation failure

---

## 7. CONSTITUTIONAL GUARANTEES

### Guarantee 1: No Hidden Authority

**Claim**: Execution CANNOT occur outside Gate

**Proof**: All execution paths route through `execution_gate.py::execute_if_authorized()`

**Validation**: Enforcement boundary tests

---

### Guarantee 2: Replay Integrity

**Claim**: Replay produces deterministic results

**Proof**: Hash validation on replay matches original execution

**Validation**: Concurrent replay tests

---

### Guarantee 3: Schema Immutability

**Claim**: Artifact schema CANNOT drift

**Proof**: Schema validation enforced at creation

**Validation**: Adversarial schema mutation tests

---

### Guarantee 4: Trace Consistency

**Claim**: trace_id CANNOT mutate within chain

**Proof**: Runtime validation on artifact creation

**Validation**: Lineage validation tests

---

## 8. FAILURE VISIBILITY

### Rejection Logging

**Location**: `src/utils/insightflow.py`

**Events**:
- `artifact.creation.rejected`
- `artifact.validation.failed`
- `replay.validation.failed`
- `parent.linkage.broken`
- `trace.consistency.violated`

**Required Fields**:
- `trace_id`
- `artifact_type`
- `rejection_reason`
- `timestamp`

---

## 9. VERSIONING

**Current Version**: 1.0.0-FINAL

**Frozen**: YES

**Modification Process**: Requires constitutional governance approval

**Backward Compatibility**: MUST be maintained

---

## 10. AUTHORITY

**Defined By**: TANTRA Constitutional Governance

**Enforced By**: Core Integrator

**Validated By**: Runtime enforcement tests

**Status**: IMMUTABLE

---

**END OF CANONICAL CHAIN DEFINITION**
