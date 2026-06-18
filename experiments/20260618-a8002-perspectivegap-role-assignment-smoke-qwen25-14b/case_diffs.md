# PerspectiveGap Qwen2.5 7B/14B Paired Smoke Diff

## qwen2.5-7b
- strict_pass: 0/4
- required_coverage: 0.5490
- boundary_precision: 0.9032
- distractor_leakage_per_eval: 0.0000
- counts: tp=28, fp=3, fn=23, distractor_leak=0

## qwen2.5-14b
- strict_pass: 0/4
- required_coverage: 0.6667
- boundary_precision: 0.8718
- distractor_leakage_per_eval: 0.2500
- counts: tp=34, fp=5, fn=17, distractor_leak=1

## Case Diffs

### pg_000__seed_1
- qwen2.5-7b: coverage=1.000, precision=0.875, leak=0, tp=7, fp=1, fn=0
  - coder: missing=-; extra=-
  - reviewer: missing=-; extra=f1
- qwen2.5-14b: coverage=0.714, precision=0.833, leak=1, tp=5, fp=1, fn=2
  - coder: missing=f1,f5; extra=-
  - reviewer: missing=-; extra=f2

### pg_004__seed_1
- qwen2.5-7b: coverage=0.438, precision=0.778, leak=0, tp=7, fp=2, fn=9
  - code-critic: missing=f3; extra=-
  - coder: missing=f1,f12,f3; extra=-
  - dispatcher: missing=-; extra=f3
  - plan-creator: missing=f3,f5; extra=-
  - plan-critic: missing=f3,f5,f8; extra=f11
- qwen2.5-14b: coverage=0.500, precision=0.800, leak=0, tp=8, fp=2, fn=8
  - code-critic: missing=f8; extra=-
  - coder: missing=f1,f12; extra=f9
  - dispatcher: missing=-; extra=-
  - plan-creator: missing=f10,f5; extra=-
  - plan-critic: missing=f3,f5,f8; extra=f9

### pg_006__seed_1
- qwen2.5-7b: coverage=0.500, precision=1.000, leak=0, tp=7, fp=0, fn=7
  - coder: missing=f7,f9; extra=-
  - dispatcher: missing=-; extra=-
  - reviewer: missing=f7,f9; extra=-
  - scientist: missing=f7,f8,f9; extra=-
- qwen2.5-14b: coverage=0.714, precision=0.909, leak=0, tp=10, fp=1, fn=4
  - coder: missing=f7; extra=f4
  - dispatcher: missing=-; extra=-
  - reviewer: missing=f7,f9; extra=-
  - scientist: missing=f9; extra=-

### pg_070__seed_1
- qwen2.5-7b: coverage=0.500, precision=1.000, leak=0, tp=7, fp=0, fn=7
  - field_collector: missing=f7,f9; extra=-
  - lead_analyst: missing=f7,f8,f9; extra=-
  - red_teamer: missing=f7,f9; extra=-
  - station_chief: missing=-; extra=-
- qwen2.5-14b: coverage=0.786, precision=0.917, leak=0, tp=11, fp=1, fn=3
  - field_collector: missing=-; extra=-
  - lead_analyst: missing=f9; extra=f1
  - red_teamer: missing=f1,f9; extra=-
  - station_chief: missing=-; extra=-
