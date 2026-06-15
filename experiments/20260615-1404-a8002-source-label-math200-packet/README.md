# Peer Source-Label MATH200 Packet

This directory contains the cross-mode comparison over three peer source-label
settings:

- anonymous:
  `experiments/20260615-1151-a8002-typed-public-state-math200-anon/`
- named:
  `experiments/20260615-1404-a8002-source-label-math200-named/`
- randomized:
  `experiments/20260615-1404-a8002-source-label-math200-randomized/`

The packet compares already-generated protocol audit JSON files. It does not
rerun the model or semantic evaluator.

## Artifacts

- `source_label_packet_audit.md`
- `source_label_packet_audit.json`

## Command

```bash
PYTHONPATH=scripts python scripts/audit_peer_source_label_packet.py \
  --audit anonymous=experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.json \
  --audit named=experiments/20260615-1404-a8002-source-label-math200-named/peer_influence_protocol_audit.json \
  --audit randomized=experiments/20260615-1404-a8002-source-label-math200-randomized/peer_influence_protocol_audit.json \
  --reference-mode anonymous \
  --out-json experiments/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.json \
  --out-md experiments/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.md
```

## Main Readout

On source-label-reliable cases:

- wrong full rationale remains high-harm across modes:
  `9/32` anonymous, `9/32` named, `8/32` randomized;
- wrong typed public state is stable:
  `3/32` anonymous, `3/32` named, `3/32` randomized;
- correct typed public state remains low utility:
  `1/7` anonymous, `1/7` named, `0/7` randomized.

This supports reading the MATH200 signal as content-field pressure more than
displayed source-label pressure, with the caveat that each source mode was run
once and MATH remains a peer-influence diagnostic.
