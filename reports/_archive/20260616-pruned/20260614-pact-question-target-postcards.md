# PACT Question-Target Postcards

## Why These Exist

These are small hand cards, not a taxonomy.

Each card asks:

```text
Original question wants:
Bridge it must cross:
Public state actually did:
What must not be lost:
Tiny machine-shape doodle:
```

The cards are deliberately uneven. The point is to keep the target-state idea
soft enough that it can still surprise us.

Sources:

- `reports/_archive/20260616-pruned/20260614-pact-target-state-sketchbook.md`
- `experiments/_archive/20260616-pruned/20260614-1719-local-pact-target-state-freeze-inspection/`
- `experiments/_archive/20260616-pruned/20260614-1458-a8002-pact-qwen25-14b-hotpot50-offset50-paired/pact_sample58_drift_packet.md`

## Postcards

### 199: Cyclone Or Film

Original question wants:
the cyclone, constrained by "strongest recorded tropical cyclone" and "had a
film made about it in 2007".

Bridge it must cross:
film evidence names `Kathantara`, but the answer is the cyclone it is about.

Public state actually did:
oscillated between `1999 Odisha cyclone` and `Cyclone Gonu`, then answered the
film title.

What must not be lost:
answer type is cyclone; film is evidence, not final answer; `Cyclone Gonu` is a
distractor anchor.

Tiny machine-shape doodle:

```text
answer_type: cyclone
evidence_object: film made in 2007
allowed_bridge: film -> cyclone
forbidden_anchor: Cyclone Gonu unless it satisfies film constraint
```

### 189: Party That Held Power

Original question wants:
the year until the party associated with Tefik Selim Mborja held power in
Albania.

Bridge it must cross:
Mborja -> Albanian Fascist Party -> year power ended.

Public state actually did:
started near Albanian Fascist Party, then late-switched to Party of Labour of
Albania and answered `1992`.

What must not be lost:
the party entity introduced by the Mborja clue.

Tiny machine-shape doodle:

```text
answer_type: year
anchor_clue: Tefik Selim Mborja
bridge_entity: Albanian Fascist Party
requested_relation: held power until
forbidden_replacement: different Albanian party
```

### 197: Founded Versus Headquartered

Original question wants:
the city where the multinational company founded by Robert Smith is
headquartered.

Bridge it must cross:
Robert Smith -> General Mills -> headquarters city.

Public state actually did:
found the company, but kept turning the predicate into where it was founded.

What must not be lost:
`headquartered` is the requested relation; `founded` is only the clue relation.

Tiny machine-shape doodle:

```text
answer_type: city
clue_relation: Robert Smith founded company
bridge_entity: General Mills
requested_relation: headquarters location
predicate_to_guard: headquartered != founded
```

### 184: Film Clue Versus Series Answer

Original question wants:
the year a CBS series aired.

Bridge it must cross:
`Rebel Without a Cause` clue -> actor -> CBS series -> air year.

Public state actually did:
walked toward the actor/show, then slipped back to the film object and answered
the film year.

What must not be lost:
the film is a clue object, not the object whose year is requested.

Tiny machine-shape doodle:

```text
answer_type: year
clue_object: Rebel Without a Cause
bridge_entity: actor
answer_object: CBS series
forbidden_object: clue film as final target
```

### 58: Town Versus Civil Parish

Original question wants:
the 2001 census population of the city or town containing Kirton End.

Bridge it must cross:
Kirton End -> Boston district / Boston town -> town population.

Public state actually did:
saw `35,124`, then retargeted to the civil parish of Kirton and answered `273`.

What must not be lost:
the target granularity is city/town containing the place, not a similarly named
parish or village.

Tiny machine-shape doodle:

```text
answer_type: population
anchor_place: Kirton End
requested_container: city_or_town
accepted_bridge: Boston town
forbidden_granularity: civil parish / village distractor
```

### 176: The Good Kind Of Drift

Original question wants:
what the museum houses approximately 65,000 of.

Bridge it must cross:
Varis works -> museum collection -> Albertina -> collection type.

Public state actually did:
moved from Varis and artworks to Albertina and drawings.

What must not be lost:
the final slot is the collection type, not the artist or the museum name.

Tiny machine-shape doodle:

```text
answer_type: collection_item_type
clue_entity: Hanna Leena Kristiina Varis
bridge_entity: Albertina
requested_quantity: approximately 65,000
allowed_refinement: artist -> museum -> item type
```

### 188: Comparison Has To Assemble

Original question wants:
yes/no, whether two films belong to different genres.

Bridge it must cross:
genre of film A; genre of film B; compare.

Public state actually did:
looked at one film, then the other, then assembled the comparison and answered
`No`.

What must not be lost:
both sides must survive until the comparison step.

Tiny machine-shape doodle:

```text
answer_type: yes_no
left_target: genre(The Importance of Being Icelandic)
right_target: genre(The Five Obstructions)
final_operation: compare_equal_or_different
allowed_bridge: single-side evidence gathering
```

### 152: Yes/No Becomes Object Answer

Original question wants:
the lamp type patented by Argand in 1780.

Bridge it must cross:
patent clue -> Argand lamp -> lighthouse similarity.

Public state actually did:
refined from generic lamp type to `Argand lamp`, fixing a final-only `Yes`.

What must not be lost:
the question asks for an object name, not confirmation.

Tiny machine-shape doodle:

```text
answer_type: lamp_type
anchor: Aime Argand
qualifier: patented in 1780
avoid_answer_type: yes_no
allowed_refinement: inventor -> lamp name
```

### 160: Early Commitment Trap

Original question wants:
the woman who held the longest service record before it was surpassed by a
former Australian politician.

Bridge it must cross:
record holder -> surpassing politician -> disambiguate which woman is asked.

Public state actually did:
committed early to Kathy Sullivan and stayed there.

What must not be lost:
the role distinction between record holder and person who surpassed the record.

Tiny machine-shape doodle:

```text
answer_type: person
role_wanted: prior record holder
contrast_role: person who surpassed record
danger: early named entity commitment
do_not_freeze: first generated entity
```

### 193: Bridge Is Not Drift

Original question wants:
the city where the headquarters of the company where Ravi Sethi worked are
located.

Bridge it must cross:
Ravi Sethi -> Bell Labs -> headquarters city.

Public state actually did:
made the bridge correctly, then answered `Murray Hill, New Jersey` instead of
strict `Murray Hill`.

What must not be lost:
bridge target change is allowed; strict span is a separate surface problem.

Tiny machine-shape doodle:

```text
answer_type: city
clue_person: Ravi Sethi
bridge_entity: Bell Labs
requested_relation: headquarters location
surface_note: city vs city+state
```

### 153: Number Surface

Original question wants:
the number of top 20 US albums by the soundtrack singer.

Bridge it must cross:
`When Harry Met Sally` soundtrack -> Harry Connick Jr. -> album count.

Public state actually did:
kept the target stable and answered `7`.

What must not be lost:
nothing target-like; the issue is `7` versus `seven`.

Tiny machine-shape doodle:

```text
answer_type: number
target_status: stable
problem_surface: numeric spelling
checker_should_ignore: target drift
```

### 154: Yes Is Present, Extraction Is Weird

Original question wants:
yes/no, whether both plants are orchids.

Bridge it must cross:
verify Broughtonia; verify Laeliocattleya; combine.

Public state actually did:
kept the target stable and produced `Yes`, but extraction surfaced a prompt
phrase.

What must not be lost:
the answer already exists in the action result.

Tiny machine-shape doodle:

```text
answer_type: yes_no
left_check: Broughtonia is orchid
right_check: Laeliocattleya is orchid
target_status: stable
problem_surface: final answer extraction
```

### 182: George Harrison Is There

Original question wants:
the English musician known for both songs.

Bridge it must cross:
song A -> musician; song B -> same musician.

Public state actually did:
kept George Harrison visible, then final extraction produced a polluted answer
string.

What must not be lost:
target state is fine; final answer contract is the fragile part.

Tiny machine-shape doodle:

```text
answer_type: person
evidence_left: See Yourself
evidence_right: Within You Without You
target_status: stable
problem_surface: field label leaked into answer
```

## Small Clusters That Fell Out

### Clue Object Is Not Answer Object

Samples: `184`, maybe `199`.

The public state needs to carry an object role:

```text
clue_object != answer_object
```

Otherwise a system can correctly retrieve evidence about the clue and then
answer the clue.

### Predicate Must Survive The Bridge

Samples: `197`, `189`, `58`.

The bridge entity can change, but the requested relation should not quietly
change with it.

```text
founded -> headquartered
held power -> different party's power
town population -> parish population
```

### Some Drift Is The Task

Samples: `176`, `188`, `152`, `193`.

Target checking cannot just punish lexical movement. HotpotQA often requires:

```text
clue -> bridge -> answer slot
single evidence target -> comparison target
generic object type -> exact answer type
```

### First Target Is Not Sacred

Sample: `160`.

Freezing first generated target state can preserve the first mistake. The
original question has higher authority than turn-0 public state.

### Target Is Not Always The Problem

Samples: `153`, `154`, `182`.

Some failures live after the target:

```text
normalization
alias granularity
field extraction
final answer contract
```

## A Messy Next Question

The thing worth touching next is maybe not "target preservation" but:

```text
target role preservation across bridge movement
```

That phrase is still ugly. Good. It has not hardened yet.

If it becomes a tool later, the tool should probably be allowed to say:

```text
This target changed, but it changed in the way the question requires.
```

and also:

```text
This target changed from clue to distractor, even though the words still look
nearby.
```

For now, the postcards are enough.
