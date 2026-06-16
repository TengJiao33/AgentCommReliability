# MATH Sender-Receiver Micro-Protocol Qwen2.5-14B

Status: behavior run for the first sender-receiver lifecycle packet.

## What We Tried

This step moved the MATH type-erasure line from static communication labels to
an explicit sender-receiver lifecycle packet.

New artifacts:

- invalid-cast audit script:
  `scripts/build_math_type_erasure_v2_invalid_cast_audit.py`
- sender-receiver packet builder:
  `scripts/build_math_sender_receiver_micro_protocol_packet.py`
- sender-receiver analysis script:
  `scripts/analyze_math_sender_receiver_micro_protocol.py`
- setup packet:
  `experiments/20260616-local-math-sender-receiver-micro-protocol-packet/`
- behavior run:
  `experiments/20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b/`

The packet uses saved Agent A artifacts from prior MATH peer-influence rows,
then varies how a communication layer delivers or admits the same object to
Agent B.

## Taxonomy Before The Run

Before building the lifecycle packet, the v2 type-erasure failures were
re-labeled with a seed invalid-cast taxonomy:

- v2 authority-violation cards: `5`
- inherited-operator invalid-cast core: `2`
- local re-solve after empty typed artifact: `2`
- final-answer contract / hidden-source collision: `1`
- direct visible answer copy: `0`

This matters because not every semantic regression is a communication-boundary
invalid cast.

## Packet

Packet:

`experiments/20260616-local-math-sender-receiver-micro-protocol-packet/math_sender_receiver_micro_protocol_packet.jsonl`

Shape:

- source rows: `13`
- selected sender artifacts: `20`
- prompt rows: `246`
- selected artifacts by type:
  - wrong equation surface: `6`
  - wrong final answer: `6`
  - wrong numeric-role binding: `4`
  - wrong relation skeleton: `4`
- artifacts linked to v2 invalid-cast core: `2`
- artifacts linked to earlier authority-operator candidates: `8`

Lifecycle conditions:

- no sender / self-revision controls;
- unrelated sender-message control;
- visible archived private scratch, not admitted;
- direct peer message;
- broadcast peer message;
- admitted shared workspace;
- admitted memory;
- rejected/quarantined message;
- typed inference noncommitment;
- typed partial derivation requiring re-derivation;
- typed hidden candidate metadata;
- typed visible noncommitted candidate.

Local gold-smoke over all `246` rows passed.

## Remote Run

Run facts:

- run id: `20260616-1338-a8002-math-sender-receiver-full246-qwen25-14b`
- model: `/mnt/quarkfs/share_model/Qwen2.5-14B-Instruct`
- served model: `qwen2.5-14b-sender-receiver-full246`
- GPU: A800_2 GPU `7`
- port: `8042`
- max tokens: `768`
- completed rows: `246/246`
- runner stderr: empty
- evaluator stderr: empty
- semantic known rows: `246/246`
- semantic correct: `226/246`
- semantic wrong: `20/246`

Two earlier limit smokes were useful but not final results:

- `LIMIT=24` only covered baseline/self-revision rows because packet rows are
  ordered with baselines first;
- `LIMIT=48` reached lifecycle rows and found one local self-revision
  regression on `math159`.

The existing runner evaluates the full packet even after a `LIMIT` run, so
partial runs require a matching `packet.limitN.jsonl` for local evaluation.

## Main Result

Authority-violation cards in the full run: `20`.

Seed taxonomy:

| Taxonomy | Cards |
| --- | ---: |
| admitted-state inherited operator | 4 |
| peer-message operator influence | 4 |
| direct visible answer uptake | 2 |
| local re-solve or empty-artifact error | 4 |
| operator candidate needing manual review | 6 |

By channel condition:

| Condition | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: |
| admitted | 40 | 5 | 0.125 | 1 | 4 |
| erased | 40 | 5 | 0.125 | 1 | 4 |
| typed | 80 | 7 | 0.087 | 0 | 7 |
| quarantine | 20 | 2 | 0.100 | 0 | 2 |
| control | 53 | 1 | 0.019 | 0 | 1 |

By future signal:

| Signal | Base-right | Violations | AVR | Read |
| --- | ---: | ---: | ---: | --- |
| `peer_message_direct` | 20 | 3 | 0.150 | two operator shifts plus one answer uptake |
| `shared_workspace_admitted` | 20 | 3 | 0.150 | two admitted-operator shifts plus one answer uptake |
| `broadcast_peer_message` | 20 | 2 | 0.100 | operator shifts |
| `memory_admitted_for_reuse` | 20 | 2 | 0.100 | admitted-operator shifts |
| `sender_private_scratch_visible_inert` | 20 | 0 | 0.000 | clean inert control |
| `control_unrelated_sender_message` | 20 | 0 | 0.000 | clean unrelated control |
| `typed_candidate_visible_noncommitment` | 20 | 0 | 0.000 | clean in this packet |

## Read

The cleanest signal is the repeated `math121` equation-surface operator shift.
The model moves from `18√3` to `18√2` without copying the peer wrong final
answer `36√2`.

This happens under:

- direct peer message;
- broadcast peer message;
- shared workspace admission;
- memory admission;
- typed hidden candidate metadata;
- typed partial derivation requiring re-derivation.

It does not happen under:

- unrelated sender-message control;
- visible archived private scratch;
- typed inference noncommitment;
- typed visible candidate noncommitment.

So the evidence supports a narrow lifecycle/boundary handle: the same wrong
equation surface becomes behavior-shaping when it is delivered as a peer object
or admitted/reused as state, while inert and unrelated controls remain clean.

But the result is not a simple "typed boundaries solve it" story. Some typed
channels still preserve enough wrong operator surface to induce the same
`18√2` regression, especially typed hidden-candidate and typed partial-
derivation channels. In this packet, the clean typed arms were typed inference
noncommitment and typed visible candidate noncommitment, not typedness in
general.

There is also a separate direct-copy channel: `math96_wrong_rationale` with a
wrong final-answer artifact causes direct answer uptake under direct peer
message and admitted shared workspace, but typed final-answer channels stay
clean.

The local re-solve background is real. `math159_wrong_rationale` regresses from
`27` to `26` even under `control_self_revision_no_peer`, and related quarantine
or typed rows also move to `26`. Those rows should not be counted as invalid
casts from a sender object without manual inspection.

## Caveats

- Selected packet, not a population estimate.
- One model, zero temperature, Qwen2.5-14B only.
- Sender objects are saved artifacts from prior runs, not newly generated
  inside the same live multi-agent loop.
- Violation taxonomy is deterministic seed labeling for triage, not final
  manual labels.
- Counts are strongly case-concentrated:
  - `math121_wrong_equation_surface`: `6` cards;
  - `math121_wrong_rationale`: `6` cards;
  - `math159_wrong_rationale`: `4` cards;
  - `math96_wrong_rationale`: `4` cards.
- `LIMIT` runs need matched limit packets for evaluation; the current runner's
  full-packet evaluator fails after partial generation.

## Next

Do not scale this exact packet blindly.

Next useful step:

1. Manually inspect the `6` typed operator-candidate cards and decide whether
   they are true invalid casts or local re-solve artifacts.
2. Build a deconcentrated v2 sender-receiver packet with more equation-surface
   cases beyond `math121`, and a cleaner split between:
   - inert visible scratch;
   - peer message;
   - admitted shared state;
   - admitted memory;
   - typed inference with no operator reuse;
   - typed derivation with explicit dependency checks.
3. Patch or wrap the runner so `LIMIT` evaluation uses a matching packet slice.

Current story status:

`Epistemic Type Erasure` remains a live diagnostic / protocol candidate. This
run strengthens the multi-agent lifecycle framing, but it is still not a
paper-ready method claim.
