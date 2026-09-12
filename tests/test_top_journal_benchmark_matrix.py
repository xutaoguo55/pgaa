import pandas as pd

from scripts.check_top_journal_benchmark_matrix import validate_matrix


def _valid_matrix():
    return pd.DataFrame(
        [
            {
                "benchmark_id": "claim_audit",
                "required_input": "docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md",
                "comparator": "prohibited_claim_list",
                "endpoint": "manuscript_claim_safety",
                "pass_condition": "No unsupported wet-lab validation claims.",
                "current_status": "not_started",
                "blocking_file": "docs/IMMUNO_EVIDENCE_CLAIM_AUDIT.md",
                "next_action": "Run claim audit on real data.",
            }
        ]
    )


def test_top_journal_benchmark_matrix_accepts_actionable_rows():
    assert validate_matrix(_valid_matrix()) == []


def test_top_journal_benchmark_matrix_rejects_empty_required_field():
    matrix = _valid_matrix()
    matrix.loc[0, "next_action"] = ""

    errors = validate_matrix(matrix)

    assert any("empty next_action" in error for error in errors)


def test_top_journal_benchmark_matrix_rejects_invalid_status():
    matrix = _valid_matrix()
    matrix.loc[0, "current_status"] = "maybe"

    errors = validate_matrix(matrix)

    assert any("invalid current_status" in error for error in errors)
