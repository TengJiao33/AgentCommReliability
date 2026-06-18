# PACT Target-State Sketchbook

## What This Is

This is a loose sketchbook over PACT target-state cases.

It is not a method proposal, not a metric, and not a parser design. The point is
to sit with the cases where "target preservation" is ambiguous: sometimes the
target should stay still, sometimes it must move through a bridge entity, and
sometimes the first generated target is already the wrong thing to preserve.

Sources:

- `experiments/_archive/20260616-pruned/20260614-1719-local-pact-target-state-freeze-inspection/`
- `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/pact_sample58_drift_packet.md`

## A Soft Vocabulary

These names are temporary.

| Name | Meaning |
| --- | --- |
| question target | The target implied by the original question before any agent speaks. |
| bridge target | A temporary target needed to cross from a clue entity to the answer entity. |
| commitment target | The public target an agent currently acts as if it must answer. |
| harmful switch | The commitment target changes to a distractor, wrong predicate, or wrong object. |
| useful refinement | The target moves closer to the answer while preserving the original question's intent. |
| target freeze trap | Freezing an early generated target would preserve a bridge state or an early wrong commitment. |
| surface failure | Target state is not the main problem; final answer formatting, alias granularity, or extraction is. |

## Case Sketches

### Sample 199: Cyclone Target Oscillation

- Question target: cyclone that had a film made about it in 2007, under the constraint "considered the strongest recorded tropical cyclone."
- Bridge needed: film paragraph identifies `Kathantara` as about the `1999 Odisha cyclone`; distractor paragraph discusses `Cyclone Gonu`.
- Public target sequence: `1999 Odisha cyclone` -> `Cyclone Gonu` -> `1999 Odisha cyclone` -> `Cyclone Gonu`.
- What changed: the public state alternates between the answer entity and a distractor cyclone.
- Reading: harmful switch. The field format is obeyed, but the target becomes a place where agents negotiate between two plausible cyclone anchors.
- Would freezing help: a first-turn freeze might help here, but the better frozen target would be question-derived as `[cyclone; film made in 2007; strongest recorded tropical cyclone]`, not first-turn generated as `[film; 1999 Odisha cyclone; 2007]`.

### Sample 189: Party Entity Switch

- Question target: year until the party associated with Tefik Selim Mborja held power in Albania.
- Bridge needed: identify the party as the Albanian Fascist Party, then find the end year.
- Public target sequence: Albanian Fascist Party held power -> Albanian Fascist Party lost power -> Albanian Fascist Party lost power -> Party of Labour of Albania held power.
- What changed: final turn switches party entity and answers `1992` instead of `1943`.
- Reading: harmful late entity switch.
- Would freezing help: probably, if the frozen state came from the question plus bridge evidence. Freezing the first generated target alone would still have to survive the first turn's wrong action result `1944`.

### Sample 197: Predicate Drift From Headquartered To Founded

- Question target: city where the company founded by Robert Smith is headquartered.
- Bridge needed: Robert Smith -> General Mills -> headquarters city.
- Public target sequence: Robert Smith founded company -> General Mills founded -> General Mills founded -> General Mills founded.
- What changed: the bridge entity becomes correct, but the predicate changes from headquarters to founded.
- Reading: harmful predicate drift. The anchor improves while the requested relation degrades.
- Would freezing help: a question-derived target could help if it keeps the predicate `headquartered`, but first-turn generated freeze is not enough because the first slot already says `founded company`.

### Sample 184: Series Target Becomes Film Target

- Question target: year a CBS series aired; the series stars the actor known for a role in `Rebel Without a Cause`.
- Bridge needed: identify the actor from the film clue, then identify the CBS series and its air year.
- Public target sequence: actor who starred in `Rebel Without a Cause` -> Jim Backus's show -> `The Jim Backus Show` aired -> `Rebel Without a Cause` aired.
- What changed: the target collapses back onto the clue object, the film, instead of the requested series.
- Reading: harmful object switch.
- Would freezing help: a question-derived target could help if it distinguishes clue object from answer object. First-turn generated target is too generic.

### Sample 58: City/Town Target Becomes Civil Parish Target

- Question target: 2001 census population of the city or town in which Kirton End is located.
- Bridge needed: Kirton End -> Boston district / Boston town -> town population.
- Public target movement: location of Kirton End -> population of Boston district -> population of civil parish of Kirton -> civil parish population.
- What changed: the run still sees `35,124`, but later retargets from Boston town to the civil parish of Kirton and answers `273`.
- Reading: harmful granularity switch. The evidence is present, but the target granularity changes.
- Would freezing help: likely a target checker could help, especially one that keeps `city/town containing Kirton End` separate from `civil parish of Kirton`.

### Sample 176: Helpful Bridge Refinement

- Question target: what the museum houses approximately 65,000 of, where works by Hanna Leena Kristiina Varis are part of its collection.
- Bridge needed: Varis works -> museum collection -> Albertina -> collection type.
- Public target sequence: Varis artworks in museum collection -> Albertina approximately 65,000 -> drawings at Albertina -> drawings.
- What changed: the target moves from the artist side to the museum/collection side.
- Reading: useful refinement. The target drift is doing the HotpotQA bridge work.
- Would freezing help: first-turn freeze would probably hurt. A checker should allow bridge refinement when it preserves the question's slot.

### Sample 188: Helpful Comparison Aggregation

- Question target: yes/no comparison of whether two films belong to different genres.
- Bridge needed: find each film's genre, then compare.
- Public target sequence: genre of first film -> genre of second film -> answer type comparing both -> final comparison.
- What changed: the target moves from individual evidence gathering to a joint comparison.
- Reading: useful aggregation.
- Would freezing help: first-turn freeze would hurt because the first target is only one side of the comparison.

### Sample 152: Helpful Answer-Type Repair

- Question target: the lamp type patented in 1780 by Aime Argand, similar to the lamp used in many lighthouses.
- Bridge needed: Argand patent -> Argand lamp -> lighthouse lamp similarity.
- Public target sequence: lamp type / Argand / 1780 -> Argand lamp -> Argand lamp as oil lamp.
- What changed: the target becomes more answer-shaped.
- Reading: useful answer-type refinement. The compact-target run corrects a final-only `Yes` into `Argand lamp`.
- Would freezing help: not needed. This is a case where target motion is productive.

### Sample 160: First Target Already Commits Wrong

- Question target: woman who held the longest service record in Australian Parliament before it was surpassed by Bronwyn Bishop.
- Bridge needed: distinguish the surpassed record holder from the later surpassing politician.
- Public target sequence: Kathy Sullivan held record -> Bronwyn Bishop as Speaker -> Kathy Sullivan / Bronwyn Bishop relation -> Kathy Sullivan.
- What changed: the first generated target already commits to Kathy Sullivan, while gold is Kathryn Jean Martin.
- Reading: target freeze trap. The danger is early commitment, not later drift.
- Would freezing help: no. Freezing first generated target would preserve the wrong answer.

### Sample 193: Necessary Bridge, Then Strict Span

- Question target: city where the headquarters of the company where Ravi Sethi worked are located.
- Bridge needed: Ravi Sethi -> Bell Labs -> headquarters city.
- Public target sequence: Ravi Sethi worked as computer scientist -> Bell Labs headquarters -> Bell Labs headquarters -> Bell Labs headquarters.
- What changed: the target moves through the bridge correctly.
- Reading: mostly necessary bridge, with a strict surface regression: `Murray Hill` versus `Murray Hill, New Jersey`.
- Would freezing help: first-turn freeze would hurt. This is not a clean target-state failure.

### Sample 153: Stable Target, Surface Metric

- Question target: number of top 20 US albums by the singer from the `When Harry Met Sally` soundtrack.
- Bridge needed: soundtrack singer -> Harry Connick Jr. -> count.
- Public target sequence: stable `number; Harry Connick Jr.; top 20 US albums`.
- What changed: compact answer is `7`, gold is `seven`.
- Reading: surface or metric issue, not target-state.
- Would freezing help: no.

### Sample 154: Stable Target, Parser Or Final-Answer Failure

- Question target: yes/no, whether Broughtonia and Laeliocattleya are both orchids.
- Bridge needed: verify each plant.
- Public target sequence: stable `yes/no; Broughtonia and Laeliocattleya; both orchids`.
- What changed: public action result says `Yes`, but extracted compact answer becomes `compact targetstate rule`.
- Reading: final-answer or extraction surface failure.
- Would freezing help: no.

### Sample 182: Stable Target, Extraction Smell

- Question target: English musician known for both `See Yourself` and `Within You Without You`.
- Bridge needed: verify both songs point to George Harrison.
- Public target sequence: stable George Harrison / both songs.
- What changed: action result contains George Harrison, but extracted answer becomes `action result george harrison`.
- Reading: extraction or answer-contract smell, not target-state.
- Would freezing help: no.

## What The Cases Are Saying

The phrase "preserve the target" is too flat.

Bad target change exists. Samples `199`, `189`, `197`, `184`, and `58` all show
some version of anchor, predicate, object, or granularity replacement.

But target movement is also necessary. Samples `176`, `188`, `152`, and `193`
need the target to pass through a bridge or become more answer-shaped. A rigid
first-turn freeze would punish the system for doing the task.

The first generated target is not an authority. Sample `160` is the warning
label: if the first target already commits to the wrong entity, freezing it
only makes the mistake more durable.

Several regressions are not target-state problems at all. Samples `153`, `154`,
and `182` keep the target stable but fail at surface, extraction, or final
answer contract.

## A Shape For The Next Local Object

If there is a next tool, it should probably be a sketchy offline projection,
not a prompt intervention.

It might represent a question target as:

```text
answer_type:
anchor_clues:
requested_relation:
required_qualifier:
bridge_slots_allowed:
forbidden_replacements:
```

The interesting part is `bridge_slots_allowed`. Without that, the checker will
call useful reasoning drift. With too much freedom, it will miss the exact
failures that made target state interesting.

So the next small move, if any, is not:

```text
freeze Target Slot turn 0
```

It is:

```text
write loose question-target sketches for a handful of cases,
then see whether a checker can distinguish bridge refinement from target
replacement.
```

## Caveats

- The notes are hand sketches.
- The sample set is deliberately lopsided toward interesting failures.
- No new model behavior was produced.
- The sketchbook should not be cited as a rate estimate.
