import numpy as np
import pandas as pd

from pgaa.core.resistance_branching import validate_dtec_branch


def test_dtc_signature_validates_in_dtec() -> None:
    generator = np.random.default_rng(17)
    genes = [f"G{index}" for index in range(1000)]
    train = generator.normal(0, 1, len(genes))
    test = train + generator.normal(0, 0.2, len(genes))
    ranked = pd.DataFrame(
        {
            "gene_id": genes,
            "dtc_pc9_minus_h4006": train,
            "pc9_dtec_effect": test / 2,
            "h4006_dtec_effect": -test / 2,
        }
    )
    validation, summary = validate_dtec_branch(
        ranked, signature_sizes=(25, 50), permutations=199, seed=3
    )
    assert (validation["validation_gate"] == "pass").all()
    assert summary.iloc[0]["all_signature_sizes_pass"]
    assert summary.iloc[0]["genomewide_dtc_dtec_spearman_rho"] > 0.9
