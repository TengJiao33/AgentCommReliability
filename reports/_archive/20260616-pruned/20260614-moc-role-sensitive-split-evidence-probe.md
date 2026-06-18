# MOC Role-Sensitive Split-Evidence Probe

## What We Tried

After the cross-system role cards left MOC as an empty compression-site card, I
added a CPU-only probe:

- script: `scripts/run_moc_role_loss_probe.py`
- run record: `experiments/_archive/20260616-pruned/20260614-1832-local-moc-role-sensitive-split-evidence-probe/`
- trace: `comm_trace_moc_role_probe_v11.jsonl`

The probe builds six hand-written split-evidence cases where clue object,
bridge entity, requested relation, qualifier, answer object, and distractor are
separated. It then emits `acr.comm_trace.v1.1` records for MOC-style public
state surfaces:

- `hop1_direct_context`
- `hop2_unmerged_context`
- `hop2_role_aware_merge`
- `hop2_flat_entity_merge`
- `hop2_answer_only_merge`

No model calls were made.

## What Happened

| Policy | Correct | Role-Loss Records | Avg Total Tokens | Avg Compressed Tokens | Transition vs Hop2 Unmerged |
| --- | ---: | ---: | ---: | ---: | --- |
| `hop1_direct_context` | `0/6` | `6` | `34.0` | `0.0` | `6` right-to-wrong |
| `hop2_unmerged_context` | `6/6` | `0` | `51.3` | `0.0` | `6` stable-right |
| `hop2_role_aware_merge` | `6/6` | `0` | `44.7` | `29.8` | `6` stable-right |
| `hop2_flat_entity_merge` | `1/6` | `6` | `26.7` | `11.8` | `5` right-to-wrong, `1` stable-right |
| `hop2_answer_only_merge` | `1/6` | `6` | `21.5` | `6.5` | `5` right-to-wrong, `1` stable-right |

The five failing families under flat or answer-only compression were:

- granularity switch;
- clue object replaces answer object;
- predicate drift;
- comparison aggregation loss;
- distractor anchor switch.

The one surviving flat/answer-only case was `useful_bridge_refinement`: the
target moved from an artist clue to a museum collection answer, and that motion
was helpful rather than harmful.

## Things Noticed

This gives the MOC card a concrete shape without pretending we have measured
MOC's real summarizer. The new useful object is not "add Target Slot to MOC."
It is:

```text
when a multi-hop summary compresses peer messages, does it preserve the role
each source played relative to the question?
```

The trace records now carry `role_slots_preserved`, `role_slots_lost`, and a
`role_probe` block. Those fields make it possible to inspect compression as
role preservation or role flattening, not just answer correctness.

The useful-bridge case matters. It prevents the checker from becoming a crude
"freeze the first target" rule. A role-sensitive audit has to allow bridge
refinement while flagging anchor, predicate, object, qualifier, or granularity
replacement.

## Failures / Friction

I inspected the remote MOC runner and did not add a new domain there. The
upstream path would require touching the domain registry, dataset class, prompt
set, and evaluator. That is too much machinery for the current contact.

This local script is intentionally separate from MOC upstream code.

## Caveats

- This is synthetic, CPU-only, deterministic, and hand-built.
- It is not a MOC paper result, not an LLM merge result, and not a benchmark.
- The accuracy numbers are stress-surface checks, not method scores.
- Token counts are rough word-count proxies.

## Loose Threads

If MOC becomes the active object again, the smallest real next contact is not a
larger GSM8K run. It is either:

- run only the MOC merge prompt over these synthetic message pairs with a local
  LLM and score role-slot preservation; or
- add a tiny role-sensitive split-evidence domain to MOC once the prompt and
  evaluation seams are worth touching.

## Evidence Register

Added row `E-053`.
