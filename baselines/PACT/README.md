# PACT

Baseline notes for PACT, Protocolized Action-state Communication and Transmission.

Files:

- `source.md`: upstream source, code map, setup notes, and reproduction constraints.
- `reproduction.md`: A800_2 reproduction status and smoke results.
- `patches/`: project-local changes used on A800_2.
- `upstream/`: git submodule for the upstream implementation.

Current scope:

- split-evidence HotpotQA interaction;
- two agents, alternating turns;
- public message surface restricted to action-state records;
- first local target is a bounded A800_2 smoke with Qwen2.5-7B-Instruct, because Qwen3-14B is not currently present on the shared model mount.
