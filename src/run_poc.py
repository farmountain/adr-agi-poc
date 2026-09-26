"""
ADR-AGI Phase-2 PoC Runner
Executes the service-repair task across 5 failure classes and multiple seeds.
Produces metrics.csv and a summary report.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import numpy as np
import json
import csv
from collections import defaultdict
from adr_core import run_single_trial

def run_experiment(n_seeds: int = 30, max_steps: int = 12):
    results = []
    configs = [
        {"name": "Baseline_A_no_belief_no_verify", "use_belief": False, "use_verification": False},
        {"name": "Baseline_C_belief_only", "use_belief": True, "use_verification": False},
        {"name": "ADR_F_full_kernel", "use_belief": True, "use_verification": True},
    ]

    for cfg in configs:
        for fclass in range(1, 6):
            for seed in range(1, n_seeds + 1):
                r = run_single_trial(
                    failure_class=fclass,
                    seed=seed,
                    use_belief=cfg["use_belief"],
                    use_verification=cfg["use_verification"],
                    max_steps=max_steps,
                )
                r["config"] = cfg["name"]
                results.append(r)

    return results


def summarize(results):
    summary = defaultdict(lambda: defaultdict(list))
    for r in results:
        key = (r["config"], r["failure_class"])
        summary[key]["recovered"].append(1 if r["recovered"] else 0)
        summary[key]["steps"].append(r["steps"])
        summary[key]["info_gain"].append(r["mean_info_gain"])
        if r["hallucination_count"] >= 0:
            summary[key]["hallucinations"].append(r["hallucination_count"])
            summary[key]["ver_success"].append(r["verification_success_rate"])

    rows = []
    for (config, fclass), metrics in sorted(summary.items()):
        row = {
            "config": config,
            "failure_class": fclass,
            "n": len(metrics["recovered"]),
            "recovery_rate_mean": float(np.mean(metrics["recovered"])),
            "recovery_rate_std": float(np.std(metrics["recovered"])),
            "steps_mean": float(np.mean(metrics["steps"])),
            "steps_std": float(np.std(metrics["steps"])),
            "info_gain_mean": float(np.mean(metrics["info_gain"])),
            "info_gain_std": float(np.std(metrics["info_gain"])),
        }
        if metrics["hallucinations"]:
            row["hallucination_mean"] = float(np.mean(metrics["hallucinations"]))
            row["ver_success_mean"] = float(np.mean(metrics["ver_success"]))
        else:
            row["hallucination_mean"] = None
            row["ver_success_mean"] = None
        rows.append(row)
    return rows


if __name__ == "__main__":
    print("Running ADR-AGI Phase-2 PoC (n=30 seeds x 5 failure classes x 3 configs)...")
    results = run_experiment(n_seeds=30)
    summary_rows = summarize(results)

    # Write raw results
    out_dir = os.path.join(os.path.dirname(__file__), "..", "results")
    os.makedirs(out_dir, exist_ok=True)

    with open(os.path.join(out_dir, "raw_results.json"), "w") as f:
        json.dump(results, f, indent=2)

    with open(os.path.join(out_dir, "metrics.csv"), "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=summary_rows[0].keys())
        writer.writeheader()
        writer.writerows(summary_rows)

    print("\n=== SUMMARY (Recovery Rate) ===")
    for row in summary_rows:
        print(
            f"{row['config']:30s} class={row['failure_class']}  "
            f"recovery={row['recovery_rate_mean']:.3f}±{row['recovery_rate_std']:.3f}  "
            f"steps={row['steps_mean']:.1f}  "
            f"info_gain={row['info_gain_mean']:.4f}"
        )
    print("\nResults written to results/metrics.csv and results/raw_results.json")
