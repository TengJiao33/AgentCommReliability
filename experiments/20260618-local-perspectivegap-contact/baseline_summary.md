# PerspectiveGap Baseline Summary

| baseline | task | strict pass | coverage | precision | distractor leak/eval | net match |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| oracle | role_assignment | 220/220 (1.000) | 1.000 | 1.000 | 0.000 | 1.000 |
| oracle | prompt_writing | 220/220 (1.000) | 1.000 | 1.000 | 0.000 | 1.000 |
| all_to_all | role_assignment | 0/220 (0.000) | 1.000 | 0.318 | 3.800 | 0.000 |
| all_to_all | prompt_writing | 0/220 (0.000) | 1.000 | 0.318 | 3.800 | 0.000 |
| no_distractor_all_to_all | role_assignment | 0/220 (0.000) | 1.000 | 0.350 | 0.000 | 0.057 |
| no_distractor_all_to_all | prompt_writing | 0/220 (0.000) | 1.000 | 0.350 | 0.000 | 0.057 |
| shared_intersection_only | role_assignment | 0/220 (0.000) | 0.031 | 1.000 | 0.000 | 0.000 |
| shared_intersection_only | prompt_writing | 0/220 (0.000) | 0.031 | 1.000 | 0.000 | 0.000 |
| role_name_heuristic | role_assignment | 0/220 (0.000) | 0.568 | 0.280 | 3.714 | 0.001 |
| role_name_heuristic | prompt_writing | 0/220 (0.000) | 0.568 | 0.280 | 3.714 | 0.001 |
