import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/benchmark_expansion_v3_ready_panel.py"


def test_ready_panel_script_blocks_non_frozen_primary_outputs(tmp_path):
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--dataset-id",
            "datlinger2017_jurkat_crispr",
            "--max-features",
            "1000",
            "--n-repeats",
            "1",
            "--output-dir",
            str(tmp_path),
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode != 0
    assert "non-frozen scoring parameters require --analysis-prefix" in result.stderr


def test_ready_panel_script_dry_run_compiles_execution_plan(tmp_path):
    # Write to tmp_path, not the repository: the plan records the source sizes the
    # script can stat right now, so regenerating it in place makes a tracked
    # evidence file dirty (with different content) on every mounted-volume run.
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "--dry-run", "--output-dir", str(tmp_path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "Dry-run ready platforms: 14" in result.stdout
    plan = tmp_path / "expansion_v3_ready_panel_execution_plan.tsv"
    assert plan.is_file()
