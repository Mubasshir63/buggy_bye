
from pathlib import Path
import subprocess
import sys

from marginal import (
    AgentAction,
    AgentCapabilities,
    BudgetLimits,
    Cost,
    Treasury,
    UniversalRuntime,
    build_policy,
)


# ==================================================
# 1. PROJECT CONFIGURATION
# ==================================================

ROOT = Path(__file__).resolve().parent

TEST_FILE = ROOT / "sample_project" / "test_calculator.py"
CALCULATOR_FILE = ROOT / "sample_project" / "calculator.py"
BACKUP_FILE = CALCULATOR_FILE.with_suffix(".py.bak")


# ==================================================
# 2. MARGINAL GOVERNANCE
# ==================================================

treasury = Treasury(
    BudgetLimits(
        max_tokens=1000,
        max_usd=0.50,
        max_risk=0.5,
    ),
    policy=build_policy("balanced"),
    mode="enforce",
)

runtime = UniversalRuntime(
    treasury,
    engine="bughunter",
    session_id="bughunter-session-001",
    task_id="calculator-bug-001",
    capabilities=AgentCapabilities(
        block_actions=True,
        record_outcomes=True,
    ),
)


# ==================================================
# 3. GOVERNED ACTION AUTHORIZATION
# ==================================================

def authorize_action(
    action_id,
    name,
    kind,
    phase,
    retry_number=0,
    is_verification=False,
    risk=0.1,
):
    action = AgentAction(
        action_id=action_id,
        name=name,
        kind=kind,
        estimated_cost=Cost(
            tokens=100,
            usd=0.01,
            risk=risk,
        ),
        expected_gain=0.8,
        current_success_probability=0.9,
        is_verification=is_verification,
        state_hash="calculator-project-state",
        phase=phase,
        retry_number=retry_number,
        deduplication_scope="allow_retry",
        metadata={
            "source_file": "sample_project/calculator.py",
            "test_file": "sample_project/test_calculator.py",
            "phase": phase,
        },
    )

    print(f"\nRequesting authorization: {name}")

    decision = runtime.before_action(action)

    print("Action ID:", decision.action_id)
    print("Allowed:", decision.allowed)
    print("Directive:", decision.directive)
    print("Reason:", decision.reason)
    print("Reason code:", decision.reason_code)
    print("Mode:", decision.mode)

    if not decision.allowed:
        print("BLOCKED: Action not authorized.")
        return None

    return action


# ==================================================
# 4. RUN TESTS
# ==================================================

def run_tests(action_id, retry_number=0):
    if not TEST_FILE.exists():
        print("ERROR: Test file not found:", TEST_FILE)
        return None

    # Read-only test execution.
    test_risk = 0.04

    action = authorize_action(
        action_id=action_id,
        name="run_calculator_tests",
        kind="verification",
        phase="verification",
        retry_number=retry_number,
        is_verification=True,
        risk=test_risk,
    )

    if action is None:
        return None

    try:
        print("\nRunning pytest...\n")

        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "pytest",
                str(TEST_FILE),
                "-q",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
            timeout=30,
        )

        print(result.stdout)

        if result.stderr:
            print(result.stderr)

        runtime.after_action(
            action.action_id,
            actual_cost=Cost(
                tokens=100,
                usd=0.01,
                risk=test_risk,
            ),
        )

        if result.returncode == 0:
            print("TEST RESULT: PASSED")
            return True

        print("TEST RESULT: FAILED")
        return False

    except Exception as exc:
        try:
            runtime.fail_action(
                action.action_id,
                reason=f"{type(exc).__name__}: {exc}",
            )
        except Exception:
            pass

        print("Test execution error:", exc)
        return None


# ==================================================
# 5. RESTORE SOURCE WITH GOVERNANCE
# ==================================================

def restore_source(
    original_source,
    retry_number=0,
    target_file=None,
):
    if target_file is None:
        target_file = CALCULATOR_FILE

    # Rollback remains governed. Never bypass a denial.
    action = authorize_action(
        action_id=f"rollback-calculator-{retry_number:03d}",
        name="restore_calculator_source",
        kind="code_modification",
        phase="rollback",
        retry_number=retry_number,
        is_verification=False,
        risk=0.2,
    )

    if action is None:
        print("ROLLBACK BLOCKED.")
        print("Manual recovery may be required.")
        return False

    try:
        target_file.write_text(
            original_source,
            encoding="utf-8",
        )

        runtime.after_action(
            action.action_id,
            actual_cost=Cost(
                tokens=100,
                usd=0.01,
                risk=0.2,
            ),
        )

        # Verify that the requested content was actually written.
        restored_source = target_file.read_text(
            encoding="utf-8"
        )

        if restored_source != original_source:
            print("ROLLBACK ERROR: Content verification failed.")
            return False

        print("ROLLBACK SUCCESS:", target_file.name)
        return True

    except Exception as exc:
        try:
            runtime.fail_action(
                action.action_id,
                reason=f"{type(exc).__name__}: {exc}",
            )
        except Exception:
            pass

        print("ROLLBACK ERROR:", exc)
        return False


# ==================================================
# 6. REPAIR THE KNOWN BUG
# ==================================================

def fix_known_bug():
    print("\n[2] Inspecting calculator source...")

    if not CALCULATOR_FILE.exists():
        print("Calculator file not found.")
        return False

    original_source = CALCULATOR_FILE.read_text(
        encoding="utf-8"
    )

    buggy_code = "return a - b"
    fixed_code = "return a + b"

    if buggy_code not in original_source:
        print("Known bug pattern not found.")
        print("No changes made.")
        return False

    action = authorize_action(
        action_id="repair-calculator-001",
        name="repair_calculator_source",
        kind="code_modification",
        phase="repair",
        retry_number=0,
        is_verification=False,
        risk=0.2,
    )

    if action is None:
        print("Repair was denied by governance.")
        return False

    try:
        # Save the original before making changes.
        BACKUP_FILE.write_text(
            original_source,
            encoding="utf-8",
        )

        updated_source = original_source.replace(
            buggy_code,
            fixed_code,
            1,
        )

        CALCULATOR_FILE.write_text(
            updated_source,
            encoding="utf-8",
        )

        runtime.after_action(
            action.action_id,
            actual_cost=Cost(
                tokens=100,
                usd=0.01,
                risk=0.2,
            ),
        )

        print("Repair authorized and applied.")
        print("Backup created:", BACKUP_FILE.name)

        return True

    except Exception as exc:
        try:
            runtime.fail_action(
                action.action_id,
                reason=f"{type(exc).__name__}: {exc}",
            )
        except Exception:
            pass

        print("Repair error:", exc)

        # A failed repair operation must not be silently ignored.
        print("Attempting separately governed recovery...")
        restore_source(
            original_source,
            retry_number=1,
        )
        return False


# ==================================================
# 7. MAIN WORKFLOW
# ==================================================

def main():
    print("=" * 50)
    print("       BugHunter AI")
    print("       Governance + Recovery")
    print("=" * 50)

    # Stage 1: Initial test.
    initial_result = run_tests(
        action_id="test-run-001",
        retry_number=0,
    )

    if initial_result is None:
        print("\nSTOPPED: Initial test was not completed.")
        return

    if initial_result is True:
        print("\nAll tests already pass!")
        print("No repair is required.")
        return

    # Stage 2: Save backup and repair the known bug.
    if not fix_known_bug():
        print("\nRepair was not completed.")
        return

    # Stage 3: Verify the repaired code.
    print("\n[3] Verifying the repair...")

    verification_result = run_tests(
        action_id="test-run-002",
        retry_number=1,
    )

    if verification_result is True:
        print("\nSUCCESS: Bug fixed and tests passed!")
        return

    print("\nWARNING: Repair could not be verified.")

    # Stage 4: Restore the pre-repair backup.
    if not BACKUP_FILE.exists():
        print("Backup not found. Manual recovery required.")
        return

    original_source = BACKUP_FILE.read_text(
        encoding="utf-8"
    )

    restored = restore_source(
        original_source=original_source,
        retry_number=2,
    )

    if restored:
        print("Original source restored and verified.")
    else:
        print("ROLLBACK FAILED OR BLOCKED.")
        print("Manual recovery may be needed.")


if __name__ == "__main__":
    main()
