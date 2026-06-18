# Peer Source-Label MATH200 Packet

Date: 2026-06-15

## Question

After the outside pressure from identity-bias / anonymization work, the next
confound is:

> Are the MATH200 peer-influence effects driven by peer content fields, or by
> displayed source identity?

This packet keeps the same MATH200 source cases and peer content, then varies
only the displayed source label:

- `anonymous`: existing MATH200 typed-public-state run;
- `named`: original compact agent labels are visible;
- `randomized`: deterministic seed-based aliases such as `PeerA`, `PeerG`
  replace source labels while preserving `original_source` in metadata.

## Run

New runs:

- `experiments/_archive/20260616-pruned/20260615-1404-a8002-source-label-math200-named/`
- `experiments/_archive/20260616-pruned/20260615-1404-a8002-source-label-math200-randomized/`

Reference run:

- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/`

Packet comparison:

- `experiments/_archive/20260616-pruned/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.md`
- `experiments/_archive/20260616-pruned/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.json`

Scripts:

- `scripts/run_peer_exposure_probe.py`
- `scripts/run_peer_source_label_packet_a8002.sh`
- `scripts/audit_peer_source_label_packet.py`

Remote execution:

- machine: A800_2;
- GPU: `5`;
- temporary vLLM port: `8031`;
- model: Qwen2.5-7B-Instruct;
- served name: `qwen2.5-7b-source-label`;
- source cases: `59`;
- records per new run: `649`;
- temporary service was stopped after completion; GPU `5` returned to `4 MiB`
  used.

## Source-Label-Reliable Readout

Wrong-peer harm:

| Condition | Anonymous | Named | Randomized |
| --- | ---: | ---: | ---: |
| wrong answer-only | `1/32` | `1/32` | `2/32` |
| wrong full rationale | `9/32` | `9/32` | `8/32` |
| wrong redacted rationale | `4/32` | `5/32` | `5/32` |
| wrong equation surface | `3/32` | `1/32` | `3/32` |
| wrong typed public state | `3/32` | `3/32` | `3/32` |

Correct-peer utility:

| Condition | Anonymous | Named | Randomized |
| --- | ---: | ---: | ---: |
| correct answer-only | `2/7` | `3/7` | `2/7` |
| correct full rationale | `5/7` | `3/7` | `4/7` |
| correct redacted rationale | `4/7` | `3/7` | `4/7` |
| correct equation surface | `1/7` | `0/7` | `2/7` |
| correct typed public state | `1/7` | `1/7` | `0/7` |

## Interpretation

The main field-level harm pattern survives source-label variation:

- wrong full rationale remains the highest-harm surface:
  `9/32`, `9/32`, `8/32`;
- wrong typed public state remains stable:
  `3/32` in all three modes;
- wrong typed public state continues to tie or track equation-like surfaces
  rather than becoming a source-identity effect.

That supports the current narrow story:

> The MATH200 signal is mostly about peer-message content fields, not merely
> whether the displayed source is named or anonymous.

The boundary is also real:

- correct full-rationale utility moves from `5/7` anonymous to `3/7` named and
  `4/7` randomized;
- correct typed public state remains low utility across modes:
  `1/7`, `1/7`, `0/7`;
- these are one-run-per-mode diagnostics, so small count changes should be read
  as pressure, not as stable source-identity estimates.

## Current Claim Update

This packet strengthens the diagnostic framing:

- source label does not explain away the typed-public-state harm result;
- typed public state is still not a method win;
- the claim-bearing unit remains field-level peer-message diagnosis.

It does not prove a general identity-bias result. The named labels are simple
agent labels, not authority titles or social identities, and this is still MATH
peer exposure rather than a distributed-information benchmark.

## Next Pressure

Two useful next checks remain:

1. Case-level labels for the source-label-sensitive rows, especially correct
   full rationale utility changes.
2. Bridge the same protocol to split-evidence/public-state tasks, where
   communication is necessary rather than artificially injected.
