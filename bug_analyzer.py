"""
BugHunter AI - Bug Analysis Module

Purpose:
1. Inspect source code and test output.
2. Identify a supported bug pattern.
3. Explain the finding.
4. Refuse to recommend an automatic repair for unknown patterns.

This module does not modify source files.
"""

from dataclasses import dataclass


@dataclass
class BugAnalysis:
    category: str
    explanation: str
    suggested_fix: str | None
    safe_to_repair: bool


def analyze_bug(source_code: str, test_output: str) -> BugAnalysis:
    """
    Analyze a source file and test output.

    Returns a BugAnalysis object describing the result.
    """

    # Step 1: Check whether tests actually failed.
    output = test_output.lower()

    test_failed = (
        "failed" in output
        or "assertionerror" in output
    )

    if not test_failed:
        return BugAnalysis(
            category="NO_CONFIRMED_FAILURE",
            explanation=(
                "The supplied output does not clearly "
                "confirm a test failure."
            ),
            suggested_fix=None,
            safe_to_repair=False,
        )

    # Step 2: Look for a supported calculator pattern.
    normalized_source = source_code.replace("\r\n", "\n")

    known_pattern = (
        "def add(a, b):\n"
        "    return a - b"
    )

    if known_pattern in normalized_source:
        return BugAnalysis(
            category="KNOWN_PATTERN_CANDIDATE",
            explanation=(
                "The add() function subtracts its arguments. "
                "This may be incorrect if add() is intended "
                "to perform addition."
            ),
            suggested_fix="return a + b",
            safe_to_repair=False,
        )

    # Step 3: Unknown patterns must not trigger automatic edits.
    return BugAnalysis(
        category="UNKNOWN_BUG",
        explanation=(
            "A test failure was reported, but the source "
            "does not match a supported bug pattern. "
            "Further investigation is required."
        ),
        suggested_fix=None,
        safe_to_repair=False,
    )


def print_analysis(result: BugAnalysis) -> None:
    """Display the analysis in a readable format."""

    print("\n" + "=" * 45)
    print("       BugHunter AI - Bug Analysis")
    print("=" * 45)

    print("Category:", result.category)
    print("Explanation:", result.explanation)
    print("Suggested fix:", result.suggested_fix)
    print("Safe to repair automatically:", result.safe_to_repair)

    print("=" * 45)


if __name__ == "__main__":
    # Example: deliberately broken calculator.
    example_source = (
        "def add(a, b):\n"
        "    return a - b\n"
    )

    example_test_output = """
    FAILED test_calculator.py::test_add
    AssertionError: assert -1 == 5
    """

    analysis = analyze_bug(
        source_code=example_source,
        test_output=example_test_output,
    )

    print_analysis(analysis)