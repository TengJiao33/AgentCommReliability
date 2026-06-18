# TypeCastArena MATH Receiver Packet

This packet sends Agent A artifacts through TypeCastArena communication boundary states before Agent B revises.

## Shape

- Source mode: `live_sender_output`
- Source rows: `35`
- Sender artifacts: `35`
- Receiver prompt rows: `315`
- Rows by channel condition: `{'admitted': 70, 'baseline': 35, 'control': 105, 'erased': 35, 'quarantine': 35, 'typed': 35}`
- Rows by admission status: `{'admitted_shared_workspace': 35, 'admitted_verifier_result': 35, 'message_only': 70, 'none': 70, 'not_admitted': 35, 'rejected': 35, 'typed_message': 35}`
- Rows by candidate visibility: `{'answer_removed': 35, 'artifact_native': 140, 'artifact_native_unrelated': 35, 'none': 105}`
- Rows with candidate literal in prompt: `203`
- Sender candidate correctness: `{'False': 35}`

## Local Validation

- Analyzer syntax check passed:
  `python -m py_compile scripts/analyze_typecast_boundary_obedience.py`.
- Gold-smoke evaluation scored the packet through the same MATH evaluator with
  `--prediction-source gold`: `315/315` rows were semantically correct and
  `0` rows were semantic-unknown.
- The ordinary evaluator reports `2` wrong-answer-uptake counts in no-sender
  gold-smoke rows; these are gold/source-candidate surface collisions under a
  synthetic gold prediction, not model behavior.
- Boundary-obedience gold-smoke passed with `0` boundary concern cards:
  `boundary-obedience-gold-smoke/summary.md`.
- Candidate visibility is intentionally split:
  - `admission_rejected_quarantine`: artifact and candidate withheld by
    protocol (`candidate_visibility=none`);
  - `typed_partial_derivation_requires_rederive`: candidate answer removed
    while partial derivation text remains visible;
  - `sender_private_scratch_visible_inert`: artifact text visible but not
    delivered or admitted;
  - `peer_message_direct`, `shared_workspace_admitted`, and
    `verifier_admitted_result`: artifact text visible by design.
- Retrospective diagnostic on the old raw-gold relabeled 304-row run produced
  only `2` boundary concern cards, both on `math200_case168` under quarantine
  or typed-rederive channels. This is a manual-review queue for the old run,
  not claim-bearing evidence for the new packet.

## Sender Artifacts

| Artifact | Case | Source mode | Surface | Candidate | Preview |
| --- | --- | --- | --- | --- | --- |
| `math200_case007::live_sender_output` | `7` | `live_sender_output` | `math200_live_sender_artifact` | `12096` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: tentative Sender key steps: 1. Total ways to place 9 beads on a 3x3 grid without any restrictions: \(9!\). Sender candidate answer: 12096 |
| `math200_case008::live_sender_output` | `8` | `live_sender_output` | `math200_live_sender_artifact` | `odd` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Since \( g(x) \) is an even function, \( g(-x) = g(x) \). Sender candidate answer: odd |
| `math200_case010::live_sender_output` | `10` | `live_sender_output` | `math200_live_sender_artifact` | `-1` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Given $ab = a - b$, we can express $a$ in terms of $b$ or vice versa. Let's solve for $\frac{a}{b} + \frac{b}{a} - ab$. Sender candidate answer: -1 |
| `math200_case012::live_sender_output` | `12` | `live_sender_output` | `math200_live_sender_artifact` | `\(\frac{1}{30}\)` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: unknown Sender key steps: Using the method of Lagrange multipliers or applying the Cauchy-Schwarz inequality, we can find the minimum value. Here, we use the Cauchy-Schwarz inequality in... |
| `math200_case016::live_sender_output` | `16` | `live_sender_output` | `math200_live_sender_artifact` | `6` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. The area of rhombus $ABCD$ is given as 24. Sender candidate answer: 6 |
| `math200_case022::live_sender_output` | `22` | `live_sender_output` | `math200_live_sender_artifact` | `44.0625%` | Sender epistemic type: partial_derivation Sender confidence: 0.85 Sender commitment status: tentative Sender key steps: 1. Original dimensions: 24 inches by 16 inches. Sender candidate answer: 44.0625% |
| `math200_case026::live_sender_output` | `26` | `live_sender_output` | `math200_live_sender_artifact` | `150` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Total ways to choose 3 marbles from 11: \( \binom{11}{3} \). Sender candidate answer: 150 |
| `math200_case032::live_sender_output` | `32` | `live_sender_output` | `math200_live_sender_artifact` | `\( \left( \frac{4}{11} \right)^2 = \frac{16}{121} \)` | Sender epistemic type: partial_derivation Sender confidence: 0.85 Sender commitment status: tentative Sender key steps: 1. The length of an arc is given by \( \theta \cdot r \), where \( \theta \) is the angle in radians and \( r \) is the radius. Sender candidate answer: \( \... |
| `math200_case057::live_sender_output` | `57` | `live_sender_output` | `math200_live_sender_artifact` | `-1` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Completed the square for the quadratic expression. Sender candidate answer: -1 |
| `math200_case064::live_sender_output` | `64` | `live_sender_output` | `math200_live_sender_artifact` | `60` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Total number of three-letter sequences from "TARGET" is \(6 \times 5 \times 4 = 120\). Sender candidate answer: 60 |
| `math200_case070::live_sender_output` | `70` | `live_sender_output` | `math200_live_sender_artifact` | `35` | Sender epistemic type: candidate_answer Sender confidence: 1.00 Sender commitment status: final Sender key steps: The area of a trapezoid is given by the formula \( \frac{1}{2} \times (b_1 + b_2) \times h \), where \( b_1 \) and \( b_2 \) are the lengths of the two parallel si... |
| `math200_case073::live_sender_output` | `73` | `live_sender_output` | `math200_live_sender_artifact` | `7` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Calculate the total cost for each possible combination of entree, drink, and dessert. Sender candidate answer: 7 |
| `math200_case079::live_sender_output` | `79` | `live_sender_output` | `math200_live_sender_artifact` | `24` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: final Sender key steps: 1. Three flicks = 8 flecks Sender candidate answer: 24 |
| `math200_case089::live_sender_output` | `89` | `live_sender_output` | `math200_live_sender_artifact` | `10\(\pi\)` | Sender epistemic type: partial_derivation Sender confidence: 0.85 Sender commitment status: tentative Sender key steps: 1. Complete the square for x and y terms. Sender candidate answer: 10\(\pi\) |
| `math200_case103::live_sender_output` | `103` | `live_sender_output` | `math200_live_sender_artifact` | `2` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: tentative Sender key steps: Analyzed the given inequality and tested small values of a and b to find the maximum value of the expression. Sender candidate answer: 2 |
| `math200_case108::live_sender_output` | `108` | `live_sender_output` | `math200_live_sender_artifact` | `\(\frac{7}{12}\)` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: tentative Sender key steps: To minimize \(\frac{1}{a + b} + \frac{1}{b + c}\), we need to maximize \(a + b\) and \(b + c\) within the given constraints. Since \(a + b + c = 5\) and \(1 \l... |
| `math200_case112::live_sender_output` | `112` | `live_sender_output` | `math200_live_sender_artifact` | `137` | Sender epistemic type: inference Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. In a parallelogram, opposite angles are equal. Therefore, angle $C$ is also 62 degrees. Sender candidate answer: 137 |
| `math200_case113::live_sender_output` | `113` | `live_sender_output` | `math200_live_sender_artifact` | `16` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. The circle and parabola have two common tangents, forming a quadrilateral at the points of tangency. Sender candidate answer: 16 |
| `math200_case121::live_sender_output` | `121` | `live_sender_output` | `math200_live_sender_artifact` | `18√2` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Since $PBD$ is an equilateral triangle with side length 6, the base $BD$ of the triangle is 6. Sender candidate answer: 18√2 |
| `math200_case123::live_sender_output` | `123` | `live_sender_output` | `math200_live_sender_artifact` | `11` | Sender epistemic type: candidate_answer Sender confidence: 1.00 Sender commitment status: final Sender key steps: Simplify the equation by dividing both sides by 3, then add 5 to both sides. Sender candidate answer: 11 |
| `math200_case124::live_sender_output` | `124` | `live_sender_output` | `math200_live_sender_artifact` | `12` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Applied the AM-GM inequality to each term. Sender candidate answer: 12 |
| `math200_case127::live_sender_output` | `127` | `live_sender_output` | `math200_live_sender_artifact` | `\(2\sqrt{105}\)` | Sender epistemic type: candidate_answer Sender confidence: 1.00 Sender commitment status: final Sender key steps: The problem involves a right triangle formed by points A, B, and C. The length AB is given as \(2\sqrt{5}\) cm. Points B and C are on the same horizontal line, and... |
| `math200_case133::live_sender_output` | `133` | `live_sender_output` | `math200_live_sender_artifact` | `2` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: tentative Sender key steps: Squared both sides to eliminate the square roots, then simplified the resulting equation. Sender candidate answer: 2 |
| `math200_case136::live_sender_output` | `136` | `live_sender_output` | `math200_live_sender_artifact` | `3` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: final Sender key steps: Let's denote the number of family members as \( n \). Each person drank an 8-ounce mixture, so the total mixture is \( 8n \) ounces. Let \( C \) be the total amoun... |
| `math200_case145::live_sender_output` | `145` | `live_sender_output` | `math200_live_sender_artifact` | `168` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Since $\angle ABC = 90^\circ$, triangle $ABC$ is a right triangle with $AB$ and $BC$ as the legs. Sender candidate answer: 168 |
| `math200_case158::live_sender_output` | `158` | `live_sender_output` | `math200_live_sender_artifact` | `25` | Sender epistemic type: candidate_answer Sender confidence: 0.85 Sender commitment status: final Sender key steps: 1. Use the property of medians in a triangle: The medians of a triangle intersect at the centroid, which divides each median into a ratio of 2:1. Sender candidate... |
| `math200_case163::live_sender_output` | `163` | `live_sender_output` | `math200_live_sender_artifact` | `2√10` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Calculated the distances between each pair of points using the distance formula. The distances are: Sender candidate answer: 2√10 |
| `math200_case165::live_sender_output` | `165` | `live_sender_output` | `math200_live_sender_artifact` | `$\frac{14 + 7\sqrt{3}}{5}$` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: Rationalize the denominators of the fractions. Sender candidate answer: $\frac{14 + 7\sqrt{3}}{5}$ |
| `math200_case166::live_sender_output` | `166` | `live_sender_output` | `math200_live_sender_artifact` | `3/5` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. The wheel has 4 numbers: 1, 2, 6, 9. Sender candidate answer: 3/5 |
| `math200_case168::live_sender_output` | `168` | `live_sender_output` | `math200_live_sender_artifact` | `\(\frac{660}{7}\)` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. The altitude from A divides BC into segments of 3 and 17, so BC = 3 + 17 = 20. Sender candidate answer: \(\frac{660}{7}\) |
| `math200_case169::live_sender_output` | `169` | `live_sender_output` | `math200_live_sender_artifact` | `\(\frac{7}{25}\)` | Sender epistemic type: candidate_answer Sender confidence: 1.00 Sender commitment status: final Sender key steps: - Triangle DEF is a right triangle with the right angle at F. Sender candidate answer: \(\frac{7}{25}\) |
| `math200_case171::live_sender_output` | `171` | `live_sender_output` | `math200_live_sender_artifact` | `(10, 0)` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. Rewrite the equation in standard form by completing the square for \(x\). Sender candidate answer: (10, 0) |
| `math200_case173::live_sender_output` | `173` | `live_sender_output` | `math200_live_sender_artifact` | `90` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: 1. The pyramid has a square base and all edges are equal, so it is a regular square pyramid. Sender candidate answer: 90 |
| `math200_case175::live_sender_output` | `175` | `live_sender_output` | `math200_live_sender_artifact` | `210` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: The problem is about finding the number of distinct ways to arrange 4 true statements and 6 false statements in a sequence of 10 statements. This is a combinatoria... |
| `math200_case176::live_sender_output` | `176` | `live_sender_output` | `math200_live_sender_artifact` | `\(\frac{5}{16}\)` | Sender epistemic type: candidate_answer Sender confidence: 0.95 Sender commitment status: final Sender key steps: - Total outcomes: \(2^4 = 16\) Sender candidate answer: \(\frac{5}{16}\) |

## Caveats

- Bootstrap mode reuses saved peer surfaces; live mode should consume actual Agent A outputs from the sender-stage packet.
- The receiver packet is still a prompt packet until a model run produces Agent B outputs.
- Candidate visibility, admission, persistence, and epistemic type are explicit fields so later analysis can separate lifecycle effects from content effects.
