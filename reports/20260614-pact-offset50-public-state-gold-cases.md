# PACT Offset50 Public-State Gold Cases

## What We Tried

I manually inspected the ten offset50 cases that the case atlas labeled
`final_public_state_contains_gold`.

The point was to see whether these are really cases where the public state has
the answer but the final answer fails, or whether the mechanical label is too
coarse.

Source:

- `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/case_atlas_focus_cases.jsonl`
- `experiments/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/public_state_gold_manual_labels.jsonl`

## What Happened

The ten cases split into five rough families:

| Manual family | Count | Samples |
| --- | ---: | --- |
| `missing_required_token_or_qualifier` | 3 | `50`, `55`, `83` |
| `wrong_answer_type_or_slot` | 2 | `60`, `67` |
| `over_specific_answer` | 3 | `87`, `89`, `92` |
| `alias_or_name_granularity` | 1 | `74` |
| `false_positive_string_signal` | 1 | `59` |

## Case Notes

| Sample | Gold | Contract final answer | Manual family |
| ---: | --- | --- | --- |
| `50` | `2009 big 12 conference` | `2009 Big 12` | missing required token |
| `55` | `marion south australia` | `Marion` | missing qualifier |
| `59` | `no` | `Yes` | false positive string signal |
| `60` | `shortest player ever to play in national basketball association` | `Muggsy Bogues` | wrong answer type |
| `67` | `usher` | `Yeah!` | wrong slot |
| `74` | `william jefferson clinton` | `Bill Clinton` | alias granularity |
| `83` | `mondelez international inc` | `Mondelez International` | missing suffix |
| `87` | `canary islands spain` | `Tenerife, La Gomera, Canary Islands, Spain` | over-specific |
| `89` | `director` | `film director` | over-specific |
| `92` | `las vegas strip in paradise` | `Flamingo Hotel and Casino, located on the Las Vegas Strip in Paradise, Nevada` | over-specific |

## Things Noticed

The mechanical `final_public_state_contains_gold` bucket was useful but too
generous. Sample `59` is a false positive: the gold answer is `no`, and the
string check can be fooled by substrings such as `northern`. The public state
actually commits to `Yes`.

The remaining nine are more interesting. They are not mostly evidence-absence
failures. They are final-commitment and answer-contract failures:

- keep the right answer but drop a required qualifier;
- choose the wrong answer slot despite the needed evidence being nearby;
- use a common alias when the gold span expects a full name;
- over-specify an answer that should be shorter.

Sample `60` is a clean public-state boundary failure. The environment state
says Muggsy Bogues is the shortest player ever to play in the NBA, but the
final answer is the person, not the distinction.

Sample `67` is a clean slot drift. The question asks for the singer, the
environment state mentions Usher, but the final answer becomes the song
`Yeah!`.

Samples `87`, `89`, and `92` show the opposite of the original verbosity
problem. The answer is not too rambling in a generic way; it is too specific
for the expected HotpotQA span.

## Interpretation

This makes the public-state-to-final-answer layer feel like a real object.

The final public state can hold the needed clue and still fail because the
system has not decided what kind of span the question asks for. "Be concise" is
not enough. The model also needs to choose the right answer type and granularity.

That does not imply a new method yet. It just gives us a sharper place to keep
looking.

## Caveats

- Manual labels over ten cases only.
- The labels are inspection handles, not a stable taxonomy.
- HotpotQA exact match may punish aliases or harmless specificity, so these
  should not all be read as reasoning failures.

## Loose Threads

- Compare these families with first-50 stable-wrong cases.
- Compare these public-state commitment failures against sample `58`'s
  target-slot drift, since they fail at different layers.
- Try a question-contract classifier only as a diagnostic, not as a method
  proposal.
