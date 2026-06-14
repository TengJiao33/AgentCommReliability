# PACT Unrecovered Case Inspection

## What We Tried

I inspected the six PACT cases that remained most relevant after the
stable-wrong audit: five unrecovered-output cases and one yes/no polarity case.
This was a case-contact step over saved action-state traces.

No model call or GPU run was launched.

## What Happened

The six cases split like this:

| Sample | Surface | What appears |
| ---: | --- | --- |
| 13 | semantic polarity or predicate failure | Gold is `no`, but the saved public state leads the final answer to `yes`. |
| 14 | timeframe span contract | The output contains `from 1986 to 2013`; extractor keeps the whole sentence. |
| 21 | entity alias with evidence conflict | `Sonic the Hedgehog` over-specifies gold `Sonic`, while public state also confuses Sonic and Dr. Robotnik. |
| 24 | answer type priority error | The output contains `World's Best Goalkeeper`, but the extractor picks `1992`. |
| 43 | overlong object span | The output contains `sovereignty` plus extra phrase. |
| 44 | relation-tail entity extraction | The output contains `Vice President Nelson Rockefeller`, but the extractor picks `Alfred Balk`. |

## Things Noticed

Four cases are mostly answer-contract or extractor-priority problems: `14`,
`24`, `43`, and `44`. Their saved public fields already carry the necessary
answer-bearing text.

One case, `13`, is a real polarity/predicate problem under the saved public
state. It should not be treated as an extraction miss.

One case, `21`, is mixed. The final string `Sonic the Hedgehog` is close to the
gold answer `Sonic`, but the public state has an evidence-use conflict: it says
Jim Cummings voiced Dr. Robotnik from Sonic the Hedgehog, then turns that into
Sonic. That makes it a poor example for a simple parser-only fix.

## Loose Threads

- If we later make a tiny PACT rerun, first control answer contract and answer
  type instructions.
- See `reports/20260614-pact-question-aware-extraction.md` for the completed
  question-aware extraction probe. Keep `13` and `21` as likely non-parser or
  parser-overcredit sentinels.
- Do not scale HotpotQA while these surfaces remain entangled.

## Caveats

- Manual labels are case notes, not rates.
- No external evidence was retrieved; labels reflect the saved PACT trace and
  HotpotQA gold answers.
