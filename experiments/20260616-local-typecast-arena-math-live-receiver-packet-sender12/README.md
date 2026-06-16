# TypeCastArena MATH Receiver Packet

This packet sends Agent A artifacts through TypeCastArena communication boundary states before Agent B revises.

## Shape

- Source mode: `live_sender_output`
- Source rows: `12`
- Sender artifacts: `12`
- Receiver prompt rows: `204`
- Rows by channel condition: `{'admitted': 48, 'baseline': 12, 'control': 36, 'erased': 24, 'quarantine': 12, 'typed': 72}`
- Rows by admission status: `{'admitted_consensus_state': 12, 'admitted_memory': 12, 'admitted_shared_workspace': 12, 'admitted_verifier_result': 12, 'message_only': 36, 'none': 24, 'not_admitted': 12, 'rejected': 12, 'typed_message': 60, 'typed_message_with_hidden_metadata': 12}`
- Rows by candidate visibility: `{'answer_removed': 36, 'artifact_native': 84, 'artifact_native_unrelated': 12, 'hidden_metadata': 12, 'none': 48, 'visible_field': 12}`
- Rows with candidate literal in prompt: `82`
- Sender candidate correctness: `{'False': 6, 'True': 6}`

## Sender Artifacts

| Artifact | Case | Source mode | Surface | Candidate | Preview |
| --- | --- | --- | --- | --- | --- |
| `math13_wrong_typed_public_state::live_sender_output` | `13` | `live_sender_output` | `typed_public_state` | `1 - 12i` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. A $90^\circ$ clockwise rotation in the complex plane corresponds to multiplication by $-i$. Sender candidate answer: 1 - 12i |
| `math21_wrong_rationale::live_sender_output` | `21` | `live_sender_output` | `full_rationale` | `900` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: To find the smallest possible positive value of \( k \) such that the product of 240 and \( k \) is a perfect cube, we first factorize 240 into its prime factors:... |
| `math25_wrong_answer_only::live_sender_output` | `25` | `live_sender_output` | `answer_only` | `24` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Calculate the prime factorization of 8! and find the highest N such that N^2 divides 8!. Sender candidate answer: 24 |
| `math28_wrong_rationale::live_sender_output` | `28` | `live_sender_output` | `full_rationale` | `1` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Set $x = y = 1$ to get $f(1) = f(1)^2 - 2$. Sender candidate answer: 1 |
| `math29_wrong_redacted_rationale::live_sender_output` | `29` | `live_sender_output` | `redacted_rationale` | `1` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Convert 629 from base 10 to base 7 and base 8, then compare the digits. Sender candidate answer: 1 |
| `math61_wrong_equation_surface::live_sender_output` | `61` | `live_sender_output` | `equation_surface` | `162` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. There are 3 teams, each with 4 players, so there are 3 * 4 = 12 players in total. Sender candidate answer: 162 |
| `math96_wrong_rationale::live_sender_output` | `96` | `live_sender_output` | `full_rationale` | `8` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. The centroid $G$ divides each median into a ratio of 2:1. Sender candidate answer: 8 |
| `math112_wrong_rationale::live_sender_output` | `112` | `live_sender_output` | `full_rationale` | `137` | Sender epistemic type: inference Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. In a parallelogram, opposite angles are equal. Therefore, angle $C$ is also 62 degrees. Sender candidate answer: 137 |
| `math121_wrong_equation_surface::live_sender_output` | `121` | `live_sender_output` | `equation_surface` | `18√2` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Since $PBD$ is an equilateral triangle with side length 6, the base $BD$ of the triangle is 6. Sender candidate answer: 18√2 |
| `math136_wrong_rationale::live_sender_output` | `136` | `live_sender_output` | `full_rationale` | `3` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: final Sender key steps: Let's denote the number of family members as \( n \). Each person drank an 8-ounce mixture, so the total mixture is \( 8n \) ounces. Let \( C \) be the total amoun... |
| `math139_wrong_rationale::live_sender_output` | `139` | `live_sender_output` | `full_rationale` | `$10\pi \sqrt{3}^2 + \frac{1}{3} \cdot 10\pi \sqrt{3}^2 = 30\pi + 10\pi = 40\pi$` | Sender epistemic type: candidate_answer Sender confidence: 1.00 Sender commitment status: final Sender key steps: The solid is composed of a cylinder and a cone. The cylinder has a height of 10 and a radius of $\sqrt{3}$. The cone has a height of 10 and a radius of $\sqrt{3}$.... |
| `math159_wrong_rationale::live_sender_output` | `159` | `live_sender_output` | `full_rationale` | `26` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Calculated the value of \(\left(\frac{17}{3}\right)^2\) and found it to be approximately 31.11. The integers between \(\frac{17}{3}\) (which is approximately 5.67)... |

## Caveats

- Bootstrap mode reuses saved peer surfaces; live mode should consume actual Agent A outputs from the sender-stage packet.
- The receiver packet is still a prompt packet until a model run produces Agent B outputs.
- Candidate visibility, admission, persistence, and epistemic type are explicit fields so later analysis can separate lifecycle effects from content effects.
