# ADR-AGI Phase-2 Proof-of-Concept

**Agentic Dynamic Reality toward Recursive Self-Improving AGI**

Private research repository containing the minimal deterministic core kernel, service-repair task with failure injection, and measured experimental results.

## Core Components

- `src/adr_core.py` — DiscreteBeliefKernel, VerificationLedger, SelfModel, SimpleEnvironment
- `src/run_poc.py` — Experiment runner (30 seeds × 5 failure classes × 3 configs)
- `results/metrics.csv` — Aggregated quantitative results
- `results/raw_results.json` — Full per-trial logs

## Quick Start

```bash
python -m venv .venv
source .venv/bin/activate
pip install numpy
python src/run_poc.py
```

## Key Measured Results (n=30 per cell)

- Recovery rate: 1.0 across all configurations (deterministic task with complete repair sequence)
- Mean information gain (nats/step): 0.0225 (belief kernel) vs 0.0 (no-belief baseline)
- Mean hallucination count under ADR full kernel: 1.0–2.0 (detected outcome mismatches)
- Verification success rate: 0.78–0.89

The verification ledger correctly flags cases where an action returns a different result than the expected success string (e.g. "driver_already_present" when the state was not driver-missing).

## Design Principles

1. Zero fabricated results — all numbers come from actual execution
2. Hard LLM boundary — language model may only propose structured actions; belief updates and verification are pure NumPy/Python
3. Intent ≠ verified outcome
4. Minimal kernel only (belief + ledger + self-model). BMR and latent abstraction deferred.

## License

Research prototype. All rights reserved for the duration of the private research phase.
