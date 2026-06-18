# PACT Offset100 Target-Contract GPU Run

## Scope

- machine: A800_2
- GPU: 5
- model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- task: HotpotQA split-evidence
- slice: zero-based samples `100-149`
- seed: 42
- samples per arm: 50

## Arms

| Arm | `PACT_FINAL_ANSWER_CONTRACT` | `PACT_TARGET_SLOT_CONTRACT` | EM | Avg F1 | Avg comm tokens | Avg total tokens |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| baseline | 0 | 0 | `16/50` | `0.5517` | `361.6` | `4477.0` |
| final contract | 1 | 0 | `26/50` | `0.6332` | `331.5` | `4526.8` |
| target + final contract | 1 | 1 | `26/50` | `0.6494` | `485.2` | `5266.0` |

## Paired Comparisons

| Comparison | Correct delta | Avg F1 delta | Transitions |
| --- | ---: | ---: | --- |
| baseline -> final contract | `+10` | `+0.0815` | 12 wrong-to-right, 2 right-to-wrong, 14 stable-right, 22 stable-wrong |
| final contract -> target + final | `0` | `+0.0162` | 3 wrong-to-right, 3 right-to-wrong, 23 stable-right, 21 stable-wrong |
| baseline -> target + final | `+10` | `+0.0977` | 14 wrong-to-right, 4 right-to-wrong, 12 stable-right, 20 stable-wrong |

## Target-Slot Diagnostic

The rough lexical target-slot diagnostic over non-stable-right focus cases found:

| Comparison | Focus cases | Candidate count | Candidate samples |
| --- | ---: | ---: | --- |
| baseline -> final contract | 36 | 6 | `107`, `112`, `139`, `140`, `142`, `147` |
| baseline -> target + final | 38 | 2 | `112`, `117` |
| final contract -> target + final | 27 | 1 | `117` |

## Interpretation

The target-slot contract reduced lexical target-drift candidates relative to the final-only contract, but did not improve exact match on this slice. It raised F1 slightly and made final answers shorter, while increasing communication cost substantially.

This is a mechanism signal, not a method win. The useful finding is that target preservation can be moved independently from final-answer surface control, and that enforcing it naively has a real token and regression cost.

## Artifacts

- raw outputs: `remote_baseline/`, `remote_final_contract/`, `remote_target_final_contract/`
- paired summaries:
  - `baseline_vs_final_summary.json`
  - `final_vs_target_summary.json`
  - `baseline_vs_target_summary.json`
- unified traces:
  - `comm_trace_offset100_baseline_v11.jsonl`
  - `comm_trace_offset100_final_contract_v11.jsonl`
  - `comm_trace_offset100_target_final_contract_v11.jsonl`
- target-slot diagnostics:
  - `target_slot_baseline_vs_final_summary.json`
  - `target_slot_baseline_vs_target_summary.json`
  - `target_slot_final_vs_target_summary.json`

## Caveats

- One 50-sample neighboring slice.
- Qwen2.5-14B, not the PACT paper's Qwen3-14B.
- The target-slot diagnostic is lexical and HotpotQA-shaped.
- No target-only arm was run, so this isolates target contract only against final-only, not against baseline by itself.
