# PACT Field-Selection Case Inspection

## What We Tried

I inspected the `9` question-aware stable-wrong PACT cases where a matching
candidate still appears in public state: `7` in the final event and `2` only in
earlier/wider public state.

No model call or GPU run was launched.

## What Happened

The mechanical buckets are useful, but too coarse:

| Bucket | Count |
| --- | ---: |
| final event has matching candidate, but policy missed it | 7 |
| matching candidate only appears in earlier/wider public state | 2 |

Manual labels separate them into:

| Family | Count | Samples |
| --- | ---: | --- |
| final field or anchor selection conflict | 3 | `1`, `15`, `31` |
| answer contract or extractor priority | 4 | `25`, `28`, `30`, `40` |
| earlier state lost or overwritten | 2 | `19`, `23` |

## Things Noticed

This makes the current PACT issue sharper. The remaining cases are not mainly
"the answer never appears." They are about which public field is trusted, which
entity anchor is followed, and what answer contract the final response obeys.

The most contact-rich examples are:

- `1`: `environment_state` has `Chief of Protocol`, but `action_result` and
  `final_answer` choose ambassador to Czechoslovakia.
- `15`: `environment_state` has `9,984`, but `action_result` asks for Kansas
  population.
- `23`: `Badly Drawn Boy` appears earlier, but the final comparison becomes a
  tie.
- `31`: `environment_state` has `Fujioka, Gunma`, while final output coarsens
  the location to Japan.

## Loose Threads

The next useful PACT step should be a tiny public-state arbitration probe or a
very small rerun with stricter final answer contract. A larger HotpotQA run
would mostly scale these confounds.

## Caveats

- Manual labels are case notes, not rates.
- Candidate availability is gold-evaluated.
- This is one local postprocessing pass over a 50-sample Qwen2.5-14B PACT
  smoke, not new model behavior.
