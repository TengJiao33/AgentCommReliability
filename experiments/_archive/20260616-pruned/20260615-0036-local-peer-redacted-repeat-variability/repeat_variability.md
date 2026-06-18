# Peer Redacted Repeat Variability

- Repeated case/conditions: `46`
- Variable case/conditions: `2`
- Variable keys: `['MAD-MM::47::correct_redacted_evidence', 'MAD-MM::47::wrong_redacted_evidence']`

## MAD-MM::47::correct_redacted_evidence

- Post answers: `['14400', '28800']`
- Transitions: `['stable_right', 'stable_wrong']`
- Target behaviors: `['None']`
- Evidence text varies: `False`

### 20260614-2330-a8002-peer-redacted-evidence-math-random8

- pre -> post: `28800` -> `28800`
- transition: `stable_right`
- target behavior: `None`
- source/gold: `None` / `28800`

Evidence:

Key evidence: Treat each party as a block (3 blocks) and arrange them in a circle (2 ways), then arrange members within each block ([blank]).

### 20260615-0012-a8002-peer-redacted-evidence-math-neighbor8

- pre -> post: `28800` -> `28800`
- transition: `stable_right`
- target behavior: `None`
- source/gold: `None` / `28800`

Evidence:

Key evidence: Treat each party as a block (3 blocks) and arrange them in a circle (2 ways), then arrange members within each block ([blank]).

### 20260615-0020-a8002-peer-redacted-neighbor-math-random8

- pre -> post: `14400` -> `14400`
- transition: `stable_wrong`
- target behavior: `None`
- source/gold: `None` / `28800`

Evidence:

Key evidence: Treat each party as a block (3 blocks) and arrange them in a circle (2 ways), then arrange members within each block ([blank]).

## MAD-MM::47::wrong_redacted_evidence

- Post answers: `['14400', '28800']`
- Transitions: `['right_to_wrong', 'wrong_to_right']`
- Target behaviors: `['None']`
- Evidence text varies: `False`

### 20260614-2330-a8002-peer-redacted-evidence-math-random8

- pre -> post: `28800` -> `14400`
- transition: `right_to_wrong`
- target behavior: `None`
- source/gold: `None` / `28800`

Evidence:

Key evidence: Arrange 3 groups in 2 ways, then arrange 5 Democrats and 5 Republicans in 24 ways each around a circular table.

### 20260615-0012-a8002-peer-redacted-evidence-math-neighbor8

- pre -> post: `28800` -> `14400`
- transition: `right_to_wrong`
- target behavior: `None`
- source/gold: `None` / `28800`

Evidence:

Key evidence: Arrange 3 groups in 2 ways, then arrange 5 Democrats and 5 Republicans in 24 ways each around a circular table.

### 20260615-0020-a8002-peer-redacted-neighbor-math-random8

- pre -> post: `14400` -> `28800`
- transition: `wrong_to_right`
- target behavior: `None`
- source/gold: `None` / `28800`

Evidence:

Key evidence: Arrange 3 groups in 2 ways, then arrange 5 Democrats and 5 Republicans in 24 ways each around a circular table.
