# Slot-Level Peer Influence Protocol

Date: 2026-06-15

## Why This Exists

The external pressure changed the job. The project should not claim "typed
public state" as the new method object. Existing work already has structured
handoff, shared verified context, and typed evidence/context cards.

The live object is narrower:

> Existing work knows agents conform to peers; this project should diagnose
> which peer-message fields carry revision hazard or utility.

MATH200 is therefore a peer-influence diagnostic, not a general multi-agent
communication benchmark. The protocol below is meant to make that diagnostic
language reusable before moving to split-evidence or distributed-information
tasks.

## Protocol Object

Each peer surface is treated as a bundle of fields rather than one message:

| Field | Local handle |
| --- | --- |
| final-answer authority | answer-only, full rationale |
| source identity | named / anonymous / randomized source mode |
| relation skeleton | redacted rationale, typed public state |
| numeric / role slots | redacted rationale, equation surface, typed public state |
| target predicate | typed public state and manual slot labels |
| equation surface | equation-only surface, typed public state |

Typed public state is one diagnostic surface in this inventory. It is not the
method claim.

## Metrics

The protocol readout aligns the saved peer-exposure records with peer-pressure
benchmark language:

- `utility`: among no-peer-known-wrong cases, the peer-exposed answer becomes
  correct.
- `resistance`: among no-peer-known-correct cases, the peer-exposed answer
  stays correct.
- `harm`: among no-peer-known-correct cases, the peer-exposed answer becomes
  wrong.
- `robustness`: record-level accuracy delta versus paired no-peer baseline,
  with semantic unknown counted as not correct.
- `peer-answer adoption`: saved adoption flag from the original probe; this is
  not yet recomputed under semantic equivalence.

The audit keeps semantic unknowns in denominators for utility, resistance, and
harm, so the rates are conservative.

## Current MATH200 Demo

Audit artifacts:

- `scripts/audit_peer_influence_protocol.py`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.md`
- `experiments/20260615-1151-a8002-typed-public-state-math200-anon/peer_influence_protocol_audit.json`

On source-label-reliable cases:

| Surface | Main readout |
| --- | --- |
| wrong full rationale | high harm: `9/32`; resistance `22/32` |
| wrong redacted rationale | harm `4/32`; resistance `28/32` |
| wrong equation surface | harm `3/32`; resistance `29/32` |
| wrong typed public state | harm `3/32`; resistance `29/32` |
| wrong answer-only | harm `1/32`; resistance `31/32` |

Correct-peer utility on source-label-reliable cases:

| Surface | Utility |
| --- | ---: |
| correct full rationale | `5/7` |
| correct redacted rationale | `4/7` |
| correct answer-only | `2/7` |
| correct equation surface | `1/7` |
| correct typed public state | `1/7` |

This is the important shape:

- full wrong rationale is the highest-harm surface;
- field-restricted surfaces reduce that full-rationale harm channel;
- typed public state does not beat equation surface;
- typed public state has low utility when the peer is correct.

## Story Consequence

The result supports a diagnostic story, not a method story.

The defensible sentence is:

> Peer messages should be decomposed at field level because different fields
> carry different revision hazards and utilities.

The unsafe sentence is:

> Typed public state is a better communication method.

Current evidence says the typed surface is useful because it makes a channel
inspectable: removing full rationale / answer authority lowers harm, but keeping
equation and numeric slots also keeps reconstructable or corrupting influence.

## Next Pressure

The first protocol validation packet has now run:

- `reports/_archive/20260616-pruned/20260615-peer-source-label-math200-packet.md`
- `experiments/_archive/20260616-pruned/20260615-1404-a8002-source-label-math200-packet/source_label_packet_audit.md`

It suggests that displayed source labels do not explain away the main
field-level harm pattern: wrong typed public state stays `3/32` harm across
anonymous, named, and randomized modes.

The next useful step is therefore not another typed-state variant. It is:

1. Case-level slot labels for source-label-sensitive harmful and rescue records:
   relation skeleton,
   numeric/role slot, target predicate, equation surface, final-answer
   authority.
2. Unknown cleanup before more MATH scaling: inspect semantic-unknown and
   source-label-unreliable cases.
3. Benchmark bridge: reuse the protocol language on split-evidence handoff
   tasks such as HotpotQA / 2Wiki / MuSiQue, then on HiddenBench-style
   distributed-information tasks if the story becomes about communication
   necessity.

## Bottom Line

After pressure, the project needs a reusable peer-influence diagnostic protocol
more than a new surface. The MATH200 run now serves as the first protocol demo:
it shows a harm/utility tradeoff across message fields and keeps typed public
state in the right place, as a diagnostic surface inside a broader field-level
analysis.
