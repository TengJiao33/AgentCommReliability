# TypeCastArena MATH Receiver Packet

This packet sends Agent A artifacts through TypeCastArena communication boundary states before Agent B revises.

## Shape

- Source mode: `bootstrap_saved_peer_surface`
- Source rows: `12`
- Sender artifacts: `12`
- Receiver prompt rows: `204`
- Rows by channel condition: `{'admitted': 48, 'baseline': 12, 'control': 36, 'erased': 24, 'quarantine': 12, 'typed': 72}`
- Rows by admission status: `{'admitted_consensus_state': 12, 'admitted_memory': 12, 'admitted_shared_workspace': 12, 'admitted_verifier_result': 12, 'message_only': 36, 'none': 24, 'not_admitted': 12, 'rejected': 12, 'typed_message': 60, 'typed_message_with_hidden_metadata': 12}`
- Rows by candidate visibility: `{'answer_removed': 36, 'artifact_native': 84, 'artifact_native_unrelated': 12, 'hidden_metadata': 12, 'none': 48, 'visible_field': 12}`
- Rows with candidate literal in prompt: `132`
- Sender candidate correctness: `{'False': 12}`

## Sender Artifacts

| Artifact | Case | Source mode | Surface | Candidate | Preview |
| --- | --- | --- | --- | --- | --- |
| `math13_wrong_typed_public_state::bootstrap_typed_public_state` | `13` | `bootstrap_saved_peer_surface` | `typed_public_state` | `-11` | Typed public state from one peer rationale. Source identity: [anonymous] Final-answer slot: [hidden] Target question: A $90^\circ$ rotation around $-4 - 5i$ in the clockwise direction is applied to $3$ (as a complex number). What is the resulting complex number? Relation / equ... |
| `math21_wrong_rationale::bootstrap_full_rationale` | `21` | `bootstrap_saved_peer_surface` | `full_rationale` | `15` | To solve this problem, let's first find the prime factorization of the number 240. Then, we'll determine what additional factors $k$ must contain to make the product a perfect cube. We want to find the smallest $k$ that meets this condition. Final answer from this peer: 15 |
| `math25_wrong_answer_only::bootstrap_answer_only` | `25` | `bootstrap_saved_peer_surface` | `answer_only` | `6` | I think the final answer is 6. |
| `math28_wrong_rationale::bootstrap_full_rationale` | `28` | `bootstrap_saved_peer_surface` | `full_rationale` | `1` | To solve the functional equation \( f(xy) = f(x) f(y) - 2 \), we start by substituting specific values for \(x\) and \(y\) to gain insight into the form of \(f\). 1. **Substitute \(x = 1\):** \[ f(1 \cdot y) = f(1) f(y) - 2 \] \[ f(y) = f(1) f(y) - 2 \] Let \(c = f(1)\), then... |
| `math29_wrong_redacted_rationale::bootstrap_redacted_rationale` | `29` | `bootstrap_saved_peer_surface` | `redacted_rationale` | `2` | Slot-control surface: full peer rationale with final-answer slot blanked. To solve this problem, we need to follow these steps: 1. Convert the decimal number $629_{10}$ to its base 7 and base 8 representations. 2. Compare the digits in these two representations to find how man... |
| `math61_wrong_equation_surface::bootstrap_equation_surface` | `61` | `bootstrap_saved_peer_surface` | `equation_surface` | `84` | Slot-control surface: equation or number-bearing lines only; final-answer slot blanked. There are 3 teams. Each team has 4 players. So, there are \(3 \times 4 = 12\) players in total. Since each team has 4 players, each player shakes hands with \(4 \times 2 = 8\) other players... |
| `math96_wrong_rationale::bootstrap_full_rationale` | `96` | `bootstrap_saved_peer_surface` | `full_rationale` | `\(\frac{128}{3}\)` | 1. Identify that the area of triangle $ABC$ is 144. 2. Recall that the centroid $G$ of a triangle divides each median into a ratio of $2:1$, with the longer segment being the part from the vertex to the centroid. 3. Since $MN$ is parallel to $BC$, triangles $AMN$ and $ABC$ are... |
| `math112_wrong_rationale::bootstrap_full_rationale` | `112` | `bootstrap_saved_peer_surface` | `full_rationale` | `43` | Given that quadrilateral \(ABCD\) is a parallelogram, we know that opposite angles are equal and consecutive angles are supplementary. 1. The measure of \(\angle A\) is 62 degrees. Therefore, the measure of \(\angle C\) is also 62 degrees because opposite angles are equal. 2.... |
| `math121_wrong_equation_surface::bootstrap_equation_surface` | `121` | `bootstrap_saved_peer_surface` | `equation_surface` | `36\sqrt{2}` | Slot-control surface: equation or number-bearing lines only; final-answer slot blanked. Given that $PABCD$ is a right square pyramid with apex $P$ and base $ABCD$, and $PBD$ is an equilateral triangle with side length 6, we need to determine the volume of $PABCD$. 1. **Identif... |
| `math136_wrong_rationale::bootstrap_full_rationale` | `136` | `bootstrap_saved_peer_surface` | `full_rationale` | `10` | Let's denote the number of family members as \( n \). Angela drank \(\frac{1}{4}\) of the total milk and \(\frac{1}{6}\) of the total coffee. For \( n \) people, each drinking 8 ounces of mixture: - Total mixture consumed = \( 8n \) ounces. - Let \( C \) be the total amount of... |
| `math139_wrong_rationale::bootstrap_full_rationale` | `139` | `bootstrap_saved_peer_surface` | `full_rationale` | `\(\frac{160\pi}{3} + 30\pi = \frac{250\pi}{3}\)` | This problem involves the volume of a solid formed by the combination of a cylinder and a cone. From the diagram, we can see that the height of both the cylinder and the cone is given as 10, and the radius, derived from the provided $\sqrt{3}$ length along the x-axis, is also... |
| `math159_wrong_rationale::bootstrap_full_rationale` | `159` | `bootstrap_saved_peer_surface` | `full_rationale` | `7` | To find the number of integers between \(\dfrac{17}{3}\) and \(\left(\dfrac{17}{3}\right)^2\), let's follow these steps: 1. Calculate the value of \(\dfrac{17}{3}\). 2. Calculate the value of \(\left(\dfrac{17}{3}\right)^2\). 3. Determine the integers that lie strictly between... |

## Caveats

- Bootstrap mode reuses saved peer surfaces; live mode should consume actual Agent A outputs from the sender-stage packet.
- The receiver packet is still a prompt packet until a model run produces Agent B outputs.
- Candidate visibility, admission, persistence, and epistemic type are explicit fields so later analysis can separate lifecycle effects from content effects.
