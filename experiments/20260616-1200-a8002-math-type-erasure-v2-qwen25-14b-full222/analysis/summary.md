# MATH Type-Erasure v2 Candidate-Visibility Analysis

Run id: `20260616-1200-a8002-math-type-erasure-v2-qwen25-14b-full222`
Records: `222`
Authority violations: `5`

## By Candidate Visibility

| Candidate visibility | Records | Base-right | Violations | AVR | Answer uptake | Operator candidates |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `answer_removed` | 24 | 24 | 0 | 0.000 | 0 | 0 |
| `answer_visible` | 24 | 24 | 0 | 0.000 | 0 | 0 |
| `artifact_native` | 48 | 48 | 2 | 0.042 | 0 | 2 |
| `artifact_native_unrelated` | 24 | 24 | 0 | 0.000 | 0 | 0 |
| `hidden_metadata` | 24 | 24 | 1 | 0.042 | 0 | 1 |
| `none` | 39 | 39 | 2 | 0.051 | 1 | 1 |
| `visible_field` | 24 | 24 | 0 | 0.000 | 0 | 0 |

## Violations

| Case | Artifact | Future signal | Candidate visibility | Base -> Variant | Uptake | Operator candidate |
| --- | --- | --- | --- | --- | --- | --- |
| `math121_wrong_equation_surface` | `wrong_equation_surface` | `type_erased_shared_workspace_entry` | `artifact_native` | `18√3` -> `18√2` | `False` | `True` |
| `math121_wrong_rationale` | `wrong_equation_surface` | `type_erased_shared_workspace_entry` | `artifact_native` | `18√3` -> `18√2` | `False` | `True` |
| `math21_wrong_rationale` | `wrong_relation_skeleton` | `typed_no_candidate_evidence_inference` | `none` | `900` -> `15` | `True` | `False` |
| `math96_wrong_rationale` | `wrong_final_answer` | `typed_hidden_candidate_metadata` | `hidden_metadata` | `8` -> `8/3` | `False` | `True` |
| `math96_wrong_rationale` | `wrong_final_answer` | `typed_no_candidate_evidence_inference` | `none` | `8` -> `24` | `False` | `True` |
