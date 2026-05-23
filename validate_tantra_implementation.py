"""
TANTRA Flow Quick Validation
=============================
Validates that all TANTRA layers are present and operational.

This script checks:
1. Direct execution removed from Core
2. CET layer present
3. Sarathi layer present
4. Execution Gate present
5. Flow wiring correct
"""

import os
import sys
import json
from pathlib import Path


class TANTRAValidator:
    """Validates TANTRA flow implementation"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent
        self.results = {
            "validation_passed": False,
            "checks": {},
            "errors": []
        }
    
    def validate_all(self):
        """Run all validation checks"""
        print("\n" + "="*80)
        print("TANTRA FLOW VALIDATION")
        print("="*80)
        
        # Check 1: Direct execution removed
        self.check_direct_execution_removed()
        
        # Check 2: CET layer exists
        self.check_cet_layer()
        
        # Check 3: Sarathi layer exists
        self.check_sarathi_layer()
        
        # Check 4: Execution Gate exists
        self.check_execution_gate()
        
        # Check 5: Flow wiring
        self.check_flow_wiring()
        
        # Check 6: Deliverables
        self.check_deliverables()
        
        # Final result
        all_passed = all(self.results["checks"].values())
        self.results["validation_passed"] = all_passed
        
        print("\n" + "="*80)
        print("VALIDATION RESULTS")
        print("="*80)
        
        for check, passed in self.results["checks"].items():
            status = "[PASS]" if passed else "[FAIL]"
            print(f"{status} - {check}")
        
        if self.results["errors"]:
            print("\nERRORS:")
            for error in self.results["errors"]:
                print(f"  [X] {error}")
        
        print("\n" + "="*80)
        if all_passed:
            print("[SUCCESS] TANTRA FLOW VALIDATION PASSED")
        else:
            print("[FAILED] TANTRA FLOW VALIDATION FAILED")
        print("="*80 + "\n")
        
        return self.results
    
    def check_direct_execution_removed(self):
        """Check that direct execution is removed from routing_engine"""
        print("\n[CHECK 1] Direct Execution Removed")
        
        routing_engine_path = self.base_path / "src" / "core" / "routing_engine.py"
        
        if not routing_engine_path.exists():
            self.results["checks"]["direct_execution_removed"] = False
            self.results["errors"].append("routing_engine.py not found")
            print("  [FAIL] routing_engine.py not found")
            return
        
        with open(routing_engine_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check that _execute_through_module is NOT present
        has_direct_execution = "_execute_through_module" in content
        
        if has_direct_execution:
            self.results["checks"]["direct_execution_removed"] = False
            self.results["errors"].append("Direct execution method still present in routing_engine")
            print("  [FAIL] Direct execution method '_execute_through_module' still exists")
        else:
            self.results["checks"]["direct_execution_removed"] = True
            print("  [PASS] Direct execution removed")
    
    def check_cet_layer(self):
        """Check CET Contract Compiler exists"""
        print("\n[CHECK 2] CET Contract Compiler")
        
        cet_path = self.base_path / "src" / "core" / "cet_contract_compiler.py"
        
        if not cet_path.exists():
            self.results["checks"]["cet_layer_present"] = False
            self.results["errors"].append("CET layer missing")
            print("  [FAIL] cet_contract_compiler.py not found")
            return
        
        with open(cet_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        has_class = "class CETContractCompiler" in content
        has_compile = "def compile_contract" in content
        has_contract_hash = "contract_hash" in content
        
        if has_class and has_compile and has_contract_hash:
            self.results["checks"]["cet_layer_present"] = True
            print("  [PASS] CET Contract Compiler present and complete")
        else:
            self.results["checks"]["cet_layer_present"] = False
            self.results["errors"].append("CET layer incomplete")
            print("  [FAIL] CET layer incomplete")
    
    def check_sarathi_layer(self):
        """Check Sarathi Authority Engine exists"""
        print("\n[CHECK 3] Sarathi Authority Engine")
        
        sarathi_path = self.base_path / "src" / "core" / "authority_engine.py"
        
        if not sarathi_path.exists():
            self.results["checks"]["sarathi_layer_present"] = False
            self.results["errors"].append("Sarathi layer missing")
            print("  [FAIL] authority_engine.py not found")
            return
        
        with open(sarathi_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        has_class = "class SarathiAuthorityEngine" in content
        has_validate = "def validate_contract" in content
        has_decision = "AuthorityDecision" in content
        
        if has_class and has_validate and has_decision:
            self.results["checks"]["sarathi_layer_present"] = True
            print("  [PASS] Sarathi Authority Engine present and complete")
        else:
            self.results["checks"]["sarathi_layer_present"] = False
            self.results["errors"].append("Sarathi layer incomplete")
            print("  [FAIL] Sarathi layer incomplete")
    
    def check_execution_gate(self):
        """Check Execution Gate exists"""
        print("\n[CHECK 4] Execution Gate")
        
        gate_path = self.base_path / "src" / "core" / "execution_gate.py"
        
        if not gate_path.exists():
            self.results["checks"]["execution_gate_present"] = False
            self.results["errors"].append("Execution Gate missing")
            print("  [FAIL] execution_gate.py not found")
            return
        
        with open(gate_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for key components
        has_class = "class ExecutionGate" in content
        has_execute_if_authorized = "def execute_if_authorized" in content
        has_gate_check = "if not authority_decision.get('allowed'" in content
        
        if has_class and has_execute_if_authorized and has_gate_check:
            self.results["checks"]["execution_gate_present"] = True
            print("  [PASS] Execution Gate present and enforced")
        else:
            self.results["checks"]["execution_gate_present"] = False
            self.results["errors"].append("Execution Gate incomplete or not enforced")
            print("  [FAIL] Execution Gate incomplete")
    
    def check_flow_wiring(self):
        """Check that TANTRA flow is wired correctly in routing_engine"""
        print("\n[CHECK 5] TANTRA Flow Wiring")
        
        routing_engine_path = self.base_path / "src" / "core" / "routing_engine.py"
        
        if not routing_engine_path.exists():
            self.results["checks"]["flow_wiring_correct"] = False
            print("  [FAIL] routing_engine.py not found")
            return
        
        with open(routing_engine_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for TANTRA flow components
        has_cet_import = "from .cet_contract_compiler import CETContractCompiler" in content
        has_sarathi_import = "from .authority_engine import SarathiAuthorityEngine" in content
        has_gate_import = "from .execution_gate import ExecutionGate" in content
        
        has_cet_init = "self.cet_compiler = CETContractCompiler()" in content
        has_sarathi_init = "self.authority_engine = SarathiAuthorityEngine()" in content
        has_gate_init = "self.execution_gate = ExecutionGate" in content
        
        has_cet_call = "self.cet_compiler.compile_contract" in content
        has_sarathi_call = "self.authority_engine.validate_contract" in content
        has_gate_call = "self.execution_gate.execute_if_authorized" in content
        
        all_wired = all([
            has_cet_import, has_sarathi_import, has_gate_import,
            has_cet_init, has_sarathi_init, has_gate_init,
            has_cet_call, has_sarathi_call, has_gate_call
        ])
        
        if all_wired:
            self.results["checks"]["flow_wiring_correct"] = True
            print("  [PASS] TANTRA flow correctly wired: Core -> CET -> Sarathi -> Gate -> Execution")
        else:
            self.results["checks"]["flow_wiring_correct"] = False
            self.results["errors"].append("TANTRA flow not fully wired")
            print("  [FAIL] TANTRA flow wiring incomplete")
            if not has_cet_call:
                print("    - CET not called")
            if not has_sarathi_call:
                print("    - Sarathi not called")
            if not has_gate_call:
                print("    - Gate not called")
    
    def check_deliverables(self):
        """Check that all deliverables are present"""
        print("\n[CHECK 6] Deliverables")
        
        review_packets_path = self.base_path / "review_packets"
        
        required_files = [
            "tantra_flow_lock_v1.md",
            "example_contract.json",
            "example_authority_decision.json",
            "example_full_flow.json"
        ]
        
        missing_files = []
        for file in required_files:
            file_path = review_packets_path / file
            if not file_path.exists():
                missing_files.append(file)
        
        if not missing_files:
            self.results["checks"]["deliverables_complete"] = True
            print("  [PASS] All deliverables present")
            for file in required_files:
                print(f"    - {file}")
        else:
            self.results["checks"]["deliverables_complete"] = False
            self.results["errors"].append(f"Missing deliverables: {', '.join(missing_files)}")
            print("  [FAIL] Missing deliverables:")
            for file in missing_files:
                print(f"    - {file}")


def main():
    """Run TANTRA validation"""
    validator = TANTRAValidator()
    results = validator.validate_all()
    
    # Save results
    results_path = Path(__file__).parent / "tantra_validation_results.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n[OK] Results saved to: {results_path}")
    
    return 0 if results["validation_passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
