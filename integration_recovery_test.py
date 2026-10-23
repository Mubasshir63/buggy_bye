
from pathlib import Path
from tempfile import TemporaryDirectory
import shutil
import subprocess
import sys


ROOT = Path(__file__).resolve().parent


def main():
    print("=" * 55)
    print("BugHunter AI - Automatic Recovery Integration Test")
    print("=" * 55)

    # Use a temporary copy so the real project remains safe.
    with TemporaryDirectory(prefix="bughunter_integration_") as temp:
        temp_root = Path(temp)
        sample_source = ROOT / "sample_project"
        temp_sample = temp_root / "sample_project"

        temp_sample.mkdir()

        # Copy the agent and its sample project.
        shutil.copy2(ROOT / "bughunter.py", temp_root / "bughunter.py")
        shutil.copy2(
            sample_source / "calculator.py",
            temp_sample / "calculator.py",
        )
        shutil.copy2(
            sample_source / "test_calculator.py",
            temp_sample / "test_calculator.py",
        )

        # Save the original source for comparison.
        calculator = temp_sample / "calculator.py"
        original_source = (
            "def add(a, b):\n"
            "    return a - b\n"
        )

        # Intentionally create a known bug.
        calculator.write_text(original_source, encoding="utf-8")

        # Force verification to fail even after the known repair.
        test_file = temp_sample / "test_calculator.py"
        test_file.write_text(
            "from calculator import add\n\n"
            "def test_add():\n"
            "    assert add(2, 3) == 999\n",
            encoding="utf-8",
        )

        print("\n[1] Temporary project created.")
        print("[2] Known bug inserted.")
        print("[3] Verification test configured to fail.")
        print("\n[4] Starting BugHunter AI...\n")

        result = subprocess.run(
            [sys.executable, str(temp_root / "bughunter.py")],
            cwd=temp_root,
            capture_output=True,
            text=True,
            timeout=60,
        )

        print(result.stdout)

        if result.stderr:
            print("\nAgent error output:")
            print(result.stderr)

        # The original buggy source should be restored after
        # the repair fails its verification test.
        final_source = calculator.read_text(encoding="utf-8")

        rollback_succeeded = final_source == original_source
        rollback_logged = "ROLLBACK SUCCESS" in result.stdout

        print("\n" + "-" * 55)

        if rollback_succeeded and rollback_logged:
            print("PASS: Automatic rollback integration test succeeded!")
            print("The original source was restored after failed verification.")
        else:
            print("FAIL: Automatic rollback was not fully verified.")
            print(f"Source restored correctly: {rollback_succeeded}")
            print(f"Rollback success logged: {rollback_logged}")
            print("Review the agent output above.")

        print("Temporary project will now be cleaned up.")

        if not (rollback_succeeded and rollback_logged):
            raise SystemExit(1)


if __name__ == "__main__":
    main()
