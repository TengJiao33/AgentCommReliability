# PACT Drift Packet: Sample 58

## Case

- Question: According to the 2001 census, what was the population of the city in which Kirton End is located?
- Gold: `35124`
- Transition: `right_to_wrong`
- Baseline final: `35,124`
- Variant final: `273`
- First differing turn: `turn 1 / Agent B / action_required, action_result`

## Turn Pairing

| Turn | Actor | Changed fields | Baseline Action Required | Variant Action Required | Baseline Action Result | Variant Action Result |
| ---: | --- | --- | --- | --- | --- | --- |
| 0 | Agent A | `none` | Provide information about the location of Kirton End. | Provide information about the location of Kirton End. | Kirton End is located in the civil parish of Kirton in the Boston district of Lincolnshire, England. | Kirton End is located in the civil parish of Kirton in the Boston district of Lincolnshire, England. |
| 1 | Agent B | `action_required, action_result` | Provide the population of the city in which Kirton End is located according to the 2001 census. | Provide information about the population of Boston district in 2001 census. | The population of Boston, the town in which Kirton End is located, was 35,124 according to the 2001 census. | The population of Boston district in the 2001 census was 35,124. |
| 2 | Agent A | `action_required, environment_state, action_result` | Provide the population of the city in which Kirton End is located according to the 2001 census. | Provide information about the population of the civil parish of Kirton in 2001 census. | The city in which Kirton End is located, Boston, had a population of 35,124 according to the 2001 census. | The population of the civil parish of Kirton in the 2001 census is not provided in the given context. |
| 3 | Agent B | `action_required, environment_state, action_result, final_answer` | Provide the population of the city in which Kirton End is located according to the 2001 census. | Provide information about the population of the civil parish of Kirton in 2001 census. | The population of Boston, the town in which Kirton End is located, was 35,124 according to the 2001 census. | The population of the civil parish of Kirton in the 2001 census was 273. |

## Numeric Mentions

| Turn | Actor | Baseline numbers | Variant numbers |
| ---: | --- | --- | --- |
| 0 | Agent A | `` | `` |
| 1 | Agent B | `2001, 2015, 35,124, 66,900` | `2001, 2015, 35,124, 66,900` |
| 2 | Agent A | `1.5, 2001, 35,124, 4` | `2001` |
| 3 | Agent B | `2001, 35,124` | `2001, 2011, 261, 273` |

## Final-Prompt Evidence Hits

| Run | Paragraph | Text |
| --- | --- | --- |
| baseline | Kirton, Nottinghamshire | Kirton is a village in Nottinghamshire, England. It is located 3 mi east of Ollerton. According to the United Kingdom Census 2001 it had a population of 273, reducing to 261 at the 2011 census. |
| baseline | Boston, Lincolnshire | Boston ( ) is a town and small port in Lincolnshire, on the east coast of England. It is the largest town of the wider Borough of Boston local government district. The borough had a total population of 66,900, at the ONS mid 2015 estimates, while the town itself had a population of 35,124 at the 2001 census. It is due north of Greenwich on the Prime Meridian. |
| variant | Kirton, Nottinghamshire | Kirton is a village in Nottinghamshire, England. It is located 3 mi east of Ollerton. According to the United Kingdom Census 2001 it had a population of 273, reducing to 261 at the 2011 census. |
| variant | Boston, Lincolnshire | Boston ( ) is a town and small port in Lincolnshire, on the east coast of England. It is the largest town of the wider Borough of Boston local government district. The borough had a total population of 66,900, at the ONS mid 2015 estimates, while the town itself had a population of 35,124 at the 2001 census. It is due north of Greenwich on the Prime Meridian. |

## Reading

- Turn 0 is identical: Agent A locates Kirton End in the Boston district.
- The contract run still sees `35,124` at turn 1, so the correct evidence is not absent.
- The harmful retargeting appears after that: the variant action requirement moves from the city/town population to the civil parish of Kirton.
- The final variant answer then selects `273` from the distractor paragraph `Kirton, Nottinghamshire`, while the baseline remains anchored to `Boston, Lincolnshire` and answers `35,124`.
- This is a target-slot drift case, not an extraction-only surface failure.
