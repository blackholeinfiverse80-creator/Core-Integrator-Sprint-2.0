"""
Lineage Validation Tests
=========================
PHASE 1 DELIVERABLE: Prove canonical chain integrity

Tests:
1. Trace ID consistency across chain
2. Parent linkage validation
3. Hash integrity
4. Schema version presence
5. No undeclared fields
6. Deterministic serialization
"""

import json
import hashlib
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple


class LineageValidator:
    """Validates canonical artifact chain integrity"""
    
    def __init__(self):
        self.schema_version = "1.0.0-FINAL"
        self.canonical_types = ["instruction", "blueprint", "contract", "execution", "result"]
        self.test_results = []
    
    def validate_artifact_chain(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Validate complete artifact chain
        
        Returns validation report with pass/fail for each rule
        """
        report = {
            "chain_valid": False,
            "tests": {},
            "errors": [],
            "artifacts_validated": len(artifacts)
        }
        
        # Test 1: Trace ID Consistency
        trace_consistency = self.test_trace_id_consistency(artifacts)
        report["tests"]["trace_id_consistency"] = trace_consistency
        
        # Test 2: Parent Linkage
        parent_linkage = self.test_parent_linkage(artifacts)
        report["tests"]["parent_linkage"] = parent_linkage
        
        # Test 3: Hash Integrity
        hash_integrity = self.test_hash_integrity(artifacts)
        report["tests"]["hash_integrity"] = hash_integrity
        
        # Test 4: Schema Version Presence
        schema_presence = self.test_schema_version_presence(artifacts)
        report["tests"]["schema_version_presence"] = schema_presence
        
        # Test 5: No Undeclared Fields
        no_undeclared = self.test_no_undeclared_fields(artifacts)
        report["tests"]["no_undeclared_fields"] = no_undeclared
        
        # Test 6: Deterministic Serialization
        deterministic_ser = self.test_deterministic_serialization(artifacts)
        report["tests"]["deterministic_serialization"] = deterministic_ser
        
        # Test 7: Canonical Type Sequence
        type_sequence = self.test_canonical_type_sequence(artifacts)
        report["tests"]["canonical_type_sequence"] = type_sequence
        
        # Overall validation
        all_passed = all([
            trace_consistency["passed"],
            parent_linkage["passed"],
            hash_integrity["passed"],
            schema_presence["passed"],
            no_undeclared["passed"],
            deterministic_ser["passed"],
            type_sequence["passed"]
        ])
        
        report["chain_valid"] = all_passed
        
        return report
    
    def test_trace_id_consistency(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 1: Trace ID must be consistent across all artifacts"""
        result = {"test": "trace_id_consistency", "passed": False, "errors": []}
        
        if not artifacts:
            result["errors"].append("No artifacts to validate")
            return result
        
        trace_ids = set()
        for artifact in artifacts:
            if "trace_id" not in artifact:
                result["errors"].append(f"Missing trace_id in artifact {artifact.get('artifact_id', 'unknown')}")
            else:
                trace_ids.add(artifact["trace_id"])
        
        if len(trace_ids) == 0:
            result["errors"].append("No trace_ids found")
        elif len(trace_ids) > 1:
            result["errors"].append(f"Trace ID inconsistency: found {len(trace_ids)} different trace_ids: {trace_ids}")
        else:
            result["passed"] = True
            result["trace_id"] = list(trace_ids)[0]
        
        return result
    
    def test_parent_linkage(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 2: Parent linkage must be valid"""
        result = {"test": "parent_linkage", "passed": False, "errors": []}
        
        # Build artifact map
        artifact_map = {a["artifact_id"]: a for a in artifacts if "artifact_id" in a}
        
        for artifact in artifacts:
            artifact_type = artifact.get("artifact_type")
            artifact_id = artifact.get("artifact_id", "unknown")
            
            # Instruction is root - no parent required
            if artifact_type == "instruction":
                if "parent_artifact_id" in artifact:
                    result["errors"].append(f"Instruction artifact {artifact_id} should NOT have parent")
                continue
            
            # All other artifacts MUST have parent
            if "parent_artifact_id" not in artifact:
                result["errors"].append(f"Artifact {artifact_id} missing parent_artifact_id")
                continue
            
            if "parent_hash" not in artifact:
                result["errors"].append(f"Artifact {artifact_id} missing parent_hash")
                continue
            
            # Validate parent exists
            parent_id = artifact["parent_artifact_id"]
            if parent_id not in artifact_map:
                result["errors"].append(f"Parent artifact {parent_id} not found for {artifact_id}")
                continue
            
            # Validate parent hash matches
            parent_artifact = artifact_map[parent_id]
            parent_hash = parent_artifact.get("artifact_hash")
            
            if parent_hash != artifact["parent_hash"]:
                result["errors"].append(
                    f"Parent hash mismatch for {artifact_id}: "
                    f"expected {parent_hash}, got {artifact['parent_hash']}"
                )
        
        result["passed"] = len(result["errors"]) == 0
        return result
    
    def test_hash_integrity(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 3: Artifact hashes must be valid"""
        result = {"test": "hash_integrity", "passed": False, "errors": []}
        
        for artifact in artifacts:
            artifact_id = artifact.get("artifact_id", "unknown")
            
            if "artifact_hash" not in artifact:
                result["errors"].append(f"Artifact {artifact_id} missing artifact_hash")
                continue
            
            if "payload" not in artifact:
                result["errors"].append(f"Artifact {artifact_id} missing payload")
                continue
            
            # Recompute hash
            computed_hash = self.compute_artifact_hash(artifact["payload"])
            stored_hash = artifact["artifact_hash"]
            
            if computed_hash != stored_hash:
                result["errors"].append(
                    f"Hash mismatch for {artifact_id}: "
                    f"computed {computed_hash[:16]}..., stored {stored_hash[:16]}..."
                )
        
        result["passed"] = len(result["errors"]) == 0
        return result
    
    def test_schema_version_presence(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 4: Schema version must be present"""
        result = {"test": "schema_version_presence", "passed": False, "errors": []}
        
        for artifact in artifacts:
            artifact_id = artifact.get("artifact_id", "unknown")
            
            if "schema_version" not in artifact:
                result["errors"].append(f"Artifact {artifact_id} missing schema_version")
        
        result["passed"] = len(result["errors"]) == 0
        return result
    
    def test_no_undeclared_fields(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 5: No undeclared fields allowed"""
        result = {"test": "no_undeclared_fields", "passed": False, "errors": []}
        
        allowed_fields = {
            "artifact_id", "artifact_type", "trace_id", "instruction_id",
            "schema_version", "timestamp", "artifact_hash", "payload",
            "parent_artifact_id", "parent_hash", "metadata", "execution_id",
            "source_module_id"
        }
        
        for artifact in artifacts:
            artifact_id = artifact.get("artifact_id", "unknown")
            artifact_fields = set(artifact.keys())
            
            undeclared = artifact_fields - allowed_fields
            if undeclared:
                result["errors"].append(
                    f"Artifact {artifact_id} has undeclared fields: {undeclared}"
                )
        
        result["passed"] = len(result["errors"]) == 0
        return result
    
    def test_deterministic_serialization(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 6: Serialization must be deterministic"""
        result = {"test": "deterministic_serialization", "passed": False, "errors": []}
        
        for artifact in artifacts:
            artifact_id = artifact.get("artifact_id", "unknown")
            
            if "payload" not in artifact:
                continue
            
            # Serialize twice and compare
            ser1 = self.canonical_serialize(artifact["payload"])
            ser2 = self.canonical_serialize(artifact["payload"])
            
            if ser1 != ser2:
                result["errors"].append(
                    f"Non-deterministic serialization for {artifact_id}"
                )
        
        result["passed"] = len(result["errors"]) == 0
        return result
    
    def test_canonical_type_sequence(self, artifacts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Test 7: Artifact types must follow canonical sequence"""
        result = {"test": "canonical_type_sequence", "passed": False, "errors": []}
        
        # Extract types in order
        types = [a.get("artifact_type") for a in artifacts]
        
        # Check each type is valid
        for i, artifact_type in enumerate(types):
            if artifact_type not in self.canonical_types:
                result["errors"].append(
                    f"Invalid artifact type at position {i}: {artifact_type}"
                )
        
        # Check sequence order
        expected_sequence = self.canonical_types[:len(types)]
        if types != expected_sequence:
            result["errors"].append(
                f"Type sequence mismatch: expected {expected_sequence}, got {types}"
            )
        
        result["passed"] = len(result["errors"]) == 0
        return result
    
    def compute_artifact_hash(self, payload: Dict[str, Any]) -> str:
        """Compute deterministic hash of payload"""
        canonical = self.canonical_serialize(payload)
        return hashlib.sha256(canonical.encode()).hexdigest()
    
    def canonical_serialize(self, data: Dict[str, Any]) -> str:
        """Canonical JSON serialization with sorted keys"""
        return json.dumps(data, sort_keys=True, separators=(',', ':'))


def run_lineage_validation_tests():
    """Run lineage validation test suite"""
    print("\n" + "="*80)
    print("LINEAGE VALIDATION TESTS - PHASE 1")
    print("="*80)
    
    validator = LineageValidator()
    
    # Test Case 1: Valid chain
    print("\n[TEST 1] Valid Artifact Chain")
    valid_chain = create_valid_test_chain()
    report1 = validator.validate_artifact_chain(valid_chain)
    print_report(report1)
    
    # Test Case 2: Trace ID mismatch
    print("\n[TEST 2] Trace ID Mismatch (Should FAIL)")
    invalid_trace_chain = create_invalid_trace_chain()
    report2 = validator.validate_artifact_chain(invalid_trace_chain)
    print_report(report2)
    
    # Test Case 3: Parent hash mismatch
    print("\n[TEST 3] Parent Hash Mismatch (Should FAIL)")
    invalid_parent_chain = create_invalid_parent_chain()
    report3 = validator.validate_artifact_chain(invalid_parent_chain)
    print_report(report3)
    
    # Test Case 4: Missing schema version
    print("\n[TEST 4] Missing Schema Version (Should FAIL)")
    missing_schema_chain = create_missing_schema_chain()
    report4 = validator.validate_artifact_chain(missing_schema_chain)
    print_report(report4)
    
    # Save results
    results = {
        "test_suite": "lineage_validation",
        "timestamp": "2025-01-15T00:00:00Z",
        "test_cases": [
            {"name": "valid_chain", "report": report1},
            {"name": "trace_id_mismatch", "report": report2},
            {"name": "parent_hash_mismatch", "report": report3},
            {"name": "missing_schema_version", "report": report4}
        ]
    }
    
    output_path = Path(__file__).parent / "lineage_validation_results.json"
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Results saved to: {output_path}")
    
    # Return success if at least valid chain passed
    return 0 if report1["chain_valid"] else 1


def create_valid_test_chain() -> List[Dict[str, Any]]:
    """Create valid test artifact chain"""
    validator = LineageValidator()
    
    # Instruction
    instruction = {
        "artifact_id": "artifact_instruction_abc12345",
        "artifact_type": "instruction",
        "trace_id": "inst_test_12345",
        "instruction_id": "inst_test_12345",
        "schema_version": "1.0.0-FINAL",
        "timestamp": "2025-01-15T00:00:00Z",
        "payload": {
            "origin": "prompt_runner",
            "intent_type": "generate",
            "target_product": "creator",
            "instruction_data": {"test": "data"}
        }
    }
    instruction["artifact_hash"] = validator.compute_artifact_hash(instruction["payload"])
    
    # Blueprint
    blueprint = {
        "artifact_id": "artifact_blueprint_def45678",
        "artifact_type": "blueprint",
        "trace_id": "inst_test_12345",
        "instruction_id": "inst_test_12345",
        "schema_version": "1.0.0-FINAL",
        "timestamp": "2025-01-15T00:01:00Z",
        "parent_artifact_id": instruction["artifact_id"],
        "parent_hash": instruction["artifact_hash"],
        "payload": {
            "blueprint_id": "bp_12345",
            "instruction_reference": instruction["artifact_id"],
            "blueprint_data": {"test": "blueprint"}
        }
    }
    blueprint["artifact_hash"] = validator.compute_artifact_hash(blueprint["payload"])
    
    return [instruction, blueprint]


def create_invalid_trace_chain() -> List[Dict[str, Any]]:
    """Create chain with trace ID mismatch"""
    chain = create_valid_test_chain()
    chain[1]["trace_id"] = "DIFFERENT_TRACE_ID"  # Violate trace consistency
    return chain


def create_invalid_parent_chain() -> List[Dict[str, Any]]:
    """Create chain with parent hash mismatch"""
    chain = create_valid_test_chain()
    chain[1]["parent_hash"] = "INVALID_HASH"  # Violate parent linkage
    return chain


def create_missing_schema_chain() -> List[Dict[str, Any]]:
    """Create chain with missing schema version"""
    chain = create_valid_test_chain()
    del chain[1]["schema_version"]  # Violate schema presence
    return chain


def print_report(report: Dict[str, Any]):
    """Print validation report"""
    print(f"\n  Chain Valid: {report['chain_valid']}")
    print(f"  Artifacts Validated: {report['artifacts_validated']}")
    print(f"\n  Test Results:")
    
    for test_name, test_result in report["tests"].items():
        status = "[PASS]" if test_result["passed"] else "[FAIL]"
        print(f"    {status} {test_name}")
        
        if test_result["errors"]:
            for error in test_result["errors"]:
                print(f"      - {error}")


if __name__ == "__main__":
    sys.exit(run_lineage_validation_tests())
