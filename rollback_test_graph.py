import os
import tempfile
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
os.environ["BUGHUNTER_PROJECT"] = "sample_project_rollback"

spec = importlib.util.spec_from_file_location(
    "agent_graph",
    ROOT / "agent_graph.py",
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

# Use a temporary source file inside the selected test project.
source_file = ROOT / "sample_project_rollback" / "calculator.py"
original_file = ROOT / "sample_project_rollback" / "calculator.py.original"

original_source = original_file.read_text(encoding="utf-8")
source_file.write_text(
    "def add(a, b):\n    return a - b\n",
    encoding="utf-8",
)

# Create the backup that rollback() expects.
backup_file = source_file.with_name("calculator.py.testbackup.bak")
backup_file.write_text(original_source, encoding="utf-8")

# Confirm the temporary source is currently buggy.
assert "return a - b" in source_file.read_text(encoding="utf-8")

# Exercise the real rollback node.
result = module.rollback({"backup_path": str(backup_file)})

restored_source = source_file.read_text(encoding="utf-8")
assert restored_source == original_source, "Rollback did not restore the original source!"
assert result["final_status"] == "ROLLED_BACK", result

print("\nPASS: Integrated rollback node restored and verified the source.")
print("Final status:", result["final_status"])
