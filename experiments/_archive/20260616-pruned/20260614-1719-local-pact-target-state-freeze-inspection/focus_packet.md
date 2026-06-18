# PACT Target-State Freeze Inspection Packet

This packet is diagnostic only. It inspects saved offset150 PACT traces
to see where a first-turn frozen target state might have been meaningful.

## Summary

- Records: `50`
- Focus records: `16`
- Unstable target slots: `23`
- First/final target mismatch: `22`

## Buckets

- `answer_type_drift`: `7`
- `regression_despite_stable_target`: `4`
- `rescue_despite_stable_target`: `1`
- `stable_target`: `22`
- `target_returns_after_drift`: `1`
- `template_collapse`: `4`
- `visible_target_drift`: `7`
- `visible_target_drift_regression`: `4`

## Focus Cases

### Sample 189 - right_to_wrong - visible_target_drift_regression

- Question: Tefik Selim Mborja was a part of a party that held power in Albania until what year?
- Gold: `1943`
- Final-only answer: `1943`
- Compact-target answer: `1992`
- First target slot: `[year; Albanian Fascist Party; held power]`
- Final target slot: `[year; Party of Labour of Albania; held power]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [year; Albanian Fascist Party; held power] | Provide the year when the Albanian Fascist Party lost power. | The Albanian Fascist Party held power until 1944. |
| 1 | Agent B | [year; Albanian Fascist Party; lost power] | Provide the year when the Albanian Fascist Party lost power. | The Albanian Fascist Party lost power in 1943. |
| 2 | Agent A | [year; Albanian Fascist Party; lost power] | Provide the year when the Albanian Fascist Party lost power. | The Albanian Fascist Party lost power in 1943. |
| 3 | Agent B | [year; Party of Labour of Albania; held power] | Provide the year when the Party of Labour of Albania lost power. | 1992 |

### Sample 193 - right_to_wrong - visible_target_drift_regression

- Question: In which city are the headquarters of the American research and scientific development company where Ravi Sethi worked as computer scientist located?
- Gold: `murray hill`
- Final-only answer: `Murray Hill`
- Compact-target answer: `Murray Hill, New Jersey`
- First target slot: `[city; Ravi Sethi; worked as computer scientist]`
- Final target slot: `[city; Bell Labs; headquarters]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [city; Ravi Sethi; worked as computer scientist] | Provide information about the city where Ravi Sethi worked. | Ravi Sethi worked at Bell Labs. |
| 1 | Agent B | [city; Bell Labs; headquarters] | Provide information about the headquarters city of Bell Labs. | The headquarters of Bell Labs are located in Murray Hill, New Jersey. |
| 2 | Agent A | [city; Bell Labs; headquarters] | Provide information on the city where Bell Labs' headquarters is located. | The headquarters of Bell Labs are located in Murray Hill, New Jersey. |
| 3 | Agent B | [city; Bell Labs; headquarters] | The city where Bell Labs' headquarters is located. | Murray Hill, New Jersey |

### Sample 197 - right_to_wrong - visible_target_drift_regression

- Question: Robert Smith founded the multinational company headquartered in what city?
- Gold: `golden valley minnesota`
- Final-only answer: `Golden Valley, Minnesota`
- Compact-target answer: `compact targetstate rule`
- First target slot: `[city; Robert Smith; founded company]`
- Final target slot: `[city; General Mills; founded]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [city; Robert Smith; founded company] | Provide information about the city where Robert Smith founded his company. | Robert Smith founded General Mills in 1856. |
| 1 | Agent B | [city; General Mills; founded] | Provide the city where General Mills was founded. | General Mills is headquartered in Golden Valley, Minnesota. |
| 2 | Agent A | [city; General Mills; founded] | Provide the city where General Mills was founded. | The context does not specify the city where General Mills was founded. |
| 3 | Agent B | [city; General Mills; founded] | Provide the city where General Mills was founded. | Golden Valley, Minnesota |

### Sample 199 - right_to_wrong - visible_target_drift_regression

- Question: Considered the strongest recorded tropical cyclone, which cyclone had a film made about it in 2007?
- Gold: `1999 odisha cyclone`
- Final-only answer: `1999 Odisha cyclone`
- Compact-target answer: `Kathantara`
- First target slot: `[film; 1999 Odisha cyclone; 2007]`
- Final target slot: `[film; Cyclone Gonu; 2007]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [film; 1999 Odisha cyclone; 2007] | Provide information about a film made about a cyclone in 2007. | A film named Kathantara was made in 2007 about the 1999 Odisha cyclone. |
| 1 | Agent B | [film; Cyclone Gonu; 2007] | Provide information about a film made about Cyclone Gonu in 2007. | No film about Cyclone Gonu is mentioned in the given context. |
| 2 | Agent A | [film; 1999 Odisha cyclone; 2007] | Provide information about a film made about the 1999 Odisha cyclone in 2007. | Kathantara is a film made about the 1999 Odisha cyclone in 2007. |
| 3 | Agent B | [film; Cyclone Gonu; 2007] | Provide information about a film made about Cyclone Gonu in 2007. | No film about Cyclone Gonu is mentioned in the given context. |

### Sample 153 - right_to_wrong - regression_despite_stable_target

- Question: The songs from the sountrack to "When Harry Met Sally" are performed by a singer that has had how many top 20 US albums?
- Gold: `seven`
- Final-only answer: `seven`
- Compact-target answer: `7`
- First target slot: `[number; Harry Connick Jr.; top 20 US albums]`
- Final target slot: `[number; Harry Connick Jr.; top 20 US albums]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A |  | Provide the number of top 20 US albums for Harry Connick Jr. | Harry Connick Jr. performed the songs from the soundtrack to "When Harry Met Sally...". |
| 1 | Agent B | [number; Harry Connick Jr.; top 20 US albums] | Provide the number of top 20 US albums for Harry Connick Jr. | Harry Connick Jr. has had seven top 20 US albums. |
| 2 | Agent A | [number; Harry Connick Jr.; top 20 US albums] | Confirm the number of top 20 US albums for Harry Connick Jr. | Harry Connick Jr. has had seven top 20 US albums. |
| 3 | Agent B | [number; Harry Connick Jr.; top 20 US albums] | Provide the number of top 20 US albums for Harry Connick Jr. | Harry Connick Jr. has had seven top 20 US albums. |

### Sample 154 - right_to_wrong - regression_despite_stable_target

- Question: Are Broughtonia and Laeliocattleya both orchids?
- Gold: `yes`
- Final-only answer: `Yes`
- Compact-target answer: `compact targetstate rule`
- First target slot: `[yes/no; Broughtonia and Laeliocattleya; both orchids]`
- Final target slot: `[yes/no; Broughtonia and Laeliocattleya; both orchids]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [yes/no; Broughtonia and Laeliocattleya; both orchids] | Provide if Laeliocattleya is an orchid. | Laeliocattleya is an orchid. |
| 1 | Agent B | [yes/no; Broughtonia and Laeliocattleya; both orchids] | Provide if Broughtonia is an orchid. | Broughtonia is an orchid. |
| 2 | Agent A | [yes/no; Broughtonia and Laeliocattleya; both orchids] | Confirm if Laeliocattleya is an orchid. | Laeliocattleya is an orchid. |
| 3 | Agent B | [yes/no; Broughtonia and Laeliocattleya; both orchids] | Confirm if Broughtonia and Laeliocattleya are both orchids. | Yes |

### Sample 164 - right_to_wrong - regression_despite_stable_target

- Question: Who did the Star and Dagger bass player marry?
- Gold: `sean yseult`
- Final-only answer: `Sean Yseult`
- Compact-target answer: `Unknown`
- First target slot: `[person; Star and Dagger bass player; spouse]`
- Final target slot: `[person; Star and Dagger bass player; spouse]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [person; Star and Dagger bass player; spouse] | Provide information about the Star and Dagger bass player's marriage. | The context does not contain information about the Star and Dagger bass player's marriage. |
| 1 | Agent B | [person; Star and Dagger bass player; spouse] | Provide information about Sean Yseult's marriage. | Sean Yseult is the Star and Dagger bass player, but no information about her spouse is provided. |
| 2 | Agent A | [person; Star and Dagger bass player; spouse] | Request information about Sean Yseult's spouse. | No information about Sean Yseult's spouse is provided in the context. |
| 3 | Agent B | [person; Star and Dagger bass player; spouse] | Request information about Sean Yseult's spouse. | None of the provided paragraphs contain information about Sean Yseult's spouse. |

### Sample 182 - right_to_wrong - regression_despite_stable_target

- Question: Which English musician is known for both the songs "See Yourself" and "Withing You Without You"?
- Gold: `george harrison`
- Final-only answer: `George Harrison`
- Compact-target answer: `action result george harrison`
- First target slot: `[musician; George Harrison; known for both "See Yourself" and "Within You Without You"]`
- Final target slot: `[musician; George Harrison; known for both "See Yourself" and "Within You Without You"]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [musician; George Harrison; known for both "See Yourself" and "Within You Without You"] | Request information about "Within You Without You" from Agent B. | Waiting for information about "Within You Without You" to confirm if it was also by George Harrison. |
| 1 | Agent B | [musician; George Harrison; known for both "See Yourself" and "Within You Without You"] | Confirm if "Within You Without You" was written by George Harrison. | "Within You Without You" was written by George Harrison. |
| 2 | Agent A | [musician; George Harrison; known for both "See Yourself" and "Within You Without You"] | Confirm if George Harrison is the answer. | George Harrison is known for both "See Yourself" and "Within You Without You". |
| 3 | Agent B | [musician; George Harrison; known for both "See Yourself" and "Within You Without You"] | Confirm if George Harrison is known for both songs. | George Harrison |

### Sample 173 - wrong_to_right - template_collapse

- Question: Which songwriting duo composed music for "La La Land", and created lyrics for "A Christmas Story: The Musical"?
- Gold: `pasek paul`
- Final-only answer: `Pasek and Paul`
- Compact-target answer: `Pasek & Paul`
- First target slot: `[songwriting duo; composed "La La Land"; created lyrics for "A Christmas Story: The Musical"]`
- Final target slot: `[answer type; anchor entity or entities; required qualifier]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [songwriting duo; composed "La La Land"; created lyrics for "A Christmas Story: The Musical"] | Provide the songwriting duo that composed "La La Land" and created lyrics for "A Christmas Story: The Musical". | Pasek & Paul created lyrics for "A Christmas Story: The Musical". |
| 1 | Agent B | [songwriting duo; composed "La La Land"; created lyrics for "A Christmas Story: The Musical"] | Provide the songwriting duo that composed "La La Land". | Pasek and Paul composed "La La Land". |
| 2 | Agent A | [answer type; songwriting duo; composed "La La Land" and created lyrics for "A Christmas Story: The Musical"] | Confirm the songwriting duo for both musical works. | Pasek and Paul composed "La La Land" and created lyrics for "A Christmas Story: The Musical". |
| 3 | Agent B | [answer type; anchor entity or entities; required qualifier] | [Pasek and Paul composed "La La Land"] | [Pasek & Paul composed "La La Land" and created lyrics for "A Christmas Story: The Musical"] |

### Sample 152 - wrong_to_right - answer_type_drift

- Question: The lamp used in many lighthouses is similiar to this type of lamp patented in 1780 by Aimé Argand?
- Gold: `argand lamp`
- Final-only answer: `Yes`
- Compact-target answer: `Argand lamp`
- First target slot: `[lamp type; Argand; patented in 1780]`
- Final target slot: `[Argand lamp; patented in 1780; oil lamp]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [lamp type; Argand; patented in 1780] | Provide information on the lamp patented by Argand in 1780. | Aimé Argand patented a lamp in 1780. |
| 1 | Agent B | [Argand lamp; patented in 1780] | Provide details about the Argand lamp patented in 1780. | The Argand lamp is a kind of oil lamp. |
| 2 | Agent A | [Argand lamp; patented in 1780; oil lamp] | Provide information on the similarity of the lamp used in lighthouses to the Argand lamp. | The Lewis lamp used a similar design to an Argand lamp. |
| 3 | Agent B | [Argand lamp; patented in 1780; oil lamp] | Provide information on the similarity of the lamp used in lighthouses to the Argand lamp. | The Lewis lamp, used in lighthouses, had a design similar to the Argand lamp. |

### Sample 176 - wrong_to_right - answer_type_drift

- Question: Works by Hanna Leena Kristiina Varis are part of a collection in a museum that houses approximately 65,000 what?
- Gold: `drawings`
- Final-only answer: `drawings and prints`
- Compact-target answer: `drawings`
- First target slot: `[artworks; Hanna Leena Kristiina Varis; part of a museum collection]`
- Final target slot: `[drawings; Albertina; approximately 65,000]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [artworks; Hanna Leena Kristiina Varis; part of a museum collection] | Provide information about the museum collection size related to Hanna Leena Kristiina Varis's works. | The context does not provide the size of the museum collection related to Hanna Leena Kristiina Varis's works. |
| 1 | Agent B | [artworks; Albertina; approximately 65,000] | The Albertina houses approximately 65,000 drawings. | The museum, Albertina, holds approximately 65,000 drawings. |
| 2 | Agent A | [drawings; Albertina; approximately 65,000] | Provide information about the Albertina's collection size related to drawings. | The Albertina houses approximately 65,000 drawings. |
| 3 | Agent B | [drawings; Albertina; approximately 65,000] | The Albertina houses approximately 65,000 drawings. | The Albertina houses approximately 65,000 drawings. |

### Sample 188 - wrong_to_right - answer_type_drift

- Question: Do The Importance of Being Icelandic and The Five Obstructions belong to different film genres ?
- Gold: `no`
- Final-only answer: `Yes`
- Compact-target answer: `No`
- First target slot: `[genre; The Importance of Being Icelandic; documentary]`
- Final target slot: `[answer type; The Importance of Being Icelandic and The Five Obstructions; different genres]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [genre; The Importance of Being Icelandic; documentary] | Provide the genre of The Importance of Being Icelandic. | The Importance of Being Icelandic is a documentary. |
| 1 | Agent B | [genre; The Five Obstructions; documentary] | Provide the genre of The Five Obstructions. | The Five Obstructions is a documentary. |
| 2 | Agent A | [answer type; The Importance of Being Icelandic and The Five Obstructions; different genres] | Provide if The Importance of Being Icelandic and The Five Obstructions belong to different film genres. | The Importance of Being Icelandic and The Five Obstructions belong to the same film genre. |
| 3 | Agent B | [answer type; The Importance of Being Icelandic and The Five Obstructions; different genres] | Compare the genres of The Importance of Being Icelandic and The Five Obstructions. | No |

### Sample 185 - wrong_to_right - rescue_despite_stable_target

- Question: What season was the character introduced that becomes the main antagonist in the  following season, from the animated television series created by Bryan Konietzko and Michael Dante DiMartino as a sequel to "", which aired from 2005 to 2008?
- Gold: `third`
- Final-only answer: `third season`
- Compact-target answer: `third`
- First target slot: `[Season; Kuvira; introduced and main antagonist]`
- Final target slot: `[Season; Kuvira; introduced and main antagonist]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [Season; Kuvira; introduced and main antagonist] | Provide the season of introduction and antagonist status of Kuvira. | Kuvira is introduced in the third season and becomes the main antagonist in the fourth season. |
| 1 | Agent B | [Season; Kuvira; introduced and main antagonist] | Provide the season of introduction and antagonist status of Kuvira. | Kuvira is introduced in the third season and becomes the main antagonist in the fourth season. |
| 2 | Agent A | [Season; Kuvira; introduced and main antagonist] | Confirm if the provided information about Kuvira is sufficient to answer the question. | Kuvira is introduced in the third season and becomes the main antagonist in the fourth season. |
| 3 | Agent B | [Season; Kuvira; introduced and main antagonist] | [Kuvira is introduced in the third season and becomes the main antagonist in the fourth season.] | Kuvira is introduced in the third season and becomes the main antagonist in the fourth season. |

### Sample 163 - stable_wrong - template_collapse

- Question: What British singer-songwriter hosted the 16th Annual Young Hollywood Awards?
- Gold: `kelly lee osbourne`
- Final-only answer: `Kelly Osbourne`
- Compact-target answer: `Kelly Osbourne`
- First target slot: `[person; host; 16th Annual Young Hollywood Awards]`
- Final target slot: `[answer type; anchor entity or entities; required qualifier]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [person; host; 16th Annual Young Hollywood Awards] | Provide the host of the 16th Annual Young Hollywood Awards. | Kelly Osbourne hosted the 16th Annual Young Hollywood Awards. |
| 1 | Agent B | [person; host; 16th Annual Young Hollywood Awards] | Verify if Kelly Osbourne is a British singer-songwriter. | Kelly Osbourne is a British singer-songwriter. |
| 2 | Agent A | [answer type; anchor entity or entities; required qualifier] | Confirm if Kelly Osbourne is the British singer-songwriter who hosted the 16th Annual Young Hollywood Awards. | Kelly Osbourne hosted the 16th Annual Young Hollywood Awards. |
| 3 | Agent B | [answer type; anchor entity or entities; required qualifier] | Verify if Kelly Osbourne is the British singer-songwriter who hosted the 16th Annual Young Hollywood Awards. | Kelly Osbourne |

### Sample 160 - stable_wrong - answer_type_drift

- Question: Who held the record for the longest service in the Australian Parliament for a woman, and was surpassed by  a former Australian politician who was the 29th Speaker of the House of Representatives?
- Gold: `kathryn jean martin`
- Final-only answer: `Kathy Sullivan`
- Compact-target answer: `Kathy Sullivan`
- First target slot: `[person; Kathy Sullivan; held longest service record for woman]`
- Final target slot: `[answer type; Kathy Sullivan; ]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [person; Kathy Sullivan; held longest service record for woman] | Provide the name of the person who held the record for the longest service in the Australian Parliament for a woman. | Kathy Sullivan held the record for the longest service in the Australian Parliament for a woman. |
| 1 | Agent B | [person; Bronwyn Bishop; 29th Speaker of the House of Representatives] | Provide the name of the person who was the 29th Speaker of the House of Representatives. | Bronwyn Bishop was the 29th Speaker of the House of Representatives. |
| 2 | Agent A | [answer type; Kathy Sullivan; Bronwyn Bishop] | Confirm if the person who held the longest service record for a woman in the Australian Parliament was surpassed by the 29th Speaker of the House of Representatives. | Bronwyn Bishop surpassed Kathy Sullivan's record for the longest service in the Australian Parliament for a woman. |
| 3 | Agent B | [answer type; Kathy Sullivan; ] | Provide the name of the person who held the longest service record for a woman in the Australian Parliament. | Kathy Sullivan |

### Sample 184 - stable_wrong - visible_target_drift

- Question: What year did the series on CBS, starring the actor who known for his role in "Rebel Without a Cause," air?
- Gold: `1952`
- Final-only answer: `1975`
- Compact-target answer: `1955`
- First target slot: `[year; actor; starred in "Rebel Without a Cause"]`
- Final target slot: `[year; "Rebel Without a Cause"; aired]`

| Turn | Agent | Target Slot | Action Required | Action Result |
| ---: | --- | --- | --- | --- |
| 0 | Agent A | [year; actor; starred in "Rebel Without a Cause"] | Provide the name of the actor who starred in "Rebel Without a Cause". | The actor who played James Dean's character's father in "Rebel Without a Cause" is Jim Backus. |
| 1 | Agent B | [year; Jim Backus; starred in his own show] | Provide the year Jim Backus starred in his own show. | The show "The Jim Backus Show" aired in 1976. |
| 2 | Agent A | [year; "The Jim Backus Show"; aired] | Provide the year "The Jim Backus Show" aired. | "The Jim Backus Show" aired in 1976. |
| 3 | Agent B | [year; "Rebel Without a Cause"; aired] | Provide the year "Rebel Without a Cause" aired. | 1955 |
