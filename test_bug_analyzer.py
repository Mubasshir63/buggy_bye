from bug_analyzer import analyze_bug


def test_known_pattern_is_only_a_candidate():
    source = (
        "def add(a, b):\n"
        "    return a - b\n"
    )

    output = "FAILED test_add.py::test_add\nassert -1 == 5"

    result = analyze_bug(source, output)

    assert result.category == "KNOWN_PATTERN_CANDIDATE"
    assert result.suggested_fix == "return a + b"
    assert result.safe_to_repair is False


def test_unknown_bug_is_not_automatically_repaired():
    source = (
        "def multiply(a, b):\n"
        "    return a + b\n"
    )

    output = "FAILED test_math.py::test_multiply\nAssertionError"

    result = analyze_bug(source, output)

    assert result.category == "UNKNOWN_BUG"
    assert result.suggested_fix is None
    assert result.safe_to_repair is False


def test_passing_output_does_not_trigger_repair():
    source = (
        "def add(a, b):\n"
        "    return a - b\n"
    )

    output = "1 passed in 0.01s"

    result = analyze_bug(source, output)

    assert result.category == "NO_CONFIRMED_FAILURE"
    assert result.suggested_fix is None
    assert result.safe_to_repair is False