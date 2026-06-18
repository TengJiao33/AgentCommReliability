---
name: repro-friction-memory
description: Use during reproduction-driven research when small operational blockers, formatting mismatches, environment quirks, data/cache issues, shell quoting failures, parser edge cases, output-path surprises, logging gaps, or remote-machine workflow mistakes appear. Captures reusable fixes and command patterns so Codex does not waste time rediscovering solved reproduction friction.
---

# Repro Friction Memory

## Purpose

Use this skill as the project's memory for small reproduction blockers. The goal is not to explain the research idea; the goal is to prevent repeated time loss on already-seen operational failures.

When a blocker is solved, convert it into a short rule, a reliable template, or a checklist item.

## What Belongs Here

Record issues that are small individually but costly when repeated:

- shell and quoting traps;
- remote SSH command patterns;
- data download/cache failures;
- model path and offline-loading quirks;
- parser or output-format mismatches;
- scripts writing outside `--out_dir`;
- debug/non-debug logging differences;
- hidden defaults in baseline code;
- GPU preflight and timeout habits;
- patch application and dirty-check routines.

Do not record passwords, tokens, private keys, proxy config contents, or broad research interpretations here.

## Use Pattern

1. Identify the blocker precisely.
2. Preserve the exact error or symptom in the run note if it affects reproduction.
3. Add a reusable prevention rule here.
4. Prefer a robust template over another one-off command.
5. Resume from the smallest smoke test that exercises the fixed path.

If the same class of blocker appears twice, update this skill before continuing.

## Current Rules

### Windows PowerShell To Remote SSH

Prefer the command shape with the fewest quoting layers. If a command fails because of quoting, stop escaping deeper and switch to PowerShell single quotes, a PowerShell here-string piped to remote Python, or a project-local launcher script.

For local inline Python in PowerShell, do not use bash heredocs such as
`python - <<'PY'`. Use a PowerShell here-string piped to Python instead:

```powershell
@'
print("local python ok")
'@ | python -
```

If the inline code imports project helper packages under `scripts/`, set
`PYTHONPATH` for that command:

```powershell
$env:PYTHONPATH='scripts'; @'
from peer_probe.answers import extract_final_answer
print(extract_final_answer('{final answer: 42}'))
'@ | python -
```

Simple remote command:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 'hostname'
```

If the local SSH config does not define `A800_2`, use the direct form from the
machine handbook:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 -p 10622 xuhaoming@124.128.251.61 'hostname'
```

If direct SSH times out but the user's local Clash SOCKS5 proxy is available,
route OpenSSH through the project stdio relay:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=20 -o ProxyCommand="python D:/develop/AgentCommReliability/scripts/ssh_socks5_proxy.py 127.0.0.1 7890 %h %p" A800_2 'hostname && date'
```

Before using it, confirm the proxy path can reach the SSH banner with a tiny
SOCKS5 handshake or a short `ssh hostname` smoke. Do not store proxy profiles,
tokens, or private network details in repo files.

Remote command with pipes or grep patterns:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 'cd /data/xuhaoming/yfy/research_workspace/baselines/DAR && grep -R "gsm8k\|data_size\|load_dataset" -n src | head -120'
```

Remote process checks with regex pipes should use remote shell quotes around the regex, not bare pipes:

```powershell
ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "pgrep -af 'python|torchrun|accelerate|run_' | grep -E 'xuhaoming/yfy|DAR|mad-mm|src/main.py' || true"
```

If the regex is not quoted on the remote side, bash may try to execute `torchrun`, `accelerate`, or other regex fragments as commands.

Remote Python data smoke, no model load:

```powershell
@'
from argparse import Namespace
from data.gsm8k import load_data

args = Namespace(data="gsm8k", data_size=5)
questions, labels = load_data(args, split="test")
print(len(questions), len(labels))
print(questions[0][:120].replace("\n", " "))
print(labels[:5])
'@ | ssh -o BatchMode=yes -o ConnectTimeout=10 A800_2 "cd /data/xuhaoming/yfy/research_workspace/baselines/DAR && PYTHONPATH=src HF_HOME=/data/xuhaoming/yfy/research_workspace/hf_home /data/xuhaoming/yfy/research_workspace/envs/mad-mm-vllm063/bin/python -"
```

Do not use bash here-docs through PowerShell for remote Python snippets. They are too easy to mangle.

If PowerShell/SSH strips quotes or turns here-doc terminators into CRLF, send the remote script as base64 and decode it on the remote side:

```powershell
$code = @'
print("remote python ok")
'@
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($code))
ssh A800_2 "echo $b64 | base64 -d | /path/to/python"
```

Use the same pattern for short bash scripts:

```powershell
$script = @'
set -euo pipefail
hostname
date
'@
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($script))
ssh A800_2 "echo $b64 | base64 -d | bash"
```

When a PowerShell-generated remote bash script will be saved and launched with
`nohup`, normalize line endings before encoding, or avoid the temporary script
entirely. CRLF can make bash look for paths such as
`scripts/run_hiddenbench_probe_a8002.sh\r`, which surfaces as a misleading
`No such file or directory` even when the file exists.

Reliable background pattern:

```powershell
$script = @'
set -euo pipefail
cd /data/xuhaoming/yfy/research_workspace
nohup env RUN_ID="example" GPU_ID="7" PORT="8047" \
  bash scripts/run_hiddenbench_probe_a8002.sh > logs/example.outer.log 2>&1 < /dev/null &
echo "PID=$!"
'@
$script = $script.Replace("`r`n", "`n")
$b64 = [Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes($script))
ssh A800_2 "bash -lc 'echo $b64 | base64 -d | bash'"
```

For remote bash cleanup from PowerShell, avoid piping a raw here-string directly
to `ssh ... bash -s`; Windows BOM/CRLF can make bash see `﻿set` or `esac\r`.
Use a PowerShell single-quoted `ssh A800_2 'bash -lc ''...'''` command for
short exact-path cleanup, or base64-decode the script on the remote side for
multi-line cleanup.

### Remote Data And Cache

Before loading a model, run a data-only smoke when the dataset may require Hugging Face, ModelScope, or local cache access.

If remote Hugging Face access fails, treat it as an environment/data blocker, not a method failure. Prefer existing project-local processed data or a documented offline fallback.

Observed example:

```text
openai/gsm8k through datasets.load_dataset failed on A800_2 because huggingface.co was unreachable and no cache entry existed.
```

Reusable response:

- check whether another reproduced baseline already has the dataset locally;
- use a project-local data path under `/data/xuhaoming/yfy/research_workspace`;
- document the fallback as a data-loading adaptation, not a method change.

### Output Paths

Check whether upstream code respects `--out_dir` before launching a longer run.

If it writes to repository-local `out/` or `result/`, patch only artifact placement and record that method behavior is unchanged.

### Partial Packet Runs

When a runner supports a generation `LIMIT`, verify whether evaluation also uses
the same sliced packet. Some project runners pass `LIMIT` only to generation and
then evaluate against the full `PACKET`, which makes a successful smoke exit
with missing-output errors.

Observed example:

```text
run_math_epistemic_type_erasure_a8002.sh generated 24/24 or 48/48 limited
MATH sender-receiver rows, then the evaluator exited with "Missing outputs for
222 rows" or "Missing outputs for 198 rows" because it scored against the full
246-row packet.
```

Reusable response:

- inspect the output JSONL count before treating the run as failed;
- create a matching sliced packet for the completed prefix and score locally, or
  patch the runner to emit and pass the sliced packet path to evaluation;
- record the runner exit as evaluation plumbing when generation completed cleanly
  and model outputs are present;
- use the full unsliced packet for the final behavior run once the smoke passes.

### Parser Compatibility

For LLM output parsers, inspect both the prompt suffix and real model output before blaming accuracy.

Observed example:

```text
Qwen2.5-7B-Instruct emitted escaped braces such as \{final answer: 371.75\}; the DAR arithmetic parser originally only matched unescaped braces.
```

Observed example:

```text
Peer-exposure MATH contact parsed LaTeX fractions such as \frac{5}{3} as the last integer token (`3`), and a final-answer regex that stopped at the first nested brace parsed `{final answer: \(\frac{5}{3}\)}` as `5`.
```

Observed example:

```text
MATH typed-public-state statistics changed under a semantic audit because boxed answers such as `1 - 12i`, `8\pi - 16`, `\sqrt{2}`, `61,328`, `144 \mbox{ m}^3`, and `1\frac{4}{5}` were not safely represented by the old last-number normalizer.
```

Observed example:

```text
MATH peer-exposure `answer_only` surfaces reused the older parsed numeric answer field, so symbolic peer answers such as `2\sqrt{3}`, `1 - 12i`, `14\pi`, and `18\sqrt{3}` were displayed as lossy slots such as `3`, `12`, `14`, and `3`.
```

Observed example:

```text
A MATH Authority Genesis packet builder initially removed any peer-surface line containing `Final answer from this peer: ...`; compact one-line peer excerpts then lost the whole rationale instead of only the final-answer slot.
```

Reusable response:

- patch the regex narrowly;
- add a parser smoke for nested-brace `\frac{a}{b}` and plain `a/b` answers before reading MATH accuracy or peer correctness labels;
- keep the expected answer format unchanged;
- record parser compatibility as evaluation plumbing, not a communication-method change.
- for MATH runs with symbolic answers, re-extract raw final-answer strings and compare against original boxed answers with a semantic/equivalence audit before scaling or claiming a peer-surface effect;
- keep semantic-unknown records explicit instead of silently falling back to numeric parsing.
- for MATH peer-exposure controls, do not treat `answer_only` as a clean final-answer-authority surface unless it is built from the raw semantic answer string, not the old numeric parser field; audit displayed answer-only slots against raw peer answers before interpreting answer-only utility/harm.
- when redacting final-answer slots from compact peer excerpts, remove only the final-answer phrase/span rather than dropping the whole line; smoke-check for empty or near-empty artifact text after redaction.
- for MATH ladder runs that ask for reasoning plus a final answer, do not reuse
  short QA caps such as `max_tokens=256` without checking completion-token cap
  hits. Qwen2.5-14B on the MATH Authority Genesis Ladder hit `256` tokens on
  `441/670` rows and produced `435` semantic unknowns by truncating near
  `{final answer:`. Use a configurable runner cap, start around
  `MAX_TOKENS=768`, and record both cap-hit count and semantic-unknown count
  before interpreting authority-violation rates.

For numeric answer leakage or answer redaction audits, do not use a right
boundary like `(?![\d.])`. It misses sentence-final answers such as `28800.`
because the period is punctuation, not a decimal tail. Use a boundary that
rejects a following digit or `.\d` decimal continuation while allowing ordinary
sentence punctuation.

### Debug Logging

Check whether non-debug mode truncates histories.

Observed example:

```text
DAR non-debug mode stores only the first 10 sample histories, even for 100-sample runs.
```

Reusable response:

- use non-debug for quick metric reproduction;
- use `--debug` or patch logging only when trace-level evidence is needed;
- record any logging expansion separately from method behavior.

### GPU Job Discipline

Before any GPU run:

- check host access;
- check GPU memory;
- inspect active Python processes without killing anything;
- check repo status and patches;
- use `CUDA_VISIBLE_DEVICES`;
- use `timeout`;
- write logs under the project log directory;
- write outputs under the project results directory;
- record command, log path, output path, and timeout before or immediately after launch.

### Remote Code Changes

For persistent remote source changes:

- create or update a patch under `baselines/<method>/patches/`;
- apply the patch remotely;
- verify with `git diff`;
- record whether the patch changes method logic, data loading, evaluation parsing, or artifact placement.

Do not use `git reset`, `git clean`, or ad hoc destructive cleanup to recover from reproduction friction.

When hand-writing a patch file, verify hunk counts before copying it remotely. A quick local count of old/new hunk lines can prevent `corrupt patch at line ...` loops. If applying still fails, use the remote `git diff` after the exact source edit as the canonical patch content.

If a source archive came from Windows or was transferred from a Windows checkout, check line endings before applying patches:

```bash
file src/llm/profile_embedding.py
```

If only one target file is affected, normalize that file and the patch file to LF before applying. If hunk matching still fails, generate a unified diff on the remote host from the actual remote source and target content, then dry-run the generated patch.

### Broken Dependency Wheels

Do not assume `pip install` means the imported module exists. Some tiny dependency wheels may install metadata but not the expected package.

Observed example:

```text
vLLM -> outlines -> pyairports.airports failed because pyairports==0.0.1 installed only sample/ and dist-info, not pyairports/.
```

Reusable response:

- run `python -c "import package.module"` after installing a suspicious dependency;
- inspect `pip show -f <package>`;
- if the dependency is only needed for an unused import-time enum, record a minimal compatibility shim in the env and mark it as backend plumbing, not method logic;
- prefer fixing the environment over patching baseline method code.
