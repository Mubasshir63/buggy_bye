
from pathlib import Path
from tempfile import TemporaryDirectory

from bughunter import restore_source


def main():
    print("=" * 45)
    print("BugHunter AI - Rollback Safety Test")
    print("=" * 45)

    with TemporaryDirectory() as temp_dir:
        test_file = Path(temp_dir) / "demo_calculator.py"

        original_source = (
            "def add(a, b):\n"
            "    return a + b\n"
        )

        damaged_source = (
            "def add(a, b):\n"
            "    return a - b\n"
        )

        # Start with intentionally damaged source.
        test_file.write_text(
            damaged_source,
            encoding="utf-8",
        )

        print("\n[1] Temporary damaged file created.")

        # Request the governed rollback.
        restored = restore_source(
            original_source=original_source,
            retry_number=50,
            target_file=test_file,
        )

        actual_source = test_file.read_text(
            encoding="utf-8"
        )

        # Confirm the original content was restored.
        if restored and actual_source == original_source:
            print("\nPASS: Original source restored correctly.")
        else:
            print("\nFAIL: Rollback verification failed.")

    print("Temporary directory cleaned up.")


if __name__ == "__main__":
    main()
