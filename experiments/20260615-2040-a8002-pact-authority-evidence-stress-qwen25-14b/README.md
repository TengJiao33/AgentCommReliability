# PACT Authority/Evidence Stress Qwen2.5-14B

Date: 2026-06-15

## What Ran

- Machine: `A800_2`
- Workspace: `/data/xuhaoming/yfy/research_workspace`
- Model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- Served model: `qwen2.5-14b-authority-evidence-stress`
- GPU: `7`
- Port: `8035`
- Runner: `scripts/run_pact_authority_evidence_stress_a8002.sh`
- Packet: `experiments/20260615-local-pact-authority-evidence-stress-packet/stress_packet.jsonl`
- Prompt rows: `200`
- Source cases: `40`
- Temperature: `0`
- Max tokens: `64`

Command:

```bash
cd /data/xuhaoming/yfy/research_workspace
RUN_STAMP=20260615-2040 GPU_ID=7 PORT=8035 \
  bash scripts/run_pact_authority_evidence_stress_a8002.sh
```

## Outputs

- Remote run dir:
  `/data/xuhaoming/yfy/research_workspace/experiments/20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b`
- Local copied summary:
  `experiments/20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b/evaluation/summary.md`
- Evaluated rows:
  `experiments/20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b/evaluation/evaluated_rows.jsonl`
- Paired deltas:
  `experiments/20260615-2040-a8002-pact-authority-evidence-stress-qwen25-14b/evaluation/paired_deltas.jsonl`

## Main Result

Overall:

- records: `200`;
- EM: `0.570`;
- avg F1: `0.679`.

Positive target-focus rows:

| Variant | Records | EM | Avg F1 |
| --- | ---: | ---: | ---: |
| `trusted_root_original_public` | 32 | 0.812 | 0.865 |
| `trusted_root_injected_action_required` | 32 | 0.594 | 0.695 |
| `delegated_action_required_authority` | 32 | 0.344 | 0.525 |
| `frozen_question_target` | 32 | 0.844 | 0.911 |
| `final_candidate_lure` | 32 | 0.469 | 0.633 |

Paired deltas versus `trusted_root_original_public` on positive target-focus
rows:

| Variant | Outcomes | Avg F1 delta |
| --- | --- | ---: |
| `trusted_root_injected_action_required` | `7` regressions, `19` stable-right, `6` stable-wrong | -0.169 |
| `delegated_action_required_authority` | `15` regressions, `11` stable-right, `6` stable-wrong | -0.339 |
| `frozen_question_target` | `5` rescues, `4` regressions, `22` stable-right, `1` stable-wrong | +0.046 |
| `final_candidate_lure` | `11` regressions, `15` stable-right, `6` stable-wrong | -0.231 |

## Interpretation

The stress packet moves behavior in the predicted direction. Public-field
authority injection hurts positive target-focus cases even when the prompt says
the original question is the trusted root, and explicit delegated authority
hurts more. Frozen question-root projection is the strongest tested condition
on the same selected cases.

This supports the evidence/authority separation handle. It does not yet prove a
general method because this is a selected saved-field packet with synthetic
authority perturbations.

## Caveats

- Selected `40` source cases, not a population sample.
- Positive cases come from target-layer focus cards; controls are only `8`
  seed controls.
- Perturbed `Action Required` text is synthetic and intentionally adversarial.
- Strict span and evidence/content failures still remain.
- This is saved-field re-answering, not a full PACT rerun.
