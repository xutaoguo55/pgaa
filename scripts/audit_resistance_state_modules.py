#!/usr/bin/env python3
"""Build and validate PC9 resistance-state modules."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from pgaa.core.resistance_state_modules import (
    discover_resistance_modules,
    render_resistance_module_audit,
    score_resistance_module_routes,
    select_resistance_reframe_route,
    validate_cortad_module_context,
    validate_resistance_modules,
)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--discovery-cpm", required=True)
    parser.add_argument("--validation-fpkm", required=True)
    parser.add_argument("--annotation", required=True)
    parser.add_argument("--cortad-expression", required=True)
    parser.add_argument("--cortad-metadata", required=True)
    parser.add_argument("--modules-out", required=True)
    parser.add_argument("--validation-out", required=True)
    parser.add_argument("--routes-out", required=True)
    parser.add_argument("--cortad-out", required=True)
    parser.add_argument("--reframe-routes-out", required=True)
    parser.add_argument("--audit-out", required=True)
    args = parser.parse_args()
    discovery = pd.read_csv(args.discovery_cpm, sep="\t", index_col=0)
    validation = pd.read_csv(args.validation_fpkm, sep="\t", index_col=0)
    annotation = pd.read_csv(args.annotation, sep="\t")
    cortad_expression = pd.read_csv(args.cortad_expression, index_col=0)
    cortad_metadata = pd.read_csv(args.cortad_metadata)
    modules = discover_resistance_modules(discovery)
    validation_results = validate_resistance_modules(modules, validation)
    routes = score_resistance_module_routes(validation_results)
    cortad_results = validate_cortad_module_context(
        modules, annotation, cortad_expression, cortad_metadata
    )
    reframe_routes = select_resistance_reframe_route(routes, cortad_results)
    outputs = {
        args.modules_out: modules,
        args.validation_out: validation_results,
        args.routes_out: routes,
        args.cortad_out: cortad_results,
        args.reframe_routes_out: reframe_routes,
    }
    for output, frame in outputs.items():
        Path(output).parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(output, sep="\t", index=False)
        print(f"Wrote {output}")
    Path(args.audit_out).parent.mkdir(parents=True, exist_ok=True)
    Path(args.audit_out).write_text(
        render_resistance_module_audit(
            modules, validation_results, routes, cortad_results, reframe_routes
        ),
        encoding="utf-8",
    )
    print(f"Wrote {args.audit_out}")
    print(f"Selected development route: {routes.iloc[0]['route']}")
    print(f"Selected reframe route: {reframe_routes.iloc[0]['candidate_route']}")


if __name__ == "__main__":
    main()
